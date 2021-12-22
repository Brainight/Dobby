
import os
import sys

PLAYLIST_FILE = 1
TASKS_FILE = 2

def is_path_traversal(base_dir, file):
    ''' 
    Check if variable file, referneces a file 
    Absolut path of playlist should be inside 'dir' (chroot directory path)
    '''
    path = os.path.abspath(file)
    return base_dir == os.path.commonpath((base_dir, path))

def file_is_alnum(filename:str):
    '''
    Only allows alpha numeric characters in playlist name.
    - Works against path traversal.
    - Prevents directory creation.
    - Prevents hidden files & strange filenames.
    '''
    return filename.isalnum()


def create_file(filetype:int, playlist:str):
    pass

def delete_file(filetype:int, playlist:str):
    pass

def append_to_file(song:str):
    pass

def delete_entry_in_file(filetype:int, entry:str):
    pass

    



