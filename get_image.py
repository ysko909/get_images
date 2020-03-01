from urllib.request import urlopen, Request
from urllib.parse import quote_plus
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import argparse
import sys
import os
import json
import re


def search_image(word, header, start_number):

    try:
        # アクセスするURLに日本語が含まれているのでエンコード
        url = 'https://search.yahoo.co.jp/image/search?p={}&ei=UTF-8&b={}'.format(
            quote_plus(word, encoding='utf-8'), start_number)

        print(url)

        # アクセスしてパース
        req = Request(url, headers=header)
        html = urlopen(req).read()
        result = BeautifulSoup(html, 'lxml')

        return result

    except HTTPError as e:
        print(e.reason)
    except URLError as e:
        print(e.reason)


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-w', '--words', default=['tiger', 'i'], nargs='*',
                        type=str, help='Words to search')
arg_parser.add_argument('-n', '--number', default=100,
                        type=int, help='Number of images to get')
args = arg_parser.parse_args()

query = '+'.join(args.words)
max_images = args.number

save_dir = os.path.join(os.getcwd(), '_'.join(args.words))
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0 '
}

item_number = 1

while item_number <= max_images:
    result = search_image(query, header, item_number)

    items = result.find_all('img')

    urls = [item.get('src')
            for item in items if item.get('src').startswith('https')]
    urls = list(set(urls))

    imgs = []
    mimes = []
    for url in urls:
        req = Request(url, headers=header)
        element = urlopen(req, timeout=3)
        imgs.append(element.read())
        mimes.append(element.getheader('Content-Type'))

    for i, (img, mime) in enumerate(zip(imgs, mimes)):
        ext = mime.split('/')[1]
        if ext == 'jpeg' or ext == 'jpg':
            result_file = os.path.join(
                save_dir, '{}.'.format(i + item_number) + ext)
            with open(result_file, mode='wb') as f:
                f.write(img)

    item_number += 20
