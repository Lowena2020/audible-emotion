# %%
# This is the most up to date file as of 16:31 07/07/20
# The design of this file is to generate the dataframe for the user

# %%
# Import

import spotipy
from spotipy import util
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials

import sys
import os
import datetime
import base64

import pandas as pd
import numpy as np


import tensorflow as tf
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler

# %%
username = ""
scope = "playlist-modify-public playlist-modify-private user-read-playback-state user-modify-playback-state ugc-image-upload user-top-read"
client_id = ""
client_secret = ""
redirect_uri = ""

# %%
# Create class instance
token = util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri) 
sp = spotipy.Spotify(auth=token)

# Not sure how to avoid the "enter the URL" part...

# %%
# ---------------------------------------------------

# Playlist functions

    
def get_user_playlists():
    # Returns a list of names of the user's playlists
    # Other information is available
    
    x = sp.user_playlists(username, limit=50, offset=0)
    
    for item in x['items']:
        print("Playlist name: ", item['name'])
        
    return x

def get_playlist_tracks(playlist_id):
    # Prints the track names and artists in a playlist
    # Other information is available
    
    tracks = []
    
    x = sp.user_playlist_tracks(user=username, playlist_id=playlist_id, fields=None, limit=100, offset=0, market=None)
    
    for item in x['items']:
        name = item['track']['name']
        artist = item['track']['artists'][0]['name']
        track_id = item['track']['id']
        tracks.append([track_id, name, artist])
        
    return tracks


# ---------------------------------------------------

# Get information about the user
    

def get_top_artists():
    # Get a user's top artists
    # Other information is available
    
    user_top_artists = {}
    
    x = sp.current_user_top_artists(limit=50, offset=0, time_range='medium_term')
    for item in x['items']:
        artist_name = item['name']
        artist_id = item['id']
        artist_genre = item['genres'] # an array
        
        #print("Artist Name: " + artist_name)
        #print("Id: "+artist_id)
        #print("Genre: ")
        #for genre in artist_genre:
        #    print(genre)
        #print("\n")
        
        user_top_artists[artist_id] = [artist_name, artist_genre]
    return user_top_artists
        
        
    
def get_top_tracks():
    # Get a user's top tracks
    # Other information is available
    
    user_top_tracks = {}
    
    x = sp.current_user_top_tracks(limit=50, offset=0, time_range='medium_term')

    
    for item in x['items']:
        track_name = item['name']
        track_id = item['id']
        track_artists = []
        
        for artist in item['artists']:
            track_artists.append(artist['name'])
        
       # print("Track Name: "+track_name)
        #print("Id: "+track_id)
        #print("Artists: ")
        #for artist in track_artists:
        #    print(artist)
        #print("\n")
            
        user_top_tracks[track_id] = [track_name, track_artists]
    return user_top_tracks


def user_top_genres():
    
    user_genres = {}
    top_genres = []

    user_top_artists = get_top_artists()
    
    for artist in user_top_artists:
        genre = user_top_artists[artist][1] # this might throw up an error
        for x in genre:
            if x not in user_genres:
                user_genres[x] = 1
            else:
                user_genres[x] += 1

    # Gets top 5 favourite genres
    for i in range(5):
        fav_genre = max(user_genres, key=user_genres.get)
        top_genres.append(fav_genre)
        user_genres[fav_genre] = 0

    return top_genres

# ---------------------------------------------------

# Audio analysis and features 

def get_audio_features(track_ids):
    # Get audio features of a list of tracks
    # Other information is available
    
    audio_features_for_tracks = {}
    
    # track_ids is a list
    x = sp.audio_features(tracks=track_ids)
    #print(x)
    
    # prev  x['audio-features']
    
    for item in x:
        danceability = item['danceability']
        energy = item['energy']
        key = item['key']
        loudness = item['loudness']
        mode = item['mode']
        speechiness = item['speechiness']
        acousticness = item['acousticness']
        instrumentalness = item['instrumentalness']
        liveness = item['liveness']
        valence = item['valence']
        tempo = item['tempo']
        track_id = item['id']
        
        audio_features_for_tracks[track_id] = [danceability, energy, key, loudness, mode, speechiness, acousticness,
                                              instrumentalness, liveness, valence, tempo]
    return audio_features_for_tracks

def get_audio_analysis(track_id):
    # Get audio analysis of a track
    # Other information is available
    
    sections_data = {}
    segments_data = {}
    track_data = {}
    
    x = sp.audio_analysis(track_id)
    bars = x['bars']
    beats = x['beats']
    
    
    key_total = 0
    number_of_sections = 0

    for section in x['sections']:
        number_of_sections += 1
        
        loudness = section['loudness']
        tempo = section['tempo']
        key = section['key']
        mode = section['mode'] #his field will contain a 0 for “minor”, a 1 for “major”, or a -1 for no result
        sections_data[str(number_of_sections)] = [loudness, tempo, key, mode]
        key_total += float(key)
    average_key = key_total / number_of_sections
        
        
    
    for segment in x['segments']:
        loudness_max = segment['loudness_max']
        pitches = segment['pitches'] # a list 
        timbre = segment['timbre'] #  a list
        
    loudness = x['track']['loudness']
    tempo = x['track']['tempo']
    key = x['track']['key']
    mode = x['track']['mode']
    
    track_data[track_id] = [loudness, tempo, key, mode] # I don't now why this exists
    # Im not sure having a dictionay with only one data item is a good idea but idk
    return sections_data, segments_data, track_data, average_key


def will_this_work(track_id):
    x = sp.audio_analysis(track_id)
    loudness = str(x['track']['loudness'])
    tempo = str(x['track']['tempo'])
    key = str(x['track']['key'])
    mode = str(x['track']['mode'])
    
    print("\n")
    print("Loudness: "+loudness)
    print("Tempo: "+tempo)
    print("Key: "+key)
    print("Mode: "+mode)

# ---------------------------------------------------

# Filtering songs and recommendations
# Personalisation

    
def get_categories():
    
    categories = {}
    
    x = sp.categories(country=None, locale=None, limit=20, offset=0)
    
    for item in x['categories']['items']:
        category_id = item['id']
        category_name = item['name']
        
        categories[category_id] = category_name
        
    return categories

def get_category_playlists(category_ids):
    
    potential_playlists = []
    
    for category_id in category_ids:
        
        x = sp.category_playlists(category_id=category_id, country=None, limit=20, offset=0)
        x = x['playlists']['items']
        for item in x:
            temp_list = []
            
            playlist_description = item['description']
            playlist_id = item['id']
            playlist_name = item['name']
            
            temp_list.append(playlist_id)
            temp_list.append(playlist_name)
            temp_list.append(playlist_description)
            
        potential_playlists.append([playlist_id, playlist_name, playlist_description])
        
    return potential_playlists


def get_user_specific_playlists(top_genres):

    categories = get_categories()
    # categories is a dictionary with key of category id and value of the category name
    
    temp_list = []
    potential_playlists = []
    
    for x in categories:
        if categories[x].lower() in top_genres or x.lower() in top_genres:
            cat_id = x
            temp_list.append(x)
            
    potential_playlists = get_category_playlists(temp_list)
    # potential playlists is a list of items [playlist_id, name and description]
            
    return potential_playlists
    


def get_recommendations():

    
    # This is a basic version of the recoomendations
    # Only takes into account genre and artist, not things like pitch, timbre, energy etc
    
    # Generates recommendations based on the user's top artists and genres
    # Gets the top playlists for the user's top genres and add those tracks as well
    
    
    # Part 1
    
    recommendations = {}
    
    #  Get the user's top artists
    top_artists = get_top_artists() #key is the id, value is [name, genre]
    
    artists = []
    
    for artist_id in top_artists:
        artists.append(artist_id)
    
    
    # Get a list of all the genre seeds available
    genres_available = sp.recommendation_genre_seeds()
    genres_available = genres_available['genres']
        
    # Find the user's top genres
    top_genres = user_top_genres()
    top_duplicate = []
    
    for genre in top_genres:
        if genre in genres_available:
            top_duplicate.append(genre)
            
            
    # find how many of the user's genres are avilable seeds
    
    num_gen_available = len(top_duplicate)
    
    if num_gen_available > 3:
        genre_1 = genre[0]
        genre_2 = genre[1]
        genre_3 = genre[2]
        
        # get two seed artists
        
        artist_1 = artists[0]
        artist_2 = artists[1]
        
        data = sp.recommendations(seed_artists=[artist_1, artist_2], seed_genres=[genre_1, genre_2, genre_3], seed_tracks=None, limit=100, country=None)
        
    elif num_gen_available == 2:
        genre_1 = genre[0]
        genre_2 = genre[1]
        
        # get 3 seed artists
        
        artist_1 = artists[0]
        artist_2 = artists[1]
        artist_3 = artists[2]
        
        data = sp.recommendations(seed_artists=[artist_1, artist_2, artist_3], seed_genres=[genre_1, genre_2], seed_tracks=None, limit=100, country=None)
        
        
    elif num_gen_available == 1:
        genre_1 = genre[0]
        
        # get four seed artists
        
        artist_1 = artists[0]
        artist_2 = artists[1]
        artist_3 = artists[2]
        artist_4 = artists[3]
        
        data = sp.recommendations(seed_artists=[artist_1, artist_2, artist_3, artist_4], seed_genres=genre_1, seed_tracks=None, limit=100, country=None)
        
    else:
        print("No available genres")
        
        # get five seed artists
        artist_1 = artists[0]
        artist_2 = artists[1]
        artist_3 = artists[2]
        artist_4 = artists[3]
        artist_5 = artists[4]
        
        data = sp.recommendations(seed_artists=[artist_1, artist_2, artist_3, artist_4, artists_5], seed_genres=None, seed_tracks=None, limit=100, country=None)
    
    #print(data)
    data = data['tracks']
    for item in data:
        
        track_name = item['name']
        track_artist = item['artists'][0]['name'] # only gets the first artist
        track_id = item['id']
        
        recommendations[track_id] = [track_name, track_artist]
        
        
        
        
    # Part 2
    
    potential_playlists = get_user_specific_playlists(top_genres)
    
    for item in potential_playlists:
        playlist_id = item[0] # id
        # get all the tracks of the playlist
        tracks = get_playlist_tracks(playlist_id) # list [id, name artist]
        for x in tracks:
            t_id = x[0]
            t_name = x[1]
            t_artist = x[2]
            recommendations[t_id] = [t_name, t_artist]
    return recommendations
        
        
    
# ---------------------------------------------------

# Dataframe functions



def get_data(track_id, data_set):
    
    data_item = []
    data_item.append(track_id)
    
    track_name = data_set[track_id][0]
    track_artist = data_set[track_id][1]
    artist_id = sp.track(track_id)['artists'][0]['id']
    
    #print(artist_id)
    artist_genres = sp.artist(artist_id)['genres']
    genre = ""
    # combine list into one long string where there is a gap between different genres but not between 
    # compound genres i.e indie pop == indiepop
    for xyz in artist_genres:
        xyz = xyz.replace(" ", "")
        genre += xyz
        genre += " "

    
    
    #artist_genre = sp.artist(artist_id)# which, for this purpose, is the same as the track genre
    
    data_item.append(track_name)
    data_item.append(track_artist)

    track_audio_features = get_audio_features([track_id]) # returns a dictionary

    for element in track_audio_features[track_id]:
        data_item.append(element)

    data_item.append(genre)
    
    return data_item

    
def create_dataframe():
    
    
    # Fill dataframe with user's top songs
    # Top songs of their top artists
    # Top songs of artists similar to their top artists
    # We want to create a big selection to filter songs from
    
    
    print("Create dataframe.")
    print("Fill with songs according to the user's taste.")
    
    df = pd.DataFrame()
    
    user_top_tracks = get_top_tracks()
    recommendations = get_recommendations()
    # similar artists top tracks <--- add this after
    
    data = []

    for track_id in user_top_tracks:
        data_item = get_data(track_id, user_top_tracks)
        data.append(data_item)
        
    for track_id in recommendations:
        data_item = get_data(track_id, recommendations)
        data.append(data_item)
        
    # I want to add genre after 'artist'
    # Add this later
    
    df = pd.DataFrame(data,columns=['id','track','artist','danceability', 'energy', 'key', 'loudness',
                                    'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                                    'valence', 'tempo', 'genre'])
    
    
    df.to_csv(r"C:/Users/lowen/Anaconda3/envs/tensor/AIMusicDataFiles/songdataframe.csv", index =False)
    
    audio_csv = pd.read_csv(r"C:/Users/lowen/Anaconda3/envs/tensor/AIMusicDataFiles/songdataframe.csv")
    
    # prints first 4 lines
    #print(audio_csv.head())
    
    return df



# %%

# Create Dataframe
df = create_dataframe()




# Create playlist
#print("Compiling playlist...")
#print("Playing temporary elevator music...")
#sp.start_playback(device_id, context_uri="3yMem9r5sAf6qYnLfORjle")


#switch_to_raspberry()

#x = user_top_genres() # a list of the user's top 5 genres
#get_recommendations()
#x = get_playlist_tracks(playlist_id)
#x = get_user_playlists()
#name, artist, t_id = get_track_currently_playing()
#volume_control("lower", device_id)
#sp.pause_playback(device_id)
#sp.start_playback(device_id)
#set_playlist_cover(playlist_id)
#user_top_artists = get_top_artists()
#user_top_tracks = get_top_tracks()
#categories = get_categories()
#playlists_data = get_category_playlists(categories)


#tracks = ["0UvUivL70eDwhTWBd8S38I", "0SzvmWfOhoxZVGrmvb56YL", "0R8P9KfGJCDULmlEoBagcO"]
#sp.user_playlist_add_tracks(username, playlist_id, tracks, position=None)

#get_recommendations()

# %%
# Maybe collect some data on spotify
# create personal playlists for my own happiness, sadness etc
# analyse the tracks
# its not a very general solution though

# %%
# Need to plan out which emotions with which features
# e.g. If lonely, play tracks they know

# %%


# %%


# %%


# %%


# %%


# %%
# Planning to use spotify connect to connect spotify to the raspberry pi
# That way the music is playing from the raspberry pi speaker

# 21/06 12:58 Got raspotify working on one of the pi 3s
# I can control the sound playing from the tv using this notebook
# I plan to install raspotify on the vision kit and (after connecting a speaker) have the music play from it
# Data would go from the pi to tell spotify the song, then back to the pi to play the music
