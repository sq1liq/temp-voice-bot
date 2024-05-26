import discord  
from discord.ext import commands
from discord.commands import slash_command
import aiosqlite
import yaml
import datetime


class BanVCUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(name = "ban_temp_vc_user", description = "Ban a user from your temporary voice channel")
    async def ban_temp_vc_user(self, ctx: discord.ApplicationContext, user: discord.User):


        with open (f"data/config.yaml", "r") as f:
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
            await ctx.respond(embed = em, ephemeral = True)
            await db.close()
            return
        
        user = ctx.guild.get_member(user.id)
        if user is None:
            em = E(
                title="<:3857cross:1230570958771982468> | invalid user",
                description="**Invalid user**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)
            await db.close()
            return
        

        db = await aiosqlite.connect('data/vc_settings.db')
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM temp_channels WHERE owner = ? AND guild_id = ?", (ctx.author.id, ctx.guild.id))
            data = await cursor.fetchone()

            if data is None:
                em = E(
                    title="<:3857cross:1230570958771982468> | no temporary voice channel",
                    description="**You do not have a temporary voice channel**",
                    color=color
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await ctx.respond(embed = em, ephemeral = True)
                await db.close()
                return

            if data[7] is None:
                banned = []
            else:
                banned = data[7].split(",")
            
            if str(user.id) in banned:
                em = E(
                    title="<:3857cross:1230570958771982468> | user already banned",
                    description="User is already banned from your temporary voice channel",
                    color=color
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await ctx.respond(embed = em, ephemeral = True)
                await db.close()
                return
            
            banned.append(str(user.id))
            banned = ", ".join(banned)
            async with db.cursor() as cursor:
                await cursor.execute(f"UPDATE temp_channels SET banned_u = ? WHERE owner = ? AND guild_id = ?", (banned, ctx.author.id, ctx.guild.id))
                await db.commit()

            em = E(
                title="<:2533warning:1231962850440904714> | user banned",
                description=f"**{user.mention} has been banned from your temporary voice channel**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)
            await db.close()

def setup(bot):
    bot.add_cog(BanVCUser(bot))