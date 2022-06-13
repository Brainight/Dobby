from discord.ext import commands, tasks
import requests
import json
import typing
import dobby_logging
from wisdom import MusicSongTypes

if typing.TYPE_CHECKING:
    from fluffy import FluffyMusic
    from dobbyvoice import DobbyVoice
    
class RandomCog(commands.Cog, name='Random wishes'):
    
    def __init__(self, bot:commands.bot):
        self.bot = bot
        logger = dobby_logging.getDobbyLogger(__name__)

    # -------- QUOTES
    # Get inspirational quotes
    @commands.command(aliases=['i','insp'], description='Inspires you with shitty quotes')
    async def inspire(self, ctx:commands.Context):
        data = requests.get('https://zenquotes.io/api/random')
        json_data = json.loads(data.text[2:-2])
        text = '"' + json_data['q'] + '"'  + '\n     -------- ' + json_data['a'] + ' --------'
        await ctx.channel.send(text)


    # ------- RANDOM THINGS
    # Get bot latency (.ping / .latency)
    @commands.command(aliases=['latency'])
    async def ping(self, ctx:commands.Context):
        await  ctx.channel.send(f'Ping is: {round(self.bot.latency * 1000)}ms')


class MusicCog(commands.Cog):
    # TODO separate this class in two. Leave the Cog functionality on one site, and DobbyMusic/DobbyVoice on the other.
    # TODO implements not only _is_playing (True, False), but "Playing", "Paused", "Not Playing"
    def __init__(self, music:'DobbyVoice', fluffy_music:'FluffyMusic'):
        # Task loop 
        self.task_start = False;
        self.music = music
        self.fluffy_music = fluffy_music

    def _accept_command(self, ctx:commands.Context):
        return not self.music.is_voiceclient_connected() or self.fluffy_music.member_is_in_voicechannel(ctx.author, self.music.get_voicechannel())
    
    def _is_valid_command(self, command:str):
        if command in self.fluffy_music._WRITE_COMMANDS or command in self.fluffy_music._READ_COMMANDS:
            return True
        else:
            return False

    # ---------------------------    MUSIC COG COMMANDS   ---------------------------------
    @commands.command()
    async def play(self, ctx:commands.Context, *song):
        if self._accept_command(ctx):
            if await self.music.handle_play_request(ctx):
                if not self.dismiss_dobby.is_running():
                    self.dismiss_dobby.start()
                    self.task_start = True
                    song_data = DobbyVoice.find_song(song)
                await self.music.prepare_song(ctx, song_data)
        else:
            await ctx.channel.send('Dobby is already in a channel, and you are not there. I won\'t do what you want unless you\'re with us...') 

    @commands.command()
    async def skip(self, ctx:commands.Context):  # There is no need to call play_song() again. It will be called internally.
        if self._accept_command(ctx):
            if self.music.vc.is_playing:
                self.music.vc.stop()
                await ctx.channel.send('Skipping current song!')
                if len(self.music.queue) == 0:
                    await ctx.channel.send('No more songs to play...')
            else:
                await ctx.channel.send('Dobby can not skip a song if he\'s not playing any...')
        else:
            await ctx.channel.send('Can\'t order Dobby to skip a song if you are not with Dobby :)')

    @commands.command()
    async def pause(self, ctx:commands.Context):
        if self._accept_command(ctx):
            if self.music.vc.is_playing:
                self.music.vc.pause()  
                await ctx.channel.send('Pausing current song!')
            else:
                await ctx.channel.send('Dobby cannot pause a song if he\'s  not playing any')
        else:
            await ctx.channel.send('Can\'t order Dobby to pause a song if you are not with Dobby :)')

    @commands.command()
    async def resume(self, ctx:commands.Context):
        if self._accept_command(ctx):
            if self.music.vc.is_paused:
                self.music.vc.resume()
                await ctx.channel.send('Resuming current song!')
            elif self.music.is_playing:
                await ctx.channel.send('Dobby is playing a song already!')
            else:
                await ctx.channel.send('Dobby is not sure what you mean sir... Are you feeling ok?')
        else:
            await ctx.channel.send('Can\'t order Dobby to resume a song if you are not with Dobby :)')
    
    
    @commands.command(description='Command used to handle playlist stuff')
    async def playlist(self, ctx:commands.Context, *args):
        if self.fluffy_music.is_playlist_allowed():
            if len(args) == 0 or self._is_valid_command(args[0]):
                if len(args) == 0:
                    command = 'help'
                else:
                    command = args[0]
                    if len(args) > 1:
                        args = args[1:]
                    else:
                        args = []
                        
                await self.fluffy_music.execute(ctx, ctx.author, command, args)
                
            else:
                await ctx.channel.send('Dobby doesn\'t recognize this type of playlist magic...')
        else:
            await ctx.channel.send('Playlists are disabled!') 
    
    # Returns a list with all songs in queue into authors text channel.
    @commands.command()
    async def songs(self, ctx:commands.Context):
        if self._accept_command(ctx):
            songs = '.       ############   DOBBY\'s MUSIC LIST   ############\n'
            for i, song in enumerate(self.dobby.music.queue):
                songs = f'{songs}{i}. {song["title"]}\n'
            if songs != '':
                await ctx.channel.send(songs)
            else:
                await ctx.channel.send('Dobby has no songs in queue...')
        else:
            await ctx.channel.send('Can\'t order Dobby to list songs if you are not listening to them!') 
            
    @commands.command(description='Sets Dobby free from the voice channel.')
    async def givesock(self, ctx:commands.Context):
        if self._accept_command(ctx):
            try:
                if self.music.vc.is_connected():
                    if self.music.vc.is_playing():
                        self.music.vc.stop()
                    self.music.queue = None
                    self.dismiss_dobby.cancel()  # Ending dissmis_dobby loop
                    await ctx.channel.send('Dobby is free!!')
                    await self.music.vc.disconnect()
            except AttributeError:
                await ctx.channel.send('I\'m already free, \'Master\'....')
        else:
            await ctx.channel.send('Can\'t order Dobby to list songs if you are not listening to them!') 

    # Dobby will check every 15 minutes if he is still needed in the voice channel he is.
    # This method should only be called once every time Dobby get a new instance of a voice client.
    @tasks.loop(minutes=60)
    async def dismiss_dobby(self):
        if (not self.music.vc.is_playing or len(self.music.vc.channel.members) == 1) and not self.task_start:
             await self.music.channel.send('Dobby seems not to be useful anymore... Dobby is living voice channel now...')
             await self.music.vc.disconnect() # Disconnecting voiceclient
             self.dismiss_dobby.cancel(); # Ending dissmis_dobby loop
        self.task_start = False
    
    # ******************    T A S K S     *********************



class WisdomCog(commands.Cog):
    def __init__(self):
        pass

    @commands.command()
    async def listroles(self, ctx:commands.Context):
        roles = ctx.channel.guild.roles
        txt = '####### SERVER ROLES #######'
        for role in roles:
            txt += role.name + '\n'

        await ctx.channel.send(txt)


