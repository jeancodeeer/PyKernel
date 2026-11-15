# Memory management policy.
#
# The Rust layer identity-maps the first 4 GiB and hands the VM an initial
# heap. Everything else about memory is decided here: which physical frames
# are free, growing the Python heap, and editing the page tables.
import _kernel
from kernel.hw import mem, peek32, peek64, poke64

PAGE = 4096
PRESENT, WRITABLE, USER, HUGE = 0x01, 0x02, 0x04, 0x80
ADDR_MASK = 0x000FFFFFFFFFF000

regions = []      # [cursor, end] of unallocated physical RAM
_freed = []       # frames given back with free_frame()
total_ram = 0


def memory_map():
    """Yield (base, length, type) from the bootloader memory map."""
    mbi = _kernel.info()["multiboot"]
    if not mbi or not peek32(mbi) & 0x40:
        return
    p = peek32(mbi + 48)
    end = p + peek32(mbi + 44)
    while p < end:
        yield peek64(p + 4), peek64(p + 12), peek32(p + 20)
        p += peek32(p) + 4


def init():
    global total_ram
    info = _kernel.info()
    floor = max(info["heap_end"], info["kernel_end"], info["initrd_end"], 0x100000)
    regions.clear()
    _freed.clear()
    total_ram = 0
    for base, length, kind in memory_map():
        if kind != 1:
            continue
        total_ram += length
        start = (max(base, floor) + PAGE - 1) & ~(PAGE - 1)
        end = min(base + length, 1 << 32) & ~(PAGE - 1)   # identity-mapped part
        if end > start:
            regions.append([start, end])


def free_bytes():
    return sum(r[1] - r[0] for r in regions) + len(_freed) * PAGE


def alloc_frame():
    """One zeroed 4 KiB physical frame."""
    if _freed:
        addr = _freed.pop()
    else:
        for r in regions:
            if r[0] < r[1]:
                addr = r[0]
                r[0] += PAGE
                break
        else:
            raise MemoryError("out of physical frames")
    mem(addr, PAGE)[:] = bytes(PAGE)
    return addr


def alloc_contiguous(count):
    for r in regions:
        if r[1] - r[0] >= count * PAGE:
            addr = r[0]
            r[0] += count * PAGE
            return addr
    raise MemoryError("no contiguous run of %d frames" % count)


def free_frame(addr):
    _freed.append(addr)


def grow_heap(mib=16):
    """Move `mib` MiB of free RAM into the Python heap."""
    addr = alloc_contiguous(mib * 256)
    _kernel.heap_add(addr, mib << 20)
    return addr


# ---- page tables ----

def root():
    return _kernel.cr(3) & ADDR_MASK


def translate(vaddr):
    """Virtual -> physical address, or None if unmapped."""
    table = root()
    for shift in (39, 30, 21, 12):
        entry = peek64(table + ((vaddr >> shift) & 0x1FF) * 8)
        if not entry & PRESENT:
            return None
        if shift == 12 or (entry & HUGE and shift < 39):
            low = (1 << shift) - 1
            return (entry & ADDR_MASK & ~low) | (vaddr & low)
        table = entry & ADDR_MASK


def map_page(vaddr, paddr, flags=PRESENT | WRITABLE):
    """Map one 4 KiB page, creating intermediate tables as needed."""
    table = root()
    for shift in (39, 30, 21):
        slot = table + ((vaddr >> shift) & 0x1FF) * 8
        entry = peek64(slot)
        if not entry & PRESENT:
            entry = alloc_frame() | PRESENT | WRITABLE
            poke64(slot, entry)
        elif entry & HUGE:
            raise ValueError("address is covered by a huge page")
        table = entry & ADDR_MASK
    poke64(table + ((vaddr >> 12) & 0x1FF) * 8, (paddr & ADDR_MASK) | flags)
    _kernel.invlpg(vaddr)


def unmap_page(vaddr):
    table = root()
    for shift in (39, 30, 21):
        entry = peek64(table + ((vaddr >> shift) & 0x1FF) * 8)
        if not entry & PRESENT or entry & HUGE:
            return False
        table = entry & ADDR_MASK
    poke64(table + ((vaddr >> 12) & 0x1FF) * 8, 0)
    _kernel.invlpg(vaddr)
    return True
