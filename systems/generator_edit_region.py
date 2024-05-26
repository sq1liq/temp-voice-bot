import discord
import aiosqlite
from discord.ext import commands
from discord.commands import slash_command, Option
import yaml
import datetime

async def get_generator(ctx: discord.AutocompleteContext):
    db = await aiosqlite.connect('data/vc_settings.db')
    async with db.cursor() as cursor:
        await cursor.execute("SELECT * FROM vc_generator WHERE guild_id = ?", (ctx.interaction.guild.id,))
        data = await cursor.fetchall()

    generators = []
    generators.append("All Generators")
    for generator in data:
        generators.append(generator[6])

    return generators

async def region_finder(ctx: discord.AutocompleteContext):
    
    regions = []
    regions.append("auto")
    for region in discord.VoiceRegion:
        if region.value == "vip-us-east":
            continue

        elif region.value == "vip-us-west":
            continue

        elif region.value == "vip-amsterdam":
            continue
        
        else:
            regions.append(region.value)

    return regions

class generator_edit_region(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="generator_edit_region", description="Edit the region of a themp voice channel generator")
    async def generator_edit_region(self, ctx: discord.ApplicationContext, generator: Option(str, "The generator you want to edit", autocomplete=get_generator), region: Option(str, "The region of the voice channel", autocomplete=region_finder)):


        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

        if generator == "All Generators":
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM vc_generator WHERE guild_id = ?", (ctx.guild.id,))
                data = await cursor.fetchall()

            for generator in data:
                channel = ctx.guild.get_channel(generator[1])
                await channel.edit(region=region)

            async with db.cursor() as cursor:
                await cursor.execute("UPDATE vc_generator SET region = ? WHERE guild_id = ?", (region, ctx.guild.id))
                await db.commit()

            em = E(
                title="<:3857check:1230570958771982468> | All generators updated",
                description=f"**All generators have been updated to have a region of {region}**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            return

        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM vc_generator WHERE guild_id = ? AND generator_name = ?", (ctx.guild.id, generator))
            data = await cursor.fetchone()

        if data is None:
            em = E(
                title="<:3857cross:1230570958771982468> | generator not found",
                description="**This generator does not exist**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return
        
        channel = ctx.guild.get_channel(data[1])
        await channel.edit(region=region)

        async with db.cursor() as cursor:
            await cursor.execute("UPDATE vc_generator SET region = ? WHERE guild_id = ? AND generator_name = ?", (region, ctx.guild.id, generator))
            await db.commit()

        em = E(
            title="<:3857check:1230570958771982468> | generator updated",
            description=f"**Generator ``{generator}`` has been updated to have a region of {region}**",
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
            title="<:3857check:1230570958771982468> | generator region updated",
            description=f"**The region of generator ``{generator}`` has been updated to {region}**",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em)
        await db.close()
        return
    
def setup(bot):
    bot.add_cog(generator_edit_region(bot))
