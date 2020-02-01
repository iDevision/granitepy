
class Track:

    def __init__(self, track_id: str, info: dict):

        self.track_id = track_id
        self.info = info

        self.title = info.get("title")
        self.author = info.get("author")
        self.length = info.get("length")
        self.yt_id = info.get("identifier")
        self.uri = info.get("uri")
        self.is_stream = info.get("isStream")
        self.is_seekable = info.get("isSeekable")
        self.position = info.get("position")

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<GraniteTrack title={self.title!r} uri={self.uri!r} length={self.length}>"


class Playlist:

    def __init__(self, playlist_info: dict, tracks: list):

        self.playlist_info = playlist_info
        self.tracks = tracks

        self.name = playlist_info.get("name")
        self.selected_track = playlist_info.get("selectedTrack")

        self.tracks = [Track(track_id=track['track'], info=track['info']) for track in self.tracks]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<GranitePlaylist name={self.name!r} track_count={len(self.tracks)}>"


class Metadata:

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

