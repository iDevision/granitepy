import asyncio
import random
import typing

import aiohttp
import discord
from discord.ext import commands

from . import exceptions
from .node import Node
from .player import Player


class Client:
    """The main client used to manage nodes and their players.

    Attributes
    ----------
    bot: Union[:class:`discord.ext.commands.Bot`, :class:`discord.ext.commands.AutoShardedBot`]
        The bot instance for granitepy to use.
    loop: Optional[Union[:class:`asyncio.AbstractEventLoop`, :class:`asyncio.ProactorEventLoop`]]
        The event loop to use. If none it will default to the currently running loop.
    session: Optional[:class:`aiohttp.ClientSession`]
        The aiohttp session to use. If none it will create one using the current loop.
    nodes: :class:`dict` [:class:`str`, :class:`.Node`]
        A mapping of Node identifiers to Node instances.
    """

    def __init__(self, bot: typing.Union[commands.Bot, commands.AutoShardedBot], loop=None, session=None):

        self.bot = bot
        self.loop = loop if loop else asyncio.get_event_loop()
        self.session = session if session else aiohttp.ClientSession(loop=self.loop)

        self.nodes = {}

        self.bot.add_listener(self._update_handler, "on_socket_response")

    def __repr__(self):
        return f"<GraniteClient node_count={len(self.nodes.values())} player_count={len(self.players.values())}>"

    @property
    def players(self):
        """:class:`dict` [:class:`int`, :class:`.Player`]: A mapping of :class:`discord.Guild` ids to Player instances for all Nodes."""

        players = []
        for node in self.nodes.values():
            players.extend(node.players.values())

        return {player.guild.id: player for player in players}

    async def _update_handler(self, data: dict):

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
        """|coro|

        Creates and returns a :class:`.Node`.

        Parameters
        ----------
        host: :class:`str`
            The ip that the andesite node is being hosted on.
        port: :class:`int`
            The port that the andesite node is being hosted on.
        password: :class:`str`
            The password used to authenticate connection to the andesite node.
        identifier: :class:`str`
            A custom identifier for this Node. This must be unique to this Node.

        Raises
        -----
        :exc:`.NodeConnectionFailure`
            The Node failed to connect.
        :exc:`.NodeCreationError`
            A Node with the given identifier already exists.

        Returns
        -------
        :class:`.Node`
            The newly created Node object.
        """

        if identifier in self.nodes.keys():
            raise exceptions.NodeCreationError(f"A Node with identifier '{identifier}' already exists.")

        node = Node(client=self, host=host, port=port, password=password, identifier=identifier)
        return await node.connect()

    def get_node(self):
        """
        Finds the best :class:`.Node` and returns it.

        Raises
        ------
        :exc:`.NoNodesAvailable`
            There are no Nodes available.

        Returns
        -------
        :class:`.Node`
            A Node object.
        """

        if not self.nodes:
            raise exceptions.NoNodesAvailable("There are no Nodes available.")

        # TODO better method of getting nodes.
        return random.choice([node for node in self.nodes.values()])

    def get_player(self, guild: discord.Guild, cls: typing.Type[Player] = None, **kwargs):
        """
        Tries to return the :class:`.Player` for the current :class:`discord.Guild`, If one doesnt exist it will be created.

        Parameters
        ----------
        guild: :class:`discord.Guild`
            The discord guild of which to get/create the Player.
        cls: Optional[:class:`.Player`]
            An optional subclass of Player.

        Raises
        ------
        :exc:`.NoNodesAvailable`
            There are no Nodes available.

        Returns
        -------
        :class:`.Player`
            The current guilds Player.
        """

        if not self.nodes:
            raise exceptions.NoNodesAvailable("There are no Nodes available.")

        if guild.id in self.players.keys():
            return self.players[guild.id]

        if not cls:
            cls = Player

        node = self.get_node()
        player = cls(node, guild, **kwargs)
        node.players[guild.id] = player

        return self.players[guild.id]
