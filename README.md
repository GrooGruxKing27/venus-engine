# Venus Engine

**Project Venus** is a low-intensity personal R&D project focused on building
an explainable outfit compatibility and color-matching engine.

## Principles
- Job comes first
- Time-boxed work only
- MVP before expansion
- Explainability over hype

## Usage

### HTTP API (primary)

```bash
pip install -r requirements.txt
uvicorn api:app --reload
```

Then POST two images to `http://localhost:8000/analyze`:

```bash
curl -X POST http://localhost:8000/analyze \
  -F "garment1=@shirt.jpg" \
  -F "garment2=@trousers.jpg"
```

Response:

```json
{
  "score": 78,
  "explanation": "The two pieces sit close to each other on the color wheel (analogous). ...\n\nScore: 78/100 — Good pairing.",
  "harmony_type": "analogous",
  "garment1": { "color_name": "navy", "pattern": "solid", "rgb": [20, 38, 108] },
  "garment2": { "color_name": "indigo", "pattern": "solid", "rgb": [55, 48, 165] }
}
```

Interactive API docs available at `http://localhost:8000/docs`.

### CLI

```bash
python main.py <image1> <image2>
```

## How It Works

1. **Color extraction** — KMeans clustering finds the 3 dominant colors per garment. The largest cluster (by pixel coverage) is the main color.
2. **Pattern classification** — Median local patch variance on a grayscale image distinguishes solid fabrics from patterned ones. Patch-based (not global) variance correctly handles gradients.
3. **Compatibility scoring** — Every color from garment 1 is compared with every color from garment 2. Each pair is weighted by combined pixel coverage, so dominant colors drive the result. Hue distance maps to a harmony type (monochromatic, analogous, complementary, etc.). Pattern and brightness-contrast modifiers are applied.
4. **Color naming** — Nearest match in CIE LAB color space (perceptually uniform), against a 39-color clothing-specific palette.
5. **Explanation** — Plain-language output describes the color relationship, pattern interaction, and brightness contrast.

## Project Structure

```
venus/
  color.py    dominant color extraction and CIE LAB color naming
  pattern.py  solid vs. patterned classification
  score.py    compatibility scoring and explanation
  engine.py   public Python API — analyze(image1, image2) -> dict
api.py        HTTP API (FastAPI)
main.py       CLI entry point
tests/        unit and integration tests
experiments/  spike notebooks and test images
docs/         vision and scope documents
```
