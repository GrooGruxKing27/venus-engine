# Venus Engine

**Project Venus** is a low-intensity personal R&D project focused on building
an explainable outfit compatibility and color-matching engine.

## Principles
- Job comes first
- Time-boxed work only
- MVP before expansion
- Explainability over hype

## Usage

```bash
pip install -r requirements.txt
python main.py <image1> <image2>
```

Example:

```
$ python main.py experiments/shirt_crop.jpg experiments/shirt_crop.jpg

Garment 1: navy (solid)  rgb=[71, 103, 160]
Garment 2: navy (solid)  rgb=[71, 103, 160]

The two pieces share the same hue family. Monochromatic outfits read as a single unified tone — inherently cohesive. Both pieces are solid, keeping the look clean and uncluttered.

Score: 93/100 — Strong match.
```

## How It Works

1. **Color extraction** — KMeans clustering on resized pixel arrays finds the 3 dominant colors. The mid-brightness cluster is used as the main color.
2. **Pattern classification** — Median local patch variance distinguishes solid fabrics (low local variance) from patterned ones (high local variance).
3. **Compatibility scoring** — Hue distance between the two garments' main colors determines a harmony type (monochromatic, analogous, complementary, etc.), each with a base score. A pattern modifier is applied (+5 for both solid, −12 for both patterned).
4. **Explanation** — A plain-language explanation describes the color relationship and pattern interaction, paired with the numeric score.

## Project Structure

```
venus/
  color.py    dominant color extraction and naming
  pattern.py  solid vs. patterned classification
  score.py    compatibility scoring and explanation
  engine.py   public API — analyze(image1, image2) -> dict
main.py       CLI entry point
experiments/  spike notebooks and test images
docs/         vision and scope documents
```
