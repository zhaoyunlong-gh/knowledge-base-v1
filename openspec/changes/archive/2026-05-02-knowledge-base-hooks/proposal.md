## Why

当前 AI 知识库 pipeline 缺少数据质量把关机制。运行中发现存在数据问题：relevance_score 超范围（8.40）、summary 过短（仅 3 字）、空标签等问题。需要通过校验和质量评分脚本在 pipeline 后置阶段进行质量把控。

## What Changes

- 新增 `hooks/validate_json.py` — JSON 结构校验脚本
  - 校验 article 和 raw 文件的必需字段、数据类型、格式
  - 发现错误直接报错，不自动修复
- 新增 `hooks/check_quality.py` — 五维度质量评分脚本
  - 摘要质量 (25分)、技术深度 (25分)、格式规范 (20分)、标签精度 (15分)、空洞词检测 (15分)
  - 满分 100，60 分以下标记为"需改进"
- 作为 pipeline 后置检查
- 同时支持对 `knowledge/articles/` 和 `knowledge/raw/` 目录下的文件进行校验

## Capabilities

### New Capabilities

- `json-validator`: 对 article JSON 和 raw JSON 进行结构校验，验证必需字段存在性、字段类型正确性、数值范围合法性、时间戳格式合规性
- `quality-scorer`: 对 article JSON 进行五维度质量评分，检测空洞词，计算加权总分

### Modified Capabilities

（无）

## Impact

- 新增 `hooks/` 目录，包含 `validate_json.py` 和 `check_quality.py`
- 作为 pipeline 后置检查，可在运行 `python -m pipeline.run` 后独立执行
- 依赖标准库（json, re, datetime），无需额外依赖