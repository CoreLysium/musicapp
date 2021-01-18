#Spotify api
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#used to get the first youtube video link from search result
from bs4 import BeautifulSoup, element

import time

from pytube import YouTube

import os
import re # for punctuation filtering

from pydub import AudioSegment

#youtube's html is mostly rendered throught javascript so I cant use a simple get request i have to render it with selenium
from selenium import webdriver

#so i can enable headless
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

client_id = 'e28b2678f2ce4edc9f3e1b2b52588c80'
client_secret = 'd787a0f00e6849a6845384e9a467119b'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp1 = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

song_names = []
links = []

os.chdir('Music')
home_path = os.getcwd()

def append_video_link(name):
    print(f'Getting link for {name}')

    link = 'https://www.youtube.com/results?search_query=' + name.replace(' ', '+')

    browser.get(link)

    soup = BeautifulSoup(browser.page_source, features="lxml")

    first_video_link = soup.find(id='video-title')

    links.append('https://www.youtube.com' + first_video_link['href'])

def get_song_info(name):
    result = sp1.search(name)
    track = result['tracks']['items'][0]

    #assigning variables to replace special characters
    album_name = track['album']["name"]

    artist_name = track['album']['artists'][0]['name']
    song_name = track['name']
    release_date = track['album']['release_date']
    release_date = release_date[:4] # only year


    album_name = re.sub(r'[^\w\s]', '', album_name) #removes all punctuation
    artist_name = re.sub(r'[^\w\s]', '', artist_name)
    
    file_path = os.path.join(artist_name, album_name)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    return file_path, artist_name, album_name, song_name, release_date


def download_video_link(link, location, artist_name, album_name, song_name, release_date):
    yt = YouTube(link)

    filtered = yt.streams.filter(only_audio=True)

    stream = filtered[0]
    print('Starting Download')
    stream.download(location)
#    os.rename(os.path.join(location, song_name+'.mp4'), os.path.join(location, song_name+'.mp3'))
    print('Finished Download, adding metadata')

    audio = AudioSegment.from_file(os.path.join(location, stream.default_filename))

    os.remove(os.path.join(location, stream.default_filename))

    audio.export(os.path.join(location, song_name.replace(' ', '_'))+'.mp3', format='mp3', tags={'album':album_name, 'artist':artist_name, 'title':song_name, 'year':release_date})

    print(f'Metadata for {song_name} added')


print('(1) Song Names')
print('(2) Album')

options = int(input('> '))

if options == 1:
    print("Type 'q' and ENTER when are done.")
    while 'q' not in song_names:
        song_names.append(input('> '))
    song_names.remove('q')

elif options == 2:
    # find album by name
    album = input("Name of album: ")
    results = sp1.search(q="album:" + album, type="album")

    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp1.album_tracks(album_id)
    for track in tracks['items']:
        name = track['name']
        song_names.append(name)

else:
    print('We didn\t understand, try again')

threads = []

#os.path.normpath()
#os.path.join()
if __name__ == '__main__':

    start = time.perf_counter()

    for song_name in song_names:
        append_video_link(song_name)
    
    browser.close()

    for link, song_name in zip(links, song_names):
        file_path, artist_name, album, song, year = get_song_info(song_name)
        download_video_link(link, file_path, artist_name, album, song, year)

    end = time.perf_counter()

    print(f'Done, this took {end-start} seconds')

