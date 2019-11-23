class Track:

    def __init__(self, track, data: dict):

        self.track = track
        self.data = data

        self.title = data.get("title", None)
        self.author = data.get("author", None)
        self.length = data.get("length", None)
        self.yt_id = data.get("identifier", None)
        self.uri = data.get("uri", None)
        self.is_stream = data.get("isStream", None)
        self.is_seekable = data.get("isSeekable", None)
        self.position = data.get("position", None)

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<Track length={0.length} is_stream={0.is_stream}>".format(self)


class Playlist:

    def __init__(self, data: dict):

        self.data = data

        self.name = data["playlistInfo"]["name"]
        self.selected_track = data["playlistInfo"]["selectedTrack"]

        self.tracks = [Track(track=track['track'], data=track['info']) for track in data['tracks']]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Playlist name={self.name} tracks={len(self.tracks)}>"


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
