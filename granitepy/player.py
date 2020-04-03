import time
import typing

import discord

from . import objects
from . import filters
from . import exceptions
from .node import Node


class Player:

    def __init__(self, bot, node: Node, guild: discord.Guild):

        self.bot = bot
        self.node = node
        self.guild = guild
        self.voice_channel = None
        self.text_channel = None

        self.voice_state = {}
        self.player_state = {}

        self.last_position = 0
        self.last_update = 0
        self.time = 0
        self.volume = 100
        self.paused = False
        self.filters = None

        self.current = None

    def __repr__(self):
        return f"<GranitePlayer is_connected={self.is_connected} is_playing={self.is_playing}>"

    @property
    def position(self):

        if self.current is None:
            return 0

        difference = (time.time() * 1000) - self.last_update
        return self.last_position + difference

    @property
    def is_connected(self):
        return self.voice_channel is not None

    @property
    def is_playing(self):
        return self.is_connected and self.current is not None

    @property
    def is_paused(self):
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

        return await self.node.get_tracks(query)

    async def connect(self, voice_channel: discord.VoiceChannel):

        self.voice_channel = voice_channel

        ws = self.bot._connection._get_websocket(self.guild.id)
        await ws.voice_state(self.guild.id, str(voice_channel.id))

    async def stop(self):

        self.current = None

        await self.node.send(op="stop", guildId=str(self.guild.id))

    async def disconnect(self):

        await self.stop()
        self.voice_channel = None

        ws = self.bot._connection._get_websocket(self.guild.id)
        await ws.voice_state(self.guild.id, None)

    async def destroy(self):

        del self.node.players[self.guild.id]

        await self.disconnect()
        await self.node.send(op="destroy", guildId=str(self.guild.id))

    async def play(self, track: objects.Track, start_position: int = 0):

        await self.node.send(op="play",
                             guildId=str(self.guild.id),
                             track=track.track_id,
                             start=start_position)

        self.current = track
        return self.current

    async def seek(self, position: int):

        if position < 0 or position > self.current.length:
            raise exceptions.TrackInvalidPosition(f"Seek position must be between 0 and the track length")

        await self.node.send(op="seek",
                             guildId=str(self.guild.id),
                             position=position)

        return self.position

    async def set_pause(self, pause: bool):

        await self.node.send(op="pause", guildId=str(self.guild.id), pause=pause)

        self.paused = pause
        return self.is_paused

    async def set_volume(self, volume: typing.Union[int, float]):

        await self.node.send(op="volume",
                             guildId=str(self.guild.id),
                             volume=volume)

        self.volume = volume
        return self.volume

    async def set_filter(self, filter_type: filters.Filter):

        await self.node.send(op="filters", **filter_type.payload, guildId=str(self.guild.id))
        return filter_type

    async def set_timescale(self, *, speed: float = 1, pitch: float = 1, rate: float = 1):
        return await self.set_filter(filters.Timescale(speed=speed, pitch=pitch, rate=rate))

    async def set_karaoke(self, *, level: float = 1, mono_level: float = 1, filter_band: float = 220, filter_width: float = 100):
        return await self.set_filter(filters.Karaoke(level=level, mono_level=mono_level, filter_band=filter_band, filter_width=filter_width))

    async def set_tremolo(self, *, frequency: float = 2, depth: float = 0.5):
        return await self.set_filter(filters.Tremolo(frequency=frequency, depth=depth))

    async def set_vibrato(self, frequency: float = 2, depth: float = 0.5):
        return await self.set_filter(filters.Vibrato(frequency=frequency, depth=depth))
