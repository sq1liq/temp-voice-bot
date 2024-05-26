import discord 
from discord.ext import commands
from discord.commands import slash_command
import aiosqlite
import yaml
import aiohttp
import asyncio

class OwnerMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="owner_menu", description="this is only for the owner of the bot")
    async def owner_menu(self, ctx: discord.ApplicationContext):

        E = discord.Embed

        with open('data/config.yaml', 'r') as f:
            data = yaml.safe_load(f)
        owner_id = data['host']['owner_id']
        
        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icon = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')



        if ctx.author.id == owner_id:

            view = discord.ui.View()

            select = discord.ui.Select(
                placeholder="Select an option",
                min_values=1,
                max_values=1,

                options=

                [
                    discord.SelectOption(
                        label="set a default vc user limit",
                        value="set_vc_limit",
                        emoji="<:Bearbeitung:1230568631809609868>"
                    ),

                    discord.SelectOption(
                        label="set a default vc bitrate",
                        value="set_vc_bitrate",
                        emoji="<:discordstaff:1230568870331551764>"
                    ),

                    discord.SelectOption(
                        label="set a default vc region",
                        value="set_vc_region",
                        emoji="<:server:1230569109255749714>"
                    ),

                    discord.SelectOption(
                        label="set a default vc permmisions",
                        value="set_vc_user_perms",
                        emoji="<:Super_Mod:1230569310729011210>"
                    ),

                    discord.SelectOption(
                        label="Change the bot name",
                        value="change_bot_name",
                        emoji="<:Bot:1230569569165508689>"
                    ),

                    discord.SelectOption(
                        label="Change the bot avatar",
                        value="change_bot_avatar",
                        emoji="<:4928applicationbot:1230570127200882779>"
                    ),

                    discord.SelectOption(
                        label="set a vc log channel",
                        value="set_vc_log_channel",
                        emoji="<:6523information:1230570627489075335>"
                    ),

                    discord.SelectOption(
                        label="set admin role",
                        value="set_admin_role",
                        emoji="<:4696members:1230836719696216156>"
                    )


                ])
            
            view.add_item(select)

            em = E(
                title="<:owner:1230566873142268056> | Owner Menu",
                description="**Please select with the dropdown what do you want to do.**",
                color=color
            )
            em.set_thumbnail(url=thumbnail)
            em.set_footer(text=footer, icon_url=footer_icon)
            await ctx.respond(embed=em, view=view)

            def checkm(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            def check(interaction):
                return interaction.channel == ctx.channel and interaction.user == ctx.author
            
            try:
                interaction = await self.bot.wait_for("interaction", check=check, timeout=120)
                interaction: discord.Interaction

                await interaction.response.defer()
                if interaction.data["values"][0] == "set_vc_limit":
                    
                    em = E(
                        title="<:Bearbeitung:1230568631809609868> | Set a default vc user limit",
                        description="Please enter the default vc user limit.",
                        color=color
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=em, view=None)

                    try:
                        msg = await self.bot.wait_for("message", check=checkm, timeout=120)
                        msg: discord.Message
                        vc_limit = msg.content
                        try:
                            vc_limit = int(msg.content)
                        except:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="Please enter a valid number!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                            

                        if vc_limit < 0:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="The vc limit must be a positive number!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                        if vc_limit > 99:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="The vc limit must be less than 100!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                        if not vc_limit:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="Please enter a valid number!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                        async with db.cursor() as cursor:
                            await cursor.execute("Select * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                            data = await cursor.fetchone()

                        if not data:
                            async with db.cursor() as cursor:
                                await cursor.execute("INSERT INTO vc_settings (guild_id, user_limit) VALUES (?, ?)", (ctx.guild.id, vc_limit))
                                await db.commit()

                        else:
                            async with db.cursor() as cursor:
                                await cursor.execute("UPDATE vc_settings SET user_limit = ? WHERE guild_id = ?", (vc_limit, ctx.guild.id))
                                await db.commit()

                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The default vc user limit has been set to ``{vc_limit}``**",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)

                        await db.close()
                        return
                    
                    except:
                        em = E(
                            title="<:3857cross:1230570958771982468> | Error",
                            description="You didn't enter a number!",
                            color=discord.Color.red()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    
                elif interaction.data["values"][0] == "set_vc_bitrate":
                    em = E(
                        title="<:discordstaff:1230568870331551764> | Set a default vc bitrate",
                        description="Please enter the default vc bitrate.",
                        color=color
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=em, view=None)

                    try:
                        msg = await self.bot.wait_for("message", check=checkm, timeout=120)
                        msg: discord.Message
                        vc_bitrate = msg.content
                        try:
                            vc_bitrate = int(msg.content)
                        except:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="Please enter a valid number!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                            

                        if vc_bitrate < 0:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="The vc bitrate must be a positive number!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                        if vc_bitrate < 8000:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="The vc bitrate must be more than 8000!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                        if vc_bitrate > 96000:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="The vc bitrate must be less than 96000!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                        if not vc_bitrate:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="Please enter a valid number!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                        async with db.cursor() as cursor:
                            await cursor.execute("Select * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                            data = await cursor.fetchone()

                        if not data:
                            async with db.cursor() as cursor:
                                await cursor.execute("INSERT INTO vc_settings (guild_id, bitrate) VALUES (?, ?)", (ctx.guild.id, vc_bitrate))
                                await db.commit()

                        else:
                            async with db.cursor() as cursor:
                                await cursor.execute("UPDATE vc_settings SET bitrate = ? WHERE guild_id = ?", (vc_bitrate, ctx.guild.id))
                                await db.commit()

                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The default vc bitrate has been set to ``{vc_bitrate}``**",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)

                        await db.close()
                        return
                    
                    except:
                        em = E(
                            title="<:3857cross:1230570958771982468> | Error",
                            description="You didn't enter a number!",
                            color=discord.Color.red()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    
                elif interaction.data["values"][0] == "set_vc_region":
                    em = E(
                        title="<:server:1230569109255749714> | Set a default vc region",
                        description="Please enter the default vc region. Please enter one of them:\n\n **us-central, us-east, us-south, us-west, europe, sydney, singapore, rotterdam, japan, hongkong, brazil, russia, india, australia, southafrica, dubai**",
                        color=color
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=em, view=None)

                    try:
                        msg = await self.bot.wait_for("message", check=checkm, timeout=120)
                        msg: discord.Message
                        vc_region = msg.content

                        if not vc_region:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="Please enter a valid region!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            return
                        
                        async with db.cursor() as cursor:
                            await cursor.execute("Select * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                            data = await cursor.fetchone()

                        if not data:
                            async with db.cursor() as cursor:
                                await cursor.execute("INSERT INTO vc_settings (guild_id, region) VALUES (?, ?)", (ctx.guild.id, vc_region))
                                await db.commit()

                        else:

                            async with db.cursor() as cursor:
                                await cursor.execute("UPDATE vc_settings SET region = ? WHERE guild_id = ?", (vc_region, ctx.guild.id))
                                await db.commit()

                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The default vc region has been set to ``{vc_region}``**",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)

                        await db.close()
                        return
                    
                    except:
                        em = E(
                            title="<:3857cross:1230570958771982468> | Error",
                            description="You didn't enter a region!",
                            color=discord.Color.red()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    
                elif interaction.data["values"][0] == "set_vc_user_perms":

                    all_perms = [
                        "connect", "speak", "stream", "mute_members", 
                        "deafen_members", "move_members", "use_voice_activation", 
                        "priority_speaker"
                    ]

                    view = discord.ui.View()
                    select = discord.ui.Select(
                        placeholder="Select Permissions",
                        min_values=1,
                        max_values=1,
                        custom_id=f"{ctx.author.id}",
                    )


                    for perm_name in all_perms:
                        select.add_option(
                            label=perm_name,  
                            value=perm_name,
                            emoji="<:Checken:1230840792382443530>"
                        )

                    select.add_option(
                        label="Done",
                        value="done",
                        emoji="<:3857cross:1230570958771982468>"
                    )



                    view.add_item(select)


                    embed = discord.Embed(
                        title="Set Default Voice Channel Permissions",
                        description="**Select the permissions you want to edit. You can select one permissions each time.**",
                        color=color
                    )
                    embed.set_thumbnail(url=thumbnail)
                    embed.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=embed, view=view)

                    while True:
                        try:
                            interaction1 = await self.bot.wait_for("interaction", check=check, timeout=120)
                            interaction1: discord.Interaction
                            await interaction1.response.defer()
                            perm, done = interaction1.data["values"][0], interaction1.data["values"][0]
                            updated_perms_str = ""

                            if done == "done":
                                em = E(
                                title="<:Checken:1230840792382443530> | Success",
                                description=f"**The default vc user permissions has been updated!**",
                                color=color
                                )
                                em.set_thumbnail(url=thumbnail)
                                em.set_footer(text=footer, icon_url=footer_icon)
                                await interaction.edit(embed=em, view=None)
                                break

                            async with db.cursor() as cursor:
                                await cursor.execute("Select perms FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                                data = await cursor.fetchone()

                            if data: 
                                perms = data[0]  
                                perms_list = perms.split(", ") 

                                if perm in perms_list:
                                    perms_list.remove(perm)
                                    updated_perms_str = ", ".join(perms_list)
                                else:
                                    perms_list.append(perm)
                                    updated_perms_str = ", ".join(perms_list)

                                
                                async with db.cursor() as cursor:
                                    await cursor.execute("UPDATE vc_settings SET perms = ? WHERE guild_id = ?", (updated_perms_str, ctx.guild.id))
                                    await db.commit()
                            else:
                                async with db.cursor() as cursor:
                                    await cursor.execute("INSERT INTO vc_settings (guild_id, perms) VALUES (?, ?)", (ctx.guild.id, f"{perm}"))
                                    await db.commit()


                            em = E(
                                title="<:Checken:1230840792382443530> | Success",
                                description=f"**The default vc user permissions has been updated!**",
                                color=color
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=view)



                

                        except asyncio.TimeoutError:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="You didn't select any option!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            break

                    await db.close()
                    return








                    
                elif interaction.data["values"][0] == "change_bot_name":

                    em = E(
                        title="<:Bot:1230569569165508689> | Change the bot name",
                        description="Please enter the new bot name.",
                        color=color
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=em, view=None)

                    try:
                        msg = await self.bot.wait_for("message", check=checkm, timeout=120)
                        msg: discord.Message
                        bot_name = msg.content

                        if not bot_name:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="Please enter a valid name!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            return
                        
                        await self.bot.user.edit(username=bot_name)
                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The bot name has been changed to ``{bot_name}``**",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)

                        await db.close()
                        return
                    
                    except:
                        em = E(
                            title="<:3857cross:1230570958771982468> | Error",
                            description="You didn't enter a name!",
                            color=discord.Color.red()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    
                elif interaction.data["values"][0] == "change_bot_avatar":

                    em = E(
                        title="<:4928applicationbot:1230570127200882779> | Change the bot avatar",
                        description="Please enter the new bot avatar URL.",
                        color=color
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=em, view=None)

                    try:
                        msg = await self.bot.wait_for("message", check=checkm, timeout=120)
                        msg: discord.Message
                        
                        
                        attachment = msg.attachments[0]

                
                        if not attachment.url.endswith((".png", ".jpeg", ".jpg", ".gif")):
                            em = discord.Embed(
                                title="Error",
                                description="Invalid file type. Please attach an image in PNG, JPEG, JPG, or GIF format.",
                                color=color
                            )
                            em.set_footer(text=footer, icon_url=ctx.guild.icon.url)
                            em.set_thumbnail(url=ctx.guild.icon.url)
                            ctx.send(embed=em)

                        
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment.url) as resp:
                                image = await resp.read()

                        await self.bot.user.edit(avatar=image)
                        await session.close()
                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The bot avatar has been changed!**",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)

                        await db.close()
                        return
                    
                    except:
                        em = E(
                            title="<:3857cross:1230570958771982468> | Error",
                            description="You didn't enter a URL!",
                            color=discord.Color.red()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    
                elif interaction.data["values"][0] == "set_vc_log_channel":

                    em = E(
                        title="<:6523information:1230570627489075335> | Set a vc log channel",
                        description="Please enter the vc log channel.",
                        color=color
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=em, view=None)

                    try:
                        msg = await self.bot.wait_for("message", check=checkm, timeout=120)
                        
                        msg: discord.Message
                        channel = msg.channel_mentions[0]

                        if channel.id is None:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="Please enter a valid channel!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            return
                        
                        async with db.cursor() as cursor:
                            await cursor.execute("Select * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                            data = await cursor.fetchone()

                        if not data:
                            async with db.cursor() as cursor:
                                await cursor.execute("INSERT INTO vc_settings (guild_id, log_channel) VALUES (?, ?)", (ctx.guild.id, channel.id))
                                await db.commit()

                        else:
                            async with db.cursor() as cursor:
                                await cursor.execute("UPDATE vc_settings SET log_channel = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
                                await db.commit()

                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The vc log channel has been set to {channel.mention}**",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)

                        await db.close()
                        return
                    
                    except:
                        em = E(
                            title="<:3857cross:1230570958771982468> | Error",
                            description="You didn't enter a channel!",
                            color=discord.Color.red()
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    

                elif interaction.data["values"][0] == "set_admin_role":

                    em = E(
                        title="<:4696members:1230836719696216156> | Set admin role",
                        description="Please enter the roles you want to set as admin role.\n**1. You can only 1 role in a message**\n**2. write ``done`` to finish**",
                        color=color
                    )
                    em.set_thumbnail(url=thumbnail)
                    em.set_footer(text=footer, icon_url=footer_icon)
                    await interaction.edit(embed=em, view=None)

                    roles = []
                    rolementions = []

                    def checkm(m):
                        return m.author == interaction.user and m.channel == interaction.channel
                    while True:
                        try:
                            role1 = await self.bot.wait_for("message", check=checkm, timeout=120)
                            role1: discord.Message
                            role = str(role1.content)

                            if role.lower() == "done":
                                await role1.add_reaction("❌")
                                break

                            else:
                                role = role.replace("<@&", "")
                                role = role.replace(">", "")
                                role = ctx.guild.get_role(int(role))
                                if role is None:
                                    em = E(
                                        title="<:3857cross:1230570958771982468> | Error",
                                        description="Please enter a valid role!**You can still carry on.**",
                                        color=discord.Color.red()
                                    )
                                    em.set_thumbnail(url=thumbnail)
                                    em.set_footer(text=footer, icon_url=footer_icon)
                                    await role1.add_reaction("❌")

                                else:
                                    roles.append(f"{str({role.id})}")
                                    rolementions.append(f"{role.mention}\n")
                                    await role1.add_reaction("✔️")

                        except:
                            em = E(
                                title="<:3857cross:1230570958771982468> | Error",
                                description="You didn't enter a role!",
                                color=discord.Color.red()
                            )
                            em.set_thumbnail(url=thumbnail)
                            em.set_footer(text=footer, icon_url=footer_icon)
                            await interaction.edit(embed=em, view=None)
                            await db.close()
                            return
                        
                    async with db.cursor() as cursor:
                        await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                        data = await cursor.fetchone()

                    if not data:
                        async with db.cursor() as cursor:
                            await cursor.execute("INSERT INTO vc_settings (guild_id, admin_roles) VALUES (?, ?)", (ctx.guild.id, f", ".join(roles)))
                            await db.commit()

                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The admin role has been set to**\n\n{''.join(rolementions)}",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    
                    else:
                        async with db.cursor() as cursor:
                            await cursor.execute("UPDATE vc_settings SET admin_roles =+ ? WHERE guild_id = ?", (f", ".join(roles), ctx.guild.id))
                            await db.commit()

                        em = E(
                            title="<:Checken:1230840792382443530> | Success",
                            description=f"**The admin role has been set to**\n\n{''.join(rolementions)}",
                            color=color
                        )
                        em.set_thumbnail(url=thumbnail)
                        em.set_footer(text=footer, icon_url=footer_icon)
                        await interaction.edit(embed=em, view=None)
                        await db.close()
                        return
                    
            except asyncio.TimeoutError:
                em = E(
                    title="<:3857cross:1230570958771982468> | Error",
                    description="You didn't select any option!",
                    color=discord.Color.red()
                )
                em.set_thumbnail(url=thumbnail)
                em.set_footer(text=footer, icon_url=footer_icon)
                await ctx.respond(embed=em, ephemeral=True)
                await db.close()
                return
                    

        else:
            em = E(
                title="<:3857cross:1230570958771982468> | Error",
                description="You are not the owner of the bot!",
                color=discord.Color.red()
            )
            await ctx.respond(embed=em, ephemeral=True)
            return
        

        
def setup(bot):

    bot.add_cog(OwnerMenu(bot))

            
            