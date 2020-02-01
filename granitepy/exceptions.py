class GraniteException(Exception):
    pass


class NodeConnectionFailure(GraniteException):
    pass


class NodeConnectionClosed(GraniteException):
    pass


class NodeNotAvailable(GraniteException):
    pass


class NoNodesAvailable(GraniteException):

    pass


class TrackLoadError(GraniteException):
    pass


class GuildNotFound(GraniteException):
    pass


class PlayerAlreadyExists(GraniteException):
    pass


class InvalidTrackPosition(GraniteException):
    pass
