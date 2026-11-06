---
name: seekdb-benchmark-review
description: 分析 seekdb 全文索引基准报告，按构建、分词和查询三类等权比较性能，定位退化并核对结果一致性。适用于评测 metrics JSON 或优化前后报告，不用于预测未知基线下的正式分数。
---

# seekdb 全文索引性能复盘

收到两份评测或本地基准报告时，先确认哪份是优化前、哪份是优化后，以及它们来自同机配对测试还是两次独立的正式评测。保留完整指标与提交号，不能用一次较快样本覆盖较慢样本。

## 先核对能否比较

- 两份报告中的 rows、batch、rounds、query_rounds、samples、warmup、skip_load 应一致。完整构建测试使用 skip_load=0。
- 检查中文、英文、混合、LIMIT 查询的命中数是否一致。命中数一致仍不能代替完整行 ID、分词结果和相关度验证。
- 本地对照需要相同的硬件、资源配置和计时范围。独立正式评测可以作现象对照，但环境波动不能直接归因于代码。
- 数据、SQL、计时逻辑、评分脚本或基线被修改时，先说明不可直接比较，不能把变化当作内核优化收益。

## 计算与解释

把平台返回的 `{"metrics": {...}}` 或指标对象分别保存为 JSON。依次验证参数相同、命中数相同、计时完整且均为有限正数，然后按下列公式计算。安装包可以仅包含本文件；此时直接用 Python 标准库读取 JSON 计算，无需外部服务。

完整源码目录另提供可选辅助脚本：

```bash
python3 scripts/compare_metrics.py before.json after.json
```

辅助脚本检查参数和命中数，输出每项耗时变化与三类等权结果。没有完整指标、参数/命中数不同或计时不是有限正数时拒绝计算；不因脚本未安装而跳过核验。

计分项分三类，先类内平均，再三类等权平均：

- 构建：build_ik_all_sec、build_ik_content_sec、build_beng_en_sec。
- 分词：tokenize_ik_avg_ms、tokenize_beng_avg_ms。
- 查询：query_cn_avg_ms、query_beng_avg_ms、query_mixed_avg_ms、query_limit_avg_ms。

单项耗时下降比例为 `(before-after)/before`。负数表示退化，仍须纳入平均。不要把九项直接平均；build_total_sec 和 select1_avg_ms 只作辅助诊断。

官方公布的性能原始分按综合改善率截断到 0～50% 后换算成 0～100 分，本题再折算到 50 分。只有明确的官方固定基线才可代入此公式。用上一提交作 before 得到的是版本间变化，不能据此预测平台成绩。

## 输出可核对的结论

1. 列出正式得分及其来源；没有新版本正式结果时明确标记为未评测。
2. 给出构建、分词、查询三类的变化，以及退化最大的指标。
3. 结合测量提出下一项验证：例如构建阶段日志、CPU 采样、同机交替复跑、完整结果差分；先验证原因再改代码。
4. 区分已测事实和推测。查询变快、总构建时间变短，都不保证综合得分提高。

示例：构建总耗时由 24.302 秒降至 5.494 秒，表示这两次回报的总构建时间下降约 77.39%；它与平台相对固定基线给出的综合改善率是不同口径。

规则来源：[OceanBase 2026 全文索引赛题](https://oceanbase.yuque.com/org-wiki-obtech-vh7w9r/hc3pio/za7cfo5cazcrihhq)。实际提交以当届题面和正式评测为准。

<!-- OB-S:TZOi1oM6U28vMHR5-eDOPg -->
