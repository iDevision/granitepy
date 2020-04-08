.. py:currentmodule:: granitepy


API Reference
=============


Client
------
.. autoclass:: Client
    :members:


Node
----
.. autoclass:: Node
    :members:


Player
------
.. autoclass:: Player
    :members:


Objects
-------
.. autoclass:: Track
.. autoclass:: Playlist
.. autoclass:: Metadata



Filters
-------
.. autoclass:: Timescale
.. autoclass:: Karaoke
.. autoclass:: Tremolo
.. autoclass:: Vibrato


Events
------
.. autoclass:: TrackStartEvent
.. autoclass:: TrackEndEvent
.. autoclass:: TrackStuckEvent
.. autoclass:: TrackExceptionEvent
.. autoclass:: WebSocketClosedEvent


Exceptions
----------
.. autoexception:: GranitepyException
.. autoexception:: NodeException
.. autoexception:: NodeCreationError
.. autoexception:: NodeConnectionFailure
.. autoexception:: NodeConnectionClosed
.. autoexception:: NodeNotAvailable
.. autoexception:: NoNodesAvailable
.. autoexception:: TrackInvalidPosition
.. autoexception:: TrackLoadError
.. autoexception:: FilterInvalidArgument


Exception Hierarchy
--------------------
.. exception_hierarchy::

    - :exc:`GranitepyException`
        - :exc:`NodeException`
            - :exc:`NodeCreationError`
            - :exc:`NodeConnectionFailure`
            - :exc:`NodeConnectionClosed`
            - :exc:`NodeNotAvailable`
            - :exc:`NoNodesAvailable`
        - :exc:`TrackInvalidPosition`
        - :exc:`TrackLoadError`
        - :exc:`FilterInvalidArgument`
