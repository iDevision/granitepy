class Track:

    def __init__(self, track_id: str, data: dict):

        self.track_id = track_id
        self.data = data

        self.title = data.get("title")
        self.author = data.get("author")
        self.length = data.get("length")
        self.yt_id = data.get("identifier")
        self.uri = data.get("uri")
        self.is_stream = data.get("isStream")
        self.is_seekable = data.get("isSeekable")
        self.position = data.get("position")

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<GraniteTrack title={self.title!r} uri={self.uri!r} length={self.length}>"


class Playlist:

    def __init__(self, data: dict):

        self.data = data

        self.title = data["playlistInfo"]["name"]
        self.selected_track = data["playlistInfo"]["selectedTrack"]

        self.tracks = [Track(track_id=track['track'], data=track['info']) for track in data['tracks']]

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<GranitePlaylist name={self.title!r} track_count={len(self.tracks)}>"


class Metadata:

    def __init__(self, data: dict):

        self.version = data.get("version", 0)
        self.version_major = data.get("versionMajor", 0)
        self.version_minor = data.get("versionMinor", 0)
        self.version_revision = data.get("versionRevision", 0)
        self.version_commit = data.get("versionCommit", 0)
        self.version_build = data.get("versionBuild", 0)
        self.node_region = data.get("nodeRegion", None)
        self.node_id = data.get("nodeId", None)
        self.enabled_sources = data.get("enabledSources", None)
        self.loaded_plugins = data.get("loadedPlugins", None)
