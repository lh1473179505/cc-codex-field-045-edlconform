"""SMPTE timecode arithmetic. Probe uses this; please reuse it."""

from __future__ import annotations

from dataclasses import dataclass


class TcError(ValueError):
    pass


LEGAL_RATES = {
    "24": (24, False),
    "25": (25, False),
    "30": (30, False),
    "30df": (30, True),
    "29.97": (30, False),  # non-drop counting at 30/1.001
    "29.97df": (30, True),
}


@dataclass(frozen=True)
class Timecode:
    hours: int
    minutes: int
    seconds: int
    frames: int
    drop_frame: bool
    nominal_fps: int  # 24, 25 or 30

    def __str__(self) -> str:
        sep = ";" if self.drop_frame else ":"
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}{sep}{self.frames:02d}"


def parse_tc(text: str, nominal_fps: int, drop_frame: bool | None = None) -> Timecode:
    text = text.strip()
    if ";" in text:
        drop = True
        parts = text.replace(";", ":").split(":")
    else:
        drop = False if drop_frame is None else drop_frame
        parts = text.split(":")
    if len(parts) != 4:
        raise TcError(f"bad timecode {text}")
    h, m, s, f = (int(x) for x in parts)
    if drop_frame is not None:
        drop = drop_frame
    tc = Timecode(h, m, s, f, drop, nominal_fps)
    _validate(tc)
    return tc


def _validate(tc: Timecode) -> None:
    if not (0 <= tc.hours < 24 and 0 <= tc.minutes < 60 and 0 <= tc.seconds < 60):
        raise TcError(f"out of range: {tc}")
    if not (0 <= tc.frames < tc.nominal_fps):
        raise TcError(f"frame out of range: {tc}")
    if tc.drop_frame:
        if tc.nominal_fps != 30:
            raise TcError("drop-frame is only defined for nominal 30")
        if tc.seconds == 0 and tc.minutes % 10 != 0 and tc.frames < 2:
            raise TcError(f"illegal drop-frame number {tc}")


def to_framecount(tc: Timecode) -> int:
    """Minutes-seconds-frames unfolded to a frame index from 00:00:00:00."""
    _validate(tc)
    if not tc.drop_frame:
        return ((tc.hours * 3600 + tc.minutes * 60 + tc.seconds) * tc.nominal_fps + tc.frames)
    # SMPTE 30 DF: drop 2 frames every minute except every 10th minute
    total_minutes = tc.hours * 60 + tc.minutes
    dropped = 2 * (total_minutes - total_minutes // 10)
    return (total_minutes * 60 + tc.seconds) * 30 + tc.frames - dropped


def from_framecount(n: int, nominal_fps: int, drop_frame: bool) -> Timecode:
    if n < 0:
        raise TcError("negative framecount")
    if not drop_frame:
        f = n % nominal_fps
        n //= nominal_fps
        s = n % 60
        n //= 60
        m = n % 60
        h = (n // 60) % 24
        return Timecode(h, m, s, f, False, nominal_fps)
    return _from_df_framecount(n)


def _from_df_framecount(n: int) -> Timecode:
    ten = 17982
    n = n % (24 * 6 * ten)
    blocks = n // ten
    rem = n % ten
    if rem < 1800:
        minutes = blocks * 10
        rem2 = rem
    else:
        rem -= 1800
        minutes = blocks * 10 + 1 + rem // 1798
        rem2 = rem % 1798 + 2
    frames = rem2 % 30
    secs = rem2 // 30
    h = (minutes // 60) % 24
    m = minutes % 60
    return Timecode(h, m, secs, frames, True, 30)


def add_frames(tc: Timecode, delta: int) -> Timecode:
    n = to_framecount(tc) + delta
    return from_framecount(n, tc.nominal_fps, tc.drop_frame)
