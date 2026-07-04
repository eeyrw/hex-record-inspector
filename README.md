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

### Example output

```
 block 1  0x0000 – 0x0030  48 B
           0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
 ────────────────────────────────────────────────────────────────────────
  00000  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  │ ................
  00010  10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F  │ ................
  00020  20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F  │  !"#$%&'()*+,-./
 ────────────────────────────────────────────────────────────────────────
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

- [Intel HEX → bin](https://github.com/eeyrw/hex-record-inspector) (companion
  tooling)
- Intel HEX is specified in [Wikipedia](https://en.wikipedia.org/wiki/Intel_HEX)

## License

MIT
