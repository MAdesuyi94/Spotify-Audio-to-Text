# Spotify Song Conversion and Sentiment Analysis
This project involves designing and implementing a GUI capable of extractingany English song(s) from user’s favorite Spotify library and converting them to text allowing user to review the sentiment and classification analysis of the song. 

# Objective
•	User can select songs from Spotify API

•	User can convert any English song from their playlist to a text file

•	User can read the sentiment analysis of the song by listeners reviews

•	User can review classification of the song 


# Approach
The execution strategy incorporates the use of Pandas, Matplotlib, Tkinter, deep learning with Tensorflow and Keras and python. We use REST API to communicate with Spotify and pull songs to a local directory; after the song is extracted out of Spotify the song is converted to text.
Sentiment analysis is performed when the user selects a song from their Spotify extraction and the song is translated into text, additionally by doing it so the user can review the song classification. 

# Challenges 
•	Having to place the ffmpeg.exe file in the Scripts folder and declaring the environment variable to convert songs that are downloaded in users’ machine – See Appendix 1 

•	Finding the right parameters needed to get the best audio to text conversion

•	Deleting the playlist from the computer when the user exits the GUI

•	Ensuring that the ordering of the downloaded songs in the playlist is the same order in the Python list

# Design 
The “GetSongs_and_Translate” python code incorporates many of the features on the spotify_data module. This package has many functions including the following:
•	Getting the song names from Spotify playlist and using YouTubeDL to download songs to computer.

•	Upload a song to the Google cloud

•	Convert song in Google cloud storage from audio to text

•	Perform a sentiment analysis and classification on the song

•	Delete the song from the cloud

•	Delete the playlist from the computer
