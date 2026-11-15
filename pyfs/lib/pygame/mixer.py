# pygame.mixer: there is no sound card driver yet, so sounds are silent.
# Every call works (so games run unchanged); nothing is played.
_init = False


def init(frequency=44100, size=-16, channels=2, buffer=512, *args, **kw):
    global _init
    _init = True


def pre_init(*args, **kw):
    pass


def quit():
    global _init
    _init = False


def get_init():
    return (44100, -16, 2) if _init else None


def stop():
    pass


def pause():
    pass


def unpause():
    pass


def fadeout(ms):
    pass


def set_num_channels(n):
    pass


def get_num_channels():
    return 8


def get_busy():
    return False


class Channel:
    def __init__(self, id=0):
        self.id = id

    def play(self, sound, loops=0, maxtime=0, fade_ms=0):
        pass

    def stop(self):
        pass

    def get_busy(self):
        return False

    def set_volume(self, *v):
        pass


def find_channel(force=False):
    return Channel()


class Sound:
    def __init__(self, file=None, buffer=None, **kw):
        self._volume = 1.0

    def play(self, loops=0, maxtime=0, fade_ms=0):
        return Channel()

    def stop(self):
        pass

    def fadeout(self, ms):
        pass

    def set_volume(self, value):
        self._volume = value

    def get_volume(self):
        return self._volume

    def get_length(self):
        return 0.0

    def get_num_channels(self):
        return 0


class _Music:
    def load(self, file, namehint=""):
        pass

    def play(self, loops=0, start=0.0, fade_ms=0):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def unpause(self):
        pass

    def fadeout(self, ms):
        pass

    def set_volume(self, v):
        pass

    def get_volume(self):
        return 1.0

    def get_busy(self):
        return False

    def queue(self, file, namehint="", loops=0):
        pass


music = _Music()
