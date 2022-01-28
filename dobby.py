
import discord
from discord.ext import commands
from fluffy import Fluffy
import dobby_logging as dlog
import dobby_cogs
from dobbyvoice import DobbyVoice

logger = dlog.getDobbyLogger(__name__)

class Dobby(commands.Bot):
    '''
    Dobby's bot class. 

    Keyword arguments for constructor:
    - cmd_prefix -- Command Prefix (default: '.')
    '''
    
    def __init__(self, configuration:dict, cmd_prefix:str = '.'):
        super().__init__(command_prefix=cmd_prefix)
   
        self.fluffy = Fluffy(configuration, self)
        self.music = DobbyVoice()
        self.description = \
        """
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
    def get_configuration(self):
        return '-------  Dobby\'s configuration  --------' \
        '\nCommand Prefix: \'' + self.command_prefix + '\'' 
        
        
    # ------------------  EVENTS  -----------------------
    async def on_ready(self):
        # This needs to be called at this point, if called before,
        # Fluffy can't ask Dobby for role verification etc...
        self.fluffy.load_conf()
        self.add_cog(dobby_cogs.MusicCog(self.music, self.fluffy.fluffymusic))
        # self.add_cog(dobby_cogs.RandomCog())
        logger.info('Cogs are set up')
        
        logger.info('Connected as: {0.user}'.format(self))
       
        
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


    # *********** HELPFUL DOBBY METHODS ***********
    def get_guild(self) -> discord.Guild:
        # Dobby can only be part of one server for each Dobby instance running    
        if len(self.guilds) > 1:
            gs = ''
            for guild in self.guilds:
                gs += guild.name + '\n'
            return None
        elif len(self.guilds) < 1:
            return None
        else:
            return self.guilds[0]
        
    def get_role(self, role:str) -> discord.Role:
        '''
        Return an object of type discord.Role if role string matches a role in the server.
        If no matching role is found, returns None.
        '''
        for r in self.fluffy.get_guild().roles:
            if r.name == role:
                return r
        
        return None
        
# ------------------------------- END OF DOBBY CLASS



    
