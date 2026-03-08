"""
Color extraction visualizer.

Usage:
    python experiments/visualize.py <image_path> [--save <output.png>]

Shows the image alongside color swatches for each dominant color,
labelled with the color name and percentage coverage.
"""
import argparse
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

# Allow running from the project root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from venus.color import color_name, extract_colors, main_color


def visualize(image_path: str, save_path: str | None = None) -> None:
    colors = extract_colors(image_path, n_colors=3)
    mc, mc_pct = main_color(colors)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle(Path(image_path).name, fontsize=13)

    # Left: original image
    from PIL import Image
    img = Image.open(image_path)
    axes[0].imshow(img)
    axes[0].axis("off")
    axes[0].set_title("Input")

    # Right: dominant color swatches
    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(colors))
    ax.axis("off")
    ax.set_title("Dominant colors")

    for i, (rgb, pct) in enumerate(colors):
        y = len(colors) - 1 - i
        hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
        name = color_name(rgb)
        is_main = np.array_equal(rgb, mc)

        rect = mpatches.FancyBboxPatch(
            (0.02, y + 0.1), 0.35, 0.75,
            boxstyle="round,pad=0.02",
            facecolor=hex_color,
            edgecolor="black" if is_main else "none",
            linewidth=2,
        )
        ax.add_patch(rect)

        label = f"{name}  {pct:.0%}"
        if is_main:
            label += "  ★ main"
        ax.text(0.42, y + 0.5, label, va="center", fontsize=11)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")
    else:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize dominant colors in a clothing image.")
    parser.add_argument("image", help="Path to the clothing image")
    parser.add_argument("--save", metavar="OUTPUT", help="Save visualization to file instead of displaying")
    args = parser.parse_args()

    visualize(args.image, save_path=args.save)


if __name__ == "__main__":
    main()
