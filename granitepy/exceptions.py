

class GranitepyException(Exception):
    """Base of all granitepy exceptions."""
    pass


class FilterInvalidArgument(GranitepyException):
    """An invalid argument was passed to a filter."""
    pass


class NodeConnectionFailure(GranitepyException):
    """There was a problem while connecting to the node."""
    pass


class NodeConnectionClosed(GranitepyException):
    """This node was closed."""
    pass


class NodeNotAvailable(GranitepyException):
    """This node is not currently available"""
    pass


class NoNodesAvailable(GranitepyException):
    """There are no nodes currently available"""
    pass


class GuildNotFound(GranitepyException):
    """The guild passed to a player was not found."""
    pass


class PlayerAlreadyExists(GranitepyException):
    """A player for this guild already exists."""
    pass


class TrackInvalidPosition(GranitepyException):
    """An invalid position was chosen for a track."""
    pass


class TrackLoadError(GranitepyException):
    """There was an error while loading a track."""
    pass
