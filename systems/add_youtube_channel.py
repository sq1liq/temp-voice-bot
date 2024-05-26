import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import aiosqlite
import scrapetube
import yaml


    


class add_yt_channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="add_youtube_channels", description="Add youtube channels to get notifications from")
    async def add_youtube_channels(self, ctx: discord.ApplicationContext, channel: Option(str, "The youtube channel name")):

    
        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

    

        yt_name = f"https://youtube.com/@{channel}"

        videos = scrapetube.get_channel(channel_url=yt_name, limit=1)

        if videos is None:
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
        
        data['youtube'][channel] = yt_name

        with open("data/config.yaml", "w") as f:
            yaml.dump(data, f)

        em = E(
            title="<:Youtube:1237027961530613801> | channel added",
            description=f"**Youtube channel ``{channel}`` added**",
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
            title="<:4928applicationbot:1230570127200882779> | Youtube channel added",
            description=f"**The channel ``{channel}`` has been added successfully from {ctx.author.mention}**",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em)
        await db.close()
        return
    
def setup(bot):
    return bot.add_cog(add_yt_channels(bot))
        


            


        