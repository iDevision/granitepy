import time

import discord

from . import exceptions
from . import filters
from . import objects
from .node import Node


class Player:
    """
    Main interface for playing a track in a guild.

    Attributes
    ----------
    node: :class:`.Node`
        The Node this Player is connected to.
    guild: :class:`discord.Guild`
        The Discord Guild this Player is connected to.
    bot: Union[:class:`discord.ext.commands.Bot`, :class:`discord.ext.commands.AutoShardedBot`]
        The Bot instance that granitepy is using.
    voice_channel: :class:`discord.VoiceChannel`
        The Voice Channel that this Player is currently connected to. Will be None if the Player is not connected to a channel.
    volume: :class:`int`
        The current volume of the player.
    paused: :class:`bool`
        Whether or not the player is paused.
    filters: :class:`dict`
        A dict of the currently set filters.
    current: :class:`.Track`
        The track that is currently playing. Can be None if nothing is playing.
    """

    def __init__(self, node: Node, guild: discord.Guild, **kwargs):

        self.node = node
        self.guild = guild
        self.bot = self.node.bot

        self.voice_channel = None

        self.volume = 100
        self.paused = False
        self.filters = None
        self.current = None

        self.voice_state = {}
        self.player_state = {}
        self.last_position = 0
        self.last_update = 0
        self.time = 0

    def __repr__(self):
        return f"<GranitePlayer is_connected={self.is_connected} is_playing={self.is_playing}>"

    @property
    def position(self):
        """:class:`float`: The current position of the player in milliseconds. Will be 0 if no track is currently playing."""

        if not self.is_playing:
            return 0

        if self.paused:
            return min(self.last_position, self.current.length)

        difference = (time.time() * 1000) - self.last_update
        return min(self.last_position + difference, self.current.length)

    @property
    def is_connected(self):
        """:class:`bool`: Whether or not the Player is connected to a Voice Channel."""
        return self.voice_channel is not None

    @property
    def is_playing(self):
        """:class:`bool`: Whether or not the Player is connected to a Voice Channel and playing a Track."""
        return self.is_connected and self.current is not None

    @property
    def is_paused(self):
        """:class:`bool`: Whether or not the Player is currently paused."""
        return self.is_connected and self.paused is True

    async def update_state(self, state: dict):

        self.player_state = state

        self.last_update = time.time() * 1000
        self.last_position = state.get("position", 0)
        self.time = state.get("time", 0)
        self.volume = state.get("volume", 100)
        self.paused = state.get("paused", False)
        self.filters = state.get("filters", self.filters)

    async def voice_server_update(self, data: dict):

        self.voice_state.update({"event": data})

        if {"sessionId", "event"} == self.voice_state.keys():
            await self.node.send(op="voice-server-update", guildId=str(self.guild.id), **self.voice_state)

    async def voice_state_update(self, data: dict):

        self.voice_state.update({"sessionId": data["session_id"]})

        if data['channel_id'] is None:
            self.voice_channel = None
            self.voice_state.clear()
        else:
            self.voice_channel = self.bot.get_channel(int(data["channel_id"]))

        if {"sessionId", "event"} == self.voice_state.keys():
            await self.node.send(op="voice-server-update", guildId=str(self.guild.id), **self.voice_state)

    async def get_tracks(self, query: str):
        """|coro|

        Shortcut for :meth:`Node.get_tracks`

        Parameters
        ----------
        query: :class:`str`
            The search to preform. Can be a link or a general search term.

        Returns
        -------
        Union[:class:`list` [:class:`.Track`], :class:`.Playlist`]
            Either a list of Tracks or a Playlist.
        """

        return await self.node.get_tracks(query)

    async def connect(self, voice_channel: discord.VoiceChannel):
        """|coro|

        Connects the Bot to the given Voice Channel.

        Parameters
        ----------
        voice_channel: :class:`discord.VoiceChannel`
            The discord Voice Channel to connect to.
        """

        self.voice_channel = voice_channel

        # noinspection PyProtectedMember
        ws = self.bot._connection._get_websocket(self.guild.id)
        await ws.voice_state(self.guild.id, str(voice_channel.id))

    async def stop(self):
        """|coro|

        Stops the current Track.
        """

        self.current = None

        await self.node.send(op="stop", guildId=str(self.guild.id))

    async def disconnect(self):
        """|coro|

        Stop the current Track and disconnects from the Voice Channel.
        """

        await self.stop()
        self.voice_channel = None

        # noinspection PyProtectedMember
        ws = self.bot._connection._get_websocket(self.guild.id)
        await ws.voice_state(self.guild.id, None)

    async def destroy(self):
        """|coro|

        Destroys the Player and removes it from the Node.
        """

        del self.node.players[self.guild.id]

        await self.disconnect()
        await self.node.send(op="destroy", guildId=str(self.guild.id))

    async def play(self, track: objects.Track, start_position: int = 0):
        """|coro|

        Plays the given Track.

        Parameters
        ----------
        track: :class:`.Track`
            The Track to play.
        start_position: :class:`float`
            The position to start the Track at.

        Returns
        -------
        :class:`.Track`
            The Track that is now being played.
        """

        await self.node.send(op="play",
                             guildId=str(self.guild.id),
                             track=track.track_id,
                             start=start_position)

        self.current = track
        return self.current

    async def seek(self, position: int):
        """|coro|

        Sets the Players position.

        Parameters
        ----------
        position: :class:`int`
            The time in milliseconds to set the position to.

        Returns
        -------
        :class:`int`
            The Players new position.
        """

        if position < 0 or position > self.current.length:
            raise exceptions.TrackInvalidPosition(f"Seek position must be between 0 and the track length")

        await self.node.send(op="seek",
                             guildId=str(self.guild.id),
                             position=position)

        return self.position

    async def set_pause(self, pause: bool):
        """|coro|

        Pause or un-pause the Player.

        Parameters
        ----------
        pause: :class:`bool`
            Whether or not the Player should be paused.

        Returns
        -------
        :class:`bool`
            Whether or not the Player is paused.
        """

        await self.node.send(op="pause", guildId=str(self.guild.id), pause=pause)

        self.paused = pause
        return self.is_paused

    async def set_volume(self, volume: int):
        """|coro|

        Sets the Players volume.

        Parameters
        ----------
        volume: :class:`int`
            The volume to set the Player too. Can be any number but levels above 200 distort the sound.

        Returns
        -------
        :class:`int`
            The Players new volume.
        """

        await self.node.send(op="volume",
                             guildId=str(self.guild.id),
                             volume=volume)

        self.volume = volume
        return self.volume

    async def set_filter(self, filter_type: filters.Filter):
        """|coro|

        Adds a Filter to the Player.

        Parameters
        ----------
        filter_type: :class:`.Filter`
            A subclass of :class:`.Filter` to add to the Player.

        Returns
        -------
        :class:`.Filter`
            The Filter that was added to the Player.
        """

        await self.node.send(op="filters", **filter_type.payload, guildId=str(self.guild.id))
        return filter_type

    async def set_timescale(self, *, speed: float = 1, pitch: float = 1, rate: float = 1):
        """|coro|

        Sets a Timescale Filter on the Player.

        Parameters
        ----------
        speed: Optional[:class:`float`]
            The filter's speed.
        pitch: Optional[:class:`float`]
            The filter's pitch.
        rate: Optional[:class:`float`]
            The filter's rate.

        Returns
        -------
        :class:`.Timescale`
            The Timescale Filter that was added to the Player
        """

        return await self.set_filter(filters.Timescale(speed=speed, pitch=pitch, rate=rate))

    async def set_karaoke(self, *, level: float = 1, mono_level: float = 1, filter_band: float = 220, filter_width: float = 100):
        """|coro|

        Sets a Karaoke Filter on the Player.

        Parameters
        ----------
        level: Optional[:class:`float`]
            The filter's level.
        mono_level: Optional[:class:`float`]
            The filter's mono level.
        filter_band: Optional[:class:`float`]
            The filter's band.
        filter_width: Optional[:class:`float`]
            The filter's width.

        Returns
        -------
        :class:`.Karaoke`
            The Karaoke Filter that was added to the Player
        """
        return await self.set_filter(filters.Karaoke(level=level, mono_level=mono_level, filter_band=filter_band, filter_width=filter_width))

    async def set_tremolo(self, *, frequency: float = 2, depth: float = 0.5):
        """|coro|

        Sets a Tremolo Filter on the Player.

        Parameters
        ----------
        frequency: Optional[:class:`float`]
            The filter's frequency.
        depth: Optional[:class:`float`]
            The filter's depth.

        Returns
        -------
        :class:`.Tremolo`
            The Tremolo Filter that was added to the Player
        """
        return await self.set_filter(filters.Tremolo(frequency=frequency, depth=depth))

    async def set_vibrato(self, frequency: float = 2, depth: float = 0.5):
        """|coro|

        Sets a Vibrato Filter on the Player.

        Parameters
        ----------
        frequency: Optional[:class:`float`]
            The filter's frequency.
        depth: Optional[:class:`float`]
            The filter's depth.

        Returns
        -------
        :class:`.Vibrato`
            The Vibrato Filter that was added to the Player
        """
        return await self.set_filter(filters.Vibrato(frequency=frequency, depth=depth))
