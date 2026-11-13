# conform 规则

默认策略见 `fixtures/policy.json`。记录时间线是 30 fps 非丢帧。

## EDL

- 解析必须走 `edl.parse_edl`。事件行是 CMX 3600 常见格式：`event reel track trans [dur] src_in src_out rec_in rec_out`。
- `C` 是切。`D` 是叠化，后面的整数是叠化持续帧数；叠化占用记录时间线上从该事件 `record_in` 起的 dur 帧，期间 A 事件（前一条同轨）和 B 事件（本条）要交叉淡化。
- `track` 为 `V` 的事件只进时间线不进 WAV 混合（公开夹具的媒体都是声音卷，视频事件只用来占位和核对句柄）。`A` / `A2` / `AA` 进混合。`AA` 表示 A1+A2 同时取同一段源。
- `* FROM CLIP NAME:` 注释写入时间线条目的 `clip_name`，不参与计算。
- 源入出与记录入出的时长必须一致（叠化事件除外：源时长等于记录时长）。若不一致，该事件 `reason_codes` 含 `duration_mismatch`，整体 reject。

## 卷号与句柄

- `fixtures/reels.json` 给出卷号、起始时间码、WAV 路径，以及可选的 `pulldown`。
- 源时间码要减去卷的 `start_tc` 再换到采样。取音频时还要向外扩 `handle_frames`（默认 8 帧）写进时间线的 `handle_in` / `handle_out`，但 `--mix` 只渲染记录入出之间的样本，不要把句柄混进节目声。
- 若句柄已经超出文件边界，把句柄钳在文件起止，并记录 `handle_clamped`。若连节目入出都超出文件，reject，原因 `offline_media`。

## 3:2 下拉

- 卷 `24A` 的 `pulldown` 为 `24->30`。该卷的 WAV 是按 24 fps 画格长度录的参考声（48 kHz，每一画格对应 2000 个采样）。
- 放到 30 fps 记录时间线时，必须按 3:2（2:3）场序展开：每 4 个源画格变成 5 个记录画格，即源时长 4/24 秒对应记录时长 5/30 秒。采样上按这个比例做离散映射：每个 30 fps 记录画格取对应 24 fps 源画格的整段音频（2000 采样），被重复的画格就把那 2000 采样再写一遍，不要做变速重采样。
- EDL 里该卷的源时间码按 24 fps 计（仍然写成四段式，帧字段 0–23）。记录时间码按 30 fps 计。因此这条事件的“源时长帧数”和“记录时长帧数”本来就会不同，这是唯一允许的 duration 例外，不要报 `duration_mismatch`。

## 混合

- `--mix` 写 48 kHz stereo 16-bit WAV。A 进左，A2 进右，AA 两路都进。叠化期间做等功率交叉（-3 dB 中点，正弦/余弦淡化），不要线性相加后削波不管。
- 时间线从记录 00:00:00:00 起到最后一条事件的 `record_out`。没有事件覆盖的区间写静音。

## 退出码

- 成功写出时间线、混合和完整报告：退出 0，`decision` 为 `ok`。
- 有 offline 或 duration 错误：退出 1，仍尽量写出能确定的部分。
- EDL 或索引无法解析：退出 2。
