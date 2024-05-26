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
    for generator in data:
        generators.append(generator[6])

    return generators

class generator_edit_name(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    @slash_command(name="generator_edit_name", description="Edit the name of a themp voice channel generator")
    async def generator_edit_name(self, ctx: discord.ApplicationContext, generator: Option(str, "The generator you want to edit", autocomplete=get_generator), new_name: str):

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
            await cursor.execute("UPDATE vc_generator SET temp_name = ? WHERE guild_id = ? AND generator_name = ?", (new_name, ctx.guild.id, generator))
            await db.commit()


        em = E(
            title="<:Checken:1230840792382443530> | generator updated",
            description=f"**The generator has been updated to have the name ``{new_name}``**",
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
        
        log_channel = self.bot.get_channel(data[4])

        if log_channel is None:
            await db.close()
            return
        
        em = E(
            title="Generator Name Updated",
            description=f"**Generator ``{generator}`` has been updated to have the name ``{new_name}``**",
            color=color,
            timestamp=datetime.datetime.now()
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em)
        await db.close()
        return
    
def setup(bot):
    bot.add_cog(generator_edit_name(bot))



