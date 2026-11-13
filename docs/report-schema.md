# 报告与时间线 schema

报告：

| 字段 | 类型 | 含义 |
|---|---|---|
| edl | string | |
| decision | string | `ok` 或 `reject` |
| reason_codes | string[] | |
| events_conformed | integer | |
| handle_clamped | integer | |
| mix_frames | integer | 输出 WAV 的采样帧数（每声道） |
| timeline | string | |

时间线 JSON 是一个 `events` 数组，每条含 event、reel、track、transition、source_in/out、record_in/out、handle_in/out（源时间码）、clip_name、pulldown、sample_range（输出 WAV 里的起止采样，切或叠化后的节目范围）。
