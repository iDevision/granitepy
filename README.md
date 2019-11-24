# granitepy
granitepy is a library for the [Lavalink](https://github.com/Frederikam/Lavalink) like audio provider called 
[Andesite](https://github.com/natanbc/andesite-node) for use with [discord.py](https://github.com/Rapptz/discord.py).

## Links
* [Discord supprt server](https://discord.gg/8a2a486)
* Documentation (Coming soon)

# Example
```python
from discord.ext import commands

import andesite

bot = commands.Bot(command_prefix = "!")
bot.andesite = andesite.Client(bot)

@bot.event
async def on_ready():
    await bot.andesite.create_node(
            host="127.0.0.1",
            port=5000,
            rest_uri = "http://127.0.0.1:5000/",
            password = "Some-random-password",
            identifier = "hello-there"
    )

@bot.command()
async def connect(ctx):
    player = bot.andesite.get_player(ctx.guild.id) # Creates or fetches a player

    if not ctx.author.voice:
        return await ctx.send("Must be connected to a voice channel")
    
    await player.connect(ctx.author.voice.channel.id) # Connects to the channel the command invoker is in.

    await ctx.send(f"Connected to {ctx.author.voice.channel.name}!")

@bot.command()
async def play(ctx, *, search):
    player = bot.andesite.get_player(ctx.guild.id)

    tracks = await player.node.get_tracks(f"ytsearch: {search}") # Returns a list of andesite.Track objects 
    if not tracks: # Andesite returned no tracks.
        return await ctx.send("No tracks were found.")

    await player.play(tracks[0]) # Plays the first track from the list.


bot.run("token")
```
