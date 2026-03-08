import numpy as np
import pytest
from pathlib import Path
from venus.color import main_color, color_name, extract_colors

SHIRT = str(Path(__file__).parent.parent / "experiments" / "shirt_crop.jpg")


def _p(rgb, pct):
    return (np.array(rgb), pct)


class TestMainColor:
    def test_returns_largest_coverage_color(self):
        palette = [_p([255, 0, 0], 0.6), _p([0, 255, 0], 0.3), _p([0, 0, 255], 0.1)]
        rgb, pct = main_color(palette)
        assert pct == 0.6
        assert list(rgb) == [255, 0, 0]

    def test_single_color_palette(self):
        palette = [_p([100, 150, 200], 1.0)]
        rgb, pct = main_color(palette)
        assert pct == 1.0

    def test_smallest_not_selected(self):
        palette = [_p([255, 0, 0], 0.1), _p([0, 0, 255], 0.9)]
        _, pct = main_color(palette)
        assert pct == 0.9


class TestColorName:
    def test_pure_red(self):
        assert color_name(np.array([220, 50, 50])) == "red"

    def test_navy(self):
        assert color_name(np.array([25, 40, 110])) == "navy"

    def test_black(self):
        assert color_name(np.array([10, 10, 10])) == "black"

    def test_white(self):
        assert color_name(np.array([250, 250, 250])) == "white"

    def test_always_returns_a_string(self):
        result = color_name(np.array([123, 45, 67]))
        assert isinstance(result, str)
        assert len(result) > 0


class TestExtractColors:
    def test_returns_requested_count(self):
        colors = extract_colors(SHIRT, n_colors=3)
        assert len(colors) == 3

    def test_percentages_sum_to_one(self):
        colors = extract_colors(SHIRT, n_colors=3)
        total = sum(p for _, p in colors)
        assert abs(total - 1.0) < 0.001

    def test_rgb_values_in_valid_range(self):
        colors = extract_colors(SHIRT, n_colors=3)
        for rgb, _ in colors:
            assert all(0 <= int(v) <= 255 for v in rgb)

    def test_different_n_colors(self):
        colors = extract_colors(SHIRT, n_colors=5)
        assert len(colors) == 5

    def test_result_is_repeatable(self):
        colors1 = extract_colors(SHIRT)
        colors2 = extract_colors(SHIRT)
        for (rgb1, pct1), (rgb2, pct2) in zip(colors1, colors2):
            assert list(rgb1) == list(rgb2)
            assert pct1 == pct2
