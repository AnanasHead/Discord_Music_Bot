import discord
from discord.ext import commands
from decouple import config
import music

API_KEY = config("API_KEY")
cogs = [music]

client = discord.ext.commands.Bot(command_prefix='!', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord. Activity(type=discord.ActivityType.listening, name='!help'))

## Real Bot
##client.run(API_KEY)

## Test Bot
client.run(API_KEY)