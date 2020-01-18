import typing

import discord

from . import exceptions
from . import filters
from . import objects
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

        self.volume = 100
        self.paused = False
        self.current = None
        self.filters = None

    @property
    def position(self):

        if self.current is None:
            return 1
        else:
            return self.player_state.get("position", 1)

    @property
    def is_connected(self):
        return self.voice_channel is not None

    @property
    def is_playing(self):
        return self.is_connected and self.current is not None

    @property
    def is_paused(self):
        return self.is_playing and self.paused is not None

    async def update_state(self, state: dict):

        self.player_state = state
        self.time = state.get("time", 0)
        self.filters = state.get("filters")

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

        async with self.node.client.session.get(url=f"{self.node.rest_uri}/loadtracks",
                                                params=dict(identifier=query),
                                                headers={"Authorization": self.node.password}) as response:
            data = await response.json()

        if data["loadType"] == "LOAD_FAILED":
            raise exceptions.TrackLoadError(f"There was an error of severity '{data['severity']}' while loading tracks.\n\n{data['cause']}")

        elif data["loadType"] == "NO_MATCHES":
            return None

        elif data["loadType"] == "PLAYLIST_LOADED":
            return objects.Playlist(data=data)

        elif data["loadType"] == "SEARCH_RESULT":
            return [objects.Track(track_id=track["track"], data=track["info"]) for track in data["tracks"]]

        elif data["loadType"] == "TRACK_LOADED":
            return objects.Track(track_id=data["tracks"][0]["track"], data=data["tracks"][0]["info"])

    async def connect(self, voice_channel: discord.VoiceChannel):

        self.voice_channel = voice_channel

        ws = self.bot._connection._get_websocket(self.guild.id)
        await ws.voice_state(self.guild.id, str(voice_channel.id))

    async def disconnect(self):

        await self.stop()

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

    async def stop(self):
        await self.node.send(op="stop", guildId=str(self.guild.id))

    async def seek(self, position: int):

        if not 0 <= position <= self.current.length:
            raise ValueError("Position cannot be smaller than 0 or larger than track's length")

        await self.node.send(op="seek",
                             guildId=str(self.guild.id),
                             position=position)

        self.current.position = position
        return self.position

    async def set_pause(self, pause: bool):

        if self.is_paused:
            return

        await self.node.send(op="pause",
                             guildId=str(self.guild.id),
                             pause=pause)

        self.paused = pause
        return self.paused

    async def set_volume(self, volume: typing.Union[int, float]):

        await self.node.send(op="volume",
                             guildId=str(self.guild.id),
                             volume=volume)

        self.volume = volume
        return self.volume



    async def set_filters(self, filter_type: filters.Filter):

        await self.node.send(op="filters", **filter_type.payload, guildId=str(self.guild_id))
        return filter_type

    async def set_timescale(self, *, speed: float = 1, pitch: float = 1, rate: float = 1):
        return await self.set_filters(filters.Timescale(speed=speed, pitch=pitch, rate=rate))

    async def set_karaoke(self, *, level: float = 1, mono_level: float = 1, filter_band: float = 220, filter_width: float = 100):
        return await self.set_filters(filters.Karaoke(level=level, mono_level=mono_level, filter_band=filter_band, filter_width=filter_width))

    async def set_tremolo(self, *, frequency: float = 2, depth: float = 0.5):
        return await self.set_filters(filters.Tremolo(frequency=frequency, depth=depth))

    async def set_vibrato(self, frequency: float = 2, depth: float = 0.5):
        return await self.set_filters(filters.Vibrato(frequency=frequency, depth=depth))
