import discord  
from discord.ext import commands
from discord.commands import slash_command, Option
import aiosqlite
import yaml
import datetime
import asyncio

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

class vc_region(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="vc_region", description="Set the region of a temporary voice channel")
    async def vc_region(self, ctx: discord.ApplicationContext, region: Option(str, "The region of the voice channel", autocomplete=region_finder)):
                
                with open("data/config.yaml", "r") as f:
                    data = yaml.safe_load(f)
        
                color = data['embed']['color']
                footer = data['embed']['footer']
                thumbnail = data['embed']['thumbnail']
                footer_icn = data['embed']['footer_icn']
        
                db = await aiosqlite.connect('data/vc_settings.db')
        
                E = discord.Embed
        
                if ctx.user.voice is None:
                    em = E(
                        title="<:3857cross:1230570958771982468> | not in voice channel",
                        description="**You are not in a voice channel**",
                        color=color
                    )
                    em.set_footer(text=footer, icon_url=footer_icn)
                    em.set_thumbnail(url=thumbnail)
                    await ctx.respond(embed=em, ephemeral=True)
                    await db.close()
                    return
                
                async with db.cursor() as cursor:
                    await cursor.execute(f"SELECT * FROM temp_channels WHERE channel_id = ?", (ctx.user.voice.channel.id,))
                    data = await cursor.fetchone()
        
                    if data is None:
                        em = E(
                            title="<:3857cross:1230570958771982468> | no temporary voice channel",
                            description="**You do not have a temporary voice channel**",
                            color=color
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        em.set_thumbnail(url=thumbnail)
                        await ctx.respond(embed=em, ephemeral=True)
                        await db.close()
                        return
        
                    if data[2] != ctx.author.id:
                        em = E(
                            title="<:3857cross:1230570958771982468> | not owner",
                            description="**You are not the owner of this temporary voice channel**",
                            color=color
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        em.set_thumbnail(url=thumbnail)
                        await ctx.respond(embed=em, ephemeral=True)
                        await db.close()
                        return

                    async with db.cursor() as cursor:
                        await cursor.execute(f"UPDATE temp_channels SET temp_region = ? WHERE channel_id = ?", (region, ctx.user.voice.channel.id))
                        await db.commit()

                    await ctx.user.voice.channel.edit(region=region)
        
                    em = E(
                        title="<:Checken:1230840792382443530> | region updated",
                        description=f"**Region has been updated to ``{region}``**",
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
                        title="<:4928applicationbot:1230570127200882779> |  Region Updated",
                        description=f"**Region of temporary voice channel ({ctx.author.voice.channel.mention}) in {ctx.guild.name} has been updated by {ctx.author.mention}**",
                        color=color,
                        timestamp=datetime.datetime.now()
                    )
                    em.set_footer(text=footer, icon_url=footer_icn)
                    await log_channel.send(embed=em)
                    await db.close()
                    return
                
def setup(bot):
    bot.add_cog(vc_region(bot))
