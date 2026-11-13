"""CMX 3600 EDL parser. Probe uses this; please reuse it."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .timecode import Timecode, parse_tc


class EdlError(ValueError):
    pass


@dataclass
class EdlEvent:
    event: int
    reel: str
    track: str  # e.g. V, A, A2, AA, B
    transition: str  # C, D, Wxxx, KB, etc.
    trans_duration: int | None
    source_in: Timecode
    source_out: Timecode
    record_in: Timecode
    record_out: Timecode
    comments: list[str] = field(default_factory=list)
    clip_name: str | None = None
    fcm_drop: bool | None = None


@dataclass
class Edl:
    title: str | None
    fcm_drop: bool
    events: list[EdlEvent]
    fps: int
    path: str


def _is_event_line(line: str) -> bool:
    parts = line.split()
    if len(parts) < 8:
        return False
    if not parts[0].isdigit():
        return False
    return True


def parse_edl(path: str, default_fps: int = 25) -> Edl:
    lines = Path(path).read_text().splitlines()
    title = None
    fcm_drop = False
    events: list[EdlEvent] = []
    pending_fcm = None
    fps = default_fps
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("TITLE:"):
            title = line.split(":", 1)[1].strip()
            continue
        if upper.startswith("FCM:"):
            val = line.split(":", 1)[1].strip().upper()
            fcm_drop = "DROP" in val and "NON" not in val
            pending_fcm = fcm_drop
            continue
        if _is_event_line(line):
            parts = line.split()
            # Standard: event reel track trans [dur] src_in src_out rec_in rec_out
            ev = int(parts[0])
            reel = parts[1]
            track = parts[2]
            trans = parts[3]
            idx = 4
            trans_dur = None
            # If next token is an integer and we still have 4 timecodes after it, it's duration
            def looks_tc(tok: str) -> bool:
                t = tok.replace(";", ":")
                return t.count(":") == 3
            remaining = parts[idx:]
            if remaining and remaining[0].isdigit() and len(remaining) >= 5:
                trans_dur = int(remaining[0])
                remaining = remaining[1:]
            if len(remaining) != 4 or not all(looks_tc(t) for t in remaining):
                raise EdlError(f"cannot parse event line: {line}")
            drop = fcm_drop if pending_fcm is None else pending_fcm
            # timecodes may use ; for drop
            src_in, src_out, rec_in, rec_out = (parse_tc(t, fps, drop if ";" in t else drop) for t in remaining)
            evto = EdlEvent(ev, reel, track, trans, trans_dur, src_in, src_out, rec_in, rec_out, [], None, drop)
            # following comment lines
            while i < len(lines) and lines[i].strip() and not _is_event_line(lines[i].strip()) and not lines[i].strip().upper().startswith("TITLE:") and not lines[i].strip().upper().startswith("FCM:"):
                c = lines[i].strip()
                evto.comments.append(c)
                if c.upper().startswith("* FROM CLIP NAME:"):
                    evto.clip_name = c.split(":", 1)[1].strip()
                if c.upper().startswith("FCM:"):
                    evto.fcm_drop = "DROP" in c.upper() and "NON" not in c.upper()
                i += 1
            events.append(evto)
            continue
        # ignore unknown
    return Edl(title, fcm_drop, events, fps, str(Path(path)))
