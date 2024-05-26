import discord
from discord.ext import commands
from discord.commands import slash_command
import aiosqlite
import yaml


class setup_cat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="setup", description="create a category for the voice channel generator")
    async def setup(self, ctx: discord.ApplicationContext):
        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']
        owner = data['host']['owner_id']

        E = discord.Embed

        db = await aiosqlite.connect('data/vc_settings.db')

        if ctx.author.id != owner and ctx.author.guild_permissions.administrator is False:
            em = E(
                title="<:3857cross:1230570958771982468> | Error",
                description="You do not have the required permissions to run this command",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)
            return
        
    
           

        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM cats WHERE guild_id = ?", (ctx.guild.id,))
            data = await cursor.fetchall()

        region = "auto"
        bitrate = 64000
        user_limit = 0
        perms = None

        if len(data) == 0:

            category = await ctx.guild.create_category("vc generator 1")
            channel = await category.create_text_channel("vc generator 1 commands")

            await channel.send("In this you channel can execute the commands for your voice channel")
            await db.execute("INSERT INTO cats (guild_id, cat_name, cat_id) VALUES (?, ?, ?)", (ctx.guild.id, category.name, category.id))
            
            channel = await category.create_voice_channel(f"🔊 | Generator 1")

            async with db.cursor() as cursor:
                await cursor.execute("UPDATE cats SET vc_ch_id = ? WHERE guild_id = ? AND cat_name = ?", (channel.id, ctx.guild.id, category.name))
                await db.commit()

            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                data = await cursor.fetchone()

                if data is None:
                    async with db.cursor() as cursor:
                        await cursor.execute("INSERT INTO vc_settings (guild_id, bitrate, region, user_limit) VALUES (?, ?, ?, ?)", (ctx.guild.id, 64000, "auto", 0))
                        await db.commit()

            
                    

                    
                

                else:
                    region = str(data[2])
                    bitrate = data[1]
                    user_limit = data[3]
                    perms = data[5]


                    


                    if user_limit == 0 or user_limit is None:
                        user_limit = None

                    if region.lower() == "auto" or region == "None":
                        region = None

                    await channel.edit(
                        user_limit=user_limit,
                        bitrate=bitrate,
                        rtc_region=region
                    )

                    if perms is not None:

                        kwargs = {perm: True for perm in perms.split(', ')}

                        await channel.set_permissions(ctx.guild.default_role, **kwargs)

            async with db.cursor() as cursor:
                await cursor.execute("INSERT INTO vc_generator (guild_id, channel_id, temp_name, temp_limit, temp_bitrate, temp_region, generator_name) VALUES (?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, channel.id, "{user}'s call", user_limit, bitrate, region, channel.name))
            await db.commit()

            em = E(
                title="<:3857check:1230570948937728000> | Success",
                description="Category created",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)


        else:


            new_generator = len(data) + 1

            category = await ctx.guild.create_category(f"vc generator {new_generator}")
            channel = await category.create_text_channel(f"vc generator {new_generator} commands")
            await channel.send("In this you channel can execute the commands for your voice channel")
            await db.execute("INSERT INTO cats (guild_id, cat_name, cat_id) VALUES (?, ?, ?)", (ctx.guild.id, category.name, category.id))
            await db.commit()

            channel = await category.create_voice_channel(f"🔊 | Generator {new_generator}")

            async with db.cursor() as cursor:
                await cursor.execute("UPDATE cats SET vc_ch_id = ? WHERE guild_id = ? AND cat_name = ?", (channel.id, ctx.guild.id, category.name))
                await db.commit()

            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM vc_settings WHERE guild_id = ?", (ctx.guild.id,))
                data = await cursor.fetchone()

                if data is None:
                    async with db.cursor() as cursor:
                        await cursor.execute("INSERT INTO vc_settings (guild_id, bitrate, region, user_limit) VALUES (?, ?, ?, ?)", (ctx.guild.id, 64000, "auto", 0))
                        await db.commit()

            
                    

                    
                

                else:
                    region = str(data[2])
                    bitrate = data[1]
                    user_limit = data[3]
                    perms = data[5]


                    


                    if user_limit == 0 or user_limit is None:
                        user_limit = None

                    if region.lower() == "auto" or region == "None":
                        region = None

                    await channel.edit(
                        user_limit=user_limit,
                        bitrate=bitrate,
                        rtc_region=region
                    )

                    if perms is not None:

                        kwargs = {perm: True for perm in perms.split(', ')}

                        await channel.set_permissions(ctx.guild.default_role, **kwargs)

            async with db.cursor() as cursor:
                await cursor.execute("INSERT INTO vc_generator (guild_id, channel_id, temp_name, temp_limit, temp_bitrate, temp_region, generator_name) VALUES (?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, channel.id, "{user}'s call", user_limit, bitrate, region, channel.name))
            await db.commit()




        await db.close()
        return
    
def setup(bot):
    bot.add_cog(setup_cat(bot))
