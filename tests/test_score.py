import numpy as np
import pytest
from venus.score import compute, _hue_distance, _hue_score, _weighted_value


def _palette(rgb, pct=1.0):
    return [(np.array(rgb), pct)]


def _two_color(rgb1, pct1, rgb2, pct2):
    return [(np.array(rgb1), pct1), (np.array(rgb2), pct2)]


class TestHueDistance:
    def test_identical_hues(self):
        assert _hue_distance(0, 0) == 0

    def test_opposite_hues(self):
        assert _hue_distance(0, 180) == 180

    def test_circular_wrap(self):
        # 350° and 10° are only 20° apart going the short way around
        assert _hue_distance(350, 10) == 20

    def test_symmetric(self):
        assert _hue_distance(30, 200) == _hue_distance(200, 30)

    def test_max_distance_is_180(self):
        for a, b in [(0, 180), (90, 270), (45, 225)]:
            assert _hue_distance(a, b) <= 180


class TestHueScore:
    def test_monochromatic_range(self):
        name, score = _hue_score(0)
        assert name == "monochromatic"
        assert score == 88

    def test_analogous_range(self):
        name, score = _hue_score(30)
        assert name == "analogous"
        assert score == 78

    def test_tension_range(self):
        name, score = _hue_score(70)
        assert name == "tension"

    def test_complementary_boundary(self):
        name, score = _hue_score(180)
        assert name == "complementary"

    def test_score_is_int(self):
        _, score = _hue_score(45)
        assert isinstance(score, int)


class TestWeightedValue:
    def test_pure_white(self):
        palette = [(np.array([255, 255, 255]), 1.0)]
        assert abs(_weighted_value(palette) - 1.0) < 0.01

    def test_pure_black(self):
        palette = [(np.array([0, 0, 0]), 1.0)]
        assert abs(_weighted_value(palette) - 0.0) < 0.01

    def test_fifty_fifty_blend(self):
        palette = [
            (np.array([255, 255, 255]), 0.5),
            (np.array([0, 0, 0]), 0.5),
        ]
        assert abs(_weighted_value(palette) - 0.5) < 0.01

    def test_dominant_color_drives_value(self):
        # 90% black, 10% white → should be close to 0
        palette = [
            (np.array([0, 0, 0]), 0.9),
            (np.array([255, 255, 255]), 0.1),
        ]
        assert _weighted_value(palette) < 0.2


class TestCompute:
    def test_identical_palettes_are_monochromatic(self):
        blue = _palette([50, 80, 200])
        score, _, harmony = compute(blue, blue, "solid", "solid")
        assert harmony == "monochromatic"
        assert score >= 85

    def test_neutral_pairs_well_with_color(self):
        black = _palette([20, 20, 20])
        red = _palette([220, 50, 50])
        score, _, harmony = compute(black, red, "solid", "solid")
        assert harmony == "neutral"
        assert score >= 75

    def test_both_neutrals(self):
        black = _palette([20, 20, 20])
        white = _palette([240, 240, 240])
        _, _, harmony = compute(black, white, "solid", "solid")
        assert harmony == "neutral-neutral"

    def test_both_patterned_scores_lower_than_both_solid(self):
        blue = _palette([50, 80, 200])
        navy = _palette([30, 50, 120])
        solid_score, _, _ = compute(blue, navy, "solid", "solid")
        patterned_score, _, _ = compute(blue, navy, "patterned", "patterned")
        assert solid_score > patterned_score

    def test_value_contrast_triggers_explanation(self):
        white = _palette([240, 240, 240])
        black = _palette([20, 20, 20])
        _, explanation, _ = compute(white, black, "solid", "solid")
        assert "lightness" in explanation

    def test_similar_value_triggers_tonal_explanation(self):
        dark_blue = _palette([30, 50, 100])
        dark_green = _palette([30, 80, 50])
        _, explanation, _ = compute(dark_blue, dark_green, "solid", "solid")
        assert "lightness" in explanation or "tonal" in explanation

    def test_score_is_clamped_0_to_100(self):
        for rgb in [[220, 50, 50], [50, 80, 200], [20, 20, 20], [240, 240, 240]]:
            palette = _palette(rgb)
            score, _, _ = compute(palette, palette, "solid", "solid")
            assert 0 <= score <= 100

    def test_explanation_contains_score(self):
        blue = _palette([50, 80, 200])
        score, explanation, _ = compute(blue, blue, "solid", "solid")
        assert f"Score: {score}/100" in explanation

    def test_dominant_palette_color_drives_harmony(self):
        # Garment 1: 80% red, 20% blue
        # Garment 2: 80% red, 20% green
        # Dominant pair (red × red, weight=0.64) should determine harmony
        g1 = _two_color([220, 50, 50], 0.8, [50, 80, 200], 0.2)
        g2 = _two_color([220, 50, 50], 0.8, [60, 160, 60], 0.2)
        _, _, harmony = compute(g1, g2, "solid", "solid")
        assert harmony == "monochromatic"

    def test_result_is_repeatable(self):
        blue = _palette([50, 80, 200])
        score1, expl1, harmony1 = compute(blue, blue, "solid", "solid")
        score2, expl2, harmony2 = compute(blue, blue, "solid", "solid")
        assert score1 == score2
        assert harmony1 == harmony2
