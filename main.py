#all modules and libraries are imported here
import discord
from discord.ext import commands
import aiosqlite
import os
from os import getcwd
import json
from colorama import *
import yaml

#this is the bot instance
bot = commands.Bot(intents=discord.Intents.all())



#this is the event that runs when the bot is ready
@bot.event
async def on_ready():
     
    db = await aiosqlite.connect('data/vc_settings.db')
    async with db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS vc_settings (guild_id int, bitrate int, region text, user_limit int, log_channel int, perms text, admin_roles text)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS vc_generator (guild_id int, channel_id int, temp_name text, temp_limit int, temp_bitrate int, temp_region text, generator_name text, generator_cat int)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS temp_channels (guild_id int, channel_id int, owner int, temp_name text, temp_limit int, temp_bitrate int, temp_region text, banned_r text, banned_u text)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS vc_templates (guild_id int, template_name text, channel_id int, temp_name text, temp_limit int, temp_bitrate int, temp_region text)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS yt_settings (guild_id int, channel_id int, notif_text text, notif_role int)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS cats(guild_id int, cat_name text, cat_id int, txt_ch_id int, vc_ch_id int)")
        await db.commit()
    
print(f" {Fore.MAGENTA} Starting bot coded by 1019.lx.n.n.y©{Fore.RESET}")
for filename in os.listdir('systems'):
    if filename.endswith('.py'):
        bot.load_extension(f'systems.{filename[:-3]}')
        print(f"{Fore.GREEN} ✓ {Fore.RESET} Loaded {filename}")


#bot start process
with open(f'data/config.yaml', 'r') as f:
    data = yaml.safe_load(f)
    TOKEN = data['host']['bot_token']

    try:
        bot.run(TOKEN)
    except:
        print(f"{Fore.RED}Invalid Token!{Fore.RESET}")
        exit()
    

