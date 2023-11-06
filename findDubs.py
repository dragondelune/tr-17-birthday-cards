import csv
import os
from PIL import Image, ImageFile
import imagehash
import concurrent.futures

INPUT_DIR = "docs/assets/images/fulls"
Image.MAX_IMAGE_PIXELS = 10000 * 10700
ImageFile.LOAD_TRUNCATED_IMAGES = True

def read_csv_to_dict(filename):
    result = {}
    with open(filename, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            author = row['name']
            img_name = row['file_name']
            result[img_name] = author
    return result

def main():
    imgAuthorDict = read_csv_to_dict('docs/_data/submissions.csv')

    # hash all images
    hashes = {}
    for filename in os.listdir(INPUT_DIR):
        # hash images in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(imagehash.average_hash, Image.open(os.path.join(INPUT_DIR, filename)))
            hash = future.result()
            if hash in hashes:
                hashes[hash].append(filename)
            else:
                hashes[hash] = [filename]
    

    # print duplicates
    for hash in hashes:
        if len(hashes[hash]) > 1:
            print(f"Duplicate images:")
            for filename in hashes[hash]:
                print(f"{filename} by {imgAuthorDict[filename]}")


if __name__ == "__main__":
    main()
