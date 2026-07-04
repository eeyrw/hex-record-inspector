# AGENTS.md — HexInspector

Python-based Intel HEX viewer with multi-segment ASCII art visualization.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Commands

```bash
# Run all tests
.venv/bin/pytest -q

# Run a single test file
.venv/bin/pytest tests/test_parser.py -q

# Lint + format check (use format to autofix)
.venv/bin/ruff check
.venv/bin/ruff format --check

# CLI usage
.venv/bin/hexinspector file.hex          # block distribution overview
.venv/bin/hexinspector -b file.hex       # summary line only
.venv/bin/hexinspector -w 8 file.hex     # 8 bytes per row
.venv/bin/hexinspector -m 64 file.hex    # merge segments within 64 bytes of each other
```

## Architecture

```
src/hexinspector/
├── __init__.py      # public API: Segment, ParseError, load, load_file, render, render_summary
├── parser.py        # Intel HEX line parser → list[Segment] (contiguous memory regions)
├── visualizer.py    # ASCII art renderer for segments (box-drawing chars)
└── cli.py           # argparse CLI entrypoint (hexinspector command)
```

- **Parser** (`load`/`load_file`): reads Intel HEX format, handles all standard record types (00–05), auto-merges adjacent data records into `Segment` objects. Non-hex lines are silently skipped.
- **Visualizer** (`render`/`render_summary`): renders a borderless block-distribution overview — each contiguous address block shows its address range, size, and first 32 bytes preview. Large blocks display a "…N B more" indicator. The `merge_gap` parameter groups nearby blocks (gap ≤ N), showing gap indicators between segments.
- **Segment**: dataclass with `start`, `data` (bytearray), and helpers `end`, `size`, `read`.

## Conventions

- `src`-layout; all package code lives under `src/hexinspector/`.
- Ruff is the sole linter + formatter (line-length 100, double quotes, py39 target).
- No third-party runtime dependencies; `intelhex` library is NOT used — the parser is hand-rolled.
- Test fixtures use `tmp_path` (pytest built-in); no external test data files.
- Checksum validation is strict — bad hex lines raise `ParseError`.
