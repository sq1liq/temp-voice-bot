import discord
import aiosqlite
import datetime
from discord.ext import commands
from discord.commands import slash_command, Option
import yaml

async def get_generator(ctx: discord.AutocompleteContext):
    db = await aiosqlite.connect('data/vc_settings.db')
    async with db.cursor() as cursor:
        await cursor.execute("SELECT * FROM vc_generator WHERE guild_id = ?", (ctx.interaction.guild.id,))
        data = await cursor.fetchall()

    generators = []
    for generator in data:
        generators.append(generator[6])

    return generators

class GeneratorEditChannelName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="generator_edit_channel_name", description="Edit the name of a themp voice channel generator")
    async def generator_edit_channel_name(self, ctx: discord.ApplicationContext, generator: Option(str, "The generator you want to edit", autocomplete=get_generator), new_name: str):

        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

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
        
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE vc_generator SET generator_name = ? WHERE guild_id = ? AND generator_name = ?", (new_name, ctx.guild.id, generator))
            await db.commit()

        
        channel = ctx.guild.get_channel(data[1])

        await channel.edit(name=new_name)

        em = E(
            title="<:Checken:1230840792382443530> | generator updated",
            description=f"**Generator ``{generator}`` has been updated**",
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
            title="<:4928applicationbot:1230570127200882779> | Generator Updated",
            description=f"**Generator ``{generator}`` has been updated by {ctx.author.mention}**",
            color=color,
            timestamp=datetime.datetime.now()
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em)
        await db.close()
        return

def setup(bot):
    bot.add_cog(GeneratorEditChannelName(bot))
