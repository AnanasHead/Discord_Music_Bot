import discord
from discord.ext import commands
import youtube_dl

class music(commands.Cog):
    def __init__(self, client):
        self.client = client

        @client.command(name="join")
        async def join(ctx):
            if ctx.author.voice is None:
                await ctx.send("Du musst in einem Channel sein um Music zu hören")
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)

        @client.command(name="leave")
        async def leave(ctx):
            await ctx.voice_client.disconnect()

        @client.command(name="play")
        async def play(ctx, url):
            ctx.voice_client.stop()
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            YDL_OPTIONS = {'format':"bestaudio"}
            vc = ctx.voice_client

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                titleInfo = info['title']
                duration = convert(info['duration'])
                source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS, executable="C:\\ffmpeg\\bin\\ffmpeg.exe")
                await ctx.reply(f"🎶Wird gespielt🎶\n**{titleInfo}** ({duration})", mention_author=False)
                vc.play(source)

        @client.command(name="pause")
        async def pause(ctx):
            ctx.voice_client.pause()
            await ctx.reply("Wiedergabe gestoppt⏸️", mention_author=False)

        @client.command(name="resume")
        async def resume(ctx):
            ctx.voice_client.resume()
            await ctx.reply("Es geht weiter⏩", mention_author=False)

def setup(client):
    client.add_cog(music(client))

def convert(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)