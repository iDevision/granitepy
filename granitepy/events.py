

class GranitepyEvent:

    def __init__(self):
        pass

    name = "null_event"


class TrackStartEvent(GranitepyEvent):
    """
    Dispatched when a track starts playing.

    Attributes
    ----------
    player: :class:`.Player`
        The Player relevant to this event.
    name: :class:`str`
        The name of this event.
    track: :class:`.Track`
        The track that started playing.
    """

    def __init__(self, player, data):
        super().__init__()

        self.player = player
        self.name = "track_start"

        self.track = data["track"]


class TrackEndEvent(GranitepyEvent):
    """
    Dispatched when a track has finished playing.

    Attributes
    ----------
    player: :class:`.Player`
        The Player relevant to this event.
    name: :class:`str`
        The name of this event.
    track: :class:`.Track`
        The track that finished playing.
    reason: :class:`str`
        Why the track has stopped.
    may_start_next: :class:`bool`
        Whether or not a track can play next.
    """

    def __init__(self, player, data):
        super().__init__()

        self.player = player
        self.name = "track_end"

        self.track = data["track"]
        self.reason = data["reason"]
        self.may_start_next = data["mayStartNext"]


class TrackStuckEvent(GranitepyEvent):
    """
    Dispatched when a track gets stuck while playing.

    Attributes
    ----------
    player: :class:`.Player`
        The Player relevant to this event.
    name: :class:`str`
        The name of this event.
    track: :class:`.Track`
        The track that got stuck.
    threshold: :class:`int`
        Unsure as of right now.
    """

    def __init__(self, player, data):
        super().__init__()

        self.player = player
        self.name = "track_stuck"

        self.track = data["track"]
        self.threshold = data["thresholdMs"]


class TrackExceptionEvent(GranitepyEvent):
    """
    Dispatched when a playing track raises an exception.

    Attributes
    ----------
    player: :class:`.Player`
        The Player relevant to this event.
    name: :class:`str`
        The name of this event.
    error: :class:`str`
        The error that was raised during playing.
    exception
        The exception that was raised.
    """

    def __init__(self, player, data):
        super().__init__()

        self.player = player
        self.name = "track_exception"

        self.error = data["error"]
        self.exception = data["exception"]


class WebSocketClosedEvent(GranitepyEvent):
    """
    Dispatched when a nodes websocket closes.

    Attributes
    ----------
    player: :class:`.Player`
        The Player relevant to this event.
    name: :class:`str`
        The name of this event.
    reason: :class:`str`
        The reason the websocket was closed.
    code: :class:`int`
        The websocket close code.
    by_remote: :class:`bool`
        Whether the websocket was closed remotely.
    """

    def __init__(self, player, data):
        super().__init__()

        self.player = player
        self.name = "websocket_closed"

        self.reason = data["reason"]
        self.code = data["code"]
        self.by_remote = data["byRemote"]
