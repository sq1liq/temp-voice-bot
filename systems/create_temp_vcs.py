import discord
from discord.ext import commands
from discord.commands import slash_command
import aiosqlite
import yaml
import datetime
import random


class temp_channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        db = await aiosqlite.connect('data/vc_settings.db')


                  

        if before.channel is not None and after.channel is not None:
            print("both channels are not none")
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM temp_channels WHERE channel_id = ?", (before.channel.id,))
                data = await cursor.fetchone()

            if data is not None:
                owner = data[2]

                if owner == member.id:
                    if len(before.channel.members) == 0:
                        await before.channel.delete()

                        async with db.cursor() as cursor:
                            await cursor.execute("DELETE FROM temp_channels WHERE channel_id = ?", (before.channel.id,))
                            await db.commit()

                        with open("data/config.yaml", "r") as f:
                            data = yaml.safe_load(f)

                        color = data['embed']['color']
                        footer = data['embed']['footer']
                        thumbnail = data['embed']['thumbnail']
                        footer_icn = data['embed']['footer_icn']

                        async with db.cursor() as cursor:
                            await cursor.execute(f"SELECT * FROM vc_settings WHERE guild_id = ?", (member.guild.id,))
                            data = await cursor.fetchone()

                        log_channel = data[4]

                        if log_channel is not None:
                            log_ch = member.guild.get_channel(log_channel)
                            em = discord.Embed(
                                title="<:4928applicationbot:1230570127200882779> | temporary voice channel deleted",
                                description=f"**{member.mention} lefted their temporary voice channel and I deleted it.**",
                                color=color,
                                timestamp=datetime.datetime.now()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await log_ch.send(embed=em)

                        await db.close()
                        return
                    
                    else:
                        
                        for member in before.channel.members:
                            async with db.cursor() as cursor:
                                await cursor.execute("UPDATE temp_channels SET owner = ? WHERE channel_id = ?", (member.id, before.channel.id))
                            await db.commit()
                            break


                        async with db.cursor() as cursor:
                            await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (member.guild.id,))
                            data = await cursor.fetchone()

                        log_channel = data[4]

                        if log_channel is not None:
                            log_ch = member.guild.get_channel(log_channel)
                            em = discord.Embed(
                                title="<:4928applicationbot:1230570127200882779> | temporary voice channel owner left",
                                description=f"**{member.mention} is the new owner of the temporary voice channel.**",
                                color=color,
                                timestamp=datetime.datetime.now()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await log_ch.send(embed=em)
                    
                    await db.close()
                    return
                else:
                    await db.close()
                    return
                
            elif data is None:
                print("data is none")
                async with db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM temp_channels WHERE channel_id = ?", (after.channel.id,))
                    data = await cursor.fetchone()
                print(data)
                if data is not None:
                    banned_r = data[7]
                    banned_u = data[8]

                    roles = banned_r.split(",") if banned_r else []
                    users = banned_u.split(",") if banned_u else []

                    with open("data/config.yaml", "r") as f:
                        data = yaml.safe_load(f)

                    color = data['embed']['color']
                    footer = data['embed']['footer']
                    thumbnail = data['embed']['thumbnail']
                    footer_icn = data['embed']['footer_icn']

                    for role_id in roles:
                        role = member.guild.get_role(int(role_id))
                        if role and role in member.roles:
                            await member.move_to(None)
                            em = discord.Embed(
                                title="<:3857cross:1230570958771982468> | Role Banned",
                                description="You have a role that is banned from this voice channel.",
                                color=color
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await member.send(embed=em)

                    for user_id in users:
                        user = member.guild.get_member(int(user_id))
                        if user:
                            await member.move_to(None)
                            em = discord.Embed(
                                title="<:3857cross:1230570958771982468> | User Banned",
                                description="You are banned from this voice channel.",
                                color=color
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await member.send(embed=em)

                    async with db.cursor() as cursor:
                        await cursor.execute(f"SELECT * FROM vc_settings WHERE guild_id = ?", (member.guild.id,))
                        data = await cursor.fetchone()

                    log_channel = data[4]

                    if log_channel is not None:
                        log_ch = member.guild.get_channel(log_channel)
                        print("log channel exists")
                        em = discord.Embed(
                            title="<:4928applicationbot:1230570127200882779> | User tried to join banned channel",
                            description=f"**{member.mention} tried to join a voice channel they were banned from.**",
                            color=color,
                            timestamp=datetime.datetime.now()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icn)
                        await log_ch.send(embed=em)

                    await db.close()
                    return
                
                else:
                    async with db.cursor() as cursor:
                        await cursor.execute("SELECT * FROM vc_generator WHERE channel_id = ?", (after.channel.id,))
                        data = await cursor.fetchone()

                    if data is not None:
                        temp_name = data[2]
                        temp_limit = data[3]
                        temp_bitrate = data[4]
                        temp_region = str(data[5])

                        temp_name = temp_name.replace("{user}", member.name)
                        temp_name = temp_name.replace("{guild}", member.guild.name)
                        temp_name = temp_name.replace("{channel}", after.channel.name)

                        if temp_limit == 0 or temp_limit is None:
                            temp_limit = None

                        if temp_region.lower() == "auto" or temp_region == "None":
                            temp_region = None

                        async with db.cursor() as cursor:
                            await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (after.channel.guild.id,))
                            data = await cursor.fetchone()
                        log_channel = data[4]

                        temp_ch = await after.channel.category.create_voice_channel(name=temp_name)

                        await temp_ch.edit(bitrate=temp_bitrate, user_limit=temp_limit, rtc_region=temp_region)

                        if data is None:
                            await temp_ch.set_permissions(after.channel.guild.default_role, connect=True, view_channel=True, speak=True, stream=True, use_voice_activation=True)

                        else:
                            perms = data[5]

                            if perms is not None:

                                kwargs = {perm: True for perm in perms.split(', ')}

                                await temp_ch.set_permissions(after.channel.guild.default_role, **kwargs)
                            
                            

                            
                        await member.move_to(temp_ch)

                        async with db.cursor() as cursor:
                            await cursor.execute("INSERT INTO temp_channels (guild_id, channel_id, owner, temp_name, temp_limit, temp_bitrate, temp_region) VALUES (?, ?, ?, ?, ?, ?, ?)", (after.channel.guild.id, temp_ch.id, member.id, temp_name, temp_limit, temp_bitrate, temp_region))
                            await db.commit()

                        if log_channel is not None:
                            log_ch = after.channel.guild.get_channel(log_channel)
                            
                            with open("data/config.yaml", "r") as f:
                                data = yaml.safe_load(f)

                            color = data['embed']['color']
                            footer = data['embed']['footer']
                            thumbnail = data['embed']['thumbnail']
                            footer_icn = data['embed']['footer_icn']

                            E = discord.Embed

                            em = E(
                                title="<:4928applicationbot:1230570127200882779> | temporary voice channel created",
                                description=f"**{member.mention} created a voice channel.**",
                                color=color,
                                timestamp=datetime.datetime.now()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await log_ch.send(embed=em)
                        else:
                            await db.close()
                            return
                        
                        await db.close()
                        return
                
        if before.channel is not None:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM temp_channels WHERE channel_id = ?", (before.channel.id,))
                data = await cursor.fetchone()

            if data is not None:
                owner = data[2]

                with open("data/config.yaml", "r") as f:
                    data = yaml.safe_load(f)

                color = data['embed']['color']
                footer = data['embed']['footer']
                thumbnail = data['embed']['thumbnail']
                footer_icn = data['embed']['footer_icn']

                if owner == member.id:
                    if len(before.channel.members) == 0:
                        await before.channel.delete()

                        async with db.cursor() as cursor:
                            await cursor.execute("DELETE FROM temp_channels WHERE channel_id = ?", (before.channel.id,))
                            await db.commit()

                        

                        async with db.cursor() as cursor:
                            await cursor.execute(f"SELECT * FROM vc_settings WHERE guild_id = ?", (member.guild.id,))
                            data = await cursor.fetchone()

                        log_channel = data[4]

                        if log_channel is not None:
                            log_ch = member.guild.get_channel(log_channel)
                            em = discord.Embed(
                                title="<:4928applicationbot:1230570127200882779> | temporary voice channel deleted",
                                description=f"**{member.mention} lefted their temporary voice channel and I deleted it.**",
                                color=color,
                                timestamp=datetime.datetime.now()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await log_ch.send(embed=em)

                        await db.close()
                        return
                    
                    else:
                        
                        for member in before.channel.members:
                            async with db.cursor() as cursor:
                                await cursor.execute("UPDATE temp_channels SET owner = ? WHERE channel_id = ?", (member.id, before.channel.id))
                                await db.commit()
                            break


                        async with db.cursor() as cursor:
                            await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (member.guild.id,))
                            data = await cursor.fetchone()

                        log_channel = data[4]

                        if log_channel is not None:
                            log_ch = member.guild.get_channel(log_channel)
                            em = discord.Embed(
                                title="<:4928applicationbot:1230570127200882779> | temporary voice channel owner left",
                                description=f"**{member.mention} is the new owner of the temporary voice channel.**",
                                color=color,
                                timestamp=datetime.datetime.now()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await log_ch.send(embed=em)
                    
                    await db.close()
                    return
                else:
                    await db.close()
                    return
                

        if after.channel is not None:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM vc_generator WHERE channel_id = ?", (after.channel.id,))
                data = await cursor.fetchone()

            if data is not None:
                temp_name = data[2]
                temp_limit = data[3]
                temp_bitrate = data[4]
                temp_region = str(data[5])

                temp_name = temp_name.replace("{user}", member.name)
                temp_name = temp_name.replace("{guild}", member.guild.name)
                temp_name = temp_name.replace("{channel}", after.channel.name)

                if temp_limit == 0 or temp_limit is None:
                    temp_limit = None

                if temp_region.lower() == "auto" or temp_region == "None":
                    temp_region = None

                async with db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (after.channel.guild.id,))
                    data = await cursor.fetchone()
                log_channel = data[4]

                temp_ch = await after.channel.category.create_voice_channel(name=temp_name)

                await temp_ch.edit(bitrate=temp_bitrate, user_limit=temp_limit, rtc_region=temp_region)

                if data is None:
                    await temp_ch.set_permissions(after.channel.guild.default_role, connect=True, view_channel=True, speak=True, stream=True, use_voice_activation=True)

                else:
                    perms = data[5]

                    if perms is not None:

                        kwargs = {perm: True for perm in perms.split(', ')}

                        await temp_ch.set_permissions(after.channel.guild.default_role, **kwargs)
                    
                    

                    
                await member.move_to(temp_ch)

                async with db.cursor() as cursor:
                    await cursor.execute("INSERT INTO temp_channels (guild_id, channel_id, owner, temp_name, temp_limit, temp_bitrate, temp_region) VALUES (?, ?, ?, ?, ?, ?, ?)", (after.channel.guild.id, temp_ch.id, member.id, temp_name, temp_limit, temp_bitrate, temp_region))
                    await db.commit()

                if log_channel is not None:
                    log_ch = after.channel.guild.get_channel(log_channel)
                    
                    with open("data/config.yaml", "r") as f:
                        data = yaml.safe_load(f)

                    color = data['embed']['color']
                    footer = data['embed']['footer']
                    thumbnail = data['embed']['thumbnail']
                    footer_icn = data['embed']['footer_icn']

                    E = discord.Embed

                    em = E(
                        title="<:4928applicationbot:1230570127200882779> | temporary voice channel created",
                        description=f"**{member.mention} created a voice channel.**",
                        color=color,
                        timestamp=datetime.datetime.now()
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icn)
                    await log_ch.send(embed=em)
                else:
                    await db.close()
                    return
                

            
            else:
                async with db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM temp_channels WHERE channel_id = ?", (after.channel.id,))
                    data = await cursor.fetchone()

                if data is not None:
                    banned_r = data[7]
                    banned_u = data[8]

                    roles = banned_r.split(",") if banned_r else []
                    users = banned_u.split(",") if banned_u else []

                    with open("data/config.yaml", "r") as f:
                        data = yaml.safe_load(f)

                    color = data['embed']['color']
                    footer = data['embed']['footer']
                    thumbnail = data['embed']['thumbnail']
                    footer_icn = data['embed']['footer_icn']

                    for role_id in roles:
                        role = member.guild.get_role(int(role_id))
                        if role and role in member.roles:
                            await member.move_to(None)
                            em = discord.Embed(
                                title="<:3857cross:1230570958771982468> | Role Banned",
                                description="You have a role that is banned from this voice channel.",
                                color=color
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await member.send(embed=em)

                    for user_id in users:
                        user = member.guild.get_member(int(user_id))
                        if user:
                            await member.move_to(None)
                            em = discord.Embed(
                                title="<:3857cross:1230570958771982468> | User Banned",
                                description="You are banned from this voice channel.",
                                color=color
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icn)
                            await member.send(embed=em)

                    async with db.cursor() as cursor:
                        await cursor.execute(f"SELECT * FROM vc_settings WHERE guild_id = ?", (member.guild.id,))
                        data = await cursor.fetchone()

                    log_channel = data[4]

                    if log_channel is not None:
                        log_ch = member.guild.get_channel(log_channel)

                        em = discord.Embed(
                            title="<:4928applicationbot:1230570127200882779> | User tried to join banned channel",
                            description=f"**{member.mention} tried to join a voice channel they were banned from.**",
                            color=color,
                            timestamp=datetime.datetime.now()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icn)
                        await log_ch.send(embed=em)

                    await db.close()
                    return

                else:
                    await db.close()
                    return
                
        await db.close()
        return
                

            

                        




            

def setup(bot):
    bot.add_cog(temp_channels(bot))

                
            
        

        