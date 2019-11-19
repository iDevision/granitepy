import asyncio

from discord.ext import commands

from .events import Event
from .exceptions import NoNodesAvailable
from .node import Node
from .player import Player


class Client:

    def __init__(self, bot: commands.Bot, loop=None):

        self.bot = bot
        self.loop = loop or asyncio.get_event_loop()

        self.nodes = {}

        bot.add_listener(self.update_handler, "on_socket_response")

    def __repr__(self):
        return f"<GraniteClient node_count={len(self.nodes.values())} player_count={len(self.players.values())}>"

    @property
    def players(self):
        return {player.guild_id: player for player in [node.players.values() for node in self.nodes.values()]}

    async def create_node(self, host: str, port: int, password: str, rest_uri: str, identifier: str, shard_id: int = None):

        await self.bot.wait_until_ready()

        node = Node(client=self, bot=self.bot, host=host, port=port, password=password, rest_uri=rest_uri, identifier=identifier, shard_id=shard_id)
        await node.connect()

        self.nodes[identifier] = node
        return node

    def get_player(self, guild_id: int, player_class=Player):

        if not self.nodes:
            raise NoNodesAvailable("No nodes available")

        try:
            return self.players[guild_id]
        except KeyError:
            nodes = list(self.nodes.values())
            player = player_class(self.bot, guild_id, nodes[0])

            # TODO Implement a way to get the best node, and use it here.
            nodes[0].players[guild_id] = player
            return player

    async def dispatch(self, event: Event):
        self.bot.dispatch("andesite_" + event.name, event)

    async def update_handler(self, data):
        if not data:
            return

        if data["t"] == "VOICE_SERVER_UPDATE":
            guild_id = int(data["d"]["guild_id"])
            try:
                player = self.players[guild_id]
            except KeyError:
                pass
            else:
                await player._voice_server_update(data["d"])

        elif data["t"] == "VOICE_STATE_UPDATE":
            if int(data["d"]["user_id"]) != self.bot.user.id:
                return

            guild_id = int(data["d"]["guild_id"])
            try:
                player = self.players[guild_id]
            except KeyError:
                pass

            else:
                await player._voice_state_update(data["d"])
        else:
            return