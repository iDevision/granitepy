import json
import socket
import time

import websockets

from . import events
from . import exceptions
from . import objects


class Node:
    """
    A python representation of an andesite node.

    Attributes
    ----------
    client: :class:`.Client`
        The granitepy Client that this Node is being used by.
    bot: Union[:class:`discord.ext.commands.Bot`, :class:`discord.ext.commands.AutoShardedBot`]
        The bot instance that granitepy is using.
    host: :class:`str`
        The ip that the andesite node is being hosted on.
    port: :class:`int`
        The port that the andesite node is being hosted on.
    password: :class:`str`
        The password used to authenticate connection to the andesite node.
    identifier: :class:`str`
        The custom identifier for this Node.
    websocket_uri: :class:`str`
        The uri of the websocket this Node will connect to.
    rest_uri: :class:`str`
        The uri of the rest api used to make requests.
    players: :class:`dict` [:class:`int`, :class:`.Player`]
        A mapping of :class:`discord.Guild` ids to Player instances for this Node.
    """

    def __init__(self, client, host: str, port: int, password: str, identifier: str):

        self.client = client
        self.bot = client.bot
        self.host = host
        self.port = port
        self.password = password
        self.identifier = identifier

        self.websocket_uri = f"ws://{self.host}:{self.port}/websocket"
        self.rest_uri = f"http://{self.host}:{self.port}/"

        self.websocket = None
        self.available = False
        self.task = None

        self.connection_id = None
        self.metadata = None

        self.headers = {
            "Authorization": self.password,
            "Andesite-Resume-Id": self.connection_id,
            "User-Id": self.bot.user.id
        }

        self.players = {}

    def __repr__(self):
        return f"<GraniteNode player_count={len(self.players.keys())} available={self.available}>"

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
                self.bot.dispatch("node_ping", time.time())
            elif op_code == "stats":
                self.bot.dispatch(f"node_stats", data["stats"])
            elif op_code == "metadata":
                self.metadata = objects.Metadata(data["data"])
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

        self.bot.dispatch(f"granitepy_{event.name}", event)

    async def send(self, **data):

        if not self.available:
            raise exceptions.NodeNotAvailable(f"The node '{self.identifier}' is not currently available.")

        await self.websocket.send(json.dumps(data))

    @property
    async def latency(self):
        """:class:`float`: The latency between granitepy and your andesite node."""

        start_time = time.time()
        await self.send(op="ping")
        end_time = await self.bot.wait_for(f"node_ping")

        return (end_time - start_time) * 1000

    @property
    async def stats(self):
        """:class:`dict`: Stats about the andesite node."""

        await self.send(op="get-stats")
        node_stats = await self.bot.wait_for(f"node_stats")

        return node_stats

    async def connect(self):
        """|coro|

        Connects this :class:`.Node` to its andesite websocket.

        Raises
        ------
        :exc:`.NodeConnectionFailure`
            The Node failed to connect.

        Returns
        -------
        :class:`.Node`
            A Node object.
        """

        await self.bot.wait_until_ready()

        try:
            self.websocket = await websockets.connect(uri=self.websocket_uri, extra_headers=self.headers)
            self.task = self.bot.loop.create_task(self.listen())
            self.client.nodes[self.identifier] = self
            self.available = True

            return self

        except websockets.InvalidHandshake:
            raise exceptions.NodeConnectionFailure(f"The password for Node '{self.identifier}' is invalid.")
        except websockets.InvalidURI:
            raise exceptions.NodeConnectionFailure(f"The URI for Node '{self.identifier}' is invalid.")
        except socket.gaierror:
            raise exceptions.NodeConnectionFailure(f"The Node '{self.identifier}' failed to connect.")

    async def disconnect(self):
        """|coro|

        Disconnects this :class:`.Node` and destroys all its :class:`.Player`'s.
        """

        for player in self.players.copy().values():
            await player.destroy()

        await self.websocket.close()
        del self.client.nodes[self.identifier]
        self.available = False
        self.task.cancel()

    async def get_tracks(self, query: str):
        """|coro|

        Returns a list of tracks or a playlist.

        Parameters
        ----------
        query: :class:`str`
            The search to preform. Can be a link or a general search term.

        Returns
        -------
        Union[:class:`list` [:class:`.Track`], :class:`.Playlist`]
            Either a list of Tracks or a Playlist.
        """

        async with self.client.session.get(url=f"{self.rest_uri}/loadtracks", params=dict(identifier=query),
                                           headers={"Authorization": self.password}) as response:
            data = await response.json()

        load_type = data.get("loadType")

        if not load_type:
            raise exceptions.TrackLoadError("There was an error while trying to load this track.")

        elif load_type == "LOAD_FAILED":
            raise exceptions.TrackLoadError(f"There was an error of severity '{data['severity']}' while loading tracks.\n\n{data['cause']}")

        elif load_type == "NO_MATCHES":
            return None

        elif load_type == "PLAYLIST_LOADED":
            return objects.Playlist(playlist_info=data["playlistInfo"], tracks=data["tracks"])

        elif load_type == "SEARCH_RESULT" or load_type == "TRACK_LOADED":
            return [objects.Track(track_id=track["track"], info=track["info"]) for track in data["tracks"]]
