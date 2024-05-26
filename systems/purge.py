import discord 
from discord.ext import commands
from discord.commands import slash_command, Option
import aiosqlite
import yaml
import chat_exporter
import io


class purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="purge", description="Delete a themp voice channel generator")
    async def purge(self, ctx: discord.ApplicationContext, amount: int):

        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

        if not ctx.author.guild_permissions.administrator:
            em = E(
                title="<:3857cross:1230570958771982468> | Error",
                description="You do not have the required permissions to run this command",
                color=color
            )
            em.set_footer(text=footer, icon_url=footer_icn)
            em.set_thumbnail(url=thumbnail)
            await ctx.respond(embed = em, ephemeral = True)
            return
        
        await ctx.channel.purge(limit=amount)

        em = E(
            title="<:3857check:1230570958771982468> | Success",
            description=f"Deleted {amount} messages",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await ctx.respond(embed = em, ephemeral = True)

        transcript = await chat_exporter.export(ctx.channel, limit=amount)

        file = discord.File(io.BytesIO(transcript.encode()), filename=f"purge-transcript-{ctx.channel.id}.html")


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
            title="<:4928applicationbot:1230570127200882779> | Purge",
            description=f"**{ctx.author.mention}** deleted {amount} messages in {ctx.channel.mention}",
            color=color
        )
        em.set_footer(text=footer, icon_url=footer_icn)
        em.set_thumbnail(url=thumbnail)
        await log_channel.send(embed=em, file=file)
        await db.close()
        return
    
def setup(bot):
    bot.add_cog(purge(bot))
    


