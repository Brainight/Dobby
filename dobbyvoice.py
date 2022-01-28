
from discord.ext import commands
import dobby_logging
from youtube_dl import YoutubeDL
import discord

logger = dobby_logging.getDobbyLogger(__name__)

_YDL_options = {'format' : 'bestaudio', 'nonplaylist' : 'True' }

class DobbyVoice():

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
        
        # Discrd FFMPEG OPTIONS
        self.ffmpeg_options = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn' }
    
    
    # --------------------------------   HELPFUL METHODS   --------------------------
    def get_voicechannel(self) -> discord.VoiceChannel:
        if self.vc is None or self.vc.channel is None:
            return None
        else:
            return self.vc.channel
        
    def is_voiceclient_connected(self) -> bool:
        if self.vc is None:
            return False
        else:
            return True
        
        
    # Finds url for video given a youtube search string
    @staticmethod
    def find_song(song):
        with YoutubeDL(_YDL_options) as yt:
            try:
                # Searching for matches of string as a youtube search.
                data = yt.extract_info(f'ytsearch:{song}', download=False)
            except:
                return False
        return {'title' : data['entries'][0]['title'], 'src' : data['entries'][0]['formats'][0]['url']}


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
    async def prepare_song(self, ctx:commands.Context, song):
        """
        Gets source for song. If queue has no songs, it adds it to queue and calls play_song method. If queue has songs, it only adds it to queue.
        """
        song_query = " ".join(song)
        song_data = self.find_song(song_query)
        
        # If data for the supplied is retrieved succesfully (else -> song_data = False)
        if song_data:
            if self.queue is None:
                self.queue = []
            
            song_data['type'] = 'uniq'
            self.queue.append(song_data)

            if len(self.queue) > 1 or self.is_playing:
                await ctx.channel.send(f'Dobby added  "{song_data["title"]}" to queue!')
            else:
                await ctx.channel.send(f'Playing "{song_data["title"]}"')
                self.play_song(ctx)

        else:
            await ctx.channel.send('Dobby can not play the song for Master. Dobby is very sorry.')
            self.is_playing = False


    async def prepare_playlist(self, ctx:commands.Context, playlist):
        logger.info('Preparing playlist \'%s\'', playlist)
        
            
    # Plays a song 
    def play_song(self, ctx:commands.Context, retry=False):
        """
        Plays the next song in queue. If there's no song in queue, it sets self.is_playing property to "False"
        """
        if self.queue is None: 
            self.queue = []
        
        if len(self.queue) > 0: 
            self.is_playing = True 
            song = self.queue.pop(0)
            print("Playing song: ", song['title'])
            try:
                self.vc.play(discord.FFmpegPCMAudio(song['src'], **self.ffmpeg_options), after=lambda e: self.play_song(ctx)) 
            except Exception as e:
                if retry:
                    logger.error('Retry on \'%s\' was unsuccessfull, ignoring song.')
                    ctx.channel.send('Retry on song \'%s\', Dobby will skip the song!', song['title'])
                else:
                    logger.error('Cannot reproduce song: \'%s\' due to:\n%s', song['title'], e.msg)
                    logger.info('Retrying to play \'%s\'...', song['title'])
                    ctx.channel.send('An error ocurred trying to play \'%s\'... Dobby will retry', song['title'])
                    self.queue.insert(0, song)
                    self.play(ctx, retry=True)
        else:
            self.is_playing = False