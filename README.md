# seekdb 全文索引性能复盘

一个独立的 Agent Skill：核对 seekdb 全文索引基准报告的参数与命中数，按构建、分词、查询三类等权比较性能，定位退化，避免把版本间改善误当成相对官方基线的得分。

## 使用

将本目录作为 Skill 安装到支持 Agent Skills 的客户端。入口为 [SKILL.md](SKILL.md)，只有该文件也可以按照其步骤分析报告，不依赖外部服务或 API Key。

完整源码另提供 Python 3.10+ 标准库辅助脚本：

```bash
python3 scripts/compare_metrics.py before.json after.json
```

JSON 可以是完整的 `{"metrics": {...}}` 或指标对象。脚本要求配置与命中数一致、完整计时且所有耗时为有限正数；负收益也纳入平均。输出不预测未知基线下的正式分数，命中数一致也不等于证明全部结果相同。

该仓库只包含本原创 Skill 及辅助脚本，与私有比赛答题仓库独立。实际赛事规则以 [OceanBase 全文索引题面](https://oceanbase.yuque.com/org-wiki-obtech-vh7w9r/hc3pio/za7cfo5cazcrihhq) 为准。

License: [Apache-2.0](LICENSE)。
