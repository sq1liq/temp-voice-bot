import discord
from discord.ext import commands
from discord.commands import slash_command
import aiosqlite
import yaml
import datetime
import asyncio


class vc_limit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="vc_limit", description="Set the user limit of a temporary voice channel")
    async def vc_limit(self, ctx: discord.ApplicationContext, limit: int):
                
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
                        await cursor.execute(f"UPDATE temp_channels SET temp_limit = ? WHERE channel_id = ?", (limit, ctx.user.voice.channel.id))
                        await db.commit()

                    await ctx.user.voice.channel.edit(user_limit=limit)
        
                    em = E(
                        title="<:Checken:1230840792382443530> | user limit set",
                        description=f"**User limit has been set to ``{limit}``**",
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
                        title="<:4928applicationbot:1230570127200882779> |  User Limit Set",
                        description=f"**User limit has been set to ``{limit}``on {ctx.author.voice.channel.mention} by {ctx.author.mention}**",
                        color=color,
                        timestamp=datetime.datetime.now()
                    )
                    em.set_footer(text=footer, icon_url=footer_icn)
                    await log_channel.send(embed=em)
                    await db.close()
                    return
                

def setup(bot):
    bot.add_cog(vc_limit(bot))