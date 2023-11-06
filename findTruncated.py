import os
from PIL import Image

INPUT_DIR = "docs/assets/images/fulls"
Image.MAX_IMAGE_PIXELS = 10000 * 10700

 # find truncated images
for filename in os.listdir(INPUT_DIR):
    try:
        Image.open(os.path.join(INPUT_DIR, filename))
    except OSError:
        print(f"Truncated image: {filename}")