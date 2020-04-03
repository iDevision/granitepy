import asyncio
import random
import typing

import aiohttp
import discord

from . import exceptions
from .node import Node
from .player import Player


class Client:

    def __init__(self, bot, loop=None, session=None):

        self.bot = bot
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)
        self.bot.add_listener(self.update_handler, "on_socket_response")

        self.nodes = {}

    def __repr__(self):
        return f"<GraniteClient node_count={len(self.nodes.values())} player_count={len(self.players.values())}>"

    @property
    def players(self):

        players = []
        for node in self.nodes.values():
            players.extend(node.players.values())

        return {player.guild.id: player for player in players}

    async def update_handler(self, data: dict):

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
                return

        else:
            return

    async def create_node(self, host: str, port: int, password: str, identifier: str):

        node = Node(client=self, bot=self.bot,
                    host=host, port=port,
                    password=password, identifier=identifier)
        await node.connect()

        return node

    def get_node(self):

        if not self.nodes:
            raise exceptions.NoNodesAvailable("There are no nodes available.")

        return random.choice([node for node in self.nodes.values()])

    def create_player(self, guild: discord.Guild, cls: typing.Type[Player]):

        if not self.nodes:
            raise exceptions.NoNodesAvailable("There are no nodes available.")

        if guild.id in self.players.keys():
            raise exceptions.PlayerAlreadyExists(f"A player for guild '{guild.id}' already exists.")

        node = self.get_node()
        player = cls(self.bot, node, guild)
        node.players[guild.id] = player
        return node.players[guild.id]

    def get_player(self, guild: discord.Guild, cls: typing.Type[Player] = Player):

        if not self.nodes:
            raise exceptions.NoNodesAvailable("There are no nodes available.")

        if guild.id not in self.players.keys():
            self.create_player(guild, cls)

        return self.players[guild.id]
