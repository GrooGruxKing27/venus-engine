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
    # Core colors
    def test_red(self):
        assert color_name(np.array([200, 40, 40])) == "red"

    def test_navy(self):
        assert color_name(np.array([20, 35, 105])) == "navy"

    def test_black(self):
        assert color_name(np.array([10, 10, 10])) == "black"

    def test_white(self):
        assert color_name(np.array([250, 250, 250])) == "white"

    def test_gray(self):
        assert color_name(np.array([145, 145, 145])) == "gray"

    # Expanded palette — clothing-relevant colors
    def test_burgundy_distinct_from_maroon(self):
        # Burgundy is more purple-red; maroon is darker brown-red
        burgundy = color_name(np.array([125, 20, 40]))
        maroon   = color_name(np.array([110, 25, 25]))
        assert burgundy == "burgundy"
        assert maroon == "maroon"

    def test_charcoal_distinct_from_black_and_gray(self):
        result = color_name(np.array([70, 75, 80]))
        assert result == "charcoal"

    def test_mustard_distinct_from_yellow(self):
        assert color_name(np.array([190, 155, 45])) == "mustard"
        assert color_name(np.array([225, 210, 35])) == "yellow"

    def test_rust(self):
        assert color_name(np.array([185, 75, 35])) == "rust"

    def test_sage(self):
        assert color_name(np.array([140, 165, 120])) == "sage"

    def test_camel(self):
        assert color_name(np.array([190, 145, 80])) == "camel"

    def test_indigo_distinct_from_navy(self):
        # Indigo is lighter and more purple than navy
        assert color_name(np.array([60, 50, 170])) == "indigo"

    # LAB distance sanity: similar perceptual colors should map correctly
    def test_dark_blue_is_navy_not_black(self):
        # RGB-distance would confuse very dark blue with black;
        # LAB correctly identifies it as navy
        assert color_name(np.array([15, 25, 80])) == "navy"

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
