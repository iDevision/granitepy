import json

import websockets

from . import events
from . import exceptions
from . import objects


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

        self.available = False
        self.websocket = None
        self.task = None

        self.connection_id = None
        self.metadata = None
        self.stats = None

        self.headers = {
            "Authorization": self.password,
            "Andesite-Resume-Id": self.connection_id,
            "User-Id": self.bot.user.id
        }

        self.players = {}

    def __repr__(self):
        return f"<GraniteNode player_count={len(self.players.keys())} available={self.available}>"

    def __str__(self):
        return f"{self.identifier}"

    async def connect(self):

        await self.bot.wait_until_ready()

        try:
            self.websocket = await websockets.connect(uri=f"ws://{self.host}:{self.port}/websocket", extra_headers=self.headers)
            self.available = True
        except websockets.InvalidHandshake:
            raise exceptions.NodeConnectionFailure(f"The password for node '{self.identifier}' was invalid.")
        except websockets.InvalidURI:
            raise exceptions.NodeConnectionFailure(f"The URI provided for node '{self.identifier}' was invalid.")

        if not self.task:
            self.task = self.bot.loop.create_task(self.listen())

    async def disconnect(self):

        if self.available is False:
            return

        self.available = False
        await self.websocket.close()

    async def listen(self):

        while self.available is True:
            try:
                data = await self.websocket.recv()
            except websockets.ConnectionClosed as e:
                if e.code == 4001:
                    self.available = False
                    raise exceptions.NodeInvalidCredentials(f"Invalid credentials were passed to node '{self.identifier}'")
                elif e.code == 1006:
                    self.available = False
                    raise exceptions.NodeConnectionClosed(f"Connection to node '{self.identifier}' was abnormally closed, this node is unavailable")
                break

            if data:
                data = json.loads(data)
                op = data.get("op", None)
                if op == "connection-id":
                    self.connection_id = data.get("id")
                elif op == "metadata":
                    self.metadata = objects.Metadata(data["data"])
                elif op == "stats":
                    self.stats = data["stats"]
                elif op == "player-update":
                    player = self.players.get(int(data["guildId"]))
                    if not player:
                        continue
                    await player.update_state(data)
                elif op == "event":
                    await self.dispatch_event(data)

    async def dispatch_event(self, data):

        player = self.players.get(int(data["guildId"]))
        if not player:
            return

        event = getattr(events, data["type"], None)
        event = event(player, data)

        self.bot.dispatch(f"andesite_{event.name}", event)

    async def send(self, **data):

        try:
            await self.websocket.send(json.dumps(data))
        except websockets.ConnectionClosed:
            raise exceptions.NodeConnectionClosed(f"The connection to the websocket of node '{self.identifier}' is closed.")
