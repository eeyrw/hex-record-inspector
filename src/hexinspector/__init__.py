"""HexInspector — Intel HEX viewer with multi-segment ASCII art visualization."""

from .parser import ParseError, Segment, load, load_file
from .visualizer import render, render_summary

__all__ = ["Segment", "ParseError", "load", "load_file", "render", "render_summary"]
