import pandas as pd
import numpy as np
from tkinter import *
from tkinter import filedialog, simpledialog
from tkinter import ttk, font, messagebox
from PIL import ImageTk, Image
from GetSongs_and_Translate import SpotifyTranslate

class Song_GUI:
    def __init__(self,guiWin):
        self.guiWin_ = guiWin
        self.guiWin_.title("Spotify Music Converter and Sentiment Analysis")
        self.guiWin_.iconbitmap("spotify_icon.ico")

        # Create Frames inside GUI guiWin_
        self.mainframe1 = ttk.Frame(self.guiWin_,relief='sunken')
        self.mainframe1.grid(row=0,column=0,rowspan=4,columnspan=2,sticky='NW')
        self.mainframe1_1 = ttk.Frame(self.guiWin_,relief='sunken',width=10,height=10)
        self.mainframe1_1.grid(row=0,column=2,rowspan=4,columnspan=2)
        self.mainframe2 = ttk.Frame(self.guiWin_,relief='sunken',padding='15 17 15 20')
        self.mainframe2.grid(row=0,column=4,rowspan=4,columnspan=5,sticky='NE')
        self.mainframe3 = ttk.Frame(self.guiWin_,relief='ridge',padding='15 5 15 5')
        self.mainframe3.grid(row=5,column=0,rowspan=1,columnspan=9,sticky='EW')
        self.mainframe4 = ttk.Frame(self.guiWin_,padding='10 10 10 10')
        self.mainframe4.grid(row=6,column=0,rowspan=4,columnspan=9,sticky='EW')

        self.imgobj = ImageTk.PhotoImage(Image.open('spotify_logo.jpg').resize((175,175)))
        self.imglab = ttk.Label(self.mainframe1_1,image=self.imgobj)
        self.imglab.grid(row=0,column=0)

        # Set styles for TK Label, Entry and Button Widgets
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Gerogia",  20, "bold"),foreground='black',background='#C3C3C3')
        self.style.configure("TEntry", font=("Gerogia",  25),foreground='green')
        self.style.configure("TCheckbutton",font=("Gerogia", 20),
                             foreground='black',background='#C3C3C3')
        self.style.configure("TButton",font=("Gerogia",  18),foreground='green')
        self.style.configure('TFrame',background='#C3C3C3')

        #Assign Variables
        self.playlist_uri_entry = StringVar()
        self.playlist_name = StringVar()
        self.num_songs = StringVar()
        self.info = StringVar()
        self.check_buttons = IntVar()
        self.check_buttons.set(0)
        self.playlist_songs = []
        self.playlist_files = ''
        self.song_num = StringVar()
        self.song = StringVar()
        self.lyrics = StringVar()
        self.info = StringVar()
        self.status = 'Welcome to the Spotify Music Translator!'+\
                    '\n\nCreated By: ISTM 610 Team 3'+\
                    '\n\nPlease enter a Spotify Playlist URI in the respective box.'

        self.status_box = Text(self.mainframe1,bg='#00CC00',fg='black',font=('Arial',12),wrap='word',height=9.5,width=50)
        self.status_box.grid(row=0,column=0,rowspan=2,columnspan=4)
        self.status_box.insert('1.0',self.status)
        ys = ttk.Scrollbar(self.guiWin_, orient = 'vertical',   command = self.status_box.yview)
        xs = ttk.Scrollbar(self.guiWin_, orient = 'horizontal', command = self.status_box.xview)
        self.status_box['yscrollcommand'] = ys.set
        self.status_box['xscrollcommand'] = xs.set
        self.guiWin_.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Add Labels for Playlist Information
        (ttk.Label(self.mainframe2,text='Playlist URI: ',style='TLabel').grid(row=0,column=0,sticky='W',columnspan=2))
        (ttk.Label(self.mainframe2,text='Playlist Name: ',style='TLabel').grid(row=1,column=0,sticky='W',columnspan=2))
        (ttk.Label(self.mainframe2,text='Number of Songs: ',style='TLabel').grid(row=2,column=0,sticky='W',columnspan=2))
        (ttk.Label(self.mainframe2,text='Song: ',style='TLabel').grid(row=3,column=0,sticky='W',columnspan=2))
        (ttk.Entry(self.mainframe2,textvariable=self.playlist_uri_entry,width=60,style='TEntry').grid(row=0,column=2,columnspan=2,sticky='E'))
        (ttk.Entry(self.mainframe2,textvariable=self.playlist_name,width=60,state='readonly',style='TEntry').grid(row=1,column=2,columnspan=2,sticky='E'))
        (ttk.Entry(self.mainframe2,textvariable=self.num_songs,width=60,state='readonly',style='TEntry').grid(row=2,column=2,columnspan=2,sticky='E'))
        (ttk.Entry(self.mainframe2,width=60,textvariable=self.song_num,style='TEntry')
        .grid(row=3,column=2,columnspan=2,sticky='E'))
        (ttk.Checkbutton(self.mainframe3,text='Song Info',variable=self.check_buttons,onvalue=1,command=self.show_song_info,style='TCheckbutton').grid(row=0,column=0,columnspan=4,sticky='EW',padx=200))
        (ttk.Checkbutton(self.mainframe3,text='Lyrics',variable=self.check_buttons,onvalue=2,command=self.show_song_lyrics,style='TCheckbutton').grid(row=0,column=4,columnspan=4,sticky='EW',padx=200))
        
        # Add text for results
        self.results = Text(self.mainframe4,bg='#00CC00',fg='black',font=('Arial',25),wrap='word',height=15)
        self.results.grid(row=0,column=0,rowspan=4,columnspan=8)
        ys = ttk.Scrollbar(self.guiWin_, orient = 'vertical',   command = self.results.yview)
        xs = ttk.Scrollbar(self.guiWin_, orient = 'horizontal', command = self.results.xview)
        self.results['yscrollcommand'] = ys.set
        self.results['xscrollcommand'] = xs.set
        
        # Add Button Widget to download songs and translate from audio to text
        (ttk.Button(self.mainframe2,text='Get Songs',command=self.download_songs,style='TButton').grid(row=0,column=8,padx=5))
        (ttk.Button(self.mainframe2,text='Convert!',command=self.translate_songs,style='TButton').grid(row=3,column=8,padx=5))

    #Download Playlist and Display Playlist Information    
    def download_songs(self):
        self.status_box.delete('1.0',END)
        self.status_box.insert('1.0','Loading Playlist....')
        playlist_uri_entry_string = self.playlist_uri_entry.get()
        self.spot = SpotifyTranslate(client_id='f7802ec0c7274924ba0b459e5c765af7',client_secret='50a04ae7a78e44d786ef1529b9f984e8',
            username='1222068017',playlist_uri = playlist_uri_entry_string,
            google_project_file="GoogleTranslateCredentials.json",project_name="datacompetition-1550183479778",
            bucket_name="istm601")
        self.playlist_name.set(self.spot.playlist_name)
        self.playlist_songs = self.spot.download_songs_and_get_titles().split('\n')
        self.status_box.delete('1.0',END)
        self.status_box.insert('1.0','\n'.join(self.playlist_songs))
        self.num_songs.set(str(len(self.playlist_songs)-1))
        self.playlist_files = self.spot.playlist_files

    #Convert Song Audio to Text
    def translate_songs(self):
        self.spot.upload_to_uri(int(self.song_num.get()))
        self.lyrics.set(self.spot.translate_to_text())
        self.results.delete('1.0',END)
        self.info.set(self.spot.display_song_information(int(self.song_num.get())))
        self.spot.delete_song()
        if self.check_buttons.get() == 1:
            self.show_song_info()
        elif self.check_buttons.get() == 2:
            self.show_song_lyrics()

    #Perform Sentiment Analysis and Classification
    def show_song_info(self):
        self.results.delete('1.0',END)
        self.results.insert('1.0',self.info.get())

    #Show Results of Song Lyrics
    def show_song_lyrics(self):
        self.results.delete('1.0',END)
        self.results.insert('1.0',self.spot.artist_name+': '+self.spot.song_only+'\n\n'+self.lyrics.get())

    #Delete Playlist from Computer 
    def on_closing(self):
        try:
            self.spot.delete_playlist()
            self.guiWin_.destroy()
        except:
            self.guiWin_.destroy()
    
if __name__ == "__main__":
    # Instantiate GUI Canvas Using Tk  
    root = Tk()
    Song_GUI(root)    
    root.mainloop()