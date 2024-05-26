import discord
import aiosqlite
from discord.ext import commands
from discord.commands import slash_command, Option
import yaml
import datetime

class unban_temp_vc_user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="unban_temp_vc_user", description="Unban a user from your temporary voice channel")
    async def unban_temp_vc_user(self, ctx: discord.ApplicationContext, user: Option(discord.User, "The user you want to unban")):

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
        
        user = ctx.guild.get_member(user.id)
        if user is None:
            em = E(
                title="<:3857cross:1230570958771982468> | invalid user",
                description="**Invalid user**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
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

        users = data[8]
        new_users = []
        for user_id in users.split(","):
            if user_id == str(user.id):
                break

            new_users.append(user_id)

        if new_users is None:
            async with db.cursor() as cursor:
                await cursor.execute(f"UPDATE temp_channels SET banned_u = ? WHERE owner = ? AND guild_id = ?", ("", ctx.author.id, ctx.guild.id))
                await db.commit()
                
        else:
            new_users = ", ".join(new_users)
            async with db.cursor() as cursor:
                await cursor.execute(f"UPDATE temp_channels SET banned_u = ? WHERE owner = ? AND guild_id = ?", (new_users, ctx.author.id, ctx.guild.id))
                await db.commit()

        em = E(
            title="<:Checken:1230840792382443530> | user unbanned",
            description=f"**{user.mention} has been unbanned from your temporary voice channel**",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await ctx.respond(embed=em, ephemeral=True)
        await db.close()
        return
    
def setup(bot):
    bot.add_cog(unban_temp_vc_user(bot))
    
