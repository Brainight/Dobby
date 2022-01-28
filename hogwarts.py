import getopt
from re import I
import sys
import os

from fluffy import Fluffy, FluffyConstants
import dobby_logging as dlog
import wisdom
from dobby import Dobby

logger = dlog.getDobbyLogger(__name__)

class Hogwarts:
    _DEF_BASE_DIR = os.path.expanduser('~')
    
    def __init__(self, args:dict):
        self.dobby = None
        logger.info('Creating Hogwarts...')
        if FluffyConstants.BASE_DIR in args.keys():
            home_dir = self._create_home_dir(args[FluffyConstants.BASE_DIR])
        else:
            home_dir = self._create_home_dir(Hogwarts._DEF_BASE_DIR)
        
        args[FluffyConstants.BASE_DIR] = home_dir
        self._call_dobby(args)
    
    
    def _call_dobby(self, args):
        self.dobby = Dobby(args)
        self.dobby.run(os.getenv('discord_token'))  
        
        
    def _create_home_dir(self, base_dir:str) -> str:
        base_dir = wisdom.add_trailing_slash(base_dir)   
        if wisdom.is_home_diretory(base_dir):
            dir = os.path.abspath(base_dir + '.hogwarts')
            
            if os.path.exists(dir):
                logger.info('Detected home hogwarts directory.')
                
                if wisdom.is_readable_directory(dir):
                    base_dir = dir
                else:
                      logger.error('Hogwarts home directory is not readable!')
                      logger.critical('Exiting due to -> UNREADBLE HOGWARTS HOME DIRECTORY')
                      exit(1)
                if not wisdom.is_writeable_directory(base_dir):
                    logger.info('Writing actions are not allowed on base directory \'%s\'. Read Only.', base_dir)
                    
            else:
                success, error = wisdom.create_directory(dir) 
                base_dir = dir
                
                if success:
                    logger.info('Created home directory \'%s\' for Hogwarts', base_dir)
                else:
                    logger.error('Could not create Hogwarts base directory \'%s\'', base_dir)
                    logger.error(error)
                
        else:
            if os.path.exists(base_dir) and wisdom.is_readable_directory(base_dir):
                logger.info('Using %s as Hogwarts base directory.', base_dir)
                if not wisdom.is_writeable_directory(base_dir):
                    logger.info('Writing actions are not allowed on base directory \'%s\'. Read Only.', base_dir)
            else:
                logger.error('Directory \'%s\' does not exist or is not readable')
                logger.critical('Exiting due to -> UNUSABLE DIRECTORY.')
                exit(1)
               
        return base_dir




def read_cmd_line_args() -> dict: 
    config = {}    
    long_options =  ['help', 'cmd-prefix=', 'base-dir=', 'allow-playlist', 'allow-tasks', 'king-role=', 'playlist-roles=', 'tasks-roles=']
    short_options = 'hb:p:'
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options , long_options)
        for opt, arg in opts:
            
            if opt in ('-h', '--help'):  # HELP option
                print_help()
                exit(0)
                
            if opt in ('-b', '--base-dir'):  #  BASE DIR configuration
                if arg is not None and arg != '':
                    config[FluffyConstants.BASE_DIR] = arg
                else:
                    print('Error: Missing %s value.' % FluffyConstants.BASE_DIR)
                    exit(1)
                
            elif opt in ('-p', '--cmd_prefix'):  # CMD PREFIX configuration
                if arg is not None and arg != '':
                    config[FluffyConstants.CMD_PREFIX] = arg
                else:
                    print('Error: Missing %s value.' % FluffyConstants.CMD_PREFIX)
                    exit(1)

            elif opt in ('--allow-playlist'):  # Allowing playlist feature
                config[FluffyConstants.ALLOW_PLAYLIST] = True

            elif opt in ('--allow-tasks'):  # Allowing tasks feature
                config[FluffyConstants.ALLOW_TASKS] = True
                
            elif opt in ('--king-role'):  # Establishing role that has full privileges over Dobby
                if arg is not None and arg != '':
                    config[FluffyConstants.ROLE_KING] = arg

                else:
                    print('Error: Missing %s value.' % FluffyConstants.ROLE_KING)
                    exit(1)
            
            elif opt in ('--playlist-roles'): # Establishing roles for playlist features
                if arg is not None and arg != '':
                    config[FluffyConstants.ROLES_PLAYLIST] = arg
                else:
                    print('Error: Missing %s value.' % FluffyConstants.ROLES_PLAYLIST)
                    exit(1)
                    
            elif opt in ('--tasks-roles'): # Establishing roles for tasks features
                if arg is not None and arg != '':
                    config[FluffyConstants.ROLES_TASKS] = arg
                else:
                    print('Error: Missing %s value.' % FluffyConstants.ROLES_TASKS)
                    exit(1)
            else:
                print('Unknown option \'%s\'' % opt)
                exit(1)
                
    except getopt.GetoptError as e:
        print(e.msg)        
        exit(1)

    logger.info('Loaded configuration from command line: \n\n' + '\n'.join(['%s=%s' % (key, val) for key, val in config.items()]) + '\n\n')
    return config


def print_help():
    with open('./dobby.texts.d/dobby_help.txt') as f:
        h = "".join(f.readlines())
    print(h)
    
    
if __name__ == "__main__":
    args = read_cmd_line_args()
    howgarts = Hogwarts(args)