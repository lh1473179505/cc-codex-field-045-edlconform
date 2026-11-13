"""CMX 3600 conform. Not implemented in the initial snapshot."""

from __future__ import annotations


class NotImplementedConform(NotImplementedError):
    pass


def conform(edl_path: str, index_path: str, policy_path: str, timeline_path: str, mix_path: str, report_path: str) -> int:
    raise NotImplementedConform(
        "edlconform.conform.conform is not implemented yet; EDL / reel probe already work"
    )
