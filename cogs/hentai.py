from datetime import datetime as dt
from datetime import timedelta
from time import time

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from psutil import Process

from hentai import Format, Hentai, Tag, Utils
from emoji import EMOJI_ALIAS_UNICODE as Emoji


class HentaiBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.process = Process()
        self.reader_id = None

    #region events

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Game("Now taking requests!💕"))    
        print(f"[{dt.now().strftime('%d.%m.%Y %H:%M:%S')}] Initializing HentaiBot")

    #endregion

    #region commands

    @commands.command(aliases=['lid'])
    async def lookup_id(self, ctx, id: int):
        if not Hentai.exists(id):
            await ctx.send("Error: Invalid ID.")
        else:
            doujin = Hentai(id)
            embed = discord.Embed(title=doujin.title(Format.Pretty), description=f"🌍 {', '.join(Tag.get_names(doujin.language))}", url=doujin.url, color=discord.Color.red())
            embed.add_field(name="Author", value=Tag.get_names(doujin.artist))
            embed.add_field(name="Favorites", value=f"❤ {doujin.num_favorites}")
            embed.add_field(name="Pages", value=f"📕 {doujin.num_pages}")
            embed.set_thumbnail(url=doujin.thumbnail)
            embed.set_footer(text=f"Tags: {', '.join(Tag.get_names(doujin.tag))}")
            await self.client.change_presence(status=discord.Status.online, activity=discord.Game(f"Now reading {doujin.title(Format.Pretty)}🥰"))
            await ctx.send(embed=embed)   
    
    @commands.command(aliases=['read'])
    async def read_id(self, ctx, id: int):
        if not Hentai.exists(id):
            await ctx.send("Error: Invalid ID.")
        else:
            doujin = Hentai(id)
            reactions = {
                'prev' : Emoji[':arrow_left:'],
                'next' : Emoji[':arrow_right:']
            }

            embed = discord.Embed(title=doujin.title(Format.Pretty), description=f"Page 1 of {doujin.num_pages}", color=discord.Color.red())
            embed.set_image(url=doujin.cover)

            # TODO: implement emoji reaction event handler for pagination
            message = await ctx.send(embed=embed)
            self.reader_id = message.id
            print(type(message))
            print(self.reader_id)

            for emoji in reactions.values():
                await message.add_reaction(emoji)

    @lookup_id.error
    async def on_argument_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: Missing argument.")

    @commands.command(aliases=['rid'])
    async def random_id(self, ctx):
        await self.lookup_id(ctx, id=Utils.get_random_id(make_request=True))

    @commands.command(aliases=['ut'], pass_context=True)
    @has_permissions(manage_roles=True)
    async def uptime(self, ctx):
        with self.process.oneshot():
            uptime = timedelta(seconds=time() - self.process.create_time())
        await ctx.send(f"Uptime: {uptime.days}d:{uptime.days // 3600}h:{(uptime.seconds // 60) % 60}m:{uptime.seconds}s.")

    @commands.command(pass_context=True)
    async def help(self, ctx):
        embed = discord.Embed(title="Usage", color=discord.Color.gold())
        embed.add_field(name="`/lookup_id id:int || /lid id:int`", value="Lookup an user-specified ID.", inline=False)
        embed.add_field(name="`/read_id id:int || /read id:int`", value="Read an user-specified ID in chat.", inline=False)
        embed.add_field(name="`/random_id || /rid`", value="Roll a random ID.", inline=False)
        embed.add_field(name="`/uptime || /ut`", value="Shows bot uptime.")
        await ctx.send(embed=embed)

    #endregion


def setup(client):
    client.add_cog(HentaiBot(client))
