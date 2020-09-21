import json
from datetime import datetime as dt
from datetime import timedelta
from time import time

import colorama
from colorama import Fore, Style

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from hentai import Format, Hentai
from psutil import Process

colorama.init()
client = commands.Bot(command_prefix='/', description="Discord bot that lets you look up magic numbers in chat.")
client.remove_command('help')
process = Process()

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Now taking requests!💖"))    
    print(f"{Style.BRIGHT}{Fore.YELLOW}[{dt.now().strftime('%d.%m.%Y %H:%M:%S')}]{Style.RESET_ALL} Booting up discord-hentai-bot . . .")

@client.command(aliases=['emn'])
async def explore_magic_number(ctx, magic_number: int):
    if not Hentai.exists(magic_number):
        ctx.send("Error: Invalid magic number.")
    else:
        doujin = Hentai(magic_number)
        embed = discord.Embed(title=doujin.title(Format.Pretty), color=discord.Color.red())
        embed.add_field(name="Start Reading", value=doujin.url)
        embed.add_field(name="Favorites", value=f"❤ {doujin.num_favorites}")
        embed.set_thumbnail(url=doujin.thumbnail)
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(f"Now reading {doujin.title(Format.Pretty)}💖"))
        await ctx.send(embed=embed)   

@explore_magic_number.error
async def on_explore_magic_number_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Error: Missing argument.")

@client.command(aliases=['rmn'])
async def random_magic_number(ctx):
    await explore_magic_number(ctx, magic_number=Hentai.get_random_id())

@client.command(aliases=['ut'], pass_context=True)
@has_permissions(manage_roles=True)
async def uptime(ctx):
    with process.oneshot():
        uptime = timedelta(seconds=time()-process.create_time())
    await ctx.send(f"Uptime: {uptime.days}d:{uptime.days // 3600}h:{(uptime.seconds // 60) % 60}m:{uptime.seconds}s.")


@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="Usage", color=discord.Color.gold())
    embed.add_field(name="/explore_magic_number || /emn [id: magic number]", value="Lookup a user-specified ID.", inline=False)
    embed.add_field(name="/random_magic_number || /rmn", value="Roll a random ID.", inline=False)
    embed.add_field(name="/uptime || /ut", value="Shows bot uptime.")
    await ctx.send(embed=embed)

def get_token() -> str:
    with open('secrets.json', mode='r') as file_handler:
        return json.load(file_handler).get('token')

if __name__ == '__main__':
    client.run(get_token())    
