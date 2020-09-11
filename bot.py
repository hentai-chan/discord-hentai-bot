import json
from datetime import datetime as dt
from urllib.parse import urljoin

import colorama
import discord
from colorama import Fore, Style
from discord.ext import commands

from hentai import Hentai, Format

colorama.init()
client = commands.Bot(command_prefix = '/', description = "ディスコードでマジック・ナンバーズの検索を行うことが出来るボットです。")
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity = discord.Game("次の索要求受を期待しているね！"))
    print(f"{Style.BRIGHT}{Fore.YELLOW}[{dt.now().strftime('%d.%m.%Y %H:%M:%S')}]{Style.RESET_ALL} ボットが起動するに成功しています。")

@client.command(aliases = ['emn'])
async def explore_magic_number(ctx, magic_number: int):
    hentai = Hentai(magic_number)
    embed = discord.Embed(title = hentai.title(Format.Pretty), color = discord.Color.red())
    embed.add_field(name = "同人誌を読み始める", value = urljoin(hentai.url, '1'))
    embed.add_field(name = "お気に入り", value = f"❤ {hentai.num_favorites}")
    embed.set_thumbnail(url = hentai.thumbnail)
    await client.change_presence(status = discord.Status.idle, activity = discord.Game(f"今{hentai.title(Format.Pretty)}を読んでいるよ"))
    await ctx.send(embed = embed)   

@explore_magic_number.error
async def on_explore_magic_number_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("警告：マジック・ナンバーズを指定する必要があります")

@client.command(aliases = ['rmn'])
async def random_magic_number(ctx):
    await explore_magic_number(ctx, magic_number = Hentai.random_id())

@client.command(pass_context = True)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(color = discord.Color.gold())
    embed.set_author(name = "使い方")
    embed.add_field(name= "/explore_magic_number || /emn [id: magic number]", value = "ＩＤに関連した変態情報を表示する。", inline = False)
    embed.add_field(name= "/random_magic_number || /rmn", value = "ランダムＩＤ自動作成し変態を検索する（パラメータの必要がない）。", inline = False)
    await author.send(embed = embed)

def get_token():
    with open('secrets.json', mode = 'r') as file_handler:
        return json.load(file_handler).get('token')

if __name__ == '__main__':
    client.run(get_token())    
