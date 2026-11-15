# Raw hardware access helpers.
from _kernel import inb, inw, inl, outb, outw, outl
import uctypes


def mem(addr, size):
    """A live bytearray view of `size` bytes of memory at `addr`."""
    return uctypes.bytearray_at(addr, size)


def peek(addr, width=8):
    """Read a little-endian integer of `width` bytes at `addr`."""
    return int.from_bytes(uctypes.bytearray_at(addr, width), "little")


def poke(addr, value, width=8):
    uctypes.bytearray_at(addr, width)[:] = value.to_bytes(width, "little")


def peek8(a):
    return uctypes.bytearray_at(a, 1)[0]


def peek16(a):
    return peek(a, 2)


def peek32(a):
    return peek(a, 4)


def peek64(a):
    return peek(a, 8)


def poke8(a, v):
    uctypes.bytearray_at(a, 1)[0] = v


def poke16(a, v):
    poke(a, v, 2)


def poke32(a, v):
    poke(a, v, 4)


def poke64(a, v):
    poke(a, v, 8)


def hexdump(addr, size=128):
    data = uctypes.bytearray_at(addr, size)
    for off in range(0, size, 16):
        row = data[off:off + 16]
        hexs = " ".join("%02x" % b for b in row)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
        print("%012x  %-47s  %s" % (addr + off, hexs, text))
