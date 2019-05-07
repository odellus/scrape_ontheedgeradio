#! /usr/bin/env python3
# -*- coding: utf-8

import urllib3
import subprocess
import argparse

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(
                        description="Scrape ontheedgeradio.com for songs")

parser.add_argument("--scrape",
                    dest="scrape",
                    default=False,
                    help="Initial scrape of ontheedge")

args = parser.parse_args()

base_url = "http://www.ontheedgeradio.com/playlists"

years = [str(yr) for yr in range(2002,2015)]

pm = urllib3.PoolManager()

def get_playlists_year(year):
    """
    Function:
                get_playlists_year ( year )
    Description:
                Get all the playlist urls for a given year.
    Arguments:
                year : str - the year we want to scrape.
    Returns:
                a list of urls.
    """
    year_url = "/".join([base_url, year])
    r = pm.request("GET", year_url)
    soup = BeautifulSoup(r.data, "html.parser")
    links = soup.find_all("a")
    return ["/".join([year_url, link.get("href")]) for link in links]

def get_songs(playlist_url):
    """
    Function:
                get_songs_playlist ( playlist_url )
    Description:
                Get all the songs on a given playlist
    Arguments:
                playlist_url : str - the url of the playlist we want to scrape.
    Returns:
                A pandas DataFrame with two columns, artist and song.
    """
    r = pm.request("GET", playlist_url)
    soup = BeautifulSoup(r.data, "html.parser")
    rows = soup.find_all("tr")
    rows = [row for row in rows if len(row.find_all("td")) == 3]
    del rows[:2]
    songs_list = []
    artist_list = []
    for row in rows:
        cell = row.find_all("td")
        songs_list.append(cell[1].get_text())
        artist_list.append(cell[2].get_text())
    df = pd.DataFrame({"artist": artist_list, "song": songs_list})
    return df

def get_all_songs():
    """
    """
    playlist_urls = []
    for year in years:
        playlist_urls.extend(get_playlists_year(year))
    song_dataframes = []
    for playlist in playlist_urls:
        song_dataframes.append(get_songs(playlist))
    df = pd.concat(song_dataframes, ignore_index=True)
    df = df.drop_duplicates()
    df.to_csv("ontheedgeradio.csv")

def get_random_song():
    """
    """
    df = pd.read_csv("ontheedgeradio.csv")
    df = df.drop(columns="Unnamed: 0")
    n = len(df)
    rand = np.random.randint(0,n-1)
    row = df.iloc[rand]
    artist, song = row.get("artist"), row.get("song")
    artist_words = artist.split(" ")
    song_words = song.split(" ")
    google_url = "https://www.google.com/search?q="
    song_url = google_url + "+".join(artist_words + song_words)
    song_url += "&tbm=vid"
    print(song_url)
    subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        song_url])

def main():
    # print(args.scrape)
    if args.scrape:
        print("Scraping ontheedgeradio.com")
        get_all_songs()
    else:
        get_random_song()

if __name__ == "__main__":
    main()
