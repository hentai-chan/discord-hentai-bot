import json
from pathlib import Path

import discord
from discord.ext import commands

client = commands.Bot(command_prefix='/', description="Discord bot that lets you look up magic numbers in chat.")
client.remove_command('help')

@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loading {extension} extension")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unload {extension} extension")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Reloading {extension} extension")

def load_cogs_from_system(client, target_dir): 
    [client.load_extension(f"cogs.{file.stem}") for file in Path(target_dir).glob('*.py')]

def get_token() -> str:
    with open('secrets.json', mode='r') as file_handler:
        return json.load(file_handler).get('token')


if __name__ == '__main__':
    load_cogs_from_system(client, target_dir="./cogs")
    client.run(get_token())    
