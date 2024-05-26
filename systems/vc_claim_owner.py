import discord
from discord.ext import commands
from discord.commands import slash_command
import aiosqlite
import yaml
import datetime
import asyncio


class claimowner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="claim_owner", description="Claim ownership of a temporary voice channel")
    async def claim_owner(self, ctx: discord.ApplicationContext):
            
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
    
                if data[2] == ctx.author.id:
                    em = E(
                        title="<:3857cross:1230570958771982468> | already owner",
                        description="**You are already the owner of this temporary voice channel**",
                        color=color
                    )
                    em.set_footer(text=footer, icon_url=footer_icn)
                    em.set_thumbnail(url=thumbnail)
                    await ctx.respond(embed=em, ephemeral=True)
                    await db.close()
                    return
                
                em = E(
                    title="<a:Laden:1235287989874065609> | ownership requested",
                    description="Your request has been sent to the owner of this temporary voice channel",
                    color=color
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                await ctx.respond(embed=em, ephemeral=True)
                
                owner = ctx.guild.get_member(data[2])

                view = discord.ui.View()

                view.add_item(discord.ui.Button(label="Accept", emoji="✔️", style=discord.ButtonStyle.green, custom_id="accept"))
                view.add_item(discord.ui.Button(label="Reject", emoji="✖️", style=discord.ButtonStyle.red, custom_id="reject"))
    
                em = E(
                    title="<a:Laden:1235287989874065609> | ownership requested",
                    description=f"**Ownership of this temporary voice channel has been requested from {ctx.author.mention} for the channel {ctx.author.voice.channel.name}**",
                    color=color
                )
                em.set_footer(text=footer, icon_url=footer_icn)
                em.set_thumbnail(url=thumbnail)
                msg = await owner.send(embed=em, view=view)

                async with db.cursor() as cursor:
                    await cursor.execute(f"SELECT * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                    data = await cursor.fetchone()

                if data is None:
                    pass

                else:
                    log_channel = ctx.guild.get_channel(data[4])

                    if log_channel is None:
                        pass

                    else:
                        em = E(
                            title="<:4928applicationbot:1230570127200882779> | Ownership Requested",
                            description=f"**Ownership of the temporary voice channel ({ctx.author.voice.channel.mention}) has been requested from {ctx.author.mention}**",
                            color=color,
                            timestamp=datetime.datetime.now()
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        await log_channel.send(embed=em)
                        
                


                def check(interaction):
                    return interaction.user == owner and interaction.channel == owner.dm_channel
                
                try:
                    interaction = await self.bot.wait_for("interaction", check=check, timeout=240)
                    interaction: discord.Interaction

                    await interaction.response.defer()

                    if interaction.custom_id == "accept":
                        async with db.cursor() as cursor:
                            await cursor.execute(f"UPDATE temp_channels SET owner = ? WHERE channel_id = ?", (ctx.author.id, ctx.user.voice.channel.id))
                            await db.commit()


                        em = E(
                            title="<:Checken:1230840792382443530> | ownership claimed",
                            description=f"**Ownership of this temporary voice channel has been claimed by {ctx.author.mention}**",
                            color=color
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        em.set_thumbnail(url=thumbnail)
                        await msg.edit(embed=em, view=None)

                        
                        em = E(
                            title="<:Checken:1230840792382443530> | ownership claimed",
                            description=f"**Ownership of this temporary voice channel has been claimed by {ctx.author.mention}**",
                            color=color
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        em.set_thumbnail(url=thumbnail)
                        await ctx.followup.send(embed=em, ephemeral=True)
                        
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
                            title="<:4928applicationbot:1230570127200882779> | Ownership Claimed",
                            description=f"**Ownership of the temporary voice channel ({ctx.author.voice.channel.mention}) has been claimed by {ctx.author.mention}**",
                            color=color,
                            timestamp=datetime.datetime.now()
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        await log_channel.send(embed=em)
                        await db.close()
                        return
                    

                    
                    elif interaction.custom_id == "reject":

                        em = E(
                            title="<:3857cross:1230570958771982468> | ownership rejected",
                            description=f"**Ownership of this temporary voice channel has been rejected by {owner.mention}**",
                            color=color
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        em.set_thumbnail(url=thumbnail)
                        await msg.edit(embed=em, view=None)

                        em = E(
                            title="<:3857cross:1230570958771982468> | ownership rejected",
                            description=f"**Ownership of this temporary voice channel has been rejected by {owner.mention}**",
                            color=color
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        em.set_thumbnail(url=thumbnail)
                        await ctx.followup.send(embed=em, ephemeral=True)
                        
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
                            title="<:4928applicationbot:1230570127200882779> | Ownership Rejected",
                            description=f"**Ownership of the temporary voice channel ({ctx.author.voice.channel.mention}) has been rejected by {owner.mention}**",
                            color=color,
                            timestamp=datetime.datetime.now()
                        )
                        em.set_footer(text=footer, icon_url=footer_icn)
                        await log_channel.send(embed=em)
                        await db.close()
                        return
                    
                except asyncio.TimeoutError:
                    em = E(
                        title="<:3857cross:1230570958771982468> | request timed out",
                        description="**The request has timed out**",
                        color=color
                    )
                    em.set_footer(text=footer, icon_url=footer_icn)
                    em.set_thumbnail(url=thumbnail)
                    await ctx.followup.send(embed=em, ephemeral=True)
                    await db.close()
                    return
            
                

def setup(bot):
    bot.add_cog(claimowner(bot))
