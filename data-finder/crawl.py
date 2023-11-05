"""
This script crawls data from https://vote.funtown.com.hk/talesrunner/vote_rank.

Output: 
- data.csv
- all submissions' images in the images/ directory (under the output directory)

Warning:
Use with caution because this script will download all images from the website.
And the script doesn't check if the image is an actual image or not, it could be a virus.
"""

import argparse
import pathlib
import os
import csv
import requests
import urllib.request
import shutil
from bs4 import BeautifulSoup
import concurrent.futures
from tqdm import tqdm

HEADERS = ['id', 'name', 'subject', 'content', 'num_of_votes']

parser = argparse.ArgumentParser(
    description='Crawl data from blacktown, download the images, and write the data to a CSV file.')
parser.add_argument('--output_dir', default=".", type=pathlib.Path,
                    help='The directory to write the output files to.')
parser.add_argument('--csv_file_name', default='data.csv', type=str,
                    help='The name of the output CSV file.')
parser.add_argument('--image_output_dir_name', default='images', type=str,
                    help='The name of the output directory for the images.')


class Submission:
    def __init__(self, sid, name, subject, content, num_of_votes, file_name):
        self.sid = sid
        self.name = name
        self.subject = subject
        self.content = content
        self.num_of_votes = num_of_votes
        # non csv fields
        self.file_name = file_name

    def getUrl(self):
        # extension depends on the file name
        # img_src example: 'https://submit.funtown.com.hk/upload/tr_video/17thCelebration/1337.png'
        return f'https://submit.funtown.com.hk/upload/tr_video/17thCelebration/{self.file_name}'


def download_image(url, out_file_name):
    with urllib.request.urlopen(url) as response, open(out_file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def download_images_in_parallel(submissions, out_file_dir):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for submission in submissions:
            url = submission.getUrl()
            out_file_name = os.path.join(out_file_dir, submission.file_name)
            futures.append(executor.submit(download_image, url, out_file_name))

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            future.result()


def create_submission_from_info_div(info_div):
    # img_src example: 'https://submit.funtown.com.hk/upload/tr_video/17thCelebration/1337.png'
    img_src = info_div.select_one('img')['src']
    img_name = img_src.rsplit('/', 1)[-1]

    submission_id = img_name.rsplit('.')[0]
    submission_id = int(submission_id)

    name = info_div.select_one('.votename').text.strip()
    subject = info_div.select_one('.votesubject').text.strip()
    content = info_div.select_one('.Introduction').text.strip()

    num_of_votes = info_div.select_one('.numberofvotes').text
    num_of_votes = int(num_of_votes)

    return Submission(submission_id, name, subject, content, num_of_votes, img_name)


def write_to_csv_file(submissions, output_dir, csv_output_file_name):
    with open(os.path.join(output_dir, csv_output_file_name), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()

        for submission in submissions:
            writer.writerow({
                'id': submission.sid,
                'name': submission.name,
                'subject': submission.subject,
                'content': submission.content,
                'num_of_votes': submission.num_of_votes
            })


def main():
    args = parser.parse_args()

    img_out_path = os.path.join(args.output_dir, args.image_output_dir_name)
    os.makedirs(img_out_path, exist_ok=True)

    r = requests.get('https://vote.funtown.com.hk/talesrunner/vote_rank')
    soup = BeautifulSoup(r.text, 'html.parser')

    project_select_form = soup.select_one('form#project_select')
    info_divs = project_select_form.select('.image_bg_rank')

    submissions = []

    for info_div in info_divs:
        submission = create_submission_from_info_div(info_div)
        submissions.append(submission)

    write_to_csv_file(submissions, args.output_dir, args.csv_file_name)

    img_output_dir = os.path.join(args.output_dir, args.image_output_dir_name)
    download_images_in_parallel(submissions, img_output_dir)


if __name__ == '__main__':
    main()
