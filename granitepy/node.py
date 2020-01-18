import json
import socket
import time

import websockets

from . import events
from . import exceptions
from . import objects


class Node:

    def __init__(self, **kwargs):

        self.client = kwargs.pop("client")
        self.bot = kwargs.pop("bot")
        self.host = kwargs.pop("host")
        self.port = kwargs.pop("port")
        self.password = kwargs.pop("password")
        self.identifier = kwargs.pop("identifier")

        self.websocket_uri = f"ws://{self.host}:{self.port}/websocket"
        self.rest_uri = f"http://{self.host}:{self.port}/"

        self.websocket = None
        self.available = False
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
        return f"<GranitepyNode player_count={len(self.players.keys())} available={self.available}>"

    async def connect(self):

        await self.bot.wait_until_ready()

        try:
            self.websocket = await websockets.connect(uri=self.websocket_uri, extra_headers=self.headers)

            self.client.nodes[self.identifier] = self
            self.task = self.bot.loop.create_task(self.listen())
            self.available = True

        except websockets.InvalidHandshake:
            raise exceptions.NodeConnectionFailure(f"The password for node '{self.identifier}' is invalid.")
        except websockets.InvalidURI:
            raise exceptions.NodeConnectionFailure(f"The URI for node '{self.identifier}' is invalid.")
        except socket.gaierror:
            raise exceptions.NodeConnectionFailure(f"The node '{self.identifier}' failed to connect.")

    async def disconnect(self):

        for player in self.players.copy().values():
            await player.destroy()

        await self.websocket.close()
        del self.client.nodes[self.identifier]
        self.available = False
        self.task.cancel()

    async def listen(self):

        while self.available is True:

            try:
                data = await self.websocket.recv()

            except websockets.ConnectionClosed:
                await self.disconnect()
                raise exceptions.NodeConnectionClosed(f"The connection to node '{self.identifier}' was closed.")

            if not data:
                return

            data = json.loads(data)

            op_code = data.get("op")
            if op_code == "pong":
                self.bot.dispatch(f"node_ping", time.time())
            elif op_code == "metadata":
                self.metadata = objects.Metadata(data["data"])
            elif op_code == "stats":
                self.stats = data["stats"]
            elif op_code == "connection-id":
                self.connection_id = data["id"]
            elif op_code == "event":
                await self.dispatch_event(data)
            elif op_code == "player-update":
                try:
                    player = self.players[int(data["guildId"])]
                    await player.update_state(data["state"])
                except KeyError:
                    continue

    async def dispatch_event(self, data: dict):

        try:
            player = self.players[int(data["guildId"])]
        except KeyError:
            return

        event = getattr(events, data["type"], None)
        event = event(player, data)

        self.bot.dispatch(f"andesite_{event.name}", event)

    async def ping(self):

        start_time = time.time()
        await self.send(op="ping")
        end_time = await self.bot.wait_for(f"node_ping")

        return (end_time - start_time) * 1000

    async def send(self, **data):

        if not self.available:
            raise exceptions.NodeNotAvailable(f"The node '{self.identifier}' is not currently available.")

        await self.websocket.send(json.dumps(data))
