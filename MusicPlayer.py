# By Lowena Hull


# ---------------------------
# Visual function from UnicornHAT GitHub
# [ https://github.com/pimoroni/unicorn-hat-hd/blob/master/examples/heartbeats.py]
#
# Joy detector code from Google AIY Github
# [https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/src/examples/vision/joy/joy_detection_demo.py]
# ---------------------------


# Import libraries

import spotipy
from spotipy import util
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials

import sys
import datetime
import time

import pandas as pd
import numpy
from random import randint, choice, random
import itertools

import colorsys
import math
import unicornhathd
from PIL import ImageFont, Image, ImageDraw

import paho.mqtt.client as mqtt

# -----------------------------

# Set server details

server = "mqtt.eclipse.org"
port = 1883

# Must have a spotify for developers account
# Can create a developer's account here: [insert link here]
# Create new project.

# Replace with own details:
# USERNAME is the user's Spotify account name
# Keep SCOPE as is
# CLIENT_ID, CLIENT_SECRET and REDIRECT_URI can be found from your spotify for developers account.

USERNAME = ""
SCOPE = "playlist-modify-public playlist-modify-private user-read-playback-state user-modify-playback-state user-top-read"
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = ""

keep_playing = True

# Genre information (used to classify songs into happy/sad/chill/energetic)

happy_genres = [
    'afrobeat',
    'comedy',
    'dance',
    'disco',
    'funk',
    'groove',
    'happy',
    'hip-hop',
    'indie',
    'indie-pop',
    'party',
    'pop',
    'pop-film',
    'power-pop',
    'reggae',
    'summer',
    'tango'
]

sad_genres = [
    'blues',
    'emo',
    'indie',
    'indie-pop',
    'rainy-day',
    'sad'
]

chill_genres = [
    'acoustic',
    'afrobeat',
    'alternative',
    'ambient',
    'chill',
    'classical',
    'indie',
    'indie-pop',
    'opera',
    'rainy-day',
    'sleep',
    'soul',
    'study'
]

energetic_genres = [
    'dance',
    'disco',
    'dubstep',
    'hip-hop',
    'k-pop',
    'party',
    'pop',
    'pop-film',
    'power-pop',
    'tango',
    'work-out'
]

# ----------------------------
# Set visual settings and images

rising = range(1, 10, 1)
ba = range(10, 5, -1)
dum = range(5, 10, 1)
falling = range(10, 0, -1)

pattern = (rising, ba, dum, falling)
brightness_levels = list(itertools.chain.from_iterable(pattern))


music_note = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0],
    [0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0],
    [0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0],
    [0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0],
    [0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0],
    [0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0],
    [0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0],
    [0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0],
    [0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]

music_note_2 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0],
    [0,0,0,1,1,0,0,1,1,1,1,1,1,0,0,0],
    [0,0,0,1,0,0,0,1,1,1,0,0,0,0,0,0],
    [0,0,1,1,0,0,0,1,1,1,0,0,0,0,0,0],
    [0,0,1,1,0,0,0,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,0],
    [0,0,0,1,1,1,1,1,1,1,0,0,0,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ]

unicornhathd.brightness(1)
unicornhathd.rotation(270)
music_1 = numpy.array(music_note)
music_2 = numpy.array(music_note_2)

# ------------------------------
# Functions

def now_connected(client, userdata, flags, rc):
    
    # Prints a message when connects to the server.
    
    print("Connected to the server.")
    
def message_received(client, userdata, message):
    
    # When a message is received it is written to a text file.
    # This text file contains all the joy_score values transmitted from the
    # Vision Kit. If the message received is "stop" (send in the case of the Vision Kit button
    # being pressed), the program is stopped.
    
    global keep_playing
    
    file = open("joy_detector_values.txt", "a+")
    file.write(message.payload.decode())
    file.write("\n")
    file.close()
    
    if message.payload.decode() == "stop":
        keep_playing = False
        print("Stop signal received.")
        
        
def receive_joy_values(device_found, playlist_id, df, device_id):
    
    # Receives joy_score values from the Vision Kit, sent via mqtt.
    # Loops until keep_playing == False (when the button on the Vision Kit is pressed)
    # Checks if there is an available device.
    # If there is an available device:
    # > Checks if a song is currently playing.
    # > If a song is currently playing it continues until the song is 10 seconds or less from finishing then generates a new song.
    # It waits for that song to finish before starting the new (generated) song.
    # > If a song is not currently playing a new song is generated and played.
    # 
    # If there is not an available device:
    # > Songs are added to the playlist (which can be played from the user's Spotify account at a later date).
    # > A new song will be added every 100 seconds.
    
    global keep_playing

    num_intervals = 1
    client = mqtt.Client()
    client.on_connect = now_connected
    client.on_message = message_received

    client.connect(server, port)
    client.subscribe("music", qos=1)
    #client.loop_forever()
    
    if device_found == True:
        
        mood, joy_score, keep_playing = get_mood()
        filtered_df = filter_songs(df, mood)

        song_id, song_name = select_song(filtered_df, joy_score)
        song_uri = "spotify:track:"+song_id
        print("Added: "+song_name)
        
        # Attempt to play song. In the case of an error, it is assumed there is no avalable device. Song will be added to the session playlist only.
        # If there is an available device the song is played and added to the session playlist.
        try:
            sp.start_playback(device_id, context_uri=None, uris=[song_uri])
            add_tracks_to_playlist(playlist_id, [song_uri])     
        except:
            device_found = False
            add_tracks_to_playlist(playlist_id, [song_uri])

    # Loop until the button on the Vision Kit is pressed to stop the program running.

    while keep_playing == True:

        # Start receiving joy values from the Vision Kit.
        client.loop_start()
        time.sleep(5)

        # Continually check if the device is still available.
        device_id, device_found = switch_to_raspberry()

        if device_found == True:
            
            x = sp.currently_playing()
            try:
                playing = x['is_playing']
            except:
                playing = False
            
            # If a song is currently playing, check how much time left until song finishes.
            if playing == True:
                
                time_progressed= x['progress_ms']
                track_length = x['item']['duration_ms']
                time_left = (track_length - time_progressed)
                
                # If there is less than 10 seconds (10000ms) left in the track, generate new song from joy values. 
                # Wait the same length of time as is left in the track, then play the new song.
                if time_left < 10000:
                    mood, joy_score, keep_playing = get_mood()
                    filtered_df = filter_songs(df, mood)
                    song_id, song_name = select_song(filtered_df, joy_score)
                    song_uri = "spotify:track:"+song_id
                    print("Added: "+song_name)

                    # Attempt to play song- if error occurs then assumed device is no longer available/accessible.
                    try:
                        time.sleep((track_length-time_progressed)/1000)
                        sp.start_playback(device_id, context_uri=None, uris=[song_uri])
                        add_tracks_to_playlist(playlist_id, [song_uri])     
                    except:
                        device_found = False
                        add_tracks_to_playlist(playlist_id, [song_uri])

            else:
                # If no song currently playing then generate a new song and play it.
                mood, joy_score, keep_playing = get_mood()
                filtered_df = filter_songs(df, mood)
                song_id, song_name = select_song(filtered_df, joy_score)
                song_uri = "spotify:track:"+song_id
                print("Added: "+song_name)

                # Attempt to play song- if error occurs then assumed device is no longer available/accessible.
                try:
                    sp.start_playback(device_id, context_uri=None, uris=[song_uri])
                    add_tracks_to_playlist(playlist_id, [song_uri])    
                except:
                    device_found = False
                    add_tracks_to_playlist(playlist_id, [song_uri])

        else:
            # If there is no active device then songs cannot be played so they are added to a playlist on the user's Spotify account.
            # Every 20 * 5 = 100 seconds a new song is added to the playlist.
            if num_intervals % 20 == 0:
                mood, joy_score, keep_playing = get_mood()
                filtered_df = filter_songs(df, mood)
                song_id, song_name = select_song(filtered_df, joy_score)
                song_uri = "spotify:track:"+song_id
                add_tracks_to_playlist(playlist_id, [song_uri])
        num_intervals += 1
        music_note_beat() 
        client.loop_stop()
        
    sp.pause_playback(device_id)
    unicornhathd.off()
    print("Goodbye")
    sys.exit()
                

def create_instance():
    
    # Creates an instance of the spotipy class.
    
    token = util.prompt_for_user_token(USERNAME,SCOPE,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI) 
    sp = spotipy.Spotify(auth=token)
    return token, sp


def create_playlist():
    
    # Creates a new playlist for the session.
    # Playlist available on the user's spotify account under "Your Library" and "Playlists".
    
    time = str(datetime.datetime.now().date())
    playlist_title = "Playlist " + time
    playlist = sp.user_playlist_create(USERNAME, name=playlist_title)
    playlist_id = playlist['id']
    return playlist_id

def add_tracks_to_playlist(playlist_id, tracks):
    
    # Adds the track to the session playlist.
    
    sp.user_playlist_add_tracks(USERNAME, playlist_id, tracks, position=None)


def switch_to_raspberry():
    
    # Finds all available devices.
    # If raspberry pi is a possible output then switch to that output.
    # If not, output the first available device.
    # If no available devices returns device_id = None and device_found = False
    
    raspberry_found = False
    device_found = False
    
    x = sp.devices()
    if x != {'devices': []}:
        device_ids = x['devices']
        device_found = True
        
        for device in device_ids:
            if device['name'] == "raspotify (raspberrypi)":
                print("Raspberry Pi output found")
                device_found = True
                return device['id'], device_found

        #print("Unable to find Raspberry Pi output")
        return device_ids[0]['id'], device_found
        
    else:
        device_found = False
        return None, device_found


def filter_songs(df, mood="happy"):
    
    # Create new dataframe of songs fitting mood criteria.
    # Select a song from the new dataframe at random.
    
    dataframe_name = ""
    
    if mood == "happy":
        genre_list = happy_genres
        dataframe_name = "dataframe_happy"
    elif mood == "sad":
        genre_list = sad_genres
        dataframe_name = "dataframe_sad"
    elif mood == "chill":
        genre_list = chill_genres
        dataframe_name = "dataframe_chill"
    elif mood == "energetic":
        genre_list = energetic_genres
        dataframe_name = "dataframe_energetic"
    
    # Create empty dataframe
    new_df = pd.DataFrame(columns=['id','track','artist','danceability', 'energy', 'key', 'loudness',
                                    'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                                    'valence', 'tempo', 'genre', 'energy_tensor'])
    
    for genre in genre_list:
        
        temp_df = remove_lack_genre(df, genre)
        if not temp_df.empty:
            new_df = pd.concat([new_df, temp_df], copy= False, sort=False)
            new_df = new_df.drop_duplicates(subset="id", keep="first", inplace=False) # changed inplace = True

    return new_df


def remove_lack_genre(df, genre):
    # Only takes songs which have the genre.
    
    genre = genre.replace("-", "")
    temp_df = df[df['genre'].str.contains(genre, na=False)].reset_index(drop=True)
    
    return temp_df


def select_song(df, joy_score=0.5):
    
    # Extra filtering on the pre-filtered dataset
    # Default joy score of 0.5 (content, neither happy nor sad)
    
    song_id = False
    
    # Use energy_tensor, danceability and energy values.
    # The energy_tensor values (0 = energetic, 1 = chill) have been generated by a machine learning tensorflow classifier model 
    # (trained and tested off Spotify data) and applied to the song dataframe. The classifier is still a work is progress and, as
    # such, the energy_tensor values are not as reliable as the df.danceability and df.energy values. Therefore, the energy_tensor 
    # values are relied less on to build the new dataframe of songs. 
    
    if joy_score >= 0.75:
        new_df = df[(df.energy_tensor == 0) & ((df.danceability >= 0.5) | (df.energy >= 0.5))]
    elif joy_score >= 0.5:
        new_df = df[(df.energy_tensor == 0) | ((df.danceability >= 0.5) | (df.energy >= 0.5))]
    elif joy_score >= 0.25:
        new_df = df[(df.energy_tensor == 1) | ((df.danceability < 0.5) | (df.energy < 0.5))]
    else:
        new_df = df[(df.energy_tensor == 1) & ((df.danceability < 0.5) | (df.energy < 0.5))]
    
  
    # Select a song from the filtered dataframe randomly

    #song = new_df.sample(n=1,replace=False) # n=N is the number of random rows to pick
    
    num_rows = new_df.shape[0]
    
    if num_rows != 0:
        random_row = randint(0,num_rows-1)
        song = new_df.iloc[random_row]
        song_id = song['id']
        song_name = song['track']

    else:
        # Less strict conditions for the filtered dataframe
        if joy_score >= 0.75:
            new_df = df[((df.danceability >= 0.5) | (df.energy >= 0.5))]
        elif joy_score >= 0.5:
            new_df = df[((df.danceability >= 0.5) | (df.energy >= 0.5))]
        elif joy_score >= 0.25:
            new_df = df[((df.danceability < 0.5) | (df.energy < 0.5))]
        else:
            new_df = df[((df.danceability < 0.5) | (df.energy < 0.5))]

        if num_rows != 0:
            random_row = randint(0,num_rows-1)
            song = new_df.iloc[random_row]
            song_id = song['id']
            song_name = song['track']

        else:
            song_id = False
            song_name = False

    return song_id, song_name
    
    
    
def get_mood():
    
    # Reads received joy_score values from the text file.
    # Calculates average of the last 5 received joy_score values if 5 score available.
    # If, for example, only 4 joy_score values were available then the average would be calculated
    # with those 4 values.
    # Using joy_score calculated average to determine mood: either happy or sad.
    
    file = open("joy_detector_values.txt", "r")
    lines = file.read().splitlines()
    file.close()
    
    joy_score = 0
    keep_playing = True
    
    if len(lines) > 5:
        for i in range(1,6):
            line = lines[-i]
            if line == "stop":
                joy_score += float(0.5)
                keep_playing = False
            else:
                joy_score += float(line)
        joy_score /= 5
        joy_score = round(joy_score, 4)
    else:
        for i in range(1,(len(lines)+1)):
            line = lines[-i]
            joy_score += float(line)
        joy_score /= (len(lines)+1)
        joy_score = round(joy_score, 4)    

    if joy_score >= 0.75:
        mood = "energetic"
    elif joy_score >= 0.5:
        mood = "happy"
    elif joy_score >= 0.25:
        mood = "chill"
    else:
        mood = "sad"
    
    return mood, joy_score, keep_playing


# -----------------------------------------------
# Visual functions

def music_note_beat():
    
    # Create a beating music note on the 16x16 LED screen whose colour is randomly selected.
    
    h = random()
    image = choice([music_1, music_2])

    for level in brightness_levels:
        for x in range(16):
            for y in range(16):
                s = 1.0
                v = image[x, y] * float(level) / 10
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                red = int(r * 255.0)
                green = int(g * 255.0)
                blue = int(b * 255.0)
                unicornhathd.set_pixel(x, y, red, green, blue)
        unicornhathd.show()
        time.sleep(0.005)
    time.sleep(0.8)

def main():
    
    # The main function.
    
    # Global variables
    global token
    global sp
    global device_id
    
    # Text files
    file = open("joy_detector_values.txt", "w")
    file.close()
    
    # Create class instance; create dataframe; create new playlist for session
    token, sp = create_instance()
    df = pd.read_csv(r"/home/pi/songdataframewithlabel.csv")
    playlist_id = create_playlist()
    
    # Find available devices (if any)
    device_id, device_found = switch_to_raspberry()

    print("""
    Face the Vision Kit- it continuously detects joy levels which will be used to filter a dataframe of songs.
    If there is not an available device (one with Spotify active) then a playlist will be created on the user's account which can be played later.
    Press the button on the Vision Kit to stop the program.
    \n
    """)
    
    print("Receiving joy values: start")
    receive_joy_values(device_found, playlist_id, df, device_id)
    
# Main    
main()

