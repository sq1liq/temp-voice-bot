import discord
import aiosqlite
from discord.ext import commands
from discord.commands import slash_command, Option
import yaml
import datetime


class unban_temp_vc_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="unban_temp_vc_role", description="Unban a role from your temporary voice channel")
    async def unban_temp_vc_role(self, ctx: discord.ApplicationContext, role: Option(discord.Role, "The role you want to unban")):

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
            
            roles = data[7]
            new_roles = []
            for role_id in roles.split(","):
                if role_id == role.id:
                    break

                new_roles.append(role_id)

            if new_roles is None:
                async with db.cursor() as cursor:
                    await cursor.execute(f"UPDATE temp_channels SET banned_r = ? WHERE owner = ? AND guild_id = ?", ("", ctx.author.id, ctx.guild.id))
                    await db.commit()
                    
            else:
                new_roles = ", ".join(new_roles)
                async with db.cursor() as cursor:
                    await cursor.execute(f"UPDATE temp_channels SET banned_r = ? WHERE owner = ? AND guild_id = ?", (new_roles, ctx.author.id, ctx.guild.id))
                    await db.commit()

            em = E(
                title="<:Checken:1230840792382443530> | role unbanned",
                description=f"**{role.mention} has been unbanned from your temporary voice channel**",
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
                title="<:Checken:1230840792382443530> | role unbanned",
                description=f"{ctx.author.mention} unbanned {role.mention} from their temporary voice channel",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await log_channel.send(embed=em)
            await db.close()
            return

def setup(bot):
    bot.add_cog(unban_temp_vc_role(bot))
    

            