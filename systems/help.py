import discord
import aiosqlite
from discord.ext import commands
from discord.commands import slash_command
import yaml
import datetime
import asyncio
import platform
import psutil
import time
from discord.ext.pages import Paginator, Page


class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.monotonic()

    @slash_command(name="help", description="Get help with the bot")
    async def help(self, ctx: discord.ApplicationContext):

        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

        system = platform.system()
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent()
        mem_total = psutil.virtual_memory().total
        mem_usage = psutil.virtual_memory().used
        process = psutil.Process()

        count = len(self.bot.all_commands)

        now = time.monotonic()
        uptime1 = datetime.timedelta(seconds=now - self.start_time)

        timestamp = datetime.datetime.now() - uptime1
        uptime = timestamp.strftime("%d-%m-%Y %H:%M:%S")

        member = 0
        for guild in self.bot.guilds:
            member += guild.member_count

        em = discord.Embed(
            title=f"informations about __{self.bot.user}__",
            description="> Multi-purpose bot is a discord bot to enhance your experience with features like channel templates, temporary channels, and an owner menu for easy management.",
            color=color
        )

        em.add_field(
            name="❓ How to use the commands?",
            value="> `/{command}` to use a command",
            inline=False
        )

        em.add_field(
            name="📈 Stats",
            value=f"> <:Bearbeitung:1230568631809609868> {count} Commands\n> 📁 {len(self.bot.guilds)} Guild's \n> <:4696members:1230836719696216156> {member} Members\n> <:6292goodconnection:1236700354981138473> Connection: `{round(self.bot.latency * 1000)}`Ping\n> <:server:1230569109255749714> Uptime: ``{uptime}``\n> 🐍 Version: {platform.python_version()}\n> <:PC:1236700658057609319> System: Hostet on {system}\n> <:cpu:1236700797484531742> CPU: {cpu_count} Cores, with {cpu_usage}% Usage\n> <:Ram:1236700956234747996> Memory: {round(mem_usage/ (1024 ** 3), 2)} GB from {round(mem_total / (1024 ** 3), 2)} GB used",
            inline=False
        )

        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
       

        em1 = E(
            title="<:join:1236701574592725042> |  Join to create commands",
            description="> `generator_create`︲ `generator_delete`︲ `generator_edit_channel_name`︲ `generator_edit_limit`︲ `generator_edit_region`︲ `generator_edit_name`",
            color=color
        )
        em1.set_footer(text=footer, icon_url=footer_icn)
        em1.set_thumbnail(url=thumbnail)

        em2 = E(
            title="<:voice:1236701790257684482> |  Voice commands",
            description="> `vc_hide`︲ `vc_limit`︲ `vc_lock`︲ `vc_unlock`> `vc_claim_owner` ︲ `ban_temp_vc_role` ︲ `ban_temp_vc_user` ︲ `unban_temp_vc_role` ︲ `unban_temp_vc_user`",
            color=color
        )
        em2.set_footer(text=footer, icon_url=footer_icn)
        em2.set_thumbnail(url=thumbnail)

        em3 = E(
            title="<:settings:1236701973196856321> |  temp channel templates",
            description="> `vc_template_create`︲ `vc_template_delete`︲ `vc_template_edit_bitrate` ︲ `vc_template_edit_limit` ︲ `vc_template_edit_name` ︲ `vc_template_edit_region`",
            color=color
        )
        em3.set_footer(text=footer, icon_url=footer_icn)
        em3.set_thumbnail(url=thumbnail)

        em4 = E(
            title="<:owner:1236702179175121922> |  Other commands",
            description="> `owner_add`︲ `owner_remove`︲ `owner_menu`",
            color=color
        )
        em4.set_footer(text=footer, icon_url=footer_icn)
        em4.set_thumbnail(url=thumbnail)

        page = [
            Page(content=f"{ctx.author.mention}", embeds=[em]),
            Page(content=f"{ctx.author.mention}", embeds=[em1]),
            Page(content=f"{ctx.author.mention}", embeds=[em2]),
            Page(content=f"{ctx.author.mention}", embeds=[em3]),
            Page(content=f"{ctx.author.mention}", embeds=[em4])
        ]

        paginator = Paginator(pages=page)
        await paginator.respond(ctx.interaction, ephemeral=True)
        return
    



def setup(bot):
    bot.add_cog(help(bot))



        
