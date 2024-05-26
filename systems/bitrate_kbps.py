import discord
from discord.ext import commands
from discord.commands import slash_command
import aiosqlite
import yaml
import datetime


class bitrate_edit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="edit_temp_vc_bitrate", description="Edit the bitrate of your temporary voice channel")
    async def edit_temp_vc_bitrate(self, ctx: discord.ApplicationContext, bitrate: int):

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
                description="You are not in a voice channel",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return

        if bitrate < 8000 or bitrate > 96000:
            em = E(
                title="<:3857cross:1230570958771982468> | invalid bitrate",
                description="**Bitrate must be between 8000 and 96000**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return

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
                await ctx.respond(embed=em, ephemeral=True)
                await db.close()
                return

            async with db.cursor() as cursor:
                await cursor.execute(f"UPDATE temp_channels SET temp_bitrate = ? WHERE owner = ? AND guild_id = ?",(bitrate, ctx.author.id, ctx.guild.id))
                await db.commit()

            async with db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM temp_channels WHERE owner = ? AND guild_id = ?", (ctx.author.id, ctx.guild.id))
                data = await cursor.fetchone()

            channel = ctx.guild.get_channel(data[1])

            if channel is None:
                em = E(
                    title="<:3857cross:1230570958771982468> | Error",
                    description="**Temporary voice channel not found**",
                    color=color
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await ctx.respond(embed=em, ephemeral=True)
                await db.close()
                return
            
            await channel.edit(bitrate=bitrate)

            em = E(
                title="<:3857check:1230570958771982468> | bitrate updated",
                description=f"**Bitrate of your temporary voice channel has been updated to ``{bitrate}``**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return
        
def setup(bot):
    bot.add_cog(bitrate_edit(bot))