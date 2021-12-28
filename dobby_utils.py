
import os
import sys 
import re

'''
This module provides different utilties for Dobby to use, such as handling files and some security measures.
'''


class Gringotts():
    '''
    This class provides methods to handle Dobby's belongings.
    Dobby may posses the following items:
    - Playlists
    - Tasks
    All these are represented as files inside Dobby's configured 'base_dir' parameter.
    '''

     # File types
    FILE_PLAYLIST = 1
    FILE_TASK = 2

    @staticmethod
    def create_file(filetype:int, file:str):
        pass

    @staticmethod
    def delete_file(filetype:int, file:str):
        pass

    @staticmethod
    def append_to_file(filetype:int, entry:str):
        pass

    @staticmethod
    def delete_entry_in_file(filetype:int, entry:str):
        pass


class Cerberus:
    '''
    This class provides methods for Dobby to avoid unwanted Masters or intruders to
    harm Dobby or the belongings Dobby keeps from their friends.
    Since Dobby won't need more than one Cerberus, this class is never instanciated and all method are static or class methods

    Dobby by default is fairly restrictive.
    '''

    # ----------------- C O N S T A N T S  -------- (Not really...) 
    # Success code
    ALOHOMORA = 0

    # File Errors
    F_ERR_FILE_EXISTS = 100
    F_ERR_INVALID_FILENAME = 101
    F_ERR_UNKNOWN_FILE_TYPE = 102

    # Access Errors
    A_ERR_ACCESS_FORBIDDEN = 200

    # ---------------- CONFIGURATION PARAMETERS  -----------------
    base_dir = os.path.expanduser('~')
    allow_playlists = False
    allow_tasks = False

    # The role that can do everything
    king_role = ''

    # List of roles + specific role permissions for playlist and task commands.
    playlist_roles = ()
    task_roles = ()

    @staticmethod
    def is_path_traversal(base_dir, file):
        ''' 
        Check if variable file, referneces a file 
        Absolut path of playlist should be inside 'dir' (chroot directory path)
        '''
        path = os.path.abspath(file)
        return base_dir == os.path.commonpath((base_dir, path))

    @staticmethod
    def is_valid_filename(filename:str):
        '''
        Only allows alpha numeric + '_' characters in playlist name.
        - Works against path traversal.
        - Prevents directory creation.
        - Prevents hidden files & strange filenames.
        '''
        if len(filename) == 0:
            return False

        return True if re.fullmatch('[\w]*', filename, re.ASCII) is not None else False

    @staticmethod
    def _file_exists(filetype:int, filename:str):
        pass

    @classmethod
    def is_allowed_member():
        return True

    @classmethod
    def is_friend():
        pass

    @classmethod
    def validate_file_creation(cls, filetype:int, filename:str):
        if filetype not in [DobbyFiles.FILE_PLAYLIST, DobbyFiles.FILE_TASK]:  # Checking for allowed filetype
            return cls.F_ERR_UNKNOWN_FILE_TYPE

        if cls.is_allowed_member():  # Deny access to unallowed members
            if cls._file_exists(filetype, filename): # Deny file override
                return cls.F_ERR_FILE_EXISTS

            if cls.is_valid_filename(filename):  # Deny invalid filenames
                return cls.ALOHOMORA
            else:
                return cls.F_ERR_INVALID_FILENAME
        else:
            return cls.A_ERR_ACCESS_FORBIDDEN

    @classmethod
    def get_error_string(cls, error_type:int):
        return {
            cls.F_ERR_FILE_EXISTS : 'You already posses what you are trying to craft...',
            cls.F_ERR_INVALID_FILENAME : 'You can not use that name...',
            cls.F_ERR_UNKNOWN_FILE_TYPE : 'Dobby can not save this type of item... ',
            cls.A_ERR_ACCESS_FORBIDDEN : 'You are not allowed here...',
        }.get(error_type, 'This magic is unknown to Dobby, and Dobby knows all kinds of magic...')

    @classmethod
    def get_configuration(cls):
        return 'Base directory: %s\nAllow Playlists: %s\nAllow Tasks: %s' % (cls.base_dir, cls.allow_playlists, cls.allow_tasks)
    



