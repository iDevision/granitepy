

class GranitepyEvent:

    name = "null_event"


class TrackStartEvent(GranitepyEvent):

    def __init__(self, player, data):

        self.player = player
        self.name = "track_start"

        self.track = data["track"]


class TrackEndEvent(GranitepyEvent):

    def __init__(self, player, data):

        self.player = player
        self.name = "track_end"

        self.track = data["track"]
        self.reason = data["reason"]
        self.may_start_next = data["mayStartNext"]


class TrackStuckEvent(GranitepyEvent):

    def __init__(self, player, data):

        self.player = player
        self.name = "track_stuck"

        self.track = data["track"]
        self.threshold = data["thresholdMs"]


class TrackExceptionEvent(GranitepyEvent):

    def __init__(self, player, data):

        self.player = player
        self.name = "track_exception"

        self.error = data["error"]
        self.exception = data["exception"]


class WebSocketClosedEvent(GranitepyEvent):

    def __init__(self, player, data):

        self.player = player
        self.name = "websocket_closed"

        self.reason = data["reason"]
        self.code = data["code"]
        self.by_remote = data["byRemote"]
