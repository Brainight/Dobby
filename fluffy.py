import os 
from discord.ext.commands import Bot
import dobby_logging


logger = dobby_logging.getDobbyLogger(__name__)

class Fluffy:
    '''
    This class provides methods for Dobby to avoid unwanted Masters or intruders to
    harm Dobby or the belongings Dobby keeps from their friends.
    Since Dobby won't need more than one Cerberus, this class is never instanciated and all method are static or class methods

    Dobby by default is fairly restrictive.
    '''
 
    # ******************  CONSTANTS  ******************* (Not really...) 
    # CONFIGURATION PARAMETERS    
    CMD_PREFIX = 'CMD_PREFIX'
    BASE_DIR = 'BASE_DIR'
    ALLOW_PLAYLIST = 'ALLOW_PLAYLIST'
    ALLOW_TASKS = 'ALLOW_TASKS'
    ROLES_TASKS = 'ROLES_TS'
    ROLES_PLAYLIST = 'ROLES_PL'
    ROLE_KING = 'KING'
    GUILD = 'GUILD'

    # THE DEFAULT CONFIGURATION
    CONFIG = {
        CMD_PREFIX : '.',
        BASE_DIR : os.path.expanduser('~'),
        ALLOW_PLAYLIST : False,
        ALLOW_TASKS : False,
        ROLES_PLAYLIST : (),
        ROLES_TASKS : (),
        ROLE_KING : None,
        GUILD : None
            }

    def __init__(self, configuration:dict):
        self.config = Fluffy.CONFIG
        self.user_input = configuration
        logger.info('Loading Fluffy\'s configuration')
        
        
    # ***************** CONFIGURATION METHODS ***********************
    def _check_dobby_prefix(self, dobby:Bot):
        pass
    
    def _check_basedir(self, basedir:str):
        pass
    
    def _check_allow_playlist(self, b:bool):
        pass
    
    def _check_allow_tasks(self, b:bool):
        pass
    
    def _check_role_permission(self, roles_perms:str, role_type:str):
        '''
        roles_perms -> (check dobby_help.txt)
        role_type -> As Fluffy constant.
        '''
        pass
    
    def load_conf(self, dobby:Bot):
        
        for key, val in self.user_input.items():
            
            if key == self.BASE_DIR:
                pass
            
            elif key == self.CMD_PREFIX:
                pass
            
            elif key == self.ALLOW_PLAYLIST:
                pass
            
            elif key == self.ALLOW_TASKS:
                pass
            
            elif key == self.ROLE_KING:
                pass
            
            elif key == self.ROLES_PLAYLIST:
                pass
            
            elif key == self.ROLES_TASKS:
                pass
        
        del self.user_input
        logger.debug('Deleted tmp configuration variable.')
        logger.info('Configuration loaded succesfully.') 
        logger.info('Running configuration:' + dobby_logging.join_multiple_configurations(dobby.get_configuration(), self.get_configuration()))
        
        
        
    @staticmethod
    def get_guild(dobby:Bot):
        # Dobby can only be part of one server for each Dobby instance running    
        if len(dobby.guilds) > 1:
            print('QUITING! Dobby can only be part of one and only one guild...')
            gs = ''
            for guild in dobby.guilds:
                gs += guild.name + '\n'
            print('Dobby is part of these guilds: \n%s' % gs)
            return None
        elif len(dobby.guilds) < 1:
            print("Dobby needs to be a member of a Guild to do something!")
            return None
        else:
            return dobby.guilds[0]


    # ***************** FLUFFY'S COMPLAINS ************************
    class UnknownRoleException(Exception):
        def __init__(self, role):
            self.role = role
            self.message = '%s: Role %s does not exist'
            
    
    #************************  CONFIGURATION TEXT AND ERRORS  *****************************

    
    def get_configuration(self):
        config_str = '--------- Fluffy\'s Configuration -----------'
        for key, val in self.config.items():
            config_str += '\n%s=%s' % (key, val)
        
        return config_str
    
