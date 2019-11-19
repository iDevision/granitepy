import aiohttp

from .objects import Playlist, Track
from .websocket import WebSocket


class Node:
    def __init__(self, client, bot, host: str, port: int, password: str, rest_uri: str, identifier: str, shard_id=None):

        self.client = client
        self.bot = bot

        self.host = host
        self.port = port
        self.password = password
        self.rest_uri = rest_uri
        self.identifier = identifier
        self.shard_id = shard_id

        self.players = {}

        self.websocket = None
        self.session = None
        self.available = False

    def __repr__(self):
        return f"<GraniteNode player_count={len(self.players.keys())} available={self.available}>"

    def __str__(self):
        return self.identifier

    async def connect(self):

        self.session = aiohttp.ClientSession(loop=self.client.loop)

        self.websocket = WebSocket(bot=self.bot, node=self, host=self.host, port=self.port, password=self.password)

        await self.websocket._connect()


    async def get_tracks(self, query: str):
        password = "null" if not self.password else self.password

        async with self.session.get(f"{self.rest_uri}/loadtracks", params=dict(identifier=query), headers={"Authorization": password}) as response:
            data = await response.json()

        if data.get('tracks', None) is None:
            return None

        if data['loadType'] == 'PLAYLIST_LOADED':
            return Playlist(data=data)

        tracks = []
        for track in data["tracks"]:
            tracks.append(Track(_id=track["track"], data=track["info"]))

        return tracks
