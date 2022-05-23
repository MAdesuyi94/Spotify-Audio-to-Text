from spotify_data import enable_multicore,  write_playlist,multicore_find_and_download_songs,find_and_download_songs
import os
import spotipy
import spotipy.oauth2 as oauth2
import google.auth
from google.cloud import translate_v2 as translate
from google.cloud import storage, texttospeech, speech
import shutil
from google.cloud import language_v1 as language

class SpotifyTranslate:
    def __init__(self,client_id,client_secret,username,playlist_uri,google_project_file,project_name,bucket_name):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.playlist_uri = playlist_uri
        self.multicore_support = enable_multicore(autoenable=False, maxcores=None, buffercores=1)
        self.auth_manager = oauth2.SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)
        self.playlist_name = write_playlist(self.username,self.playlist_uri,self.spotify)
        self.reference_file = "{}.txt".format(self.playlist_name)
        self.google_project_file = google_project_file
        self.project_name = project_name
        self.bucket_name = bucket_name
        self.credentials, self.project_id = google.auth.\
                      load_credentials_from_file(self.google_project_file)
        self.storage_client = storage.Client(credentials=self.credentials,project=self.project_name)

        self.song_number = 0
        self.song_name = ""
        self.source_file_name = ""
        self.destination_name = ""
        self.artist_name = ""
        self.song_only = ""
        self.blob = ""
        
    def download_songs_and_get_titles(self):
        if not os.path.exists(self.playlist_name):
            os.makedirs(self.playlist_name)
        os.rename(self.reference_file, self.playlist_name + "/" + self.reference_file)
        os.chdir(self.playlist_name)
        # Enable multicore support
        if self.multicore_support > 1:
            multicore_find_and_download_songs(self.reference_file, self.multicore_support)
        else:
            find_and_download_songs(self.reference_file)
        print("Operation complete.")

        self.playlist_files = [i for i in os.listdir() if i.endswith(".wav")]
        self.playlist_files = sorted(self.playlist_files,key=os.path.getctime)
        print('playlist files \n')
        print(self.playlist_files)
        print('')
        os.chdir(os.path.dirname(os.getcwd()))
        song_files = ''
        with open('{}//{}'.format(self.playlist_name,self.reference_file)) as play_list:
            for i, l in enumerate(play_list.readlines()):
                single_song = '{:,d}. Song: {}; Artist: {}'.format(i+1,l.rsplit(',',2)[0],l.rsplit(',',2)[1])
                song_files = song_files + "\n" + single_song

        return song_files

    def upload_to_uri(self, song_number):

        self.source_file_name = self.playlist_files[song_number-1]

        shutil.copy(os.path.join(os.getcwd(),self.playlist_name,self.source_file_name),os.getcwd())
        self.destination_name = self.playlist_name+'/'+self.source_file_name
        bucket = self.storage_client.bucket(self.bucket_name)
        self.blob = bucket.blob(self.destination_name)
        self.blob.upload_from_filename(self.source_file_name)
        print("Upload Complete!!!")

    def translate_to_text(self):
        self.input_text = ""
        self.conf = 0.0
        client = speech.SpeechClient(credentials=self.credentials)
        audio = speech.RecognitionAudio(uri = "gs://istm601/"+self.destination_name)
        config = speech.RecognitionConfig(encoding = 'LINEAR16',
        language_code = 'en-US',
        sample_rate_hertz = 48000,
        audio_channel_count = 2,
        use_enhanced=True,
        model='video')
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=10000)
        chunks          = 0
        # For long recordings, the response will be in chunks (paragraphs)
        for result in response.results:
            chunks += 1
            self.input_text = self.input_text + \
                                result.alternatives[0].transcript 
            self.conf += result.alternatives[0].confidence
        self.conf = 100.08*self.conf/chunks
        #print(u"Transcript: {}".format(self.input_text))
        size = len(self.input_text)
        self.conf = round(self.conf, 1)
        
        return self.input_text

    def display_song_information(self, song_number):
        with open('{}//{}'.format(self.playlist_name,self.reference_file)) as play_list:
                self.song_name = play_list.readlines()[song_number-1]
                self.artist_name = self.song_name.rsplit(',',2)[1]
                self.song_only = self.song_name.rsplit(',',2)[0]
        information = "Artist: "+self.artist_name +"\nSong: "+self.song_only +'\n\n'
        client = language.LanguageServiceClient(credentials=self.credentials)
    
        document = language.Document(content=self.input_text, language='en',
                                        type_=language.Document.Type.PLAIN_TEXT)
    
        response = client.analyze_sentiment(document=document, encoding_type = 'UTF32')
        sentiment = response.document_sentiment
        information += "Sentiment Analysis:" + "\n\n" + "Sentiment: " + \
            '{:6.3f}'.format(sentiment.score) + "\n" + "Magnitude: " + \
            '{:6.3f}'.format(sentiment.magnitude) + '\n\nCategories:'
    
        result = {}
        response   = client.classify_text(request={'document': document})
        for category in response.categories:
                result[category.name] = category.confidence
        for r in result:
                information +=('\n'+r[1:].replace('/',', ')+'; Confidence: {:.1%}'.format(result[r]))
        return(information)
    
    def delete_song(self):
        self.blob.delete()
        print('Song Deleted from Cloud')
        os.remove(self.source_file_name)
        print('Song Deleted from Path')
    
    def delete_playlist(self):
        shutil.rmtree(self.playlist_name,ignore_errors=True)
        print('Playlist Deleted')


