# edlconform

按 CMX 3600 回批时间线的工具。`probe` 已经能解析 EDL 和卷号索引。`conform` 还没有实现。

不要引入 OpenTimelineIO、ffmpeg-python 或任何 NLE 库，也不要使用 Docker。请复用 `edlconform.edl`、`edlconform.timecode` 和 `edlconform.media`。

## 命令

```
python -m edlconform probe --edl fixtures/cut.edl --index fixtures/reels.json --policy fixtures/policy.json
python -m edlconform conform \
  --edl fixtures/cut.edl \
  --index fixtures/reels.json \
  --policy fixtures/policy.json \
  --timeline /tmp/edlconform-timeline.json \
  --mix /tmp/edlconform-mix.wav \
  --report /tmp/edlconform-report.json
```

规则见 `docs/conform-rules.md`，报告与时间线字段见 `docs/report-schema.md`。
