import os
import tempfile
import numpy as np
from PIL import Image
from venus.pattern import classify


def _solid_image(color=(100, 150, 200), size=(100, 100)) -> str:
    img = Image.new("RGB", size, color)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return tmp.name


def _checkerboard_image(size=100, tile=5) -> str:
    # Use tile < patch_size (10) so each patch spans multiple tiles.
    # Use black/white for maximum grayscale contrast.
    pixels = np.zeros((size, size, 3), dtype=np.uint8)
    for i in range(size):
        for j in range(size):
            pixels[i, j] = [255, 255, 255] if (i // tile + j // tile) % 2 == 0 else [0, 0, 0]
    img = Image.fromarray(pixels)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return tmp.name


class TestClassify:
    def test_solid_image_classified_as_solid(self):
        path = _solid_image()
        try:
            label, _ = classify(path)
            assert label == "solid"
        finally:
            os.unlink(path)

    def test_checkerboard_classified_as_patterned(self):
        path = _checkerboard_image()
        try:
            label, _ = classify(path)
            assert label == "patterned"
        finally:
            os.unlink(path)

    def test_solid_complexity_lower_than_patterned(self):
        solid = _solid_image()
        patterned = _checkerboard_image()
        try:
            _, solid_score = classify(solid)
            _, patterned_score = classify(patterned)
            assert solid_score < patterned_score
        finally:
            os.unlink(solid)
            os.unlink(patterned)

    def test_returns_float_complexity(self):
        path = _solid_image()
        try:
            label, complexity = classify(path)
            assert isinstance(complexity, float)
            assert complexity >= 0.0
        finally:
            os.unlink(path)

    def test_gradient_classified_as_solid(self):
        # A gradient has high global variance but low local patch variance — should read as solid
        pixels = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            pixels[i, :] = [i * 2, i * 2, i * 2]
        img = Image.fromarray(pixels)
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        img.save(tmp.name)
        try:
            label, _ = classify(tmp.name)
            assert label == "solid"
        finally:
            os.unlink(tmp.name)

    def test_result_is_repeatable(self):
        path = _solid_image()
        try:
            label1, score1 = classify(path)
            label2, score2 = classify(path)
            assert label1 == label2
            assert score1 == score2
        finally:
            os.unlink(path)
