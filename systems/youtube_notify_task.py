import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option
import aiosqlite
import scrapetube
import yaml
import asyncio


class youtube_notify_task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vids = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_youtube.start()


    @tasks.loop(seconds=5)
    async def check_youtube(self):

        with open("data/config.yaml", "r") as f:
            data = yaml.safe_load(f)

        color = data['embed']['color']
        footer = data['embed']['footer']
        thumbnail = data['embed']['thumbnail']
        footer_icn = data['embed']['footer_icn']

        yt_channels = data['youtube']

        db = await aiosqlite.connect('data/vc_settings.db')

        E = discord.Embed

        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM yt_settings")
            data = await cursor.fetchall()

        for row in data:
            guild = self.bot.get_guild(row[0])
            channel = guild.get_channel(row[1])
            role = guild.get_role(row[3])
            text = row[2]

            if channel is None:
                await db.close()
                return
            
            for yt_channel in yt_channels:
                videos = scrapetube.get_channel(channel_url=yt_channels[yt_channel], limit=5)
     
                video_ids = [video['videoId'] for video in videos]

                if self.check_youtube.current_loop == 0:
                    self.vids[yt_channel] = video_ids
                    print("first loop")
                    continue

                for video_id in video_ids:
                    if video_id not in self.vids[yt_channel]:
                        url = f"https://youtu.be/{video_id}"
                        thumbnail = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"


                        if role is not None:
                            em = E(
                                title="<:Youtube:1237027961530613801> | new video",
                                description=f"**{text}**\n\n[**Click here to watch**]({url})",
                                color=color
                            )
                            em.set_footer(text=footer, icon_url=footer_icn)
                            em.set_image(url=thumbnail)
                            await channel.send(role.mention, embed=em)

                        else:
                            em = E(
                                title="<:Youtube:1237027961530613801> | new video",
                                description=f"**{text}**\n\n[**Click here to watch**]({url})",
                                color=color
                            )
                            em.set_footer(text=footer, icon_url=footer_icn)
                            em.set_image(url=thumbnail)
                            await channel.send(embed=em)

                        self.vids[yt_channel] = video_ids





def setup(bot):
    bot.add_cog(youtube_notify_task(bot))