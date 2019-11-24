from . import filters
from . import objects
from . import exceptions


class Player:

    def __init__(self, bot, guild_id, node):

        self.bot = bot
        self.node = node

        self.guild_id = guild_id
        self.channel_id = None

        self.voice_state = {}
        self.player_state = {}

        self.volume = 100
        self.paused = False
        self.current = None
        self.filters = None
        self.time = None

        self.mixer_enabled = None
        self.mixer = None

    @property
    def position(self):

        if self.current is None:
            return 0
        else:
            return self.player_state.get("position", 0)

    @property
    def is_connected(self):
        return self.channel_id is not None

    @property
    def is_playing(self):
        return self.is_connected and self.current is not None

    async def update_state(self, state):

        self.player_state = state
        self.time = state.get("time", 0)
        self.filters = state.get("filters", None)
        self.mixer_enabled = state.get("mixerEnabled", None)
        self.mixer = state.get("mixer", None)

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

    async def get_tracks(self, query: str):

        async with self.node.client.session.get(f"{self.node.rest_uri}/loadtracks", params=dict(identifier=query), headers={"Authorization": self.node.password}) as response:
            data = await response.json()

        if data["loadType"] == "LOAD_FAILED":
            raise exceptions.TrackLoadError(f"There was an error of severity '{data['severity']}' while loading tracks.\n\n{data['cause']}")

        elif data["loadType"] == "NO_MATCHES":
            return None

        elif data['loadType'] == 'PLAYLIST_LOADED':
            return objects.Playlist(data=data)

        tracks = []
        for track in data["tracks"]:
            tracks.append(objects.Track(track=track["track"], data=track["info"]))
        return tracks

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

    async def play(self, track, position: int = 0):

        await self.node.send(op="play", guildId=str(self.guild_id), track=track.track, start=position)
        self.current = track
        return self.current

    async def seek(self, position: int):

        if not 0 <= position <= self.current.length:
            raise ValueError("Position cannot be smaller than 0 or larger than track's length")

        await self.node.send(op="seek", guildId=str(self.guild_id), position=position)

    async def stop(self):
        await self.node.send(op="stop", guildId=str(self.guild_id))

    async def destroy(self):
        await self.stop()
        await self.disconnect()
        await self.node.send(op="destroy", guildId=str(self.guild_id))
        del self.node.players[self.guild_id]

    async def set_pause(self, paused: bool):

        if self.paused is paused:
            return

        await self.node.send(op="pause", guildId=str(self.guild_id), pause=paused)
        self.paused = paused
        return self.paused

    async def set_volume(self, volume):

        await self.node.send(op="volume", guildId=str(self.guild_id), volume=volume)
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
