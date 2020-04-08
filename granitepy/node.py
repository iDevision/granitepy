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
        The :class:`.Client` that this :class:`.Node` is being used by.
    host: :class:`str`
        The ip that the andesite node is being hosted on.
    port: :class:`int`
        The port that the andesite node is being hosted on.
    password: :class:`str`
        The password used to authenticate connection to the andesite node.
    identifier: :class:`str`
        A custom identifier for this :class:`.Node`. This can not be the same as an already existing :class:`.Node`'s identifier.
    websocket_uri: :class:`str`
        The uri of the websocket this :class:`.Node` will connect to.
    rest_uri: :class:`str`
        The uri of the rest api used to make requests.
    players: :class:`dict` [:class:`int`, :class:`.Player`]
        A mapping of :class:`discord.Guild` ids to :class:`.Player` instances for this :class:`.Node`.
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

    @property
    async def ping(self):
        """:class:`float`: The latency between granitepy and your andesite node."""

        start_time = time.time()
        await self.send(op="ping")
        end_time = await self.bot.wait_for(f"node_ping")

        return (end_time - start_time) * 1000

    @property
    async def stats(self):
        """:class:`float`: Stats about the andesite node."""

        await self.send(op="get-stats")
        node_stats = await self.bot.wait_for(f"node_stats")

        return node_stats

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

    async def connect(self):
        """|coro|

        Connects this :class:`.Node` to its andesite websocket.

        Raises
        ------
        :exc:`.NodeConnectionFailure`
            If there was a problem while the :class:`.Node` was connecting.

        Returns
        -------
        :class:`.Node`
            A :class:`.Node` object.
        """

        await self.bot.wait_until_ready()

        try:
            self.websocket = await websockets.connect(uri=self.websocket_uri, extra_headers=self.headers)

            self.client.nodes[self.identifier] = self
            self.task = self.bot.loop.create_task(self.listen())
            self.available = True

            return self

        except websockets.InvalidHandshake:
            raise exceptions.NodeConnectionFailure(f"The password for node '{self.identifier}' is invalid.")
        except websockets.InvalidURI:
            raise exceptions.NodeConnectionFailure(f"The URI for node '{self.identifier}' is invalid.")
        except socket.gaierror:
            raise exceptions.NodeConnectionFailure(f"The node '{self.identifier}' failed to connect.")

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
            The query you want to search youtube with. Can be a link or a general search.


        Returns
        -------
        Union[:class:`list` [:class:`.Track`], :class:`.Playlist`]
            Either a :class:`list` of :class:`.Track`'s or a :class:`.Playlist`
        """

        async with self.client.session.get(url=f"{self.rest_uri}/loadtracks",
                                           params=dict(identifier=query),
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
