from PIL import Image
import numpy as np


def classify(image_path: str, patch_size: int = 10) -> tuple[str, float]:
    """
    Classify an image as 'solid' or 'patterned'.

    Uses median local patch variance: solid fabrics have low variance within
    each local region; patterns create high local variance. This handles
    gradients correctly — a gradient has low local variance even if global
    variance is high.

    Returns (label, complexity_score) where complexity_score is the median
    patch variance. Higher = more visually complex.
    """
    # Convert to grayscale: we care about spatial texture, not color.
    # Using RGB would contaminate the variance with inter-channel differences
    # (R≠G≠B) even for a perfectly solid colored garment.
    img = Image.open(image_path).convert("L")
    img_small = img.resize((100, 100))
    pixels = np.array(img_small).astype(float) / 255.0  # shape: (100, 100)

    size = pixels.shape[0]
    variances = []
    for i in range(0, size, patch_size):
        for j in range(0, size, patch_size):
            patch = pixels[i : i + patch_size, j : j + patch_size]
            variances.append(float(patch.var()))

    complexity = float(np.median(variances))
    label = "patterned" if complexity > 0.005 else "solid"
    return label, complexity
