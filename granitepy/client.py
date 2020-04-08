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
    """The main client used to manage :class:`.Node`'s and their :class:`.Player`'s.

    Attributes
    ----------
    bot: Union[:class:`discord.ext.commands.Bot`, :class:`discord.ext.commands.AutoShardedBot`]
        The bot instance for granitepy to use.
    loop: Optional[Union[:class:`asyncio.AbstractEventLoop`, :class:`asyncio.ProactorEventLoop`]]
        The event loop to use. If none it will default to the currently running loop.
    session: Optional[:class:`aiohttp.ClientSession`]
        The aiohttp session to use. If none it will create one using the current loop.
    nodes: :class:`dict` [:class:`str`, :class:`.Node`]
        A mapping of :class:`.Node` identifiers to :class:`.Node` instances.

    """

    def __init__(self, bot: typing.Union[commands.Bot, commands.AutoShardedBot], loop=None, session=None):

        self.bot = bot
        self.loop = loop if loop else asyncio.get_event_loop()
        self.session = session if session else aiohttp.ClientSession(loop=self.loop)

        self.nodes = {}

        self.bot.add_listener(self._update_handler, "on_socket_response")

    def __repr__(self):
        return f"<GraniteClient node_count={len(self.nodes.values())} player_count={len(self.players.values())}>"

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
            A custom identifier for this :class:`.Node`. This can not be the same as an already existing :class:`.Node`'s identifier.

        Raises
        ------
        :exc:`.NodeConnectionFailure`
            If there was an error while creating the :class:`.Node`.

        Returns
        -------
        :class:`.Node`
            The newly created :class:`.Node` object.
        """

        node = Node(client=self, host=host, port=port,
                    password=password, identifier=identifier)
        return await node.connect()

    def get_node(self):
        """
        Returns a :class:`.Node`.

        Raises
        ------
        :exc:`.NodesNotAvailable`
            If there are no :class:`.Node`'s available.

        Returns
        -------
        :class:`.Node`
            A :class:`.Node` object.
        """

        if not self.nodes:
            raise exceptions.NodesNotAvailable("There are no nodes available.")

        # TODO better method of getting nodes.
        return random.choice([node for node in self.nodes.values()])

    @property
    def players(self):
        """:class:`dict` [:class:`int`, :class:`.Player`]: A mapping of :class:`discord.Guild` ids to :class:`.Player` instances for all :class:`.Node`'s."""

        players = []
        for node in self.nodes.values():
            players.extend(node.players.values())

        return {player.guild.id: player for player in players}

    def get_player(self, guild: discord.Guild, cls: typing.Type[Player] = None):
        """
        Tries to return the :class:`.Player` for the current :class:`discord.Guild`, If one doesnt exist it will be created.

        Parameters
        ----------
        guild: :class:`discord.Guild`
            The :class:`discord.Guild` of which to get/create the :class:`.Player`.
        cls: Optional[:class:`.Player`]
            An optional subclass of :class:`.Player`.

        Raises
        ------
        :exc:`.NodesNotAvailable`
            If there are no :class:`.Node`'s available.

        Returns
        -------
        :class:`.Player`
            The current guilds :class:`.Player`.
        """

        if not self.nodes:
            raise exceptions.NodesNotAvailable("There are no nodes available.")

        if guild.id in self.players.keys():
            return self.players[guild.id]

        if not cls:
            cls = Player

        node = self.get_node()
        player = cls(self.bot, node, guild)
        node.players[guild.id] = player

        return self.players[guild.id]
