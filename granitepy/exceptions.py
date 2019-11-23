class GraniteException(Exception):
    """Base of all exceptions."""


class NodeConnectionFailure(GraniteException):
    """There was an error while connecting to the websocket of a node."""


class NodeConnectionClosed(GraniteException):
    """The connection to the nodes websocket is closed."""


class NodeInvalidCredentials(GraniteException):
    """Invalid credentials were passed."""


class NodesUnavailable(GraniteException):
    """Either no nodes are currently active or all current nodes are not available."""


class TrackLoadError(GraniteException):
    """There was an error while loading tracks."""





