# pygame.font: text, drawn with the video card's own 8x16 font (the one the
# text console uses), scaled to the requested size. Every name and size
# gives that font; bold draws it twice, italic is accepted and ignored.
import _gfx
from kernel import video
from kernel.console import CP437
from pygame.surface import Surface
from pygame.constants import SRCALPHA
from pygame.color import pixel

_init = False
GLYPH_W, GLYPH_H = 8, 16


def init():
    global _init
    video.font()                     # read it now, while the screen is in text mode
    _init = True


def quit():
    global _init
    _init = False


def get_init():
    return _init


def get_default_font():
    return "vgafont"


def get_fonts():
    return ["vgafont"]


def match_font(name, bold=False, italic=False):
    return "vgafont"


def _cp437(text):
    out = bytearray()
    for ch in text:
        o = ord(ch)
        out.append(o if o < 0x80 else CP437.get(o, 0x3F))
    return bytes(out)


class Font:
    def __init__(self, file=None, size=24):
        size = max(1, int(size))
        self.scale_y = max(1, (size + 12) // 24)     # pygame size 24 ~ 16 pixels
        self.scale_x = self.scale_y
        self.bold = False
        self.italic = False
        self.underline = False
        self.strikethrough = False
        self.point_size = size

    def size(self, text):
        return (len(text) * GLYPH_W * self.scale_x + (1 if self.bold else 0),
                GLYPH_H * self.scale_y)

    def get_height(self):
        return GLYPH_H * self.scale_y

    get_linesize = get_height

    def get_ascent(self):
        return 12 * self.scale_y

    def get_descent(self):
        return -4 * self.scale_y

    def set_bold(self, on):
        self.bold = bool(on)

    def get_bold(self):
        return self.bold

    def set_italic(self, on):
        self.italic = bool(on)

    def get_italic(self):
        return self.italic

    def set_underline(self, on):
        self.underline = bool(on)

    def get_underline(self):
        return self.underline

    def set_strikethrough(self, on):
        self.strikethrough = bool(on)

    def render(self, text, antialias=False, color=(255, 255, 255), background=None, wraplength=0):
        text = str(text).replace("\n", " ")
        w, h = self.size(text)
        surf = Surface((max(1, w), h), 0 if background is not None else SRCALPHA)
        fg = pixel(color) | 0xFF000000
        if background is not None:
            surf.fill(background)
        else:
            surf.fill((0, 0, 0, 0))
        chars = _cp437(text)
        font = video.font()
        for dx in ((0, 1) if self.bold else (0,)):
            _gfx.text(surf._buf, surf._w, surf._h, dx, 0, font, chars, fg,
                      self.scale_x, self.scale_y, -1)
        if self.underline:
            _gfx.fill(surf._buf, surf._w, surf._h, 0, h - self.scale_y, w, self.scale_y, fg)
        if self.strikethrough:
            _gfx.fill(surf._buf, surf._w, surf._h, 0, h // 2, w, self.scale_y, fg)
        return surf

    def metrics(self, text):
        return [(0, GLYPH_W * self.scale_x, 0, GLYPH_H * self.scale_y, GLYPH_W * self.scale_x)
                for _ in text]


def SysFont(name=None, size=24, bold=False, italic=False):
    f = Font(None, size)
    f.bold, f.italic = bold, italic
    return f
