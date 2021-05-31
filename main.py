from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pandas.tseries.offsets import BDay
from datetime import datetime
import os
last_business_day = datetime.today()-BDay(2)
year = last_business_day.year
last_business_day = last_business_day.strftime("%Y-%m-%d")
OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_ID"]
PLAYLIST_PRIVATE_AUTHORIZATION_SCOPE = "playlist-modify-private"
SPOTIPY_REDIRECT_URI = "http://example.com"

# Selecting a day on your own
# last_business_day = input("Which date do you want to create a playlist for (YYYY-MM-DD)?\n")
# year = last_business_day[0:4]

# BillBoard top 100 url for the day specified
URL = "https://www.billboard.com/charts/hot-100/" + last_business_day
response = requests.get(URL)
data = response.text

soup = BeautifulSoup(data, "html.parser")
# Finds all the top songs for the day
top_songs_list = soup.find_all(name="span",
                               class_="chart-element__information__song text--truncate color--primary")
# Finds all the top artists for the day
top_artists_list = soup.find_all(name="span",
                                 class_="chart-element__information__artist text--truncate color--secondary")

top_songs = [song.getText() for song in top_songs_list]
top_artists = [artist.getText() for artist in top_artists_list]
# Authorize using OAuth 2.0 with the Spotipy Authorization Client with a Playlist Private Scope.
# Returns the authorization client and the token which is cached in Token.txt
spotipy_authorization_client = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                            scope=PLAYLIST_PRIVATE_AUTHORIZATION_SCOPE,
                                            redirect_uri=SPOTIPY_REDIRECT_URI, cache_path="Token.txt")
# Create spotify connection using Spotipy Authorization Client as authorization manager
sp = spotipy.Spotify(auth_manager=spotipy_authorization_client)
# Get the User Id from the spotify connection
user_id = sp.current_user()['id']
song_url_list = []
# Search through spotify based on song name, artist name and song year published.
# Returns dictionary containing url to spotify track. Try Except for cases where song is not found.
for i in range(len(top_songs)):

    current_song = sp.search(q=f"track:{top_songs[i]} year:{year} artist:{top_artists[i]}", type="track")
    try:
        song_url_list.append(current_song['tracks']['items'][0]['external_urls']["spotify"])
    except IndexError:
        pass
# Create a new playlist with the naming convention 'YYYY-MM-DD Billboard 100'. Returns dictionary containing playlist id
play_list = sp.user_playlist_create(user=user_id, name=f"{last_business_day} Billboard 100", public=False
                                    , description=f"Billboard Top 100 for {last_business_day}")
# Get Playlist Id from dict
play_list_id = play_list['id']
# Add songs to the created playlist based on the song list
sp.playlist_add_items(playlist_id=play_list_id, items=song_url_list)
