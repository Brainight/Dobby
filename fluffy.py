from abc import abstractmethod
import os
import discord
import typing

import dobby_logging
from gringotts import Gringotts
import wisdom

if typing.TYPE_CHECKING:
    from dobby import Dobby
    from dobbyvoice import DobbyVoice
    from discord.ext.commands import Context
    
logger = dobby_logging.getDobbyLogger(__name__)

class FluffyConstants():
    
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
    
    # Permission types
    PERM_WR = 0b11
    PERM_R = 0b01
    PERM_W = 0b10
    PERM_DENY = 0b00

    # THE DEFAULT CONFIGURATION
    CONFIG = {
        CMD_PREFIX : '.',
        BASE_DIR : os.path.expanduser('~'),
        ALLOW_PLAYLIST : False,
        ALLOW_TASKS : False,
        ROLES_PLAYLIST : {},  
        ROLES_TASKS : {},
        ROLE_KING : None,
        GUILD : None
    }
    
    
class Fluffy():
    '''
    This class provides methods for Dobby to avoid unwanted Masters or intruders to
    harm Dobby or the belongings Dobby keeps from their friends.

    Dobby by default is fairly restrictive.
    '''
    
    def __init__(self, configuration:dict, dobby:'Dobby'):
        self.user_input = configuration  # This variable is deleted after method "load_conf" is called.
        self.config = FluffyConstants.CONFIG
        self._hagrid = None
        self.fluffymusic = None
        self.dobby = dobby
        self._gringotts = None
        
    def get_guild(self):
        return self.config[FluffyConstants.GUILD]
    
    # ***************** CONFIGURATION METHODS ***********************
    def _conf_dobby_prefix(self):
        if self.user_input[FluffyConstants.CMD_PREFIX] in ['.', '!', '?', '¿', '¡', '/', '\\', ':', ';']:
            self.dobby.command_prefix = self.user_input[Fluffy.CMD_PREFIX]
            self.config[FluffyConstants.CMD_PREFIX] = self.user_input[FluffyConstants.CMD_PREFIX]
            logger.info('Setting Dobby\'s %s = %s', FluffyConstants.CMD_PREFIX, self.config[FluffyConstants.CMD_PREFIX])
        else:
            logger.warning('Invalid %s \'%s\' -> Using default: \'%s\'', FluffyConstants.CMD_PREFIX,
                           self.user_input[FluffyConstants.CMD_PREFIX], self.config[Fluffy.CMD_PREFIX])
                                                                                                    
                                                                                                            
    def _conf_basedir(self, basedir:str):
        self.config[FluffyConstants.BASE_DIR] = wisdom.add_trailing_slash(basedir)
    
    def _conf_allow_playlist(self, b:bool):
        self.config[FluffyConstants.ALLOW_PLAYLIST] = b;
    
    
    def _conf_allow_tasks(self, b:bool):
        self.config[FluffyConstants.ALLOW_TASKS] = b;
    
    def _conf_king_role(self, role:str):
        checked_role = self.dobby.get_role(role)
        if checked_role is not None:
            self.config[FluffyConstants.ROLE_KING] = checked_role
            logger.info('King Role established for role: %s.', checked_role)
        else:
            logger.error('The chosen King Role \'%s\' does not exists in the guild %s', role, self.config[FluffyConstants.GUILD])
            exit(1)
            
              
    def _load_roles_permissions(self, roles_perms:str, role_type:str):
        role_s = ','
        role_perm_s = ':'
        role = None
        perms = FluffyConstants.PERM_DENY
        roles_p = roles_perms.split(role_s)
        
        for role_p in roles_p:
            rp = role_p.split(role_perm_s)
            if len(rp) > 2: # Wrong usage
                logger.warning('Wrong usage of role-permission option on \'%s\' for \'%s\'', roles_perms, role_type)
                logger.warning('Ignoring configuration for: \'%s\'', rp)
                continue
            elif 1 <= len(rp) <= 2: # Role + permission || Role only
                role = self.dobby.get_role(rp[0])
                if role is None:
                    logger.warning('Ignoring unknown role \'%s\' for %s', rp[0], role_type)
                    continue
                
                if len(rp) == 2:  # Role + permissions
                    perms = self._parse_permissions(rp[1], role=rp[0])
                else: # Role only
                    perms = FluffyConstants.PERM_R
                
                if self.config[role_type].get(role) is None:
                    self.config[role_type][role] = perms
                else:
                    logger.error('Duplicate permissions for role \'%s\' in \'%s\'', role, role_type)
                    logger.info('Ignoring permissiosn for duplicate role: %s', role)
            else:  # Missing values
                logger.warning('Missing values on %s option.', role_type)
    
    
    def _parse_permissions(self, permissions:str, role='Unknown'):
        
        if permissions in ('rw', 'wr'):
            return FluffyConstants.PERM_WR
        
        elif permissions == 'r':
            return FluffyConstants.PERM_R
        
        elif permissions == 'w':
            return FluffyConstants.PERM_W
        
        else:
            logger.info('Ignoring unknown permissions \'%s\' for role: %s. No permissions will be applied.', permissions, role)
            return FluffyConstants.PERM_DENY
       
        
    def load_conf(self):
        
        self.config[FluffyConstants.GUILD] = self.dobby.get_guild()
       
        for key, val in self.user_input.items():
            
            if key == FluffyConstants.BASE_DIR:
                self._conf_basedir(val)
            
            elif key == FluffyConstants.CMD_PREFIX:
                self._conf_dobby_prefix()
            
            elif key == FluffyConstants.ALLOW_PLAYLIST:
                self._conf_allow_playlist(val)
            
            elif key == FluffyConstants.ALLOW_TASKS:
                self._conf_allow_tasks(val)
            
            elif key == FluffyConstants.ROLE_KING:
                self._conf_king_role(val)
                
            elif key == FluffyConstants.ROLES_PLAYLIST:
                self._load_roles_permissions(val, FluffyConstants.ROLES_PLAYLIST)
            
            elif key == FluffyConstants.ROLES_TASKS:
                self._load_roles_permissions(val, FluffyConstants.ROLES_TASKS)
                
        self.load_the_order()
    
    def load_the_order(self):
        del self.user_input
        logger.debug('Deleted tmp configuration variable.')
        
        basedir = self.config[FluffyConstants.BASE_DIR]
        self.config[FluffyConstants.BASE_DIR] = wisdom.add_trailing_slash(basedir)
        logger.info('Calling Gringotts...')
        
        gringotts_chambers = {
            FluffyConstants.ALLOW_PLAYLIST : self.config[FluffyConstants.ALLOW_PLAYLIST],
            FluffyConstants.ALLOW_TASKS : self.config[FluffyConstants.ALLOW_TASKS]
        }
        self._gringotts = Gringotts(self.config[FluffyConstants.BASE_DIR], gringotts_chambers)
        
        logger.info('Calling Hagrid...')
        self._hagrid = Hagrid(self.config)
        
        logger.info('Calling FluffyMusic...')
        self.fluffymusic = FluffyMusic(self._hagrid, self._gringotts, self.dobby.music)
        
        logger.info('Configuration loaded succesfully.') 
        logger.info('Running configuration:' + dobby_logging.join_multiple_configurations(self.dobby.get_configuration(), self.get_configuration()))
            
    
    # ************************  CONFIGURATION TEXT AND ERRORS  *****************************
    def get_configuration(self):
        config_str = '------- Fluffy\'s Configuration ---------'
        for key, val in self.config.items():
            config_str += '\n%s=%s' % (key, val)
        
        return config_str
    

class Hagrid:
    
    def __init__(self, configuration:dict):
        self._config = configuration
        
        
    def get_hogwarts_dir(self):
        return self._config.get(FluffyConstants.BASE_DIR)
    
    
    def get_gringotts_chambers(self) -> list:
        chambers = []
        if self._config[FluffyConstants.ALLOW_PLAYLIST]:
            chambers.append(FluffyConstants.ALLOW_PLAYLIST)
        
        if self._config[FluffyConstants.ALLOW_TASKS]:
            chambers.append(FluffyConstants.ALLOW_TASKS)
        
        return chambers
            
    
    def is_playlist_allowed(self) -> bool:
        return self._config.get(FluffyConstants.ALLOW_PLAYLIST)
    
    
    def is_tasks_allowed(self) -> bool:
        return self._config.get(FluffyConstants.ALLOW_TASKS)
    
    
    def get_guild(self) -> discord.Guild:
        return self._config[FluffyConstants.GUILD]
    
    
    def get_roles_for_member(self, member:discord.Member, role_type:str) -> typing.List[discord.Role]:
        roles = []
        if role_type is None:
            return member.roles
        
        for role in member.roles:
            for pl_role in self._config[role_type].keys():
                if role.id == pl_role.id:
                    roles.append(pl_role)
        
        return roles
        
        
    def get_highest_role_permissions(self, roles:list, role_type:str) -> typing.Tuple[discord.Role, int]:
        role = None
        perms = FluffyConstants.PERM_DENY
        for rp in roles:
            permissions = self._config[role_type].get(rp)
            if permissions > perms:
                role = rp
                perms = permissions
        
        return role, perms
        
    
###################################################################################################
# **************************   PLAYLIST SECURITY HANDLER   ****************************
class FluffyMusic():
    
    _WRITE_COMMANDS = ('create', 'delete', 'add' 'remove')
    _READ_COMMANDS = ('list', 'help', 'play')
    
    def __init__(self, hagrid:Hagrid, gringotts:Gringotts, music:'DobbyVoice'):
        self._hagrid = hagrid
        self._gringotts = gringotts
        self._music = music
        
    
    def is_playlist_allowed(self) -> bool:
        return self._hagrid.is_playlist_allowed()
    
    
    def member_is_in_voicechannel(self, member:discord.Member, channel:discord.VoiceChannel):
        if member.voice is not None and member.voice.channel == channel:
            return True
        else:
            return False
        
        
    def execute(self, ctx:'Context', member:discord.Member, command:str, *args:str) -> str:
        '''
        Checks if member is allowed to do a given action regarding playlist.
        action: The action the user has written (create, delete, remove, add, list).
        Returns a message for Cog to send.
        '''
        roles = self._hagrid.get_roles_for_member(member, FluffyConstants.ROLES_PLAYLIST)
        role, perm = self._hagrid.get_highest_role_permissions(roles, FluffyConstants.ROLES_PLAYLIST)
        
        if command in FluffyMusic._WRITE_COMMANDS:
            
            if perm in (FluffyConstants.PERM_W, FluffyConstants.PERM_WR):
                self.handle_write_command(member, command, args)
            else:
                return 'Permission denied'
            
        elif command in FluffyMusic._READ_COMMANDS:
            
            if perm in (FluffyConstants.PERM_R, FluffyConstants.PERM_WR):
                if command == 'play':
                    self.handle_play_command(member, args)
                else:
                    self.handle_read_command(ctx, member, command, args)
            else:
                return 'Permission denied'
            
        else:
            return 'Unknown command: %s'


    def handle_write_command(self, member:discord.Member, command:str, *args) -> str:
        
        if command == 'create':
            if len(args) > 0:
                playlist = args[0]
                self._ignore_extra_commands('playlist ' + command, 1, args)
                return self._gringotts.create_playlist(playlist, member)
            else:
                return 'Bad usage. Check help.'
            
        elif command == 'delete':
            if len(args) > 0:
                self._ignore_extra_commands('playlist ' + command, 1, args)
                return self._gringotts.delete_playlist(args[0])
            else:
                return 'Bad usage. Check help.'
            
        elif command == 'add':
            if len(args) > 1:
                self._ignore_extra_commands('playlist ' + command, 2, args)
                return self._gringotts.write_to_playlist(args[0])
            else:
                return 'Bad usage. Check help.'
            
        elif command == 'remove':
            if len(args) > 1:
                self._ignore_extra_commands('playlist ' + command, 2, args)
                return self._gringotts.remove_from_playlist(args[0])
            else:
                return 'Bad usage. Check help.'
    
    
    def handle_read_command(self, ctx:'Context', member:discord.Member, command:str, *args) -> object:
        
        if command == 'help':
            self._ignore_extra_commands('playlist ' + command, 1, args)
            self._print_playlist_help(ctx)
            return
        
        elif command == 'list':
            self._ignore_extra_commands('playlist ' + command, 1, args)
            
        
    def handle_play_command(self, member:discord.Member, *args) -> str:
        self._ignore_extra_commands('playlist play', 1, args)
        succes, mode, playlist = self._gringotts.open_playlist(args)
        if succes:
            return 'Playlist \'%s\' opened.'

        
    async def _list_songs_in_playlist(playlist:str):
        pass
    
    
    async def _lists_playlists():
        pass
    
    async def _print_playlist_help(self, ctx:'Context'):
        # TODO Bootstrapper / Installer of Dobby
        with open('./dobby.texts.d/playlist_help.txt') as f:
            await ctx.channel.send("".join(f.readlines()))
            
    def _ignore_extra_commands(self, action, offset, *args):
        if len(args) > 0:
            logger.info('Ignoring extra arguments -> %s on \'%s\' command', args[offset:], action)
        
        