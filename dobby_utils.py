
import os

class PlayListHandler():
    """
    PlayListHandler offers methods for Dobby to handle and configure playlist for MusicCog.
    
    Playlists are saved as files containing a JSON string.
    This JSON string has the song name as keys, and the song url as values.
    
    Example:
            { 'Brainache - Livia' : '<url>', k2 : v2, ...}
    
    This files are stored in the user's home directory, under '~/.dobby/playlists/'.

    The playlist name is the same as the filename containing the songs.
    """
    def __init__(self):

        # Checks if Dobby is executing in a Windows or Linux (POSIX) machine.
        if os.name == 'nt': 
            self.home_path = os.path.expanduser('~')
        else:
            pass

    def create_playlist(name):
        with open('./playlists/',  ) as f:
            pass

def process_msg(txt):
    pass