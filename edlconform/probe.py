"""Inventory an EDL and its reel index."""

from __future__ import annotations

import json

from . import edl, media
from .timecode import to_framecount


def probe_paths(edl_path: str, index_path: str, fps: int = 25) -> dict:
    doc = edl.parse_edl(edl_path, default_fps=fps)
    reels = media.load_index(index_path, fps)
    evs = []
    for e in doc.events:
        evs.append(
            {
                "event": e.event,
                "reel": e.reel,
                "track": e.track,
                "transition": e.transition,
                "trans_duration": e.trans_duration,
                "source_in": str(e.source_in),
                "source_out": str(e.source_out),
                "record_in": str(e.record_in),
                "record_out": str(e.record_out),
                "source_frames": to_framecount(e.source_out) - to_framecount(e.source_in),
                "record_frames": to_framecount(e.record_out) - to_framecount(e.record_in),
                "clip_name": e.clip_name,
                "reel_known": e.reel in reels,
            }
        )
    return {
        "edl": edl_path,
        "title": doc.title,
        "fcm_drop": doc.fcm_drop,
        "fps": doc.fps,
        "events": evs,
        "reels": {
            n: {
                "path": r.path,
                "start_tc": str(r.start_tc),
                "sample_rate": r.sample_rate,
                "channels": r.channels,
                "frames_audio": r.frames_audio,
                "pulldown": r.pulldown,
            }
            for n, r in reels.items()
        },
    }


def format_probe(info: dict) -> str:
    return json.dumps(info, ensure_ascii=False, indent=2)
