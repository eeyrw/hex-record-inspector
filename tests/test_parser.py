"""Tests for the Intel HEX parser."""

import pytest

from hexinspector.parser import ParseError, load, load_file


def _temp_hex(tmp_path, content: str) -> str:
    p = tmp_path / "test.hex"
    p.write_text(content)
    return str(p)


class TestLoadBasic:
    def test_empty(self):
        assert load("") == []

    def test_eof_only(self):
        assert load(":00000001FF") == []

    def test_single_data_record(self):
        segs = load(":10010000214601360121470136007EFE09D2190140")
        assert len(segs) == 1
        assert segs[0].start == 0x0100
        assert segs[0].size == 16

    def test_two_adjacent_records_merge(self):
        hex_str = (
            ":10010000214601360121470136007EFE09D2190140\n"
            ":10011000214601360121470136007EFE09D2190130\n"
        )
        segs = load(hex_str)
        assert len(segs) == 1
        assert segs[0].size == 32

    def test_gap_produces_two_segments(self):
        hex_str = (
            ":10010000214601360121470136007EFE09D2190140\n"
            ":10020000214601360121470136007EFE09D219013F\n"
        )
        segs = load(hex_str)
        assert len(segs) == 2


class TestRecordTypes:
    def test_extended_linear_address(self):
        hex_str = ":020000040001F9\n:10010000214601360121470136007EFE09D2190140\n"
        segs = load(hex_str)
        assert segs[0].start == 0x00010100

    def test_extended_segment_address(self):
        hex_str = ":020000020000FC\n:10010000214601360121470136007EFE09D2190140\n"
        segs = load(hex_str)
        assert segs[0].start == 0x0100

    def test_eof_stops_parsing(self):
        hex_str = (
            ":10010000214601360121470136007EFE09D2190140\n"
            ":00000001FF\n"
            ":10020000214601360121470136007EFE09D219013F\n"
        )
        segs = load(hex_str)
        assert len(segs) == 1


class TestValidation:
    def test_skips_non_hex_lines(self):
        segs = load("nothex\n:10010000214601360121470136007EFE09D2190140\n")
        assert len(segs) == 1

    def test_bad_checksum(self):
        with pytest.raises(ParseError, match="checksum"):
            load(":10010000214601360121470136007EFE09D21901FF")

    def test_odd_hex_length(self):
        with pytest.raises(ParseError, match="odd"):
            load(":10010000214601360121470136007EFE09D2190140E")


def test_load_file(tmp_path):
    p = tmp_path / "f.hex"
    p.write_text(":10010000214601360121470136007EFE09D2190140\n:00000001FF\n")
    segs = load_file(str(p))
    assert len(segs) == 1
    assert segs[0].start == 0x0100
