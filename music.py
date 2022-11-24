import discord
from discord.ext import commands
import youtube_dl

queueList = {}
titleList = {}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format':"bestaudio"}
class music(commands.Cog):
    def __init__(self, client):
        self.client = client

        @client.command(name="join", aliases = ["j", "Join"], help='Lets me join the channel')
        async def join(ctx):
            if ctx.author.voice is None:
                await ctx.send("You must be in a channel to listen to music")
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)

        @client.command(name="leave", aliases = ["l", "Leave", "quit", "Quit"], help='Leave channel')
        async def leave(ctx):
            await ctx.voice_client.disconnect()

        @client.command(name="play", aliases = ["p", "Play"], help='Starts the Song "!play [Link]"')
        async def play(ctx, url):
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)
                
            ctx.voice_client.stop()
            vc = ctx.voice_client
   
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                titleInfo = info['title']
                duration = convert(info['duration'])
                source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
                await ctx.reply(f"🎶Wird gespielt🎶\n**{titleInfo}** ({duration})", mention_author=False)
                vc.play(source, after=lambda e: play_next(ctx))

        @client.command(name="queue", aliases = ["q", "Queue", "next", "Next"], help='Puts a Song into the Queue "!queue [Link]"')
        async def queue(ctx, url):
            if ctx.author.voice is None:
                await ctx.send("You must be in a channel to edit the queue")
            else:
                try:
                    queueList[ctx.guild.id].append(url)
                except:
                    queueList[ctx.guild.id] = [url]
                YDL_OPTIONS = {'format':"bestaudio"}
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    titleInfo = info['title']
                    duration = convert(info['duration'])
                try:
                    titleList[ctx.guild.id].append(titleInfo)
                except:
                    titleList[ctx.guild.id] = [titleInfo]
                await ctx.reply(f"Added **{titleInfo}** ({duration}) to the Queue", mention_author=False)

        @client.command(name="listQueue", aliases = ["lq", "ListQueue", "List", "list"], help='Lists the songs in the queue')
        async def listQueue(ctx):
            await ctx.reply(f"In der Queue befinden sich im Moment: \n {titleList[ctx.guild.id]}", mention_author=False)        

        @client.command(name="pause", aliases = ["ps", "Pause"], help='Pauses the current Song')
        async def pause(ctx):
            ctx.voice_client.pause()
            await ctx.reply("Song paused⏸️", mention_author=False)

        @client.command(name="resume", aliases = ["r", "Resume"], help='Continues the Song')
        async def resume(ctx):
            ctx.voice_client.resume()
            await ctx.reply("It continues⏩", mention_author=False)

        @client.command(name="skip", aliases = ["s", "Skip"], help='Skips to the next song')
        async def skip(ctx):
            ctx.voice_client.stop()
            play_next(ctx)

        @client.command(name="clearQueue", aliases = ["cl", "ClearQueue", "clear", "Clear"], help='Cleans up the queue')
        async def clearQueue(ctx):
            clearQ(ctx)

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
    if len(queueList[ctx.guild.id]) > 0:
        url = getQueue(ctx)
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            currentTrack = info['title']
            url2 = info['formats'][0]['url']
            source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            vc.play(source, after=lambda e: play_next(ctx))

def getQueue(ctx):
    url = queueList[ctx.guild.id][0]
    del(queueList[ctx.guild.id][0])
    del(titleList[ctx.guild.id][0])
    return url

def clearQ(ctx):
     del(queueList[ctx.guild.id])
     del(titleList[ctx.guild.id])