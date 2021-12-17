
import os
import sys

PLAYLIST_FILE = 1
TASKS_FILE = 2

def denegate_path_traversal(dir, playlist):
    ''' 
    Check if variable 'playlist' is safe against path traversal.
    Absolut path of playlist should be inside 'dir' (chroot directory path)
    '''
    path = os.path.abspath(playlist)
    print(path)
    return dir == os.path.commonpath((dir, path))

def allow_only_alnum_playlists(playlist:str):
    '''
    Only allows alpha numeric characters in playlist name.
    - Works against path traversal.
    - Prevents directory creation.
    - Prevents hidden files & strange filenames.
    '''
    if playlist.isalnum(): 
        return True
    
    return False


def create_file(filetype:int, playlist:str):
    pass

def delete_file(filetype:int, playlist:str):
    pass

def append_to_file(song:str):
    pass

def delete_entry_in_file(filetype:int, entry:str):
    pass

    



