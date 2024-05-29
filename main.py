import os
import discord
import music
from keep_alive import keep_alive

cogs = [music]
secret = os.environ['DISCORD_API_KEY']

client = discord.ext.commands.Bot(command_prefix='!',
                                  intents=discord.Intents.all())

for i in range(len(cogs)):
  cogs[i].setup(client)

  @client.event
  async def on_ready():
    await client.change_presence(activity=discord.Activity(
      type=discord.ActivityType.listening, name='!help'))


## Real Bot
##client.run(config.API_KEY)

## Test Bot
keep_alive()
client.run(secret)
