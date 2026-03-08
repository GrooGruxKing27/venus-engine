from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

# Reference RGB values for color naming.
# Nearest match is found in CIE LAB space (perceptually uniform),
# so these values just need to be representative, not exact boundaries.
_COLOR_REFS = {
    # Reds
    "red":          (200,  40,  40),
    "maroon":       (110,  25,  25),
    "burgundy":     (125,  20,  40),
    "rust":         (185,  75,  35),
    "coral":        (240, 120,  90),
    "rose":         (230, 140, 150),
    # Oranges
    "orange":       (225, 120,  40),
    # Yellows
    "yellow":       (225, 210,  35),
    "mustard":      (190, 155,  45),
    "gold":         (210, 165,  30),
    # Greens
    "green":        ( 50, 140,  50),
    "sage":         (140, 165, 120),
    "olive":        (110, 125,  55),
    "teal":         ( 35, 140, 130),
    "mint":         (160, 220, 190),
    # Blues
    "sky blue":     (110, 185, 235),
    "blue":         ( 50,  75, 210),
    "indigo":       ( 60,  50, 170),
    "navy":         ( 20,  35, 105),
    # Purples
    "purple":       (130,  45, 180),
    "lavender":     (185, 165, 235),
    "lilac":        (195, 170, 210),
    # Pinks
    "pink":         (240, 145, 185),
    "blush":        (240, 200, 200),
    "hot pink":     (225,  55, 150),
    # Browns & tans
    "brown":        (130,  75,  35),
    "tan":          (195, 165, 120),
    "camel":        (190, 145,  80),
    "beige":        (220, 205, 170),
    "cream":        (245, 238, 210),
    # Neutrals
    "white":        (250, 250, 250),
    "light gray":   (210, 210, 210),
    "gray":         (145, 145, 145),
    "charcoal":     ( 70,  75,  80),
    "black":        ( 18,  18,  18),
}


def _rgb_to_lab(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert sRGB (0–255) to CIE LAB (D65 illuminant).

    LAB is perceptually uniform: equal numerical distances correspond to
    roughly equal perceived color differences, unlike RGB or HSV.
    """
    def linearize(c: float) -> float:
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r_lin, g_lin, b_lin = linearize(r), linearize(g), linearize(b)

    # Linear RGB → XYZ (D65 whitepoint matrix)
    x = 0.4124564 * r_lin + 0.3575761 * g_lin + 0.1804375 * b_lin
    y = 0.2126729 * r_lin + 0.7151522 * g_lin + 0.0721750 * b_lin
    z = 0.0193339 * r_lin + 0.1191920 * g_lin + 0.9503041 * b_lin

    # XYZ → LAB (D65 white point: Xn=0.95047, Yn=1.0, Zn=1.08883)
    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    L = 116 * f(y)           - 16
    a = 500 * (f(x / 0.95047) - f(y))
    b = 200 * (f(y)            - f(z / 1.08883))
    return L, a, b


# Pre-compute LAB coordinates for all reference colors at import time.
_COLOR_REFS_LAB = {name: _rgb_to_lab(*rgb) for name, rgb in _COLOR_REFS.items()}


def extract_colors(image_path: str, n_colors: int = 3):
    """Return list of (rgb_array, percentage) for the n dominant colors."""
    img = Image.open(image_path).convert("RGB")
    img_small = img.resize((150, 150))
    pixels = np.array(img_small).reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    colors = kmeans.cluster_centers_.astype(int)
    counts = np.bincount(kmeans.labels_)
    percentages = counts / counts.sum()

    return list(zip(colors, percentages))


def main_color(colors_with_pct):
    """Return (rgb, percentage) for the largest-coverage dominant color."""
    return max(colors_with_pct, key=lambda x: x[1])


def color_name(rgb) -> str:
    """Return the nearest color name using perceptual CIE LAB distance."""
    L, a, b = _rgb_to_lab(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return min(
        _COLOR_REFS_LAB,
        key=lambda name: (
            (L - _COLOR_REFS_LAB[name][0]) ** 2
            + (a - _COLOR_REFS_LAB[name][1]) ** 2
            + (b - _COLOR_REFS_LAB[name][2]) ** 2
        ),
    )
