
import discord
from discord.ext import commands, tasks
import requests
import json
from youtube_dl import YoutubeDL
from dobby_utils import Cerberus

class RandomCog(commands.Cog, name='Random wishes'):
    
    def __init__(self, bot:commands.bot):
        self.bot = bot

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
    # TODO implements not only _is_playing (True, False), but "Playing", "Paused", "Not Playing"
    def __init__(self):

        # Music Bot Stuff
        self.queue = []  # This playlist contains the songs for Dobby to play
        self.play_list_queue = None  # Contains the name of the playlist to play
        self.is_playing = False

        # This is only used to write to the last channel that told Dobby to play a song. It is used for Dobby to say good bye after no more songs are in queue.
        self.channel = None
        # Voiceclient (not voice channel)
        self.vc = None
        
        # Task loop 
        self.task_start = False;
        
        # YoutubeDL stuff
        self.YDL_options = {'format' : 'bestaudio', 'nonplaylist' : 'True' }
        # Discrd FFMPEG OPTIONS
        self.ffmpeg_options = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn' }


    # --------------------------------   HELPFUL METHODS   --------------------------
    # Finds url for video given a youtube search string
    def find_song(self, song):
        with YoutubeDL(self.YDL_options) as yt:
            try:
                # Searching for matches of string as a youtube search.
                data = yt.extract_info(f'ytsearch:{song}', download=False)
            except:
                return False
        return {'src' : data['entries'][0]['formats'][0]['url'], 'title' : data['entries'][0]['title']}


    # Prepares Dobby for playing music after commands 'play' is executed
    async def handle_play_request(self, ctx:commands.Context):
        """
        Handles a play request to Dobby. Return True if request should be processes, False if request should be dismissed.
        """
        if ctx.author.voice is not None: # Command Author is in a VoiceChannel
            
            voice_channel = ctx.author.voice.channel
            
            if self.vc is None or not self.vc.is_connected(): # If no VoiceClient is set for bot.
            # Connect dobby to channel and save VoiceClient in self.vc
                self.vc = await voice_channel.connect()
                await ctx.channel.send('Dobby joined \'{0}\' channel...'.format(voice_channel.name))
                self.task_start = True;
                self.dismiss_dobby.start()
                return True

            # If different channel asks Dobby to play, but he is playing on another channel with people listening. Dobby stays in current channel.
            elif self.vc.channel != voice_channel and len(self.vc.channel.members) > 1:
                await ctx.channel.send('Dobby can not join another channel while he is playing for his master')
                return False

            # If differet channel asks Dobby to play and nobody is in current channel. Dobby moves to other channel.
            elif self.vc.channel != voice_channel and len(self.vc.channel.members) == 1: 
                await ctx.channel.send('Oh Master! Is that you? Dobby didnt see you leave... Dobby is coming!')
                await self.vc.move_to(voice_channel)
                return True
            else: # Msg was sent from someone in the current bot VoiceClient channel.
                return True

        elif self.vc is not None:
            await ctx.channel.send('Dobby is busy with Master. Oh and... You need to be in a voice channel to summon me to play music')
        
        else:
            await ctx.channel.send('Dobby needs you to join a voice channel before delighting you with music')
            
        return False

    # Add song to queue 
    async def _prepare_song(self, ctx:commands.Context, song):
        """
        Gets source for song. If queue has no songs, it adds it to queue and calls play_song method. If queue has songs, it only adds it to queue.
        """
        song_query = " ".join(song)
        song_data = self.find_song(song_query)
        
        # If data for the supplied is retrieved succesfully (else -> song_data = False)
        if song_data:
            if self.queue is None:
                self.queue = []
                
            self.queue.append(song_data)

            if len(self.queue) > 1 or self.is_playing:
                await ctx.channel.send(f'Dobby added  "{song_data["title"]}" to queue!')
            else:
                await ctx.channel.send(f'Playing "{song_data["title"]}"')
                self.play_song()

        else:
            await ctx.channel.send('Dobby can not play the song for Master. Dobby is very sorry.')
            self.is_playing = False

            
    # Plays a song 
    def play_song(self):
        """
        Plays the next song in queue. If there's no song in queue, it sets self.is_playing property to "False"
        """
        if self.queue is None: self.queue = []
        
        if len(self.queue) > 0: 
            self.is_playing = True 
            song = self.queue.pop(0)
            print("Playing song: ", song['src'])
            self.vc.play(discord.FFmpegPCMAudio(song['src'], **self.ffmpeg_options), after=lambda e: self.play_song()) 
        else:
            self.is_playing = False
    
    
    # ---------------------------    MUSIC COG COMMANDS   ---------------------------------
    @commands.command()
    async def play(self, ctx:commands.Context, *song):
        if await self.handle_play_request(ctx):
            self.channel = ctx.channel
            await self._prepare_song(ctx, song)


    @commands.command()
    async def skip(self, ctx:commands.Context):  # There is no need to call play_song() again. It will be called internally.
        if self.vc.is_playing:
            self.vc.stop()
            await ctx.channel.send('Skipping current song!')
        else:
            await ctx.channel.send('Dobby can not skip a song if he\'s not playing any...')

    @commands.command()
    async def pause(self, ctx:commands.Context):
        if self.vc.is_playing:
            self.vc.pause()  
            await ctx.channel.send('Pausing current song!')
        else:
            await ctx.channel.send('Dobby cannot pause a song if he\'s  not playing any')

    @commands.command()
    async def resume(self, ctx:commands.Context):
        if self.vc.is_paused:
            self.vc.resume()
            await ctx.channel.send('Resuming current song!')
        elif self.is_playing:
            await ctx.channel.send('Dobby is playing a song already!')
        else:
            await ctx.channel.send('Dobby is not sure what you mean sir... Are you feeling ok?')
        
    # Returns a list with all songs in queue into authors text channel.
    @commands.command()
    async def songs(self, ctx:commands.Context):
        songs = '.       ############   DOBBY\'s MUSIC LIST   ############\n'
        for i, song in enumerate(self.queue):
            songs = f'{songs}{i}. {song["title"]}\n'
        if songs != '':
            await ctx.channel.send(songs)
        else:
            await ctx.channel.send('Dobby has no songs in queue...')
            
    @commands.command(description='Sets Dobby free from the voice channel.')
    async def givesock(self, ctx:commands.Context):
        try:
            if self.vc.is_connected():
                if self.vc.is_playing():
                    self.vc.stop()
                self.queue = None
                self.dismiss_dobby.cancel()  # Ending dissmis_dobby loop
                await ctx.channel.send('Dobby is free!!')
                await self.vc.disconnect()
        except AttributeError:
            await ctx.channel.send('I\'m already free, \'Master\'....')
        


    # -------- TASKS  
    # Dobby will check every 15 minutes if he is still needed in the voice channel he is.
    # This method should only be called once every time Dobby get a new instance of a voice client.
    @tasks.loop(minutes=15)
    async def dismiss_dobby(self):
        if (not self.vc.is_playing or len(self.vc.channel.members) == 1) and not self.task_start:
            await self.channel.send('Dobby seems not to be useful anymore... Dobby is living voice channel now...')
            await self.vc.disconnect() # Disconnecting voiceclient
            self.dismiss_dobby.cancel(); # Ending dissmis_dobby loop
        self.task_start = False;
        
        
        
class BelongingsCog(commands.Cog):
    
     # *****************   P L A Y L I S T   *****************
    @commands.command(description='Command used to handle playlist stuff')
    async def playlist(self, ctx:commands.Context, *args):
        if not Cerberus.allow_playlists:  # Check if playlist are allowed on the server
            await ctx.channel.send('Dobby will not give you the pleasure of using playlist! Playlists are disabled.')
            return
        


        if len(args) < 2 :  # Wrong or 1 arg Dobby Belonging Command handling
            if len(args) == 1:
                if args[0] in ['h', 'help']:  # Print help section
                    await self._print_playlist_help(ctx)
                elif args[0] in ['l', 'list']:  # List all playlists
                    pass
            else:
                await ctx.channel.send('Dobby does not know what Master means by "%s"...' % 'playlist ' + " ".join(args))
                await ctx.channel.send('Check "playlist help" for more information')

        else:  # 2 or more arguments Dobby Beloging Commands handling
            if args[0] in ['c', 'create']:  # Create playlist
                pass
            elif args[0] in ['d', 'delete']:  # Delete playlist
                pass
            elif args[0] in ['a', 'add']:  # Add song  to playlist
                pass
            elif args[0] in ['r', 'remove']:  # Remove song from playlist
                pass
            elif args[0] in ['l', 'list']:  # List songs in playlist (different from above)
                pass

    async def _print_playlist_help(self, ctx:commands.Context):
        with open('./helptexts/playlist_help.txt') as f:
            await ctx.channel.send("".join(f.readlines()))
        

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



def set_up_cogs(bot:commands.bot.Bot):
    bot.add_cog(RandomCog(bot))
    bot.add_cog(MusicCog())
    bot.add_cog(BelongingsCog())
    bot.add_cog(WisdomCog())


