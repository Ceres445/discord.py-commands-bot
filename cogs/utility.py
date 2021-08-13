from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.snipe_dict = {}  # configured to work per server ( you might be able to snipe other servers the bot is in )
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        message: Optional[discord.Message]  # just to force pycharm to ignore NoneType errors
        message, deleted_at = self.snipe_dict.get(channel.id, [(None, None)])[-1]
        if message is None:
            return await ctx.send("No messages to snipe")
        else:
            embed = discord.Embed(title='SNIPE', description=f"`{message.content or 'They sent nothing'}` \n "
                                                             f"deleted at {deleted_at}",
                                  timestamp=datetime.utcnow())
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed.set_footer(text=message.channel.name)
            await ctx.send(embed=embed, files=[await x.to_file() for x in message.attachments])

    @commands.command(aliases=['sl'])
    @commands.check(commands.has_permissions(administrator=True))
    async def snipe_list(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        messages = self.snipe_dict.get(channel.id, None)
        if messages is None:
            return await ctx.send("No messages to snipe")
        else:
            embed = discord.Embed(title='Snipe list',
                                  timestamp=datetime.utcnow())
            files = []
            for message, deleted_at in messages:
                embed.add_field(name=f'Message deleted by {message.author.name}',
                                value=f"`{message.content or 'They sent nothing'}`, deleted {deleted_at}")
                files.append([await x.to_file() for x in message.attachments])
            await ctx.send(embed=embed, files=files)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if self.snipe_dict.get(message.channel.id, None) is not None:
            self.snipe_dict[message.channel.id].append((message, datetime.now()))
        else:
            self.snipe_dict[message.channel.id] = [(message, datetime.now())]
        if len(self.snipe_dict[message.channel.id]) >= 10:  # avoid destroying your cache memory
            self.snipe_dict[message.channel.id] = self.snipe_dict[message.channel.id][-10:]


def setup(bot):
    bot.add_cog(Utility(bot))
