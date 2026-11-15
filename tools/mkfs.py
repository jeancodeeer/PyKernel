"""Pack pyfs/ into the boot archive the kernel loads as its root filesystem.

Format: b"PYFS", u32 file count, then per file: u16 name length, u32 data
length, name (utf-8, '/'-separated), data. init.py is what Rust executes.
"""
import struct
import sys
from pathlib import Path


def pack(src: Path, out: Path) -> int:
    files = sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    if not (src / "init.py").is_file():
        sys.exit(f"{src}/init.py is missing")
    blob = bytearray(b"PYFS" + struct.pack("<I", len(files)))
    for p in files:
        name = p.relative_to(src).as_posix().encode()
        data = p.read_bytes().replace(b"\r\n", b"\n")
        blob += struct.pack("<HI", len(name), len(data)) + name + data
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)
    return len(files)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    n = pack(root / "pyfs", root / "build" / "pyfs.img")
    print(f"pyfs.img: {n} files")
