"""Tests for the visualizer."""

from hexinspector.parser import Segment
from hexinspector.visualizer import render, render_summary


class TestRenderSummary:
    def test_empty(self):
        assert render_summary([]) == "No segments."

    def test_one_segment(self):
        seg = Segment(start=0x0100, data=bytearray(range(16)))
        result = render_summary([seg])
        assert "1 segment(s)" in result
        assert "16 bytes total" in result
        assert "seg1: 0x0100-0x0110" in result

    def test_two_segments(self):
        s1 = Segment(start=0x0100, data=bytearray(range(8)))
        s2 = Segment(start=0x0200, data=bytearray(range(8)))
        result = render_summary([s1, s2])
        assert "2 segment(s)" in result
        assert "16 bytes total" in result


class TestRender:
    def test_no_segments(self):
        assert render([]) == "No segments found."

    def test_small_segment(self):
        seg = Segment(start=0x0100, data=bytearray(b"Hello, World!"))
        out = render([seg])
        assert "block 1" in out
        assert "0x0100" in out
        assert "Hello, World!" in out

    def test_multiple_segments_no_merge(self):
        s1 = Segment(start=0x0100, data=bytearray(b"AAAA"))
        s2 = Segment(start=0x0300, data=bytearray(b"BBBB"))
        out = render([s1, s2])
        assert "block 1" in out
        assert "block 2" in out

    def test_non_printable_bytes(self):
        seg = Segment(start=0x0000, data=bytearray(range(16)))
        out = render([seg])
        assert "." in out

    def test_large_segment_truncated(self):
        data = bytearray((i & 0xFF) for i in range(40))
        seg = Segment(start=0x0000, data=data)
        out = render([seg])
        assert "more" in out

    def test_small_segment_not_truncated(self):
        data = bytearray((i & 0xFF) for i in range(16))
        seg = Segment(start=0x0000, data=data)
        out = render([seg])
        assert "more" not in out

    def test_merge_gap_groups_segments(self):
        s1 = Segment(start=0x0100, data=bytearray(b"AA"))
        s2 = Segment(start=0x0120, data=bytearray(b"BB"))
        out = render([s1, s2], merge_gap=64)
        assert "block 1" in out
        assert "block 2" not in out  # merged into one block
        assert "gap" in out

    def test_merge_gap_within_block_shows_preview(self):
        s1 = Segment(start=0x0100, data=bytearray(20))
        s2 = Segment(start=0x0120, data=bytearray(20))
        out = render([s1, s2], merge_gap=64)
        assert "gap: 12 B" in out  # gap = 0x0120 - (0x0100 + 20) = 12
