.. py:currentmodule:: granitepy


Getting started
===============
A quick and easy example of how to use granitepy.

.. code:: py

    from discord.ext import commands
    import granitepy

    bot = commands.Bot(command_prefix = "!")
    bot.granitepy = granitepy.Client(bot)

    @bot.event
    async def on_ready():
        await bot.granitepy.create_node(
            host="node-ip",
            port=12345,
            password="node-password",
            identifier="node-name",
        )

    @bot.command()
    async def connect(ctx):
        # Create or fetch a player.
        player = bot.granitepy.get_player(ctx=ctx)

        # Check is the author is in a voice channel.
        if not ctx.author.voice:
            return await ctx.send("You must be connected to a voice channel")

        # Connect to the authors voice channel.
        await player.connect(ctx.author.voice.channel)
        return await ctx.send(f"Connected to {ctx.author.voice.channel.name}!")

    @bot.command()
    async def play(ctx, *, search):
        player = bot.granitepy.get_player(ctx=ctx)

        # Search for whatever the user has inputted.
        result = await player.get_tracks(search)

        # The users search returned nothing.
        if not result:
            return await ctx.send("No tracks were found.")

        # Check if the result is a playlist.
        if isinstance(result, granitepy.Playlist):
            # Play the first track in the playlist.
            return await player.play(result.tracks[0])
        else:
            # Play the first track in the list of results.
            return await player.play(results[0])

    bot.run("token")