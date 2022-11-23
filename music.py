import discord
from discord.ext import commands
import youtube_dl

queueList = []
titleList = []
currentTrack = 0

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format':"bestaudio"}
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
            vc = ctx.voice_client
   
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                titleInfo = info['title']
                currentTrack = titleInfo
                duration = convert(info['duration'])
                source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
                await ctx.reply(f"🎶Wird gespielt🎶\n**{titleInfo}** ({duration})", mention_author=False)
                vc.play(source, after=lambda e: play_next(ctx))

        @client.command(name="queue")
        async def queue(ctx, url):
            if ctx.author.voice is None:
                await ctx.send("Du musst in einem Channel sein um die Queue zu bearbeiten")
            else:
                queueList.append(url)
                YDL_OPTIONS = {'format':"bestaudio"}
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    titleInfo = info['title']
                    titleList.append(titleInfo)
                    await ctx.reply(f"**{titleInfo}** der Warteschlange hinzugefügt", mention_author=False)

        @client.command(name="listQueue")
        async def listQueue(ctx):
            await ctx.reply("In der Queue befinden sich im Moment: \n" + '\n'.join(map(str, titleList)), mention_author=False)        

        @client.command(name="pause")
        async def pause(ctx):
            ctx.voice_client.pause()
            await ctx.reply("Wiedergabe gestoppt⏸️", mention_author=False)

        @client.command(name="resume")
        async def resume(ctx):
            ctx.voice_client.resume()
            await ctx.reply("Es geht weiter⏩", mention_author=False)

        @client.command(name="skip")
        async def skip(ctx):
            ctx.voice_client.stop()
            play_next(ctx)

        @client.command(name="stop")
        async def stop(ctx):
            clearQueue()
            await leave(ctx)

def setup(client):
    client.add_cog(music(client))

def convert(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)

def play_next(ctx):
    vc = ctx.voice_client
    if len(queueList) > 0:
        url = getQueue()
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            currentTrack = info['title']
            url2 = info['formats'][0]['url']
            source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS, executable="C:\\ffmpeg\\bin\\ffmpeg.exe")
            vc.play(source, after=lambda e: play_next(ctx))

def getQueue():
    url = queueList.pop(0)
    titleList.pop(0)
    return url

def clearQueue():
    queueList.clear
    titleList.clear