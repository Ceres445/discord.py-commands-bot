import asyncio
import datetime
import sys
import traceback

import discord
from aiohttp import ClientSession
from discord.ext import commands
from discord.ext.commands import CommandNotFound

import config

cogs = []  # Add cogs here Ex. cogs.test


class Bot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        """Initialize the bot"""
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        super().__init__(command_prefix=kwargs.pop('command_prefix', ['+']), case_insensitive=True,
                         allowed_mentions=allowed_mentions)
        self.session = ClientSession()
        self.start_time = datetime.datetime.utcnow()
        self.clean_text = commands.clean_content(escape_markdown=True, fix_channel_mentions=True)
        for extension in cogs:
            self.load_extension(extension)
            print("loaded extension", extension)

    async def on_message(self, message):
        """Handle commands"""
        await self.wait_until_ready()
        if message.guild is None or message.author.bot:
            return
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def on_ready(self):
        """Change presence after connecting to discord"""
        print(f'Successfully logged in as {self.user}\nSharded to {len(self.guilds)} guilds')
        await self.change_presence(status=discord.Status.online, activity=discord.Game(name='use the prefix "+"'))

    async def on_command_error(self, ctx, error):
        """Basic Error Handling"""
        if isinstance(error, CommandNotFound):
            await ctx.send('that is not a command')
            return
        embed = discord.Embed(title=f"{type(error).__name__}", colour=discord.Colour.red(),
                              description=str(error))
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=embed)
        else:
            await ctx.send("Some other error occured")
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @classmethod
    async def setup(cls, toke):
        bot = cls()
        try:
            await bot.start(toke)

        except KeyboardInterrupt:
            await bot.close()


def main():
    postgres, token = config.load_vars()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Bot.setup(token))


if __name__ == "__main__":
    main()
