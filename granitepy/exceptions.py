class GraniteException(Exception):
    """Base of all exceptions."""


class NodeWebsocketError(GraniteException):
    """There was an error while connecting to the websocket of a node."""


class NodesUnavailable(GraniteException):
    """Either no nodes are currently active or all current nodes are not available."""


class TrackLoadError(GraniteException):
    """There was an error while loading tracks."""


class NodeConnectionClosed(GraniteException):
    """There was an error while connecting to a node."""


class InvalidCredentials(GraniteException):
    """Invalid credentials were passed."""

