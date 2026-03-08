from pathlib import Path
from venus.engine import analyze

SHIRT = str(Path(__file__).parent.parent / "experiments" / "shirt_crop.jpg")


class TestAnalyze:
    def test_returns_required_keys(self):
        result = analyze(SHIRT, SHIRT)
        assert {"score", "explanation", "harmony_type", "garment1", "garment2"} <= result.keys()

    def test_garment_dicts_have_required_keys(self):
        result = analyze(SHIRT, SHIRT)
        for garment in [result["garment1"], result["garment2"]]:
            assert {"color_name", "pattern", "rgb"} <= garment.keys()

    def test_score_in_valid_range(self):
        result = analyze(SHIRT, SHIRT)
        assert 0 <= result["score"] <= 100

    def test_same_image_produces_monochromatic_result(self):
        result = analyze(SHIRT, SHIRT)
        assert result["harmony_type"] == "monochromatic"

    def test_same_image_produces_high_score(self):
        result = analyze(SHIRT, SHIRT)
        assert result["score"] >= 80

    def test_rgb_values_in_valid_range(self):
        result = analyze(SHIRT, SHIRT)
        for garment in [result["garment1"], result["garment2"]]:
            assert all(0 <= v <= 255 for v in garment["rgb"])

    def test_color_name_is_nonempty_string(self):
        result = analyze(SHIRT, SHIRT)
        for garment in [result["garment1"], result["garment2"]]:
            assert isinstance(garment["color_name"], str)
            assert len(garment["color_name"]) > 0

    def test_pattern_is_valid_label(self):
        result = analyze(SHIRT, SHIRT)
        for garment in [result["garment1"], result["garment2"]]:
            assert garment["pattern"] in ("solid", "patterned")

    def test_explanation_contains_score(self):
        result = analyze(SHIRT, SHIRT)
        assert f"Score: {result['score']}/100" in result["explanation"]

    def test_result_is_repeatable(self):
        r1 = analyze(SHIRT, SHIRT)
        r2 = analyze(SHIRT, SHIRT)
        assert r1["score"] == r2["score"]
        assert r1["harmony_type"] == r2["harmony_type"]
        assert r1["garment1"]["color_name"] == r2["garment1"]["color_name"]
