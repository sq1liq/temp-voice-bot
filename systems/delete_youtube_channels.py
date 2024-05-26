import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import aiosqlite
import yaml

async def get_saved_yt_channels(ctx: discord.AutocompleteContext):

    with open("data/config.yaml", "r") as f:
        data = yaml.safe_load(f)

    return [channel for channel in data['youtube']]

class YourCogName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="delete_youtube_channels", description="Delete youtube channels to get notifications from")
    async def delete_youtube_channels(self, ctx: discord.ApplicationContext, channel: Option(str, "The youtube channel name", autocomplete=get_saved_yt_channels)):
        # Lade die Konfigurationsdaten
        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']


        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

        yt_name = f"https://youtube.com/@{channel}"

        if channel not in data['youtube']:
            em = E(
                title="<:3857cross:1230570958771982468> | invalid channel",
                description="**Invalid youtube channel**",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed=em, ephemeral=True)
            await db.close()
            return


        del data['youtube'][channel]

        with open("data/config.yaml", "w") as f:
            yaml.safe_dump(data, f)


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
            title="<:4928applicationbot:1230570127200882779> | Youtube channel deleted",
            description=f"**The channel ``{channel}`` has been deleted successfully from {ctx.author.mention}**",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em)
        await db.close()

        em = E(
            title="<:Checken:1230840792382443530> | Channel deleted",
            description=f"**The channel ``{channel}`` has been deleted successfully**",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await ctx.respond(embed=em, ephemeral=True)

def setup(bot):
    bot.add_cog(YourCogName(bot))
