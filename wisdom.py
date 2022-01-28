import re
import os
import typing
import json
from datetime import date

"""
This module defines utility methods for whole Hogwarts.
"""


# ********************* FILE RELATED METHODS ******************
def is_path_traversal(base_dir, file) -> bool:
    ''' 
    Given a base_dir, checks if file is outside this directory.
    '''
    path = os.path.abspath(file)
    return base_dir == os.path.commonpath((base_dir, path))


def is_valid_filename(filename:str) -> bool:
    '''
    Only allows alpha numeric + '_' characters in playlist name.
    - Works against path traversal.
    - Prevents directory creation.
    - Prevents hidden files & strange filenames.
    '''
    if len(filename) == 0:
        return False

    return True if re.fullmatch('[\w]*', filename, re.ASCII) is not None else False


def is_home_diretory(dir:str) -> bool:
   return dir in (os.path.expanduser('~'), os.path.expanduser('~') + os.path.sep, '~') 


def add_trailing_slash(base_dir:str) -> None:
    '''
    Returns the absolute path for 'base_dir' followed by system path separator.
    '''
    base_dir = os.path.abspath(base_dir)
    if base_dir[-1] in ('\\', '/'):
        return base_dir
    else:
        return base_dir + os.path.sep
        
def is_writeable_directory(directory:str) -> bool:
    # I could use os.access(dir, os.W_OK), but the implemented method asks for forgiveness rather than for permission.
    try:
        tmp_prefix = "tfile";
        count = 0
        filename = os.path.join(directory, tmp_prefix)
    
        while(os.path.exists(filename)):
            filename = "{}.{}".format(os.path.join(directory, tmp_prefix),count)
            count = count + 1
            
        f = open(filename,"w")
        f.close()
        os.remove(filename)
        return True
    except Exception:
        return False
  
    
def is_readable_directory(directory:str) -> bool:
    return os.access(directory, os.R_OK)

def file_exists(file_abs_path:str):
    return os.path.exists(file_abs_path)

def create_directory(directory:str) -> typing.Tuple[bool, OSError]:
    try:
        os.mkdir(directory)
        return True, None
    except OSError as e:
        return False, e
    
    
def create_file(path:str) -> typing.Tuple[bool, OSError]:
    try:
        f = open(path, 'x')
    except OSError as err:
        return False, err 
    
def create_file_and_write_json(path:str, data:object):
    try:
        f = open(path, 'w')
        json.dump(data, f)
        f.close()
        return True, None
    except OSError as err:
        return False, err 
    
def read_file_json(path:str) -> typing[dict, OSError]:
    try:
        f = open(path, 'rt')   
        data = json.load(f)
        return data
    except OSError as err: return None, err
    finally: f.close()
        


def append_playlist_song(songs:list):
    pass  # TODO Get data from file and add new data


def is_valid_cmd_prefix(prefix:str) -> bool:
    return prefix in ['.', '!', '?', '¿', '¡', '/', '\\', ':', ';']