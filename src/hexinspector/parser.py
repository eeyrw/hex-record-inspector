"""Intel HEX format parser supporting all standard record types."""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

RECORD_DATA = 0x00
RECORD_EOF = 0x01
RECORD_EXT_SEG_ADDR = 0x02
RECORD_START_SEG_ADDR = 0x03
RECORD_EXT_LIN_ADDR = 0x04
RECORD_START_LIN_ADDR = 0x05


@dataclass
class Segment:
    """A contiguous memory segment with data."""

    start: int
    data: bytearray = field(default_factory=bytearray)

    @property
    def end(self) -> int:
        return self.start + len(self.data)

    @property
    def size(self) -> int:
        return len(self.data)

    def read(self, offset: int, size: int) -> bytes:
        return bytes(self.data[offset : offset + size])


class ParseError(ValueError):
    """Raised when parsing an invalid Intel HEX line."""


def _parse_line(line: str) -> tuple[int, int, int, bytes]:
    line = line.strip()
    if not line:
        raise ParseError("empty line")
    if line[0] != ":":
        raise ParseError(f"line must start with ':', got {line[0]!r}")
    hex_part = line[1:]
    if len(hex_part) % 2 != 0:
        raise ParseError("hex data has odd length")

    raw = bytes.fromhex(hex_part)
    checksum = (-sum(raw)) & 0xFF
    if checksum != 0:
        raise ParseError(f"checksum mismatch (expected 0, got {checksum:#04x})")

    byte_count = raw[0]
    address = (raw[1] << 8) | raw[2]
    record_type = raw[3]
    data = raw[4 : 4 + byte_count]

    if len(data) != byte_count:
        raise ParseError("byte count does not match data length")

    return byte_count, address, record_type, data


def load(hex_data: str) -> list[Segment]:
    """Parse an Intel HEX file and return contiguous memory segments.

    Adjacent data records are merged into segments. Non-contiguous
    regions become separate segments.
    """
    collector: dict[int, bytearray] = {}
    base_linear = 0
    base_seg = 0

    for raw_line in hex_data.splitlines():
        line = raw_line.strip()
        if not line or line[0] != ":":
            continue

        _, address, record_type, data = _parse_line(line)

        if record_type == RECORD_DATA:
            addr = base_linear + base_seg + address
            collector.setdefault(addr, bytearray()).extend(data)

        elif record_type == RECORD_EOF:
            break

        elif record_type == RECORD_EXT_SEG_ADDR:
            base_seg = struct.unpack(">H", data)[0] << 4

        elif record_type == RECORD_EXT_LIN_ADDR:
            base_linear = struct.unpack(">H", data)[0] << 16

        elif record_type in (RECORD_START_SEG_ADDR, RECORD_START_LIN_ADDR):
            pass

    return _coalesce(collector)


def load_file(path: str) -> list[Segment]:
    """Parse an Intel HEX file from disk."""
    with open(path) as f:
        return load(f.read())


def _coalesce(collector: dict[int, bytearray]) -> list[Segment]:
    """Merge adjacent byte arrays into contiguous segments."""
    if not collector:
        return []
    sorted_items = sorted(collector.items(), key=lambda x: x[0])
    segments: list[Segment] = []
    current = Segment(start=sorted_items[0][0], data=sorted_items[0][1])
    for addr, data in sorted_items[1:]:
        if addr == current.end:
            current.data.extend(data)
        else:
            segments.append(current)
            current = Segment(start=addr, data=data)
    segments.append(current)
    return segments
