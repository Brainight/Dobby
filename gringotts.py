
import os
import json
from datetime import date

import dobby_logging
from dobbyvoice import DobbyVoice
from fluffy import FluffyConstants
import wisdom
import typing

if typing.TYPE_CHECKING:
    from fluffy import Hagrid
    import discord

logger = dobby_logging.getDobbyLogger(__name__)


_PLAYLISTS = 'playlists'
_TASKS = 'tasks'

# Errors
ERR_F_FILE_EXISTS = 0b00000001
ERR_F_INVALID_FILENAME = 0b00000010
ERR_F_UNKNOWN_FILE_TYPE = 0b0000011
ERR_F_ACCESS_FORBIDDEN = 0b00000100


# OBJECTS DATA
META_AUTHOR = 'author'
META_AUTHOR_ID = 'author_id'
META_CREATION_DATE = 'crafted'
META_LAST_MODIFIED = 'last_modified'
META_ROLES = 'roles'
META_DESCRIPTION = 'description'
META_SONGS = 'songs'

    
    
#####################################    G R I N G O T T S    ####################################### 
class Gringotts():
    '''
    This class provides methods to handle Dobby's belongings.
    Dobby may posses the following items:
    - Playlists
    - Tasks
    All these are represented as files inside.
    '''

    def __init__(self, hagrid:Hagrid):
        self._base_dir = wisdom.add_trailing_slash(hagrid.get_base_dir()) + 'gringotts'
        self._playlist_dir = None
        self._tasks_dir = None
        self._chambers = hagrid.get_gringotts_chambers()
        self._build_chamber()
        
        
    @staticmethod
    def get_error_string(error_type:int):
        return {
            ERR_F_FILE_EXISTS : 'You already posses what you are trying to craft...',
            ERR_F_INVALID_FILENAME : 'You can not use that name...',
            ERR_F_UNKNOWN_FILE_TYPE : 'Dobby can not save this type of item... ',
            ERR_F_ACCESS_FORBIDDEN : 'You are not allowed here...',
        }.get(error_type, 'This magic is unknown to Dobby, and Dobby knows all kinds of magic...')
        
    
    # ******************** Methods to build the chamber (Dobby's base directory structure) *************************
    def _build_chambers(self) -> None:
        if os.path.exists(self.base_dir):
            logger.info('Gringotts directory \'%s\' exists!', self.base_dir)
        else:
            logger.info('Creating Gringotts directory \'%s\'', self.base_dir)
            success, error = wisdom.create_directory(self.base_dir)
            if success:
                logger.info('Gringotts directory created!')
            else:
                logger.error('Unable to create Gringotts directory')
                logger.error(error)
                
        if FluffyConstants.ALLOW_PLAYLIST in self._chambers:
            self._build_chamber_of_playlists()
        else:
            logger.info('Gringotts chambers of playlists is hidden')
            
        if FluffyConstants.ALLOW_TASKS in self._chambers:
            self._build_chamber_of_tasks()
        else:
            logger.info('Gringotts chamber of tasks is hidden')
            
                
    def _build_chamber_of_playlists(self) -> None:
            
            if os.path.exists(self.base_dir + _PLAYLISTS):
                logger.info('The Chamber of playlist is open.')
                self._playlist_dir = wisdom.add_trailing_slash(self._base_dir + _PLAYLISTS)
            else:
                logger.info('Opening chamber of playlists...')
                success, error = wisdom.create_directory(self._base_dir + _PLAYLISTS)
                if success:
                    logger.info('The chamber of playlist is open')
                    self._playlist_dir = wisdom.add_trailing_slash(self._base_dir + _PLAYLISTS)
                else:
                    logger.error('Could not create chamber of secrets')
                    logger.error(error)
                
    
    def _build_chamber_of_tasks(self) -> None: 
       
            if os.path.exists(self.base_dir + _TASKS):
                logger.info('Chamber of tasks is open.')
                self._tasks_dir = wisdom.add_trailing_slash(self._base_dir + _TASKS)
            else:
                logger.info('Opening chamber of tasks...')
                success, error = wisdom.create_directory(self._base_dir + _TASKS)
                
                if success:
                    logger.info('The chamber of secrets is open')
                    self._task_dir = wisdom.add_trailing_slash(self._base_dir + _TASKS)
                else:
                    logger.error('Could not open the chamber of secrets')
                    logger.error(error)


    # ****************  Methods for Chamber of Playlist  *****************
    def create_playlist(self, playlist:str, author:discord.Member) -> typing.Tuple[bool, object]:
        if wisdom.is_valid_filename(playlist):
            playlist_path = wisdom.add_trailing_slash(self._playlist_dir + playlist)
            data = self._build_playlist_meta(author)
            success, error = wisdom.create_file_and_write(playlist_path, data)
            if success:
                logger.info('Created file (playlist): \'%s\'', playlist_path)
                return True, None
            else:
                logger.error('Cannot create file (playlist): \'%s\' due to:', playlist_path)
                logger.error(error)
                return False, error
        else:
            logger.info('Invalid filename \'%s\' for playlist chamber.', playlist)
            return False, 'Invalid playlist name \'%s\'' % playlist
    
    
    def _build_playlist_meta(self, author:discord.Member) -> dict:
        d = date.today().strftime('%d/%m/%Y')
        playlist = {
            META_AUTHOR : author.display_name,
            META_AUTHOR_ID : author.id,
            META_CREATION_DATE : d,
            META_LAST_MODIFIED : d,
            META_SONGS : {}
        }   
        
        return playlist
        
        
    def delete_playlist(self, playlist:str):
        if wisdom.is_valid_filename(playlist):
            playlist_path = wisdom.add_trailing_slash(self._playlist_dir + playlist)
            success, error = wisdom.delete_file(playlist_path)
            if success:
                return True, None
            else:
                logger.error('Cannot delete playlist: \'%s\' due to: ', playlist_path)
                logger.error(error)
                return False, error
        else:
            logger.info('Invalid playlist name...')
            return False, 'Invalid playlist name'
    
    
    def write_to_playlist(self, playlist:str, *songs, author:str):
        if wisdom.is_valid_filename(playlist):
            if not self._playlist_exists():
                return False, 'Playlist doesn\'t exist'
            
            data = []
            for song in songs:
                song_data = dict()
                ydl_data = DobbyVoice.find_song(song) 
                song_data['executer'] = author
                song_data['date'] = date.today().strftime('%d/%m/%Y')
                song_data = {**data, **ydl_data}
                data.append(song_data)
            
            wisdom.append_playlist_song(data)
        else:
            return False
    
    def remove_from_playlist(self, playlist:str, *songs):
        pass
    
    def open_playlist(self, playlist:str, args) -> dict:
        '''
        Returns a dictionary with all the playlist information or None
        '''
        if wisdom.is_valid_filename(playlist):
            path = self._playlist_dir + playlist
            data, error = wisdom.read_file_json(path)
            if data is not None:
                return data
            else:
                logger.error('Cannot read content from file \'%s\' due to: %s', path, error)
                return None
        else:
            return None
        
    # ****************  Methods for Chamber of Tasks  ***************
        
        

            
        
            
 



