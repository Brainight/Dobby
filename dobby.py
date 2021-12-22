
import discord
import getopt
import os
import sys
from discord.ext import commands
import dobby_cogs
import dobby_utils 

class Dobby(commands.Bot):
    '''
    Dobby's bot class. 

    Keyword arguments for constructor:
    - cmd_prefix -- Command Prefix (default: '.')
    - base_dir: -- Dobby's root directory (default: os.path.expanduser('~'))
    '''
    def __init__(self, cmd_prefix:str = '.', base_dir=os.path.expanduser('~')):
        super().__init__(command_prefix=cmd_prefix)
        
        # Dobby's parameters
        self.base_dir = base_dir
        
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
        print('\n--- Running with following configuration ---')
        print(f'CMD_PREFIX \'%s\'' % self.command_prefix)
        print(f'BASE_DIR: \'%s\'' % self.base_dir)
        
    # ------------------  EVENTS  -----------------------
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self)) 
          
    # Processing messages
    async def on_message(self, msg:discord.Message):
        if msg.author == self.user:
            return
        elif msg.content.startswith(self.command_prefix):
            print(msg.content)
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


def set_up(dobby:commands.Bot):
    opts, args = getopt.getopt(sys.argv[1:], 'hb:p:', ['help', 'cmd_prefix=', 'base_dir='])
    for opt, arg in opts:
        if opt in ('-h', '--help'):  # Help option
            print_help()
        elif opt in ('-b', '--base_dir'):
            if arg is not None and arg != '':
                if dobby_utils.is_path_traversal(os.path.expanduser('~'), arg):
                    print('WARNING! Dobby should run inside your home directory...')
                dobby.base_dir = arg
                
        elif opt in ('-c', '--cmd_prefix'):
            if len(arg) == 1:
                dobby.command_prefix = arg
            else:
                print(args, 'is not a valid command prefix!')
                exit(1)
            
def print_help():
    help =  f'######################   D O B B Y   ######################## \
    \nThis is the help manual for executing dobby discord bot. \
    \nUsage: {sys.argv[0]}.py [Options]\
    \n\n Options: \
    \n\t -h | --help) \
    \n\t\t Displays this help message.\
    \n\
    \n\t -b | --base_dir) \
    \n\t\t Sets the base directory. Dobby won\'t be allowed to create or read files outside this directory. \
    \n\
    \n\t -p | --cmd_prefix) \
    \n\t\t Sets the command prefix. \
    \n\
    \nExample:\
    \n\t {sys.argv[0]}.py -b ~/discord -c \'!\'\
    \n\n Note that dobby can be execute with a default configuration. \
    \n The default configuration is: \
    \n cmd_prefix = \'.\'\
    \n base_dir = ~ (dobby executing user\'s home directory) \
    \n If base_dir has is user home directory, dobby will create/use a subfolder ~/.dobby'
    print(help)

# Execute Dobby
if __name__ == "__main__":
    dobby = Dobby() 
    set_up(dobby)
    dobby.print_configuration()
    dobby.run(os.getenv('discord_token'))
    
