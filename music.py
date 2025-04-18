from time import thread_time
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import logging
##from lyricsgenius import Genius
##import os

# Warteschlangen für die Songs
queueList = {}
titleList = {}
durationList = {}

# Logging Setup
logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log',
                    encoding='utf-8',
                    level=logging.DEBUG)

# Genius API Setup
##secret = os.environ['GENIUS_ACCESS_TOKEN']
##genius = Genius(secret)

# FFmpeg and YDL Options
FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
YDL_OPTIONS = {'format': "bestaudio"}


class music(commands.Cog):

  def __init__(self, client):
    self.client = client

    @client.command(name="join",
                    aliases=["j", "Join"],
                    help='Lets me join the channel')
    async def join(ctx):
      if ctx.author.voice is None:
        await ctx.send("You must be in a channel to listen to music")
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await ctx.voice_client.move_to(voice_channel)

    @client.command(name="leave",
                    aliases=["l", "Leave", "quit", "Quit"],
                    help='Leave channel')
    async def leave(ctx):
      await ctx.voice_client.disconnect()
      # Lösche die Warteschlange für diese Guild
      try:
        clearQ(ctx)
      except KeyError:
        pass

    @client.command(name="play",
                    aliases=["p", "Play"],
                    help='Starts the Song "!play [Link]"')
    async def play(ctx, url):
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await ctx.voice_client.move_to(voice_channel)

      ctx.voice_client.stop()
      await player(ctx, url, None, None, None)

    @client.command(name="queue",
                    aliases=["q", "Queue", "next", "Next"],
                    help='Puts a Song into the Queue "!queue [Link]"')
    async def queue(ctx, url):
      if ctx.author.voice is None:
        await ctx.send("You must be in a channel to edit the queue")
      else:
        # Prüfe, ob es sich um eine URL handelt (einfache Validierung)
        if not url.startswith(("http://", "https://", "www.")):
          # Suchanfrage statt direkter URL
          await add_queue(ctx, None, url)
        else:
          # Direkter Link
          await add_queue(ctx, url, None)

    @client.command(name="listQueue",
                    aliases=["lq", "ListQueue", "List", "list"],
                    help='Lists the songs in the queue')
    async def listQueue(ctx):
      await ctx.reply(
          f"In der Queue befinden sich im Moment: \n {titleList[ctx.guild.id]}",
          mention_author=False)

    @client.command(name="lofi",
                    aliases=["chill", "Lofi"],
                    help='Play lofi music')
    async def lofi(ctx):
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await ctx.voice_client.move_to(voice_channel)
      url = "https://www.youtube.com/watch?v=jfKfPfyJRdk"
      await player(ctx, url, None, None, None)

    @client.command(name="karaoke",
                    help='Search for any song you want to sing karaoke')
    async def karaoke(ctx, *, search_term):
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await ctx.voice_client.move_to(voice_channel)
      yt_query = f"{search_term} Karaoke"
      # Suche nach dem Song auf Genius
      ##gn_query = f"{search_term}"
      ##song = genius.search_song(gn_query)
      # Sende die Lyrics als Nachricht
      ##if song:
      ## lyrics = song.lyrics[:2000]  # Begrenzung auf 2000 Zeichen
      await player(ctx, None, None, None, yt_query)

    @client.command(name="search", help='Search for any song you want')
    async def search_song(ctx, *, search_term):
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await ctx.voice_client.move_to(voice_channel)
      yt_query = f"{search_term}"
      vc = ctx.voice_client
      if vc.is_playing():
        await add_queue(ctx, None, yt_query)
      else:
        await player(ctx, None, None, None, yt_query)

    @client.command(name="pause",
                    aliases=["ps", "Pause"],
                    help='Pauses the current Song')
    async def pause(ctx):
      ctx.voice_client.pause()
      await ctx.reply("Song paused⏸️", mention_author=False)

    @client.command(name="resume",
                    aliases=["r", "Resume"],
                    help='Continues the Song')
    async def resume(ctx):
      ctx.voice_client.resume()
      await ctx.reply("It continues⏩", mention_author=False)

    @client.command(name="skip",
                    aliases=["s", "Skip"],
                    help='Skips to the next song')
    async def skip(ctx):
      vc = ctx.voice_client
      if vc.is_playing():
        vc.stop()
        # Warte kurz, damit der Voice-Client den Stop verarbeitet
        await asyncio.sleep(0.1)
      # Starte den nächsten Song thread-sicher
      await play_next(ctx)

    @client.command(name="stop",
                    aliases=["stp", "Stop"],
                    help='Stops the current Song')
    async def stop(ctx):
      vc = ctx.voice_client
      if vc.is_playing():
        vc.stop()

    @client.command(name="clearQueue",
                    aliases=["cl", "ClearQueue", "clear", "Clear"],
                    help='Cleans up the queue')
    async def clearQueue(ctx):
      clearQ(ctx)


def setup(client):
  client.add_cog(music(client))


def convert(seconds):
  if seconds < 3600:  # Wenn die Zeit weniger als eine Stunde beträgt
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)
  else:  # Wenn die Zeit eine Stunde oder mehr beträgt
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


async def play_next(ctx):
  if len(queueList[ctx.guild.id]) > 0:
    url, title, duration = getQueue(ctx)
    await player(ctx, url, title, duration, None)


def getQueue(ctx):
  url = queueList[ctx.guild.id][0]
  title = titleList[ctx.guild.id][0]
  duration = durationList[ctx.guild.id][0]
  del (queueList[ctx.guild.id][0])
  del (titleList[ctx.guild.id][0])
  del (durationList[ctx.guild.id][0])
  return url, title, duration


def clearQ(ctx):
  del (queueList[ctx.guild.id])
  del (titleList[ctx.guild.id])
  del (durationList[ctx.guild.id])


async def player(ctx, url, title, duration, search):
  vc = ctx.voice_client
  with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
    if search:
      info = ydl.extract_info(f"ytsearch:{search}",download=False)['entries'][0]
    elif url:
      info = ydl.extract_info(url, download=False)
    url2 = info['url']
    # Überprüfe, ob der Titel vorhanden ist, bevor du ihn verwendest
    if title:
      titleInfo = title
    elif title is None:
      titleInfo = info['title']
    # Überprüfe, ob die Dauer vorhanden ist, bevor du sie verwendest
    logger.debug(f"Sekunden des aktuellen Songs {duration}")
    if duration is None:
      duration = convert(info.get('duration'))
    elif duration is not None:
      duration = convert(duration)
    if duration is not None:
      logger.debug(f"Sekunden des aktuellen Songs vor Convert {duration}")
      await ctx.reply(f"🎶Wird gespielt🎶\n**{titleInfo}**  ({duration}))",
                      mention_author=False)
    else:
      await ctx.reply(f"🎶Wird gespielt🎶\n**{titleInfo}**",
                      mention_author=False)
    source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
    discord.opus.load_opus('opus/libopus.so')
    if not discord.opus.is_loaded():
      raise RuntimeError('Opus failed to load')
    vc.play(source,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                play_next(ctx), ctx.bot.loop).result())


async def add_queue(ctx, url, search):
  # Stelle sicher, dass die Warteschlange für die Guild existiert
  if ctx.guild.id not in queueList:
    queueList[ctx.guild.id] = []
    titleList[ctx.guild.id] = []
    durationList[ctx.guild.id] = []

  if search:
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      # Extrahiere Song-Daten aus der Suchanfrage
      info = ydl.extract_info(f"ytsearch:{search}",
                              download=False)['entries'][0]
      url = info['url']  # Verwende direkt die URL aus der Suche
      title = info['title']
      duration = info.get('duration')
    queueList[ctx.guild.id].append(url)
    titleList[ctx.guild.id].append(title)
    durationList[ctx.guild.id].append(info.get('duration'))

  elif url:
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      # Extrahiere Song-Daten aus dem direkten Link
      info = ydl.extract_info(url, download=False)
      title = info['title']
      duration = info.get('duration')
    queueList[ctx.guild.id].append(url)
    titleList[ctx.guild.id].append(title)
    durationList[ctx.guild.id].append(info.get('duration'))

  if duration is not None:
    duration = convert(info['duration'])
    await ctx.reply(
        f"**{title}** ({duration}) zur Warteschlange hinzugefügt 🎶",
        mention_author=False)
  else:
    await ctx.reply(f"**{title}** zur Warteschlange hinzugefügt 🎶",
                    mention_author=False)
