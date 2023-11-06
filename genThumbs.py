"""
Generate thumbnails for all images in a directory.
"""

import os
import concurrent.futures
from PIL import Image, ImageFile
from tqdm import tqdm

INPUT_DIR = "docs/assets/images/fulls"
OUTPUT_DIR = "docs/assets/images/thumbs"
Image.MAX_IMAGE_PIXELS = 10000 * 10700
ImageFile.LOAD_TRUNCATED_IMAGES = True

"""
Binary search to find the best thumbnail size.
"""


def generate_thumbnail(filename):
    out_filename = os.path.join(OUTPUT_DIR, filename)
    im = Image.open(os.path.join(INPUT_DIR, filename))
    # some interesting jpgs is in RGBA mode
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGB")

    min_ratio = 0.0
    max_ratio = 1.0
    PRECISION = 0.01

    while max_ratio - min_ratio > PRECISION:
        mid_ratio = (min_ratio + max_ratio) / 2
        size = tuple([int(x * mid_ratio) for x in im.size])
        size = tuple([x if x > 0 else 1 for x in size])

        try:
            new_im = im.copy()
            new_im.thumbnail(size)
            new_im.save(out_filename)

            if os.path.getsize(out_filename) < 200 * 1024:
                min_ratio = mid_ratio
            else:
                max_ratio = mid_ratio
        except Exception as e:
            # print Exception
            print(f"Error generating thumbnail for {filename}")
            print(f"{type(e).__name__}: {e}")


def generate_thumbnail_native(filename):
    im = Image.open(os.path.join(INPUT_DIR, filename))
    size = tuple([int(x * 0.8) for x in im.size])

    out_filename = os.path.join(OUTPUT_DIR, filename)
    try:
        # some interesting jpgs is in RGBA mode
        if im.mode in ("RGBA", "P"):
            im = im.convert("RGB")

        im.thumbnail(size)
        im.save(out_filename)

        # retry until the thumbnail size is smaller than 200KB
        while os.path.getsize(out_filename) > 200 * 1024:
            size = tuple([int(x * 0.8) for x in size])
            im.thumbnail(size)
            im.save(out_filename)

    except Exception as e:
        print(f"Error generating thumbnail for {filename}\n{e}")


def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(INPUT_DIR):
            futures.append(executor.submit(generate_thumbnail, filename))

        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            future.result()


if __name__ == "__main__":
    main()
