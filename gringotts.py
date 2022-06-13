
import os
import json
from datetime import date
from socketserver import DatagramRequestHandler

import dobby_logging
from dobbyvoice import DobbyVoice
import wisdom
from wisdom import Errors, Configurations, GringottsMetadata
import typing

if typing.TYPE_CHECKING:
    from fluffy import Hagrid
    import discord

logger = dobby_logging.getDobbyLogger(__name__)
    
#####################################    G R I N G O T T S    ####################################### 
class Gringotts():
    '''
    This class provides methods to handle Dobby's belongings.
    Dobby may posses the following items:
    - Playlists
    - Tasks
    All these are represented as files inside.
    
    All methods regarding tasks/playlist handling return either (bool, str) or (object, str)
    where:
    - bool | object -> is the result of the operation 
    - str           -> Description of the error for Dobby to send to channel
    '''
    
    A_CREATE = 'create'
    A_DELETE = 'delete'
    A_WRITE = 'write'
    A_ADD = 'add'
    A_REMOVE = 'remove'
    A_LIST = 'list'

    def __init__(self, hagrid:'Hagrid'):
        self._base_dir = wisdom.add_trailing_slash(hagrid.get_hogwarts_dir()+ 'gringotts')
        self._playlist_dir = None
        self._tasks_dir = None
        self._chambers = hagrid.get_gringotts_chambers()
        self._build_chambers()
        
    def get_config(self):
        config = \
        '\n-------- Gringott\'s Configuration -------- ' + \
        '\nBASEDIR: %s' % self._base_dir + \
        '\nCHAMBERS: %s' % self._chambers + \
        '\nPLAYLISTDIR: %s' % self._playlist_dir + \
        '\nTASKSDIR: %s' % self._tasks_dir 
        
        return config
            
    @staticmethod
    def get_error_string(error_type:int):
        return {
           Errors.ERR_F_FILE_EXISTS : 'You already posses what you are trying to craft...',
           Errors.ERR_F_INVALID_FILENAME : 'You can not use that name...',
           Errors.ERR_F_UNKNOWN_FILE_TYPE : 'Dobby can not save this type of item... ',
           Errors.ERR_F_ACCESS_FORBIDDEN : 'You are not allowed here...',
        }.get(error_type, 'This magic is unknown to Dobby, and Dobby knows all kinds of magic...')
        
    
    # ******************** Methods to build the chamber (Dobby's base directory structure) *************************
    def _build_chambers(self) -> None:
        if os.path.exists(self._base_dir):
            logger.info('Gringotts directory \'%s\' exists!', self._base_dir)
        else:
            logger.info('Creating Gringotts directory \'%s\'', self._base_dir)
            success = wisdom.create_directory(self._base_dir)
            if success:
                logger.info('Gringotts directory created!')
            else:
                logger.error('Unable to create Gringotts directory')
                
        if Configurations.ALLOW_PLAYLIST in self._chambers:
            self._build_chamber_of_playlists()
        else:
            logger.info('Gringotts chambers of playlists is hidden')
            
        if Configurations.ALLOW_TASKS in self._chambers:
            self._build_chamber_of_tasks()
        else:
            logger.info('Gringotts chamber of tasks is hidden')
            
                
    def _build_chamber_of_playlists(self) -> None:
            
            if os.path.exists(self._base_dir + GringottsMetadata._PLAYLISTS.value):
                self._playlist_dir = wisdom.add_trailing_slash(self._base_dir + GringottsMetadata._PLAYLISTS.value)
                logger.info('The Chamber of playlist is open: %s', self._playlist_dir)
            else:
                logger.info('Opening chamber of playlists...')
                success = wisdom.create_directory(self._base_dir + GringottsMetadata._PLAYLISTS.value)
                if success:
                    self._playlist_dir = wisdom.add_trailing_slash(self._base_dir + GringottsMetadata._PLAYLISTS.value)
                    logger.info('The Chamber of playlist has been opened: %s', self._playlist_dir)
                else:
                    logger.error('Could not create chamber of playlists')
                
    
    def _build_chamber_of_tasks(self) -> None: 
       
            if os.path.exists(self._base_dir + GringottsMetadata._TASKS.value):                
                logger.info('Chamber of tasks is open.')
                self._tasks_dir = wisdom.add_trailing_slash(self._base_dir + GringottsMetadata._TASKS.value)
            else:
                logger.info('Opening chamber of tasks...')
                success= wisdom.create_directory(self._base_dir + GringottsMetadata._TASKS.value)
                
                if success:
                    logger.info('The chamber of tasks is open')
                    self._task_dir = wisdom.add_trailing_slash(self._base_dir + GringottsMetadata._TASKS.value)
                else:
                    logger.error('Could not open the tasks of secrets')


    # ****************  Methods for Chamber of Playlist  *****************
    def create_playlist(self, playlist:str, author:'discord.Member') -> typing.Tuple[bool, str]:
        if wisdom.is_valid_filename(playlist):
            playlist_path = self._playlist_dir + playlist
            data = self._build_playlist_meta(author)
            success, error = wisdom.create_file(playlist_path)
            if success:
                success, error = wisdom.write_file_json(playlist_path, data)
                if success:
                    logger.info('Playlist creation success. Author: %s | Playlist: %s', author.display_name, playlist_path)
                    return True, None
                else:
                    return False, get_and_log_oserror_msg(GringottsMetadata._PLAYLISTS, error, author, Gringotts.A_CREATE)
            else:
                return False, get_and_log_oserror_msg(GringottsMetadata._PLAYLISTS, error, author, Gringotts.A_CREATE)
        else:
            logger.info('Invalid playlist name: %s', playlist)
            return False, 'Invalid playlist name \'%s\'' % playlist
    
    
    def _build_playlist_meta(self, author:'discord.Member') -> dict:
        d = date.today().strftime('%d/%m/%Y')
        playlist = { 
            GringottsMetadata.META_AUTHOR.value : author.display_name,
            GringottsMetadata.META_AUTHOR_ID.value : author.id,
            GringottsMetadata.META_CREATION_DATE.value : d,
            GringottsMetadata.META_LAST_MODIFIED.value : d,
            GringottsMetadata.META_ROLES.value : [],
            GringottsMetadata.META_SONGS.value : []
        }   
        
        return playlist
        
        
    def delete_playlist(self, playlist:str, member:'discord.Member') -> typing.Tuple[bool, str]:
        if wisdom.is_valid_filename(playlist):
            playlist_path = self._playlist_dir + playlist
            success, error = wisdom.delete_file(playlist_path, member)
            if success:
                logger.info('Playlist \'%s\' (%s) has been deleted. Executer: %s', playlist, playlist_path, member.display_name)
                return True, None
            else:
                return False, get_and_log_oserror_msg(GringottsMetadata._PLAYLISTS, error, member, Gringotts.A_DELETE)
        else:
            logger.info('Invalid playlist name...')
            return False, 'Invalid playlist name'
    
    
    def write_song_to_playlist(self, playlist:str, songs:list, author:'discord.Member') -> typing.Tuple[bool, str]:
        if wisdom.is_valid_filename(playlist):
            
            songs_data = self._build_meta_4_songs(songs, author)
            playlist_path = self._playlist_dir + playlist 
            data, error = wisdom.read_file_json(playlist_path)
            if data is not None:
                songs = data[GringottsMetadata.META_SONGS.value]
                songs.extend(songs_data)
                data[GringottsMetadata.META_SONGS.value] = songs
                success, error = wisdom.write_file_json(playlist_path, data)
                if success:
                    logger.info('Added songs to playlist: %s' % songs_data) 
                    return True, None
                else:
                    return False, get_and_log_oserror_msg(GringottsMetadata._PLAYLISTS, error, author, Gringotts.A_WRITE + ":" + Gringotts.A_ADD)
            else:
                return False, get_and_log_oserror_msg(GringottsMetadata._PLAYLISTS, error, author, Gringotts.A_WRITE + ":" + Gringotts.A_ADD)
        else: 
            return False, 'Playlist cannot have this type of name...'
    
    def _build_meta_4_songs(self, songs:list, author:'discord.Member') -> list:
        songs_data = []
        for song in songs:
            song_data = dict()
            ydl_data = DobbyVoice.find_song(song) 
            song_data[GringottsMetadata.META_ADD_SONG_EXECUTER.value] = author.display_name
            song_data[GringottsMetadata.META_ADD_SONG_DATE.value] = date.today().strftime('%d/%m/%Y')
            song_data = {**song_data, **ydl_data}
            songs_data.append(song_data)
        return songs_data
    
    def _playlist_exists(self, playlist) -> bool:
        for file in os.listdir(self._playlist_dir):
            if file == playlist:
                return True
        return False


    def remove_from_playlist(self, playlist_path:str, *songs:int) -> typing.Tuple[bool, str]:
        data, error = wisdom.read_file_json(playlist_path)
        if data is not None:
            s_data = data[GringottsMetadata.META_SONGS.value]
            for i_song in songs:
                try:
                    del s_data[i_song]
                except IndexError as ie:
                    logger.info('Cannot delete index  \'%s\' from list. List length: \'%s\'', i_song, len(s_data))
                    return False, ie
                
            data[GringottsMetadata.META_SONGS.value] = s_data
            return wisdom.write_file_json(data)
        else:
            return False, error
    
    
    def list_playlists(self) -> typing.Tuple[bool, str]:
        data = "###############   PLAYLISTS   ###############\n"
        for i, file in enumerate(os.listdir(self._playlist_dir)):
            data += '%d. %s\n' % (i + 1, file)
        return True, data
        
        
    def list_playlist_songs(self, playlist:str, member:'discord.Member') -> typing.Tuple[bool, str]:
        '''
        Returns a dictionary with all the playlist information or None
        '''
        if wisdom.is_valid_filename(playlist):
            path = self._playlist_dir + playlist
            pl_data, error = wisdom.read_file_json(path)
            if pl_data is not None:
                data = '###############  PLAYLIST: %s  ##############\n' % playlist
                for i, song in enumerate(pl_data.get(GringottsMetadata.META_SONGS.value)):
                    data += '%d. %s\n' % (i, song.get(GringottsMetadata.META_SONG_TITLE.value))
                return True, data
            else:
                return False, get_and_log_oserror_msg(GringottsMetadata._PLAYLISTS, error, member, Gringotts.A_LIST)
        else:
            return False, 'Invalid playlist name!'
        
    # ****************  Methods for Chamber of Tasks  ***************
        
        

            
        
def get_and_log_oserror_msg(context:GringottsMetadata, error:OSError, author:'discord.Member', action:str) -> str:

    if error.errno == 2:  # No such file or dir
        logger.error('[%s] Author: %s | Action: %s | File: %s | Error: %s', context.value, author.display_name, action, error.filename, error.strerror)
        return 'This does not exist!'
    
    elif error.errno == 5:  # I/O Error
        logger.error('[%s] Author: %s | Action: %s | File: %s | Error: %s', context.value, author.display_name, action, error.filename, error.strerror)
        return 'Some unknown magic has stopped Dobby!'
    
    elif error.errno == 13:  # Permission denied
        logger.error('[%s] Author: %s | Action: %s | File: %s | Error: %s', context.value, author.display_name, action, error.filename, error.strerror)
        return 'Dobby will not open this door for you! Permission denied!'
    
    elif error.errno == 17:  # File exists
        logger.error('[%s] Author: %s | Action: %s | File: %s | Error: %s', context.value, author.display_name, action, error.filename, error.strerror)
        return 'Somebody has already crafted this!'
    
    elif error.errno == 26: # Text file busy
        logger.error('[%s] Author: %s | Action: %s | File: %s | Error: %s', context.value, author.display_name, action, error.filename, error.strerror)
        return 'Seems like somebody is already using that chamber...'

    elif error.errno == 30: #  Read only file system
        logger.error('[%s] Author: %s | Action: %s | File: %s | Error: %s', context.value, author.display_name, action, error.filename, error.strerror)
        return 'The chambers are closed with very powerful magic!'
    
    else:
        logger.error('[%s] Author: %s | Action: %s | File: %s | Error: %s', context.value, author.display_name, action, error.filename, error.strerror)
        logger.error(error)
        return 'Dobby has been stopped by some unknown magic... See the logs...'



