# audible-emotion
Google AIY Vision Kit and Spotify API project


This file will give a brief overview of how to set up what I've built.
The project requires the Vision Kit, a standard Raspberry Pi (I used a Pi 3) and a UnicornHAT LED 16x16 display screen. It also requires a Spotify Developers account (create a new app to generate client id and client secret values and set redirect uri) and Spotify Premium.
Both the Vision Kit Pi and the Raspberry Pi must be running simulatenously for the project to run.

There are 4 python (.py) files, one .h5 model and one .csv file associated with this project:
- GenerateDataframe.py
- ApplyModelToDataframe.py
- TransmitJoy.py
- MusicPlayer.py
- songdataframewithlabel.csv (created when GenerateDataframe.py and ApplyModelToDataframe.py are run)
- best-model.h5 (a classifier model to determine whether a song is energetic or chill based on its audio features like timbre, loudness, valence etc)


This is the list of module requirements on the Raspberry Pi.
- pandas
- spotipy
- numpy
- colorsys
- itertools
- unicornhathd
- PIL
- paho.mqtt.client

This is the list of module requirements for the Vision Kit:
- paho.mqtt.client

This is the list of module requirements for the GenerateDataframe.py file:
- pandas
- spotipy

This is the list of module requirements for the ApplyModelToDataframe.py file:
- tensorflow
- tensorflow.keras.models
- tensorflow.keras.models
- sklearn.preprocessing
- pandas

This is a list of instructions on how to set up the project.

1. Run GenerateDataframe.py (can be from computer or pi)
This generates the user's song dataframe (called songdataframewithlabel.csv). 
The songs added to the dataframe are recommendations from Spotify (based on user's top artists and top genres) and the user's top tracks.

2. Run ApplyModelToDataframe.py (can be from computer or pi)
This applies the classifier model (best-model.h5) to the song dataframe. The model was created using tensorflow and Spotify data, but it is only a rough model and does not work perfectly.

3. Copy over the created song dataframe (songdataframewithlabel.csv) to the pi.
Keep it in the same area as the MusicPlayer.py file.

4. Run TransmitJoy.py on the Vision Kit.
This starts the Vision Kit sending joy_score values (how happy the face seen in the camera looks) to the server.

5. Run MusicPlayer.py on the Raspberry Pi
The TransmitJoy.py must be running before the MusicPlayer.py is run.
The MusicPlayer.py file choses songs to play (or add to a playlist if there is no available device to play songs on) based on mood detected.


A note on authetication:
Because the files are accessing user's data, the user is required to log in for authetication. When the .py files are run, the user will be directed to a website (the redirect uri). 
For example, my redirect was google.com so I was redirected there. It will ask you to log into your Spotify Account- this is so it can give access to your (the user's) listening data.
Log in then copy the url of the website it redirects you to into the python shell and press enter.
This allows the python files to access the user's listening data which is required for this project.
