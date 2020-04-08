

class Track:
    """
    A granitepy Track.

    Attributes
    ----------
    title: :class:`str`
        The Track's title.
    author: :class:`str`
        The Track's author.
    length: :class:`int`
        The Track's length in milliseconds.
    identifier: :class:`str`
        The Track's identifier.
    uri: :class:`str`
        The Track's url.
    is_stream: :class:`bool`
        Whether or not the Track is a stream.
    is_seekable: :class:`bool`
        Whether or not the Track is seekable.
    position: :class:`int`
        The Track's current position.
    """

    def __init__(self, track_id: str, info: dict):

        self.track_id = track_id
        self.info = info

        self.title = info.get("title")
        self.author = info.get("author")
        self.length = info.get("length")
        self.identifier = info.get("identifier")
        self.uri = info.get("uri")
        self.is_stream = info.get("isStream")
        self.is_seekable = info.get("isSeekable")
        self.position = info.get("position")

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<GraniteTrack title={self.title!r} uri=<{self.uri!r}> length={self.length}>"


class Playlist:
    """
    A granitepy Playlist.

    Attributes
    ----------
    name: :class:`str`
        The Playlist's name.
    selected_track: Optional[:class:`int`]
        The Track the playlist is currently on. Can be None if the playlist was linked directly.
    tracks: :class:`list` [:class:`.Track`]
        A list of Tracks belonging to the Playlist.
    """

    def __init__(self, playlist_info: dict, tracks: list):

        self.playlist_info = playlist_info
        self.tracks_raw = tracks

        self.name = playlist_info.get("name")
        self.selected_track = playlist_info.get("selectedTrack")

        self.tracks = [Track(track_id=track["track"], info=track["info"]) for track in self.tracks_raw]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<GranitePlaylist name={self.name!r} track_count={len(self.tracks)}>"


class Metadata:
    """
    Metadata about a andesite node.

    Attributes
    ----------
    version: :class:`str`
        The andesite node's full version number.
    version_major: :class:`str`
        The andesite node's major version.
    version_minor: :class:`str`
        The andesite node's minor version.
    version_revision: :class:`str`
        The andesite node's revision version.
    version_commit: :class:`str`
        The andesite nodes commit version.
    version_build: :class:`str`
        The andesite node's build number.
    node_region: :class:`str`
        The andesite node's region.
    node_id: :class:`str`
        The andesite node's id
    enabled_sources: :class:`list`
        The andesite node's enabled sources
    loaded_plugins: :class:`list`
        The andesite node's loaded plugins
    """

    def __init__(self, metadata: dict):

        self.version = metadata.get("version", 0)
        self.version_major = metadata.get("versionMajor", 0)
        self.version_minor = metadata.get("versionMinor", 0)
        self.version_revision = metadata.get("versionRevision", 0)
        self.version_commit = metadata.get("versionCommit", 0)
        self.version_build = metadata.get("versionBuild", 0)
        self.node_region = metadata.get("nodeRegion")
        self.node_id = metadata.get("nodeId")
        self.enabled_sources = metadata.get("enabledSources")
        self.loaded_plugins = metadata.get("loadedPlugins")

    def __str__(self):
        return self.version

    def __repr__(self):
        return f"<GraniteMetadata version={self.version!r} region={self.node_region!r} id={self.node_id} enabled_sources={self.enabled_sources}>"
