# HexInspector

Intel HEX viewer with multi-segment ASCII art visualization. A command-line tool
that parses Intel HEX files and renders a human-readable block-distribution
overview — no third-party dependencies, pure Python, hand-rolled parser.

## Features

- **Full Intel HEX support** — data records (00), EOF (01), extended linear
  address (04), extended segment address (02), start addresses (03/05)
- **Strict checksum validation** — invalid lines raise `ParseError`
- **Auto-merge adjacent records** — contiguous data records are coalesced into
  `Segment` objects
- **Multi-segment display** — each non-contiguous memory region is shown as a
  separate block with address range, size, and byte preview
- **Gap merging** — optionally group nearby blocks (≤ N bytes apart) into a
  single visual block with gap indicators
- **Configurable display width** — adjustable bytes-per-row
- **Summary mode** — one-line segment overview for quick inspection
- **Zero runtime dependencies** — only stdlib
- **Python 3.9+**

## Installation

```bash
git clone https://github.com/eeyrw/hex-record-inspector.git
cd hex-record-inspector
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Usage

```bash
# Block distribution overview (default: 16 bytes per row)
hexinspector file.hex

# Summary line only
hexinspector -b file.hex

# 8 bytes per row
hexinspector -w 8 file.hex

# Merge segments within 64 bytes of each other
hexinspector -m 64 file.hex
```

### Options

| Flag            | Description                                              | Default |
| --------------- | -------------------------------------------------------- | ------- |
| `file`          | Path to an Intel HEX file (required)                     | —       |
| `-w`, `--width` | Bytes per row in the hex preview                         | 16      |
| `-b`, `--brief` | Show only a one-line summary                             | off     |
| `-m`, `--merge-gap` | Group segments within N bytes into one visual block  | 0       |

## Examples

### Real-world PIC32 firmware (`examples/pic32-music-box.hex`)

```bash
# Summary — 50 segments, ~100 KB total
$ hexinspector -b examples/pic32-music-box.hex
50 segment(s), 102940 bytes total | seg1: 0x1D000000-0x1D018EE8 (102120B)
| seg2: 0x1D01F180-0x1D01F190 (16B) | seg3: 0x1D01F200-0x1D01F208 (8B) …
```

```
# Default view — each segment as a block
$ hexinspector examples/pic32-music-box.hex
=== block 1  0x1D000000 – 0x1D018EE8  102120 B (99.7 KB) ===
           │ 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F  │
————————————————————————————————————————————————————————————————————————————───
  1D000000 │ 07 00 07 00 07 00 08 00 08 00 09 00 0A 00 0A 00 │ ................
  1D000010 │ 0B 00 0B 00 0C 00 0D 00 0E 00 0F 00 0F 00 10 00 │ ................
  … 102088 B (99.7 KB) more
———————————————————————————————————————————————————————————————————————————————

=== block 2  0x1D01F180 – 0x1D01F190  16 B ===
           │ 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F  │
———————————————————————————————————————————————————————————————————————————————
  1D01F180 │ 01 9D 1A 3C CC 7F 5A 27 08 00 40 03 00 00 00 00 │ ...<..Z'..@.....
———————————————————————————————————————————————————————————————————————————————

=== block 3  0x1D01F200 – 0x1D01F208  8 B ===
  1D01F200 │ 33 62 40 0B 00 00 00 00 -- -- -- -- -- -- -- -- │ 3b@.....        
… (47 more blocks)
```

```
# Merge gap — group nearby segments
$ hexinspector -m 32 examples/pic32-music-box.hex
=== block 1  0x1D000000 – 0x1D018EE8  102120 B (99.7 KB) ===
    …
=== block 2  0x1D01F180 – 0x1D01F190  16 B ===
    …
=== block 3  0x1D01F200 – 0x1D01F768  352 B  (+gap: 1032 B (1.0 KB) gaps) ===
           │ 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F  │
———————————————————————————————————————————————————————————————————————————————
  1D01F200 │ 33 62 40 0B 00 00 00 00 -- -- -- -- -- -- -- -- │ 3b@.....        
  ── gap: 24 B ──
  1D01F220 │ 33 62 40 0B 00 00 00 00 -- -- -- -- -- -- -- -- │ 3b@.....        
  ── gap: 24 B ──
  1D01F240 │ 33 62 40 0B 00 00 00 00 -- -- -- -- -- -- -- -- │ 3b@.....        
  ── gap: 24 B ──
    … (44 repeating 8‑byte config records merged with gap indicators)
———————————————————————————————————————————————————————————————————————————————
=== block 4  0x1FC00000 – 0x1FC00178  376 B ===
  …
=== block 5  0x1FC00380 – 0x1FC00390  16 B ===
  …
=== block 6  0x1FC00480 – 0x1FC004AC  44 B ===
  …
=== block 7  0x1FC00BF0 – 0x1FC00C00  16 B ===
  1FC00BF0 │ FF FF FF 7F 89 79 F8 FF 5B CD 60 FF E3 FF FF 7F │ .....y..[.`.....
```

## Python API

```python
from hexinspector import load, load_file, render, render_summary, Segment, ParseError

# Parse a hex string
segments: list[Segment] = load(hex_string)

# Parse from a file
segments = load_file("firmware.hex")

# Render a block-distribution overview
print(render(segments, per_line=16, merge_gap=0))

# Render a one-line summary
print(render_summary(segments))
```

### Segment dataclass

```python
@dataclass
class Segment:
    start: int              # starting address
    data: bytearray         # raw byte data

    @property
    def end -> int          # start + len(data)
    @property
    def size -> int         # len(data)
    def read(offset, size)  # slice data as bytes
```

## Architecture

```
src/hexinspector/
├── __init__.py      # public API exports
├── parser.py        # Intel HEX line parser → list[Segment]
├── visualizer.py    # ASCII art renderer for segments
└── cli.py           # argparse CLI entrypoint
```

- **Parser** (`load` / `load_file`) — reads Intel HEX format, handles record
  types 00–05, auto-merges adjacent data records into `Segment` objects.
  Non-hex lines are silently skipped.
- **Visualizer** (`render` / `render_summary`) — renders a borderless
  block-distribution overview with address range, size, first 32 bytes preview,
  and ASCII sidebar. Large blocks show a "…N B more" indicator. The `merge_gap`
  parameter groups nearby blocks (gap ≤ N) with gap indicators between segments.
- **CLI** — argument parsing, wires parser + visualizer together.

## Development

```bash
# Run all tests
.venv/bin/pytest -q

# Run a single test file
.venv/bin/pytest tests/test_parser.py -q

# Lint + format check
.venv/bin/ruff check
.venv/bin/ruff format --check

# Auto-fix formatting
.venv/bin/ruff format
```

## Related Projects

- Intel HEX is specified in [Wikipedia](https://en.wikipedia.org/wiki/Intel_HEX)

## License

MIT
