import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import aiosqlite
import yaml
import datetime
import asyncio

async def templates(ctx: discord.AutocompleteContext):
    db = await aiosqlite.connect('data/vc_settings.db')
    async with db.cursor() as cursor:
        await cursor.execute("SELECT * FROM vc_templates WHERE guild_id = ?", (ctx.interaction.guild.id,))
        data = await cursor.fetchall()
    await db.close()
    return [template[1] for template in data] + ["all"]




class vc_template_edit_lt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="vc_template_edit_limit", description="Edit the user limit of a voice channel template")
    async def vc_template_edit_lt(self, ctx: discord.ApplicationContext, template_name: Option(str, "The name of the template", autocomplete=templates), user_limit: int):

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
    
            if data is None:
                em = E(
                    title="<:3857cross:1230570958771982468> | template not found",
                    description="**This template does not exist**",
                    color=color
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await ctx.respond(embed=em, ephemeral=True)
                await db.close()
                return
    
            if template_name == "all":
                async with db.cursor() as cursor:
                    await cursor.execute("UPDATE vc_templates SET temp_limit = ? WHERE guild_id = ?", (user_limit, ctx.guild.id))
                    await db.commit()

                em = E(
                    title="<:Checken:1230840792382443530> | templates updated",
                    description=f"**All templates have been updated**",
                    color=color
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await ctx.respond(embed=em, ephemeral=True)
            
            else:
                async with db.cursor() as cursor:
                    await cursor.execute(f"UPDATE vc_templates SET temp_limit = ? WHERE guild_id = ? AND template_name = ?", (user_limit, ctx.guild.id, template_name))
                    await db.commit()
        
                em = E(
                    title="<:Checken:1230840792382443530> | template updated",
                    description=f"**Template ``{template_name}`` has been updated**",
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
            
            if template_name == "all":
                em = E(
                    title="<:4928applicationbot:1230570127200882779> | Template Updated",
                    description=f"**All templates have been updated by {ctx.author.mention}**",
                    color=color,
                    timestamp=datetime.datetime.now()
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await log_channel.send(embed=em)

            else:
                em = E(
                    title="<:4928applicationbot:1230570127200882779> | Template Updated",
                    description=f"**Template ``{template_name}`` has been updated by {ctx.author.mention}**",
                    color=color,
                    timestamp=datetime.datetime.now()
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await log_channel.send(embed=em)

            await db.close()
            return
    
def setup(bot):
    bot.add_cog(vc_template_edit_lt(bot))
