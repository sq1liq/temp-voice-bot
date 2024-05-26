import discord
import aiosqlite
from discord.ext import commands
from discord.commands import slash_command, Option
import yaml
import datetime


async def templates(ctx: discord.AutocompleteContext):
    db = await aiosqlite.connect('data/vc_settings.db')
    async with db.cursor() as cursor:
        await cursor.execute("SELECT * FROM vc_templates WHERE guild_id = ?", (ctx.interaction.guild.id,))
        data = await cursor.fetchall()
    await db.close()
    return [template[1] for template in data] + ["all"]




class vc_template_apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="vc_template_apply", description="Apply a voice channel template to a voice channel")
    async def vc_template_apply(self, ctx: discord.ApplicationContext, template_name: Option(str, "The name of the template", autocomplete=templates)):
        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM vc_templates WHERE guild_id = ? AND template_name = ?", (ctx.guild.id, template_name))
            data = await cursor.fetchone()

        if data is None:
            em = E(
                title="<:3857cross:1230570958771982468> | template not found",
                description="**This template does not exist**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return

        name = data[3]
        limit = data[4]
        bitrate = data[5]
        region = data[6]

        if limit == 0:
            limit = 99

        if bitrate == 0:
            bitrate = 64000

        if region == "auto":
            region = None

        if not ctx.author.voice:
            em = E(
                title="<:3857cross:1230570958771982468> | not in a voice channel",
                description="**You must be in a voice channel to apply a template**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return
        
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM temp_channels WHERE guild_id = ? AND channel_id = ?", (ctx.guild.id, ctx.author.voice.channel.id))
            data = await cursor.fetchone()

        if data is None:
            em = E(
                title="<:3857cross:1230570958771982468> | channel not found",
                description="**This channel is not a temporary channel**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return
        
        await ctx.author.voice.channel.edit(name=name, user_limit=limit, bitrate=bitrate, rtc_region=region)

        em = E(
            title="<:Checken:1230840792382443530> | template applied",
            description=f"**Template ``{template_name}`` has been applied to your voice channel**",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await ctx.respond(embed=em, ephemeral=True)
        
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
            data = await cursor.fetchone()

        if data is None:
            await db.close()
            return
        
        log_channel = ctx.guild.get_channel(data[4])

        if log_channel is None:
            await db.close()
            return
        
        em = E(
            title="<:4928applicationbot:1230570127200882779> | Template Applied",
            description=f"**Template ``{template_name}`` has been applied to {ctx.author.voice.channel.mention}**",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em)
        await db.close()
        return
    

def setup(bot):
    bot.add_cog(vc_template_apply(bot))
