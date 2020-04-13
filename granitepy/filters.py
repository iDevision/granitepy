from . import exceptions


class Filter:

    def __init__(self):
        self.payload = None


class Timescale(Filter):
    """
    A representation of an andesite Timescale Filter.

    Attributes
    ----------
    speed: :class:`float`
        The filter's speed.
    pitch: :class:`float`
        The filter's pitch.
    rate: :class:`float`
        The filter's rate.
    """

    def __init__(self, *, speed: float, pitch: float, rate: float):
        super().__init__()

        if speed < 0:
            raise exceptions.FilterInvalidArgument("Timescale speed must be more than 0.")
        if pitch < 0:
            raise exceptions.FilterInvalidArgument("Timescale pitch must be more than 0.")
        if rate < 0:
            raise exceptions.FilterInvalidArgument("Timescale rate must be more than 0.")

        self.speed = speed
        self.pitch = pitch
        self.rate = rate

        self.payload = {"timescale": {"speed": self.speed,
                                      "pitch": self.pitch,
                                      "rate": self.rate}}

    def __repr__(self):
        return f"<GraniteFilterTimescale speed={self.speed} pitch={self.pitch} rate={self.rate}>"


class Karaoke(Filter):
    """
    A representation of an andesite Karaoke Filter.

    Attributes
    ----------
    level: :class:`float`
        The filter's level.
    mono_level: :class:`float`
        The filter's mono level.
    filter_band: :class:`float`
        The filter's band.
    filter_width: :class:`float`
        The filter's width.
    """

    def __init__(self, *, level: float, mono_level: float, filter_band: float, filter_width: float):
        super().__init__()

        self.level = level
        self.mono_level = mono_level
        self.filter_band = filter_band
        self.filter_width = filter_width

        self.payload = {"karaoke": {"level": self.level,
                                    "monoLevel": self.mono_level,
                                    "filterBand": self.filter_band,
                                    "filterWidth": self.filter_width}}

    def __repr__(self):
        return f"<GraniteFilterKaraoke level={self.level} mono_level={self.mono_level} filter_band={self.filter_band} filter_width={self.filter_width}>"


class Tremolo(Filter):
    """
    A representation of an andesite Tremolo Filter.

    Attributes
    ----------
    frequency: :class:`float`
        The filter's frequency.
    depth: :class:`float`
        The filter's depth.
    """

    def __init__(self, *, frequency: float, depth: float):
        super().__init__()

        if frequency < 0:
            raise exceptions.FilterInvalidArgument("Tremolo frequency must be more than 0.")
        if depth < 0 or depth > 1:
            raise exceptions.FilterInvalidArgument("Tremolo depth must be between 0 and 1.")

        self.frequency = frequency
        self.depth = depth

        self.payload = {"tremolo": {"frequency": self.frequency,
                                    "depth": self.depth}}

    def __repr__(self):
        return f"<GraniteFilterTremolo frequency={self.frequency} depth={self.depth}>"


class Vibrato(Filter):
    """
    A representation of an andesite Vibrato Filter.

    Attributes
    ----------
    frequency: :class:`float`
        The filter's frequency.
    depth: :class:`float`
        The filter's depth.
    """

    def __init__(self, *, frequency: float, depth: float):

        super().__init__()
        if frequency < 0 or frequency > 14:
            raise exceptions.FilterInvalidArgument("Vibrato frequency must be between 0 and 14.")
        if depth < 0 or depth > 1:
            raise exceptions.FilterInvalidArgument("Vibrato depth must be between 0 and 1.")

        self.frequency = frequency
        self.depth = depth

        self.payload = {"vibrato": {"frequency": self.frequency,
                                    "depth": self.depth}}

    def __repr__(self):
        return f"<GraniteFilterVibrato frequency={self.frequency} depth={self.depth}>"
