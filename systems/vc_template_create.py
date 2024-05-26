import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import yaml
import aiosqlite
import asyncio
import datetime

async def region_finder(ctx: discord.AutocompleteContext):
    
    regions = []
    regions.append("auto")
    for region in discord.VoiceRegion:
        if region.value == "vip-us-east":
            continue

        elif region.value == "vip-us-west":
            continue

        elif region.value == "vip-amsterdam":
            continue
        
        else:
            regions.append(region.value)

    return regions

class vc_template_create(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="vc_template_create", description="Create a voice channel template")
    async def vc_template_create(self, ctx: discord.ApplicationContext, channel_name: str, template_name: str, user_limit: int, bitrate: int, region: Option(str, "The region of the voice channel", autocomplete=region_finder)):
        
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

        if data is not None:
            em = E(
                title="<:3857cross:1230570958771982468> | template exists",
                description="**This template already exists**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return
        
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO vc_templates (guild_id, template_name, channel_id, temp_name, temp_limit, temp_bitrate, temp_region) VALUES (?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, template_name, ctx.channel.id, channel_name, user_limit, bitrate, region))
            await db.commit()

        em = E(
            title="<:Checken:1230840792382443530> | template created",
            description=f"**Template ``{template_name}`` has been created**",
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
            title="<:4928applicationbot:1230570127200882779> |  Template Created",
            description=f"**Template ``{template_name}`` has been created by {ctx.author.mention}**",
            color=color,
            timestamp=datetime.datetime.now()
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em)
        await db.close()
        return
    
def setup(bot):
    bot.add_cog(vc_template_create(bot))

