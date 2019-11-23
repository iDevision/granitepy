import asyncio
import random

import aiohttp

from . import exceptions
from .node import Node
from .player import Player


class Client:

    def __init__(self, bot, loop=None, session=None):

        self.bot = bot
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession()

        self.nodes = {}

        bot.add_listener(self.update_handler, "on_socket_response")

    def __repr__(self):
        return f"<GraniteClient node_count={len(self.nodes.values())} player_count={len(self.players.values())}>"

    @property
    def players(self):
        players = []
        for node in self.nodes.values():
            players.extend(node.players.values())
        return {player.guild_id: player for player in players}

    def get_player(self, guild_id: int, cls=None):

        if not self.nodes:
            raise exceptions.NodesUnavailable("There are no nodes currently available.")

        try:
            return self.players[guild_id]
        except KeyError:

            if not cls:
                cls = Player

            node = self.get_node()
            player = cls(self.bot, guild_id, node)

            node.players[guild_id] = player
            return player

    async def create_node(self, host: str, port: int, password: str, rest_uri: str, identifier: str, shard_id: int = None):

        await self.bot.wait_until_ready()

        node = Node(client=self, bot=self.bot, host=host, port=port, password=password, rest_uri=rest_uri, identifier=identifier, shard_id=shard_id)
        await node.connect()

        self.nodes[node.identifier] = node

    def get_node(self):
        # TODO Better method of getting the best node.
        return random.choice([node for node in self.nodes.values() if node.available is True])

    async def update_handler(self, data):

        if not data:
            return

        if data["t"] == "VOICE_SERVER_UPDATE":
            guild_id = int(data["d"]["guild_id"])
            try:
                player = self.players[guild_id]
                await player.voice_server_update(data["d"])
            except KeyError:
                return

        elif data["t"] == "VOICE_STATE_UPDATE":

            if int(data["d"]["user_id"]) != self.bot.user.id:
                return

            guild_id = int(data["d"]["guild_id"])
            try:
                player = self.players[guild_id]
                await player.voice_state_update(data["d"])
            except KeyError:
                pass

        else:
            return
