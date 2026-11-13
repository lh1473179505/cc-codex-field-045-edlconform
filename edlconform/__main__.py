from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import conform, probe


def cmd_probe(args: argparse.Namespace) -> int:
    fps = 25
    if args.policy:
        fps = int(json.loads(Path(args.policy).read_text()).get("record_fps", 25))
    info = probe.probe_paths(args.edl, args.index, fps=fps)
    text = probe.format_probe(info)
    if args.out:
        Path(args.out).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


def cmd_conform(args: argparse.Namespace) -> int:
    try:
        return conform.conform(args.edl, args.index, args.policy, args.timeline, args.mix, args.report)
    except conform.NotImplementedConform as e:
        sys.stderr.write(str(e) + "\n")
        return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="edlconform")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("probe", help="parse an EDL and reel index")
    sp.add_argument("--edl", required=True)
    sp.add_argument("--index", required=True)
    sp.add_argument("--policy", default=None)
    sp.add_argument("--out", default=None)
    sp.set_defaults(func=cmd_probe)
    sc = sub.add_parser("conform", help="build a record timeline and mix")
    sc.add_argument("--edl", required=True)
    sc.add_argument("--index", required=True)
    sc.add_argument("--policy", required=True)
    sc.add_argument("--timeline", required=True)
    sc.add_argument("--mix", required=True, help="output WAV mix of the record timeline")
    sc.add_argument("--report", required=True)
    sc.set_defaults(func=cmd_conform)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
