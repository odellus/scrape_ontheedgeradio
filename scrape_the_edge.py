import os
import json
import requests
import datetime
import re
import argparse
import numpy as np

from bs4 import BeautifulSoup

fpath = './songs_on_the_edge.json'

def parse_args():
    parser = argparse.ArgumentParser(description='Find a song to listen to.')
    parser.add_argument('--scrape', action='store_true')
    parser.add_argument('--suggest', action='store_true')
    return parser.parse_args()

def get_base_url():
    return 'https://ontheedgeradio.blogspot.com'

def zero_pad(k):
    if k < 10:
        return f'0{k}'
    else:
        return str(k)

def get_ranges(base_url):
    n_months = 12 # Duh.
    now = datetime.datetime.now()
    min_year = 2011
    min_month = 2
    max_year = now.year
    max_month = now.month
    urls = []
    for k in range(2011, max_year + 1):
        for kk in range(1, n_months + 1):
            if (k <= min_year and kk < min_month) \
            or (k == max_year and kk > max_month):
                continue
            urls.append(f'{base_url}/{k}/{zero_pad(kk)}')
    return urls

def get_text(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup.text

def get_songs(url):
    text = get_text(url)
    pattern = r'[0-9]+:[0-9]+ : '
    return [x for x in re.split(pattern, text) if '\n' not in x]

def scrape():
    base_url = get_base_url()
    urls = get_ranges(base_url)
    songs = []
    for url in urls:
        songs.extend(get_songs(url))
    with open(fpath, 'w') as f:
        json.dump(songs, f)

def get_song():
    with open(fpath, 'r') as f:
        data = json.load(f)
    print(np.random.choice(data, size=1).tolist().pop())

def main():
    args = parse_args()
    if os.path.exists(fpath):
        if not args.scrape:
            get_song()
        else:
            scrape()
    else:
        if not args.suggest:
            scrape()
        else:
            print('There was no saved file found. Scraping.')
            scrape()
            get_song()

if __name__ == '__main__':
    main()
