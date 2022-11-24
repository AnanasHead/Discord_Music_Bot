import discord
from discord.ext import commands
import music

cogs = [music]

client = discord.ext.commands.Bot(command_prefix='!', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord. Activity(type=discord.ActivityType.listening, name='!help'))

## Real Bot
##client.run("MTA0MzkyNjc5NzgzMTY0MzE3OQ.GprBtv.HtwT4bRfaFo6v6mAeta6JPStNZIR_nj2hALKgY")

## Test Bot
client.run("MTA0NTM3MDAzOTg2MTI0ODEwMA.GuRXOD.Z_2emtHEbqj8lbXjHzWM651MB1MXuBLVgPoejs")