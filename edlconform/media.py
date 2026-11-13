"""Reel index loader. Probe uses this; please reuse it."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import wavio
from .timecode import parse_tc, to_framecount


class MediaError(ValueError):
    pass


@dataclass
class Reel:
    name: str
    path: str
    start_tc: object
    sample_rate: int
    channels: int
    frames_audio: int
    pulldown: str | None  # None, "23.976->29.97", "24->25"


def load_index(path: str, fps: int) -> dict[str, Reel]:
    doc = json.loads(Path(path).read_text())
    base = Path(path).resolve().parent
    out = {}
    for item in doc["reels"]:
        wav_path = str((base / item["path"]).resolve()) if not Path(item["path"]).is_absolute() else item["path"]
        wav = wavio.read_wav(wav_path)
        start = parse_tc(item["start_tc"], fps, item.get("drop_frame", False))
        reel = Reel(item["name"], wav_path, start, wav.sample_rate, wav.channels, wav.frames, item.get("pulldown"))
        out[reel.name] = reel
    return out
