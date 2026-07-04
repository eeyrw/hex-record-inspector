"""ASCII art visualization for Intel HEX memory segments."""

from __future__ import annotations

from .parser import Segment

_PREVIEW_BYTES = 32


def _printable(b: int) -> str:
    return chr(b) if 0x20 <= b <= 0x7E else "."


def _addr_width(segments: list[Segment]) -> int:
    if not segments:
        return 4
    max_addr = max(s.end for s in segments)
    return max(4, len(f"{max_addr:X}"))


def _ruler(per_line: int, addr_w: int) -> str:
    cols = "  ".join(f"{i:X}" for i in range(per_line))
    return f"  {'':>{addr_w}}  {cols:<{per_line * 3 - 1}} \u2502"


def _str_seg_preview(seg: Segment, max_bytes: int, per_line: int, addr_w: int) -> list[str]:
    lines: list[str] = []
    n = min(max_bytes, seg.size)
    for off in range(0, n, per_line):
        chunk = seg.read(off, min(per_line, n - off))
        h = " ".join(f"{b:02X}" for b in chunk)
        a = "".join(_printable(b) for b in chunk)
        addr = seg.start + off
        lines.append(f"  {addr:0{addr_w}X}  {h:<{per_line * 3 - 1}} \u2502 {a}")
    return lines


def _size_str(size: int) -> str:
    if size >= 1024:
        return f"{size} B ({size / 1024:.1f} KB)"
    return f"{size} B"


def _gap_str(gap: int) -> str:
    if gap >= 1024:
        return f"gap: {gap} B ({gap / 1024:.1f} KB)"
    return f"gap: {gap} B"


def _block_label(
    idx: int, start: int, end: int, total_data: int, total_gap: int, addr_w: int
) -> str:
    base = f" block {idx}  0x{start:0{addr_w}X} \u2013 0x{end:0{addr_w}X}  {_size_str(total_data)}"
    if total_gap:
        base += f"  (+{_gap_str(total_gap)} gaps)"
    return base


def _render_seg_preview(seg: Segment, max_bytes: int, per_line: int, addr_w: int) -> list[str]:
    lines = _str_seg_preview(seg, max_bytes, per_line, addr_w)
    if seg.size > max_bytes:
        lines.append(f"  ... {_size_str(seg.size - max_bytes)} more")
    return lines


def _sep_line(width: int) -> str:
    return "\u2500" * width


def _block_sep(per_line: int, addr_w: int) -> str:
    width = 2 + addr_w + 2 + per_line * 3 - 1 + 2 + per_line
    return _sep_line(width)


def render(segments: list[Segment], per_line: int = 16, merge_gap: int = 0) -> str:
    """Block-distribution overview."""
    if not segments:
        return "No segments found."

    blocks = _group_blocks(segments, merge_gap)
    addr_w = _addr_width(segments)
    sep = _block_sep(per_line, addr_w)
    lines: list[str] = []

    for bi, block in enumerate(blocks):
        segs = block["segs"]
        gap_sizes = block["gaps"]
        total_data = sum(s.size for s in segs)
        total_gap = sum(gap_sizes)

        if bi > 0:
            lines.append("")

        label = _block_label(bi + 1, segs[0].start, segs[-1].end, total_data, total_gap, addr_w)
        lines.append(label)
        lines.append(_ruler(per_line, addr_w))
        lines.append(sep)

        if len(segs) == 1:
            lines.extend(_render_seg_preview(segs[0], _PREVIEW_BYTES, per_line, addr_w))
        else:
            for si, seg in enumerate(segs):
                if si > 0:
                    lines.append(f"  \u2500\u2500 {_gap_str(gap_sizes[si - 1])} \u2500\u2500")
                max_bytes = _PREVIEW_BYTES if si == 0 else per_line
                lines.extend(_render_seg_preview(seg, max_bytes, per_line, addr_w))

        lines.append(sep)

    return "\n".join(lines)


def _group_blocks(segments: list[Segment], max_gap: int) -> list[dict]:
    """Group segments into blocks where successive gap <= max_gap."""
    if not segments or max_gap == 0:
        return [{"segs": [s], "gaps": []} for s in segments]

    blocks: list[dict] = []
    current_segs = [segments[0]]
    current_gaps: list[int] = []

    for seg in segments[1:]:
        gap = seg.start - current_segs[-1].end
        if gap <= max_gap:
            current_segs.append(seg)
            current_gaps.append(gap)
        else:
            blocks.append({"segs": current_segs, "gaps": current_gaps})
            current_segs = [seg]
            current_gaps = []

    blocks.append({"segs": current_segs, "gaps": current_gaps})
    return blocks


def render_summary(segments: list[Segment]) -> str:
    """One-line summary of all segments."""
    if not segments:
        return "No segments."
    total = sum(s.size for s in segments)
    parts = []
    for i, s in enumerate(segments):
        parts.append(f"seg{i + 1}: 0x{s.start:04X}-0x{s.end:04X} ({s.size}B)")
    return f"{len(segments)} segment(s), {total} bytes total | " + " | ".join(parts)
