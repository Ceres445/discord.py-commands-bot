import io
import textwrap
import traceback
from contextlib import redirect_stdout

from discord.ext import commands


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')


class Owner(commands.Cog):
    """Owner only commands for testing"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, args):
        """Evaluates code"""
        """Sourced from: https://github.com/Rapptz/RoboDanny"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        stdout = io.StringIO()
        args = cleanup_code(args)
        to_compile = f'async def func():\n{textwrap.indent(args, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have perms to use that!')


def setup(bot):
    bot.add_cog(Owner(bot))
