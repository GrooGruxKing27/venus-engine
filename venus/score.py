import colorsys
import numpy as np


def _rgb_to_hsv(rgb):
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360.0, s, v


def _hue_distance(h1: float, h2: float) -> float:
    diff = abs(h1 - h2)
    return min(diff, 360.0 - diff)


# (max_hue_distance, harmony_name, base_score)
_HARMONY_TABLE = [
    ( 15, "monochromatic",       88),
    ( 45, "analogous",           78),
    (100, "tension",             45),
    (130, "triadic",             55),
    (160, "split-complementary", 63),
    (180, "complementary",       72),
]

_PATTERN_MODIFIERS = {
    ("solid",    "solid"):     +5,
    ("solid",    "patterned"):  0,
    ("patterned","solid"):      0,
    ("patterned","patterned"): -12,
}


def _hue_score(dist: float) -> tuple[str, int]:
    for threshold, name, score in _HARMONY_TABLE:
        if dist <= threshold:
            return name, score
    return "complementary", 72


def _weighted_value(colors_with_pct) -> float:
    """Return the coverage-weighted average brightness (V in HSV) for a palette."""
    return sum(_rgb_to_hsv(c)[2] * p for c, p in colors_with_pct)


def compute(colors1, colors2, pattern1: str, pattern2: str) -> tuple[int, str, str]:
    """
    Compute a compatibility score and explanation for two garments.

    Args:
        colors1, colors2: list of (rgb_array, percentage) from extract_colors().
        pattern1, pattern2: 'solid' or 'patterned'.

    Returns:
        (score, explanation, harmony_type)

    Scoring approach:
        Every color in garment 1 is compared with every color in garment 2.
        Each pair is weighted by its combined pixel coverage (pct1 * pct2) so
        that dominant colors drive the result. Value (brightness) contrast
        between the two palettes adds a small bonus for intentional dark/light
        pairings.
    """
    weighted_base = 0.0
    total_weight = 0.0
    dominant_harmony = None
    dominant_weight = 0.0

    for c1, pct1 in colors1:
        h1, s1, _ = _rgb_to_hsv(c1)
        for c2, pct2 in colors2:
            h2, s2, _ = _rgb_to_hsv(c2)
            weight = pct1 * pct2

            if s1 < 0.15 and s2 < 0.15:
                harmony, base = "neutral-neutral", 88
            elif s1 < 0.15 or s2 < 0.15:
                harmony, base = "neutral", 82
            else:
                harmony, base = _hue_score(_hue_distance(h1, h2))

            weighted_base += base * weight
            total_weight += weight

            if weight > dominant_weight:
                dominant_weight = weight
                dominant_harmony = harmony

    base_score = weighted_base / total_weight

    # Value contrast: reward clear dark/light separation (+5)
    v_contrast = abs(_weighted_value(colors1) - _weighted_value(colors2))
    value_mod = 5 if v_contrast > 0.45 else 0

    pattern_mod = _PATTERN_MODIFIERS[(pattern1, pattern2)]
    score = int(min(100, max(0, base_score + pattern_mod + value_mod)))
    explanation = _explain(score, dominant_harmony, pattern1, pattern2, v_contrast)
    return score, explanation, dominant_harmony


def _explain(score: int, harmony_type: str, pattern1: str, pattern2: str, v_contrast: float = 0.0) -> str:
    harmony_lines = {
        "monochromatic":
            "The two pieces share the same hue family. Monochromatic outfits read "
            "as a single unified tone — inherently cohesive.",
        "analogous":
            "The two pieces sit close to each other on the color wheel (analogous). "
            "The result is harmonious without being too matchy.",
        "complementary":
            "The two pieces are opposite each other on the color wheel (complementary). "
            "The contrast is bold and intentional — works best when one color clearly dominates.",
        "split-complementary":
            "The hues form a split-complementary relationship. There's contrast without "
            "the full tension of direct opposites — a versatile pairing.",
        "triadic":
            "The hues are roughly 120° apart (triadic). This is a dynamic, high-energy "
            "combination that requires balance.",
        "tension":
            "The hues don't align with a standard harmonic relationship. "
            "The combination can feel unresolved or visually clashing.",
        "neutral":
            "One piece is a neutral (black, white, or gray). "
            "Neutrals are highly versatile and pair well with almost any color.",
        "neutral-neutral":
            "Both pieces are neutrals. The result is clean, calm, and easy to wear — "
            "classic monochromatic dressing.",
    }

    pattern_lines = {
        ("solid",    "solid"):
            "Both pieces are solid, keeping the look clean and uncluttered.",
        ("solid",    "patterned"):
            "The mix of solid and patterned adds texture without visual overload.",
        ("patterned","solid"):
            "The mix of patterned and solid adds texture without visual overload.",
        ("patterned","patterned"):
            "Both pieces carry patterns, adding complexity — they can compete for visual attention.",
    }

    if v_contrast > 0.45:
        contrast_line = "The pieces also differ significantly in lightness, which adds definition and prevents the look from feeling flat."
    elif v_contrast < 0.1:
        contrast_line = "Both pieces sit at a similar lightness level, creating a seamless tonal blend."
    else:
        contrast_line = ""

    harmony_line = harmony_lines.get(harmony_type, "")
    pattern_line = pattern_lines.get((pattern1, pattern2), "")
    verdict = _verdict(score)
    parts = [p for p in [harmony_line, pattern_line, contrast_line] if p]
    return " ".join(parts) + f"\n\nScore: {score}/100 — {verdict}"


def _verdict(score: int) -> str:
    if score >= 85:
        return "Strong match."
    elif score >= 70:
        return "Good pairing."
    elif score >= 55:
        return "Works with intention."
    elif score >= 40:
        return "Proceed with caution."
    else:
        return "Likely to clash."
