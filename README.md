# DOBBY
Dobby is a discord bot written in python using [discord.py](https://github.com/Rapptz/discord.py).

### DOBBY IS A FREE ELF!
Dobby has no Master but he will do what you ask him. At least 95% of the time.
To do so, you only have to summon him.
Dobby may be summoned by mentioning him or by adding a '.' before the desired command.

## REQUIEREMENTS
In order for Dobby to work, you'll need to have the modules written in Pipfile installed.

Music Features will only work if you have the ffmpeg package installed in the server where Dobby is being executed.
In Ubuntu 20.04:
> sudo apt install ffmpeg

## FEATURES AND COMMANDS
### MusicBot
Dobby can play music for you if you ask him gently.

**Commands:**
- play <song> -> Dobby will search and play (or add to queue) the first match on youtube for the given input.
- stop -> Dobby will stop playing the current song.
- resume -> Dobby will resume playing a previously stopped song.
- skip -> Dobby will skip the current song
- giveSock -> Dobby will stop playing music and leave the voice channel.

### Random Stuff
Dobby can be ordered to do some random stuff too.
If you feel sad, you can always tell him to inspire you...

**Commands:**
- inspire -> Dobby will try to inspire you with a shitty [zenquote](https://zenquotes.io)
- ping -> Check if Dobby has good internet connection