"""
Extract individual reference images from all_gestures.jpg collage.
7 rows x 5 columns = 35 signs.
Order: '1'..'9', 'A'..'Z'
"""
import os
from PIL import Image

def extract_tiles():
    collage_path = "all_gestures.jpg"
    output_dir = os.path.join("src", "static", "references")
    os.makedirs(output_dir, exist_ok=True)

    labels = [
        '1', '2', '3', '4', '5',
        '6', '7', '8', '9', 'A',
        'B', 'C', 'D', 'E', 'F',
        'G', 'H', 'I', 'J', 'K',
        'L', 'M', 'N', 'O', 'P',
        'Q', 'R', 'S', 'T', 'U',
        'V', 'W', 'X', 'Y', 'Z'
    ]

    im = Image.open(collage_path)
    width, height = im.size
    cols = 5
    rows = 7
    tile_w = width // cols
    tile_h = height // rows

    print(f"Collage size: {width}x{height}, Tile size: {tile_w}x{tile_h}")

    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= len(labels):
                break
            label = labels[idx]
            box = (c * tile_w, r * tile_h, (c + 1) * tile_w, (r + 1) * tile_h)
            tile = im.crop(box)
            out_file = os.path.join(output_dir, f"{label}.jpg")
            tile.save(out_file, "JPEG", quality=95)
            idx += 1

    print(f"Extracted {idx} sign references to {output_dir}")

if __name__ == "__main__":
    extract_tiles()
