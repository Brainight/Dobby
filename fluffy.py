from abc import abstractmethod
import os
import discord
import typing

import dobby_logging
from gringotts import Gringotts
import wisdom
from wisdom import Configurations, Permissions

if typing.TYPE_CHECKING:
    from dobby import Dobby
    from dobbyvoice import DobbyVoice
    from discord.ext.commands import Context
    
logger = dobby_logging.getDobbyLogger(__name__)
    
    
class Fluffy():
    
        # THE DEFAULT CONFIGURATION
    CONFIG = {
        Configurations.CMD_PREFIX : '.',
        Configurations.BASE_DIR : os.path.expanduser('~'),
        Configurations.ALLOW_PLAYLIST : False,
        Configurations.ALLOW_TASKS : False,
        Configurations.ROLES_PLAYLIST : {},  
        Configurations.ROLES_TASKS : {},
        Configurations.ROLE_KING : None,
        Configurations.GUILD : None
    }
    '''
    This class provides methods for Dobby to avoid unwanted Masters or intruders to
    harm Dobby or the belongings Dobby keeps from their friends.

    Dobby by default is fairly restrictive.
    '''
    
    def __init__(self, configuration:dict, dobby:'Dobby'):
        self.user_input = configuration  # This variable is deleted after method "load_conf" is called.
        self.config = Fluffy.CONFIG
        self._hagrid = None
        self.fluffymusic = None
        self.dobby = dobby
        self._gringotts = None
        
    def get_guild(self):
        return self.config[Configurations.GUILD]
    
    # ***************** CONFIGURATION METHODS ***********************
    def _conf_dobby_prefix(self):
        if self.user_input[Configurations.CMD_PREFIX] in ['.', '!', '?', '¿', '¡', '/', '\\', ':', ';']:
            self.dobby.command_prefix = self.user_input[Fluffy.CMD_PREFIX]
            self.config[Configurations.CMD_PREFIX] = self.user_input[Configurations.CMD_PREFIX]
            logger.info('Setting Dobby\'s %s = %s', Configurations.CMD_PREFIX, self.config[Configurations.CMD_PREFIX])
        else:
            logger.warning('Invalid %s \'%s\' -> Using default: \'%s\'', Configurations.CMD_PREFIX,
                           self.user_input[Configurations.CMD_PREFIX], self.config[Fluffy.CMD_PREFIX])
                                                                                                    
                                                                                                            
    def _conf_basedir(self, basedir:str):
        self.config[Configurations.BASE_DIR] = wisdom.add_trailing_slash(basedir)
    
    def _conf_allow_playlist(self, b:bool):
        self.config[Configurations.ALLOW_PLAYLIST] = b;
    
    
    def _conf_allow_tasks(self, b:bool):
        self.config[Configurations.ALLOW_TASKS] = b;
    
    def _conf_king_role(self, role:str):
        checked_role = self.dobby.get_role(role)
        if checked_role is not None:
            self.config[Configurations.ROLE_KING] = checked_role
            logger.info('King Role established for role: %s.', checked_role)
        else:
            logger.error('The chosen King Role \'%s\' does not exists in the guild %s', role, self.config[Configurations.GUILD])
            exit(1)
            
              
    def _load_roles_permissions(self, roles_perms:str, role_type:str):
        role_s = ','
        role_perm_s = ':'
        role = None
        perms = Permissions.PERM_DENY.value
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
                    perms = Permissions.PERM_R
                
                if self.config[role_type].get(role) is None:
                    self.config[role_type][role] = perms
                else:
                    logger.error('Duplicate permissions for role \'%s\' in \'%s\'', role, role_type)
                    logger.info('Ignoring permissiosn for duplicate role: %s', role)
            else:  # Missing values
                logger.warning('Missing values on %s option.', role_type)
    
    
    def _parse_permissions(self, permissions:str, role='Unknown'):
        
        if permissions in ('rw', 'wr'):
            return Permissions.PERM_WR
        
        elif permissions == 'r':
            return Permissions.PERM_R
        
        elif permissions == 'w':
            return Permissions.PERM_W
        
        else:
            logger.info('Ignoring unknown permissions \'%s\' for role: %s. No permissions will be applied.', permissions, role)
            return Permissions.PERM_DENY
       
        
    def load_conf(self):
        
        self.config[Configurations.GUILD] = self.dobby.get_guild()
       
        for key, val in self.user_input.items():
            
            if key == Configurations.BASE_DIR:
                self._conf_basedir(val)
            
            elif key == Configurations.CMD_PREFIX:
                self._conf_dobby_prefix()
            
            elif key == Configurations.ALLOW_PLAYLIST:
                self._conf_allow_playlist(val)
            
            elif key == Configurations.ALLOW_TASKS:
                self._conf_allow_tasks(val)
            
            elif key == Configurations.ROLE_KING:
                self._conf_king_role(val)
                
            elif key == Configurations.ROLES_PLAYLIST:
                self._load_roles_permissions(val, Configurations.ROLES_PLAYLIST)
            
            elif key == Configurations.ROLES_TASKS:
                self._load_roles_permissions(val, Configurations.ROLES_TASKS)
                
        self.load_the_order()
    
    def load_the_order(self):
        del self.user_input
        logger.debug('Deleted tmp configuration variable.')
        
        logger.info('Calling Hagrid...')
        self._hagrid = Hagrid(self.config)
        
        basedir = self.config[Configurations.BASE_DIR]
        self.config[Configurations.BASE_DIR] = wisdom.add_trailing_slash(basedir)
        logger.info('Calling Gringotts...')
        
        self._gringotts = Gringotts(self._hagrid)
        

        
        logger.info('Calling FluffyMusic...')
        self.fluffymusic = FluffyMusic(self._hagrid, self._gringotts, self.dobby.music)
        
        logger.info('Configuration loaded succesfully.') 
        logger.info('Running configuration:' + dobby_logging.join_multiple_configurations(self.dobby.get_configuration(), self.get_configuration(), self._gringotts.get_config()))
            
    
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
        return self._config.get(Configurations.BASE_DIR)
    
    
    def get_gringotts_chambers(self) -> list:
        chambers = []
        if self._config[Configurations.ALLOW_PLAYLIST]:
            chambers.append(Configurations.ALLOW_PLAYLIST)
        
        if self._config[Configurations.ALLOW_TASKS]:
            chambers.append(Configurations.ALLOW_TASKS)
        
        return chambers
            
    
    def is_playlist_allowed(self) -> bool:
        return self._config.get(Configurations.ALLOW_PLAYLIST)
    
    
    def is_tasks_allowed(self) -> bool:
        return self._config.get(Configurations.ALLOW_TASKS)
    
    
    def get_guild(self) -> discord.Guild:
        return self._config[Configurations.GUILD]
    
    
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
        perms = Permissions.PERM_DENY
        for rp in roles:
            permissions = self._config[role_type].get(rp)
            if permissions > perms:
                role = rp
                perms = permissions
        
        return role, perms
        
    
###################################################################################################
# **************************   PLAYLIST SECURITY HANDLER   ****************************
class FluffyMusic():
    
    _WRITE_COMMANDS = ('create', 'delete', 'add', 'remove')
    _READ_COMMANDS = ('list', 'help', 'play')
    _MUSIC_HALL = '.music_hall'
    _MUSIC_HALL_CMD = "!musichall"
    
    def __init__(self, hagrid:Hagrid, gringotts:Gringotts, music:'DobbyVoice'):
        self._hagrid = hagrid
        self._gringotts = gringotts
        self._music = music
        self._music_hall = None 
        self._build_music_hall()   
        
    
    def is_playlist_allowed(self) -> bool:
        return self._hagrid.is_playlist_allowed()
    
    
    def member_is_in_voicechannel(self, member:discord.Member, channel:discord.VoiceChannel):
        if member.voice is not None and member.voice.channel == channel:
            return True
        else:
            return False
        
    ###########################  MUSIC HALL RELATED STUFF
    def _build_music_hall(self):
        if self._hagrid.is_playlist_allowed():
            logger.info('Building Music Hall...')
            mh = wisdom.add_trailing_slash(self._hagrid.get_hogwarts_dir()) + FluffyMusic._MUSIC_HALL
            if wisdom.file_exists(mh):
               logger.info('Music Hall found!')
            else:
                logger.info('No Music Hall found... Forging...')
                wisdom.create_directory(mh)
                
            self._music_hall = mh
            
            
    def get_music_hall_contents(self) -> list:
        songs = []
        for file in wisdom.list_directory(self._music_hall):
            if wisdom.is_music_file(wisdom.add_trailing_slash(self._music_hall) + file):
                songs.append(file)
                
        return songs  
    
    ##############################################
        
        
    async def execute(self, ctx:'Context', member:discord.Member, command:str, args:list):
        '''
        Checks if member is allowed to do a given action regarding playlist.
        action: The action the user has written (create, delete, remove, add, list).
        Returns a message for Cog to send.
        '''
        roles = self._hagrid.get_roles_for_member(member, Configurations.ROLES_PLAYLIST)
        role, perm = self._hagrid.get_highest_role_permissions(roles, Configurations.ROLES_PLAYLIST)
        logger.info('Playlist command: %s | Args: %s | Executer: %s', command, args, member.display_name)
        if command in FluffyMusic._WRITE_COMMANDS:
            
            if perm in (Permissions.PERM_W, Permissions.PERM_WR):
                await self.handle_write_command(ctx, member, command, args)
            else:
                await ctx.channel.send('Permission denied')
            
        elif command in FluffyMusic._READ_COMMANDS:
            
            if perm in (Permissions.PERM_R, Permissions.PERM_WR):
                if command == 'play':
                    if len(args) > 0:
                        await self.handle_play_command(ctx, member, args)
                    else:
                        await ctx.channel('Dobby does not know what you want him to play...')
                else:
                    await self.handle_read_command(ctx, member, command, args)
            else:
                await ctx.channel.send('Permission denied')
            
        else:
            await ctx.channel.send('Unknown command: %s' % command)


    async def handle_write_command(self, ctx:'Context', member:discord.Member, command:str, args:list):
        
        if command == 'create':
            if len(args) > 0:
                playlist = args[0]
                self._ignore_extra_commands('playlist ' + command, 1, args)
                success, msg = self._gringotts.create_playlist(playlist, member)
                if success:
                    await ctx.channel.send('Playlist \'%s\' created successfully!' % playlist)
                else:
                    await ctx.channel.send(msg)
            else:
                await ctx.channel.send('Bad usage. Check help.')
            
        elif command == 'delete':
            if len(args) > 0:
                self._ignore_extra_commands('playlist ' + command, 1, args)
                playlist = args[0]
                success, error = self._gringotts.delete_playlist(playlist, member)
                if success:
                    await ctx.channel.send('Playlist %s deleted!' % playlist)
                else:
                    await ctx.channel.send(error)
            else:
                await ctx.channel.send('Bad usage. Check help.')
            
        elif command == 'add':
            if len(args) > 1:
                playlist = args[0]
                songs = args[1].split(':')
                success, error = self._gringotts.write_song_to_playlist(playlist, songs, member)
                if success:
                    await ctx.channel.send('Songs added successfully')
                else:
                    await ctx.channel.send(error)
            else:
                await ctx.channel.send('Bad usage. Check help.')
            
        elif command == 'remove':
            if len(args) > 1:
                return self._gringotts.remove_from_playlist(args)
            else:
                await ctx.channel.send('Bad usage. Check help.')
        else:
            logger.info('Unknown command: \'playlist %s\'', command)
    
    
    async def handle_play_command(self, ctx:'Context', member:discord.Member, args):
        self._ignore_extra_commands('playlist play', 1, args)
        play_arg = args[0]
        print(args)
        print(play_arg)
        if play_arg == FluffyMusic._MUSIC_HALL_CMD:
            await ctx.channel.send("Dobby doesn't know how to do this yet...")
            
        elif play_arg.startswith(FluffyMusic._MUSIC_HALL_CMD + ":"):
            song = play_arg.split(":")[1]
            song_data = wisdom.build_simple_song_data_entry(song, wisdom.add_trailing_slash(self._music_hall) + song, wisdom.MusicSongTypes.LOCAL)
            await self._music.handle_play_request(ctx)
            await self._music.prepare_song(ctx, song_data)
        else:
            await ctx.channel.send("Dobby doesn't know how to do this yet...")
            #succes, mode, playlist = self._gringotts.open_playlist(args)
            pass
        
        
    async def handle_read_command(self, ctx:'Context', member:discord.Member, command:str, args) -> object:
        
        if command == 'help':
            self._ignore_extra_commands('playlist ' + command, 1, args)
            await self._print_playlist_help(ctx)
            
        
        elif command == 'list':
            if len(args) < 1:
                succ, data = self._gringotts.list_playlists()
                if succ:
                    await ctx.channel.send(data)
                else:
                    await ctx.channel.send('Error listing playlists')
            else:
                self._ignore_extra_commands('playlist ' + command, 1, args[2:])
                playlist = args[0]
                
                if playlist == FluffyMusic._MUSIC_HALL_CMD:
                    music_hall = self.get_music_hall_contents()
                    text = '     #######  MUSIC HALL SONGS  #######\n'
                    for i, song in enumerate(music_hall):
                        text += "%s. %s\n" % (i + 1, song)
                        
                    await ctx.channel.send(text)
                    
                else:
                    succ, msg = self._gringotts.list_playlist_songs(playlist, member)
                    if succ:
                        await ctx.channel.send(msg)
                    else:
                        await ctx.channel.send(msg)
    
    
    async def _print_playlist_help(self, ctx:'Context'):
        # TODO Bootstrapper / Installer of Dobby
        with open('./dobby.texts.d/playlist_help.txt') as f:
            await ctx.channel.send("".join(f.readlines()))
            
    def _ignore_extra_commands(self, action, offset, args):
        if len(args) > 0:
            logger.info('Ignoring extra arguments -> %s on \'%s\' command', args[offset:], action)
        
        