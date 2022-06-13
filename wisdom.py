import re
import os
import typing
import json
from datetime import date
from enum import Enum, IntFlag
import dobby_logging

if typing.TYPE_CHECKING:
    import discord
"""
This module defines utility methods for whole Hogwarts.
"""

logger = dobby_logging.getDobbyLogger(__name__)

class Errors(IntFlag):
    # Errors
    ERR_F_FILE_EXISTS = 0b00000001
    ERR_F_INVALID_FILENAME = 0b00000010
    ERR_F_UNKNOWN_FILE_TYPE = 0b0000011
    ERR_F_ACCESS_FORBIDDEN = 0b00000100


class GringottsMetadata(Enum):
    META_AUTHOR = 'author'
    META_AUTHOR_ID = 'author_id'
    META_CREATION_DATE = 'crafted'
    META_LAST_MODIFIED = 'last_modified'
    META_ROLES = 'roles'
    META_DESCRIPTION = 'description'
    META_SONGS = 'songs'
    META_ADD_SONG_DATE = 'date'
    META_ADD_SONG_EXECUTER = 'executer'
    META_SONG_TITLE = 'title'
    META_SONG_SRC = 'src'
    META_SONG_TYPE = 'song_type'
    _PLAYLISTS = 'playlists'
    _TASKS = 'tasks'
    
class MusicSongTypes(Enum):
    YOUTUBE = 'yb'
    LOCAL = 'local'
    
    
class Permissions(IntFlag):
    # Permission types
    PERM_WR = 0b11
    PERM_R = 0b01
    PERM_W = 0b10
    PERM_DENY = 0b00
    
class Configurations(Enum):
    # CONFIGURATION PARAMETERS    
    CMD_PREFIX = 'CMD_PREFIX'
    BASE_DIR = 'BASE_DIR'
    ALLOW_PLAYLIST = 'ALLOW_PLAYLIST'
    ALLOW_TASKS = 'ALLOW_TASKS'
    ROLES_TASKS = 'ROLES_TS'
    ROLES_PLAYLIST = 'ROLES_PL'
    ROLE_KING = 'KING'
    GUILD = 'GUILD'
    
# *********************** HELPFUL METHODS ************************
def build_simple_song_data_entry(title:str, resource:str, type:MusicSongTypes) -> dict:
    return {GringottsMetadata.META_SONG_TITLE.value : title,
            GringottsMetadata.META_SONG_SRC.value : resource,
            GringottsMetadata.META_SONG_TYPE : type.value}
    

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


def add_trailing_slash(base_dir:str) -> str:
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

def is_file(file:str):
    return os.path.isfile(file)

def is_directory(file:str):
    return os.path.isdir(file)


def create_directory(directory:str) -> bool:
    try:
        os.mkdir(directory)
        return True
    except OSError as e:
        return False
    
    
def create_file(path:str) -> typing.Tuple[bool, OSError]:
    try:
        f = open(path, 'x')
        return True, None
    except OSError as err:
        return False, err
    
    
def write_file_json(path:str, data:dict) -> typing.Tuple[bool, OSError]:
    try:
        f = open(path, 'w')
        print(data)
        json.dump(data, f)
        f.close()
        return True, None
    except OSError as err:
        return False, err

def read_file_json(path:str) -> typing.Tuple[dict, OSError]:
    try:
        f = open(path, 'rt')   
        data = json.load(f)
        f.close()
        return data, None
    except OSError as err: 
        return None, err


def _get_file_creator_id(path:str) -> typing.Tuple[int, OSError]:
    '''
    Returns the ID of the playlist creator or -1 if error.
    '''
    data, error = read_file_json(path)
    if data is not None:
        return data.get(GringottsMetadata.META_AUTHOR_ID.value), None
    else:
        return data, error


def delete_file(path:str, member:'discord.Member') -> typing.Tuple[bool, OSError]:
    '''
    Use with love and care.
    '''
    m_id, error = _get_file_creator_id(path)
    if m_id is None:
        return False, error
    if m_id == member.id:
        try:
            os.remove(path)
            return True, None
        except OSError as err:
            return False, err
    else:
        return False, OSError(13, 'Member is not owner of file!', path)                                                                     
  
def list_directory(directory:str):
    return os.listdir(directory)  
    

def is_valid_cmd_prefix(prefix:str) -> bool:
    return prefix in ['.', '!', '?', '¿', '¡', '/', '\\', ':', ';']


def is_music_file(file:str):
    with open(file, 'rb') as f:
        magic_number = f.read(12)
        if magic_number[0:4] == b'\x52\x49\x46\x46' and magic_number[8:12] == b'\x41\x56\x49\x20': # .wav file
            return True
        if magic_number[0:2] in [b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2', b'\xFF\xF1']: # .mp3 or .aac
            return True
        
        return False
    
        
def get_and_log_oserror_msg(context:GringottsMetadata, error:OSError) -> str:

    if error.errno == 2:  # No such file or dir
        logger.error('[%s] File does not exists. File: %s', context.value, error.filename)
        return 'Dobby doesn\'t recognize what you are searching.'
    
    elif error.errno == 5:  # I/O Error
        logger.error('[%s] IOError! %s', context.value, error.filename)
        return 'Some unknown magic has stopped Dobby!'
    
    elif error.errno == 13:  # Permission denied
        logger.error('[%s] Permission denied. %s', context.value, error.filename)
        return 'Dobby will not open this door for you! Permission denied!'
    
    elif error.errno == 17:  # File exists
        logger.error('[%s] File exists!', context.value)
        return 'Somebody has already crafted this!'
    
    elif error.errno == 26: # Text file busy
        logger.error('[%s] File is busy. (Maybe already in use..): %s', context.value, error.filename)
        return 'Seems like somebody is already using that chamber...'

    elif error.errno == 30: #  Read only file system
        logger.error('[%s] Read only filesystem. Cannot write here!! %s', context.value, error.filename)
        return 'The chambers are closed with very powerful magic!'
    
    else:
        logger.error('[%s] Unknown OSError occurred. %s', context.value, error.filename)
        logger.error(error)
        return 'Dobby has been stopped by some unknown magic... See the logs...'
        