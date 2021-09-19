
import discord
import os
from discord.ext import commands
import dobby_utils
import dobby_cogs

class Dobby(commands.Bot):

    def __init__(self, cmd_prefix):
        super().__init__(command_prefix=commands.when_mentioned_or(cmd_prefix))
        dobby_cogs.set_up_cogs(self)

        # -------------------  CONFIGURATION  ----------------------
        # Setting a description
        self.description = """My name is Dobby! Dobby has no master. Dobby is a free elf!\n   
        You may order Dobby to do things for you by writing a '.' before saying what you want me to do.
    
        Try this: .inspire
        
        You may aswell talk to Dobby if you fancy some company...
        """
        
        # Changing default "no category" cog in help description
        self.help_command = commands.DefaultHelpCommand(
                no_category = 'Commands'
        )

    # ------------------  EVENTS  -----------------------
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(bot))

    # Processing messages
    async def on_message(self, msg:discord.Message):
        if msg.author == self.user:
            return
        elif msg.content.startswith('.') or self.user in msg.mentions:
                await self.process_commands(msg)
        else:
            dobby_utils.process_msg(msg.content)
    
    
    # Action on deleting message. Only works for msgs written while bot was online.
    async def on_message_delete(self, msg:discord.Message):
        if msg.author == self.user:
            pass
        else:
            txt = '{0.author} has deleted a message...\n Message said:  \n"{0.content}"'.format(msg)
            await msg.channel.send(txt)


# Execute Dobby
if __name__ == "__main__":
    bot = Dobby('.')
    bot.run(os.getenv('discord_token'))