
import os
import sys 
import re
import dobby_logging

logger = dobby_logging.getDobbyLogger(__name__)

#####################################    G R I N G O T T S    ####################################### 
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
    
    # Errors
    ERR_F_FILE_EXISTS = ''
    ERR_F_INVALID_FILENAME = ''  
    ERR_F_UNKNOWN_FILE_TYPE = ''   
    ERR_F_ACCESS_FORBIDDEN = ''
    
     
    @staticmethod
    def delete_file(filetype:int, file:str):
        pass

    @staticmethod
    def append_to_file(filetype:int, entry:str):
        pass

    @staticmethod
    def delete_entry_in_file(filetype:int, entry:str):
        pass

    @staticmethod
    def get_error_string(error_type:int):
        return {
            Fluffy.F_ERR_FILE_EXISTS : 'You already posses what you are trying to craft...',
            Fluffy.F_ERR_INVALID_FILENAME : 'You can not use that name...',
            Fluffy.F_ERR_UNKNOWN_FILE_TYPE : 'Dobby can not save this type of item... ',
            Fluffy.A_ERR_ACCESS_FORBIDDEN : 'You are not allowed here...',
        }.get(error_type, 'This magic is unknown to Dobby, and Dobby knows all kinds of magic...')


    # ***************** FILE SECURITY METHODS **********************
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



