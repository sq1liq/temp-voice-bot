import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import aiosqlite    
import asyncio
import yaml
import datetime


class BanVCRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @slash_command(name = "ban_temp_vc_role", description = "Ban a role from your temporary voice channel")
    async def ban_temp_vc_role(self, ctx: discord.ApplicationContext, role: discord.Role):


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
                description="You are not in a voice channel",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)
            await db.close()
            return
        
        role = ctx.guild.get_role(role.id)
        if role is None:
            em = E(
                title="<:3857cross:1230570958771982468> | invalid role",
                description="Invalid role",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)
            await db.close()
            return
        

        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM temp_channels WHERE owner = ? AND guild_id = ?", (ctx.author.id, ctx.guild.id))
            data = await cursor.fetchone()

        if data is None:
            em = E(
                title="<:3857cross:1230570958771982468> | not enough permissions",
                description="You are not the owner of a temporary voice channel",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)

        else:
            if data[7] is None:
                async with db.cursor() as cursor:
                    await cursor.execute(f"UPDATE temp_channels SET banned_r = ? WHERE owner = ? AND guild_id = ?", (role.id, ctx.author.id, ctx.guild.id))
                    await db.commit()

                
            else:
                banned_roles = data[7]
                banned_roles = banned_roles.split(", ")
                banned_roles.append(str(role.id))
                banned_roles = ", ".join(banned_roles)
                async with db.cursor() as cursor:
                    await cursor.execute(f"UPDATE temp_channels SET banned_r = ? WHERE owner = ? AND guild_id = ?", (banned_roles, ctx.author.id, ctx.guild.id))
                    await db.commit()
                
            em = E(
                title="<:2533warning:1231962850440904714> | role banned",
                description=f"{role.mention} has been banned from your temporary voice channel",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)

            async with db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                data = await cursor.fetchone()

            log_channel = data[4]

            if log_channel is not None:
                log_ch = ctx.guild.get_channel(log_channel)
                em = E(
                    title="<:2533warning:1231962850440904714> | role banned",
                    description=f"{ctx.author.mention} banned {role.mention} from their temporary voice channel",
                    color=color,
                    timestamp=datetime.datetime.now()
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await log_ch.send(embed = em)
            await db.close()
            return


def setup(bot):
    bot.add_cog(BanVCRole(bot))




