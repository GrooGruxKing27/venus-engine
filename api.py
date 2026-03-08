import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from venus.engine import analyze

app = FastAPI(
    title="Venus Engine",
    description="Outfit compatibility scoring API — given two clothing images, returns a 0–100 score and a plain-language explanation.",
    version="0",
)

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@app.get("/")
def health():
    return {"status": "ok", "service": "venus-engine", "version": "0"}


@app.post("/analyze")
async def analyze_outfit(
    garment1: UploadFile = File(..., description="First clothing item image"),
    garment2: UploadFile = File(..., description="Second clothing item image"),
):
    """
    Analyze color compatibility between two clothing items.

    Upload two garment images (JPEG, PNG, or WebP). Returns:
    - **score** (0–100): compatibility score
    - **explanation**: plain-language reasoning
    - **harmony_type**: color relationship label (e.g. "analogous", "complementary")
    - **garment1 / garment2**: per-garment color name, pattern, and dominant RGB
    """
    for upload in (garment1, garment2):
        if upload.content_type not in _ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"'{upload.filename}' has unsupported type '{upload.content_type}'. "
                    "Upload a JPEG, PNG, or WebP image."
                ),
            )

    tmp1 = tmp2 = None
    try:
        suffix1 = Path(garment1.filename or "img").suffix or ".jpg"
        suffix2 = Path(garment2.filename or "img").suffix or ".jpg"

        with tempfile.NamedTemporaryFile(suffix=suffix1, delete=False) as f:
            f.write(await garment1.read())
            tmp1 = f.name

        with tempfile.NamedTemporaryFile(suffix=suffix2, delete=False) as f:
            f.write(await garment2.read())
            tmp2 = f.name

        return analyze(tmp1, tmp2)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        for path in (tmp1, tmp2):
            if path and os.path.exists(path):
                os.unlink(path)
