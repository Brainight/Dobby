
import discord
import getopt
import os
import sys
from discord.ext import commands
import dobby_cogs
from dobby_utils import Cerberus, Gringotts

class Dobby(commands.Bot):
    '''
    Dobby's bot class. 

    Keyword arguments for constructor:
    - cmd_prefix -- Command Prefix (default: '.')
    '''
    def __init__(self, cmd_prefix:str = '.'):
        super().__init__(command_prefix=cmd_prefix)
        
        # Set up cogs        
        dobby_cogs.set_up_cogs(self)

        # -------------------  CONFIGURATION  ----------------------
        # Setting a description
        self.description = """
        My name is Dobby! Dobby has no master. Dobby is a free elf!\n   
        You may order Dobby to do things for you by writing a '.' before saying what you want me to do.
    
        Try this: .inspire
        
        You may aswell talk to Dobby if you fancy some company...
        """
        
        # Changing default "no category" cog in help description
        self.help_command = commands.DefaultHelpCommand(
                no_category = 'Commands'
        )
    
    # ------------------  USEFUL METHODS  ----------------

    def print_configuration(self):
        print('\n-------  Dobby\'s configuration  --------')
        print('\n# Dobby:')
        print(f'Command Prefix: \'%s\'' % self.command_prefix)
        print('\n# Cerberus:')
        print(Cerberus.get_configuration())
        
    # ------------------  EVENTS  -----------------------
    async def on_ready(self):
        print('\nWe have logged in as {0.user}'.format(self)) 
          
    # Processing messages
    async def on_message(self, msg:discord.Message):
        if msg.author == self.user:
            return
        elif msg.content.startswith(self.command_prefix):
            await self.process_commands(msg)
        elif self.user in msg.mentions:
            return
        else:
            return
    
    
    # Action on deleting message. Only works for msgs written while bot was online.
    async def on_message_delete(self, msg:discord.Message):
        if msg.author == self.user:
            pass
        else:
            txt = '{0.author} has deleted a message...\n Message said:  \n"{0.content}"'.format(msg)
            await msg.channel.send(txt)

# ------------------------------- END OF DOBBY CLASS

# -------------------------------  SETTING UP DOBBY  ----------------------
def set_up(dobby:commands.Bot):
    long_options =  ['help', 'cmd-prefix=', 'base-dir=', 'allow-playlist', 'allow-tasks', 'king-role', 'playlist-roles', 'tasks-roles']
    short_options = 'hb:p:'
    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options , long_options)
        for opt, arg in opts:
            if opt in ('-h', '--help'):  # HELP option
                print_help()
                exit(0)
            elif opt in ('-b', '--base_dir'):  #  BASE DIR configuration
                if arg is not None and arg != '':
                    if dobby_utils.is_path_traversal(os.path.expanduser('~'), arg):
                        print('WARNING! Dobby should run inside your home directory...')
                    Cerberus.base_dir = arg
                
            elif opt in ('-p', '--cmd_prefix'):  # CMD PREFIX configuration
                if len(arg) == 1 and arg in ['.', ':','!','?','*', '/']:
                    dobby.command_prefix = arg
                else:
                    print(args, 'is not a valid command prefix! Max length is 1. Possible prefixes: ' + ','.join(['.', ':','!','?','*', '/'])[:-1])
                    exit(1)

            elif opt in ('--allow-playlist'):  # Allowing playlist feature
                Cerberus.allow_playlists = True

            elif opt in ('--allow-tasks'):  # Allowing tasks feature
                Cerberus.allow_tasks = True

            elif opt in ('--king-role'):  # Establishing role that has full privileges over Dobby
                pass
            
            elif opt in ('--playlist-roles'): # Establishing roles for playlist features
                pass

            elif opt in ('--tasks-roles'): # Establishing roles for tasks features
                pass

            else:
                print('Ignoring unknown option \'%s\'' % opt)
    except getopt.GetoptError as e:
        print("Unknown option \'%s\'")        
        exit(1)


def print_help():
    with open('./helptexts/dobby_help.txt') as f:
        h = "".join(f.readlines())
    print(h)

# Execute Dobby
if __name__ == "__main__":
    dobby = Dobby() 
    set_up(dobby)
    dobby.print_configuration()
    dobby.run(os.getenv('discord_token'))
    
