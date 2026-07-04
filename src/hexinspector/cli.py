"""CLI entrypoint for the Intel HEX inspector."""

from __future__ import annotations

import argparse

from .parser import load_file
from .visualizer import render, render_summary


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    segments = load_file(args.file)
    if args.brief:
        print(render_summary(segments))
    else:
        print(render(segments, per_line=args.width, merge_gap=args.merge_gap))


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Intel HEX inspector with ASCII art visualization.")
    p.add_argument("file", help="Path to an Intel HEX file")
    p.add_argument(
        "-w", "--width", type=int, default=16, metavar="N", help="Bytes per row (default: 16)"
    )
    p.add_argument("-b", "--brief", action="store_true", help="Show only a summary line")
    p.add_argument(
        "-m",
        "--merge-gap",
        type=int,
        default=0,
        metavar="N",
        help="Group segments within N bytes of each other (default: 0 = no grouping)",
    )
    return p.parse_args(argv)


if __name__ == "__main__":
    main()
