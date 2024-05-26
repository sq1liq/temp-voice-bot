import discord
import aiosqlite
from discord.ext import commands
from discord.commands import slash_command, Option
import yaml
import datetime


class vc_unhide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="vc_unhide", description="Unhide a hidden voice channel")
    async def vc_unhide(self, ctx: discord.ApplicationContext):
                    
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

            await ctx.user.voice.channel.set_permissions(ctx.guild.default_role, view_channel=True)

            em = E(
                title="<:Checken:1230840792382443530> | channel unhidden",
                description="**Your voice channel has been unhidden**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)

            async with db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                data = await cursor.fetchone()

            if data is None:
                await db.close()
                return
            
            log_channel = ctx.guild.get_channel(data[4])

            if log_channel is None:
                await db.close()
                return
            
            em = E(
                title="<:4928applicationbot:1230570127200882779> | channel unhidden",
                description=f"**{ctx.author.mention} has unhidden their voice channel**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await log_channel.send(embed=em)
            await db.close()
            return
        
def setup(bot):
    bot.add_cog(vc_unhide(bot))