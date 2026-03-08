from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

_COLOR_NAMES = {
    "red":        (220,  50,  50),
    "orange":     (230, 130,  50),
    "yellow":     (220, 210,  50),
    "green":      ( 60, 160,  60),
    "teal":       ( 40, 150, 140),
    "blue":       ( 50,  80, 200),
    "navy":       ( 25,  40, 110),
    "purple":     (140,  50, 180),
    "pink":       (240, 150, 180),
    "brown":      (130,  80,  40),
    "white":      (245, 245, 245),
    "light gray": (200, 200, 200),
    "gray":       (128, 128, 128),
    "dark gray":  ( 70,  70,  70),
    "black":      ( 20,  20,  20),
    "cream":      (240, 235, 210),
    "beige":      (210, 195, 160),
    "olive":      (110, 130,  60),
    "maroon":     (120,  30,  30),
    "coral":      (240, 120,  90),
    "sky blue":   (110, 180, 230),
    "lavender":   (180, 160, 225),
}


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
    """Return the nearest human-readable color name for an RGB value."""
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    best, best_dist = "unknown", float("inf")
    for name, (cr, cg, cb) in _COLOR_NAMES.items():
        dist = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if dist < best_dist:
            best_dist = dist
            best = name
    return best
