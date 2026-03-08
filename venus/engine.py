from venus.color import extract_colors, main_color, color_name
from venus.pattern import classify as classify_pattern
from venus import score as scoring


def analyze(image1_path: str, image2_path: str) -> dict:
    """
    Analyze color compatibility between two clothing items.

    Input:
        image1_path: path to the first garment image (JPEG, PNG, etc.)
        image2_path: path to the second garment image

    Output dict:
        score        (int)   0–100 compatibility score
        explanation  (str)   human-readable explanation of the score
        harmony_type (str)   color relationship label
        garment1     (dict)  { color_name, pattern, rgb }
        garment2     (dict)  { color_name, pattern, rgb }
    """
    colors1 = extract_colors(image1_path)
    mc1, _ = main_color(colors1)
    pattern1, _ = classify_pattern(image1_path)

    colors2 = extract_colors(image2_path)
    mc2, _ = main_color(colors2)
    pattern2, _ = classify_pattern(image2_path)

    result_score, explanation, harmony_type = scoring.compute(colors1, colors2, pattern1, pattern2)

    return {
        "score": result_score,
        "explanation": explanation,
        "harmony_type": harmony_type,
        "garment1": {
            "color_name": color_name(mc1),
            "pattern": pattern1,
            "rgb": mc1.tolist(),
        },
        "garment2": {
            "color_name": color_name(mc2),
            "pattern": pattern2,
            "rgb": mc2.tolist(),
        },
    }
