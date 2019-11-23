import json
import time

from . import filters
from . import objects
from . import exceptions


class Player:

    def __init__(self, bot, guild_id, node):

        self.bot = bot
        self.node = node

        self.guild_id = guild_id
        self.channel_id = None

        self.last_update = None
        self.last_position = None
        self.last_state = None
        self.position_timestamp = None

        self.voice_state = {}

        self.volume = 100
        self.paused = False
        self.current = None
        self.filters = None

    @property
    def is_connected(self):
        return self.channel_id is not None

    @property
    def is_playing(self):
        return self.is_connected and self.current is not None

    @property
    def position(self):

        if not self.is_playing:
            return 0

        if not self.current:
            return 0

        if self.paused:
            return min(self.last_position, self.current.length)

        difference = time.time() * 1000 - self.last_update
        return min(self.last_position + difference, self.current.length)

    async def update_state(self, state):

        self.last_state = state

        self.last_update = time.time() * 1000

        self.last_position = state.get("position", 0)
        self.position_timestamp = state.get("time", 0)
        self.filters = state.get("filters", None)

    async def voice_server_update(self, data):

        self.voice_state.update({"event": data})

        if {"sessionId", "event"} == self.voice_state.keys():
            await self.node.send(op="voice-server-update", guildId=str(self.guild_id), **self.voice_state)

    async def voice_state_update(self, data):

        self.voice_state.update({"sessionId": data["session_id"]})

        if data['channel_id'] is None:
            self.channel_id = None
            self.voice_state.clear()
        else:
            self.channel_id = int(data["channel_id"])

        if {"sessionId", "event"} == self.voice_state.keys():
            await self.node.send(op="voice-server-update", guildId=str(self.guild_id), **self.voice_state)

    async def connect(self, channel_id: int):

        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            raise ValueError(f"Invalid guild id {self.guild_id}")

        self.channel_id = channel_id

        ws = self.bot._connection._get_websocket(guild.id)
        await ws.voice_state(self.guild_id, str(channel_id))

    async def disconnect(self):

        ws = self.bot._connection._get_websocket(self.guild_id)
        await ws.voice_state(self.guild_id, None)

    async def play(self, track, position=0):

        self.last_update = 0
        self.last_position = 0
        self.position_timestamp = 0

        self.current = track

        await self.node.send(op="play", guildId=str(self.guild_id), track=track.track, start=position)

    async def set_pause(self, pause: bool):

        if pause is self.paused:
            return

        await self.node.send(op="pause", guildId=str(self.guild_id), pause=pause)
        self.paused = pause

    async def set_volume(self, volume):

        await self.node.send(op="volume", volume=volume, guildId=str(self.guild_id))
        self.volume = volume

    async def seek(self, position: int):

        if not 0 <= position <= self.current.length:
            raise ValueError("Position cannot be smaller than 0 or larger than track's length")

        await self.node.send(op="seek", guildId=str(self.guild_id), position=position)

    async def stop(self):
        await self.node.send(op="stop", guildId=str(self.guild_id))
        self.current = None

    async def destroy(self):
        await self.stop()
        await self.disconnect()
        await self.node.send(op="destroy", guildId=str(self.guild_id))
        del self.node.players[self.guild_id]

    async def get_tracks(self, query: str):

        async with self.node.client.session.get(f"{self.node.rest_uri}/loadtracks", params=dict(identifier=query), headers={"Authorization": self.node.password}) as response:
            data = await response.json()

        if data["loadType"] == "NO_MATCHES":
            return None

        elif data["loadType"] == "TRACK_LOADED":
            return objects.Track(track=data["tracks"][0]["track"], data=data["tracks"][0]["info"])

        elif data['loadType'] == 'PLAYLIST_LOADED':
            return objects.Playlist(data=data)

        elif data['loadType'] == 'SEARCH_RESULT':
            tracks = [objects.Track(track=track["track"], data=track["info"]) for track in data["tracks"]]
            return tracks

        else:
            raise exceptions.TrackLoadError(f"There was an error or severity '{data['severity']}' while loading tracks.\n\n{data['cause']}")

    async def set_filters(self, filter_type):

        if not issubclass(filter_type.__class__, filters.Filter):
            raise TypeError("All filters must derive from `Filter`")

        await self.node.send(json.dumps({'op': 'filters', 'guildId': str(self.guild_id)}, **filter_type.payload))
        return filter_type

    async def set_timescale(self, *, speed: float = 1, pitch: float = 1, rate: float = 1):

        timescale = filters.Timescale(speed=speed, pitch=pitch, rate=rate)
        return await self.set_filters(timescale)

    async def set_karaoke(self, *, level: float = 1, mono_level: float = 1, filter_band: float = 220, filter_width: float = 100):

        karaoke = filters.Karaoke(level=level, mono_level=mono_level, filter_band=filter_band, filter_width=filter_width)
        return await self.set_filters(karaoke)

    async def set_tremolo(self, *, frequency: float = 2, depth: float = 0.5):

        tremolo = filters.Tremolo(frequency=frequency, depth=depth)
        return await self.set_filters(tremolo)

    async def set_vibrato(self, frequency: float = 2, depth: float = 0.5):

        vibrato = filters.Vibrato(frequency=frequency, depth=depth)
        return await self.set_filters(vibrato)
