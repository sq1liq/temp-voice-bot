import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option
import aiosqlite
import scrapetube
import yaml
import asyncio

class youtube_notifications(commands.Cog):  
    def __init__(self, bot):
        self.bot = bot
        

    @slash_command(name="setup_youtube_notifications", description="Setup youtube notifications")
    async def setup_youtube_notifications(self, ctx: discord.ApplicationContext, channel: Option(discord.TextChannel, "The channel you want to send notifications to"), role: Option(discord.Role, "The role you want to mention", required=False)):
        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

        em = E(
            title="<:Youtube:1237027961530613801> | notification text",
            description="Please send me the text you want to send with the notification.",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await ctx.respond(embed=em, ephemeral=True)

        def check(m):
            return m.author == ctx.user and m.channel == ctx.channel
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=120)
            msg: discord.Message

            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM yt_settings WHERE guild_id = ?", (ctx.guild.id,))
                data = await cursor.fetchone()

            if data is not None:
                if role is not None:
                    async with db.cursor() as cursor:
                        await cursor.execute("UPDATE yt_settings SET channel_id = ?, notif_text = ?, notif_role = ? WHERE guild_id = ?", (channel.id, msg.content, role.id, ctx.guild.id))
                        await db.commit()

                else:
                    async with db.cursor() as cursor:
                        await cursor.execute("UPDATE yt_settings SET channel_id = ?, notif_text = ? WHERE guild_id = ?", (channel.id, msg.content, ctx.guild.id))
                        await db.commit()

            else:
                if role is not None:
                    async with db.cursor() as cursor:
                        await cursor.execute("INSERT INTO yt_settings (guild_id, channel_id, notif_text, notif_role) VALUES (?, ?, ?, ?)", (ctx.guild.id, channel.id, msg.content, role.id))
                        await db.commit()

                else:
                    async with db.cursor() as cursor:
                        await cursor.execute("INSERT INTO yt_settings (guild_id, channel_id, notif_text) VALUES (?, ?, ?)", (ctx.guild.id, channel.id, msg.content))
                        await db.commit()

            em = E(
                title="<:Checken:1230840792382443530> | setup complete",
                description="Youtube notifications have been setup",
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
                title="<:4928applicationbot:1230570127200882779> | Youtube notifications setup",
                description=f"**Youtube notifications have been setup by {ctx.author.mention}**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await log_channel.send(embed=em)
            await db.close()
            return

        except asyncio.TimeoutError:
            em = E(
                title="<:3857cross:1230570958771982468> | timeout",
                description="You took too long to respond",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return

        
    
def setup(bot):
    bot.add_cog(youtube_notifications(bot))