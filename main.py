import sys
from venus.engine import analyze


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <image1> <image2>")
        sys.exit(1)

    image1, image2 = sys.argv[1], sys.argv[2]
    result = analyze(image1, image2)

    g1 = result["garment1"]
    g2 = result["garment2"]

    print(f"\nGarment 1: {g1['color_name']} ({g1['pattern']})  rgb={g1['rgb']}")
    print(f"Garment 2: {g2['color_name']} ({g2['pattern']})  rgb={g2['rgb']}")
    print(f"\n{result['explanation']}\n")


if __name__ == "__main__":
    main()
