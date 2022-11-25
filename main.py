import discord
from discord.ext import commands
import music
import config

cogs = [music]

client = discord.ext.commands.Bot(command_prefix='!', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord. Activity(type=discord.ActivityType.listening, name='!help'))

## Real Bot
##client.run(config.API_KEY)

## Test Bot
client.run(config.TEST_API_KEY)