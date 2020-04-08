

class GranitepyException(Exception):
    """Base of all granitepy exceptions."""


class NodeException(Exception):
    """Base exception for nodes."""


class NodeCreationError(NodeException):
    """There was a problem while creating the node."""


class NodeConnectionFailure(NodeException):
    """There was a problem while connecting to the node."""


class NodeConnectionClosed(NodeException):
    """The nodes connection is closed."""
    pass


class NodeNotAvailable(GranitepyException):
    """The node is not currently available."""
    pass


class NoNodesAvailable(GranitepyException):
    """There are no nodes currently available."""
    pass


class TrackInvalidPosition(GranitepyException):
    """An invalid position was chosen for a track."""
    pass


class TrackLoadError(GranitepyException):
    """There was an error while loading a track."""
    pass


class FilterInvalidArgument(GranitepyException):
    """An invalid argument was passed to a filter."""
    pass

