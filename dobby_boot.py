import getopt
from dobby_utils import Gringotts, Fluffy
import getopt
import os
import sys


# -------------------------------  SETTING UP DOBBY  ----------------------
def set_up(): 
    long_options =  ['help', 'cmd-prefix=', 'base-dir=', 'allow-playlist', 'allow-tasks', 'king-role=', 'playlist-roles=', 'tasks-roles=']
    short_options = 'hb:p:'
    
    config = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options , long_options)
        for opt, arg in opts:
            
            if opt in ('-h', '--help'):  # HELP option
                print_help()
                exit(0)
                
            if opt in ('-b', '--base_dir'):  #  BASE DIR configuration
                if arg is not None and arg != '':
                    config[Fluffy.BASE_DIR] = arg
                else:
                    print('Warning: Missing base_dir value.')
                
            elif opt in ('-p', '--cmd_prefix'):  # CMD PREFIX configuration
                if len(arg) == 1 and arg in ['.', ':','!','?','*', '/']:
                    config[Fluffy.CMD_PREFIX] = arg
                    print(arg)
                else:
                    print(args, 'is not a valid command prefix! Max length is 1. Possible prefixes: ' + ','.join(['.', ':','!','?','*', '/'])[:-1])
                    exit(1)

            elif opt in ('--allow-playlist'):  # Allowing playlist feature
                config[Fluffy.ALLOW_PLAYLIST] = True

            elif opt in ('--allow-tasks'):  # Allowing tasks feature
                config[Fluffy.ALLOW_TASKS] = True
                
            elif opt in ('--king-role'):  # Establishing role that has full privileges over Dobby
                if arg is not None and arg != '':
                    config[Fluffy.ROLE_KING] = arg
                else:
                    print("WARNING: Missing KING_ROLE value")
            
            elif opt in ('--playlist-roles'): # Establishing roles for playlist features
                if arg is not None and arg != '':
                    config[Fluffy.ROLES_PLAYLIST] = arg
                else:
                    print('WARNING: Missing ROLES_PLAYLIST value')
                    
            elif opt in ('--tasks-roles'): # Establishing roles for tasks features
                if arg is not None and arg != '':
                    config[Fluffy.ROLES_TASKS] = arg
                else:
                    print('WARNING: Missing ROLES_TASKS value')
            else:
                print('Unknown option \'%s\'' % opt)
                exit(1)
                
    except getopt.GetoptError as e:
        print("Unknown option \'%s\'")        
        exit(1)
        
    return config


def print_help():
    with open('./helptexts/dobby_help.txt') as f:
        h = "".join(f.readlines())
    print(h)