from pathlib import Path
from fastapi.testclient import TestClient
from api import app

SHIRT = Path(__file__).parent.parent / "experiments" / "shirt_crop.jpg"

client = TestClient(app)


def _shirt_files():
    """Return both garment slots populated with the test shirt image."""
    return {
        "garment1": ("shirt.jpg", open(SHIRT, "rb"), "image/jpeg"),
        "garment2": ("shirt.jpg", open(SHIRT, "rb"), "image/jpeg"),
    }


class TestHealth:
    def test_returns_200(self):
        r = client.get("/")
        assert r.status_code == 200

    def test_status_ok(self):
        assert client.get("/").json()["status"] == "ok"


class TestAnalyzeEndpoint:
    def test_returns_200(self):
        r = client.post("/analyze", files=_shirt_files())
        assert r.status_code == 200

    def test_response_has_required_keys(self):
        r = client.post("/analyze", files=_shirt_files())
        body = r.json()
        assert {"score", "explanation", "harmony_type", "garment1", "garment2"} <= body.keys()

    def test_garment_dicts_have_required_keys(self):
        r = client.post("/analyze", files=_shirt_files())
        body = r.json()
        for garment in [body["garment1"], body["garment2"]]:
            assert {"color_name", "pattern", "rgb"} <= garment.keys()

    def test_score_in_valid_range(self):
        r = client.post("/analyze", files=_shirt_files())
        score = r.json()["score"]
        assert 0 <= score <= 100

    def test_same_image_monochromatic(self):
        r = client.post("/analyze", files=_shirt_files())
        assert r.json()["harmony_type"] == "monochromatic"

    def test_pattern_is_valid_label(self):
        r = client.post("/analyze", files=_shirt_files())
        body = r.json()
        assert body["garment1"]["pattern"] in ("solid", "patterned")
        assert body["garment2"]["pattern"] in ("solid", "patterned")

    def test_rgb_values_in_range(self):
        r = client.post("/analyze", files=_shirt_files())
        body = r.json()
        for garment in [body["garment1"], body["garment2"]]:
            assert all(0 <= v <= 255 for v in garment["rgb"])

    def test_explanation_contains_score(self):
        r = client.post("/analyze", files=_shirt_files())
        body = r.json()
        assert f"Score: {body['score']}/100" in body["explanation"]


class TestInputValidation:
    def test_non_image_content_type_returns_422(self):
        r = client.post(
            "/analyze",
            files={
                "garment1": ("doc.pdf", b"fake", "application/pdf"),
                "garment2": ("shirt.jpg", open(SHIRT, "rb"), "image/jpeg"),
            },
        )
        assert r.status_code == 422

    def test_missing_garment_returns_422(self):
        r = client.post(
            "/analyze",
            files={"garment1": ("shirt.jpg", open(SHIRT, "rb"), "image/jpeg")},
        )
        assert r.status_code == 422

    def test_png_upload_accepted(self):
        # Confirm PNG content type is accepted alongside JPEG
        with open(SHIRT, "rb") as img:
            r = client.post(
                "/analyze",
                files={
                    "garment1": ("shirt.png", img, "image/png"),
                    "garment2": ("shirt.jpg", open(SHIRT, "rb"), "image/jpeg"),
                },
            )
        assert r.status_code == 200
