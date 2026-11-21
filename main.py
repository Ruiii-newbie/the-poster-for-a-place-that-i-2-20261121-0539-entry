#!/usr/bin/env python3
"""Entry program: validate entry.png beside this file and write it to
/output/entry.png.

Standard library only. No network. Deterministic: the output is a
byte-for-byte copy of entry.png, so every run writes identical bytes.
"""
import os
import struct
import sys
import zlib

LIMIT_BYTES = 1_048_576
LIMIT_PIXELS = 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


def die(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def check_png(blob):
    """Walk the PNG chunk list, verifying CRCs, sizes and structure."""
    if len(blob) > LIMIT_BYTES:
        die(f"entry.png is {len(blob)} bytes, above the 1048576 limit")
    if len(blob) < 8 or blob[:8] != MAGIC:
        die("entry.png does not start with the PNG signature")
    width = height = None
    offset = 8
    count = 0
    got_idat = False
    got_iend = False
    while True:
        if offset + 8 > len(blob):
            die("PNG ends inside a chunk header")
        size = struct.unpack(">I", blob[offset:offset + 4])[0]
        kind = blob[offset + 4:offset + 8]
        if offset + 12 + size > len(blob):
            die(f"PNG chunk {kind!r} is truncated")
        body = blob[offset + 8:offset + 8 + size]
        stored = struct.unpack(">I", blob[offset + 8 + size:offset + 12 + size])[0]
        actual = zlib.crc32(body, zlib.crc32(kind)) & 0xFFFFFFFF
        if actual != stored:
            die(f"PNG chunk {kind!r} has a bad CRC")
        count += 1
        if count == 1:
            if kind != b"IHDR":
                die("first PNG chunk is not IHDR")
            if size != 13:
                die("IHDR chunk is not 13 bytes long")
            width, height = struct.unpack(">II", body[:8])
            if width == 0 or height == 0:
                die("PNG dimensions must be nonzero")
            if width > LIMIT_PIXELS or height > LIMIT_PIXELS:
                die(f"PNG is {width}x{height}, above the 1024x1024 limit")
        if kind == b"IDAT":
            got_idat = True
        if kind == b"IEND":
            if size != 0:
                die("IEND chunk is not empty")
            got_iend = True
            break
        offset += 12 + size
    if not got_idat:
        die("PNG has no IDAT chunk")
    if not got_iend:
        die("PNG has no IEND chunk")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        die("entry.png is missing beside main.py")
    with open(src, "rb") as fh:
        blob = fh.read()
    width, height = check_png(blob)
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    with open(out, "wb") as fh:
        fh.write(blob)
    print(f"wrote {out}: {width}x{height}, {len(blob)} bytes")


if __name__ == "__main__":
    main()
