from PIL import Image, ImageDraw
import hashlib
import random

def generate_prediction_image(seed: str) -> Image.Image:
    hash_val = hashlib.sha256(seed.encode()).hexdigest()
    random.seed(int(hash_val[:8], 16))

    grid_size = 5
    safe_tiles = random.sample(range(25), 5)

    img_size = 500
    cell_size = img_size // grid_size
    img = Image.new("RGB", (img_size, img_size), color="white")
    draw = ImageDraw.Draw(img)

    for i in range(grid_size):
        for j in range(grid_size):
            index = i * grid_size + j
            x0, y0 = j * cell_size, i * cell_size
            x1, y1 = x0 + cell_size, y0 + cell_size
            color = "#4CAF50" if index in safe_tiles else "#CCCCCC"
            draw.rectangle([x0, y0, x1, y1], fill=color, outline="black")

    return img
