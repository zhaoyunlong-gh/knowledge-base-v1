## Context

当前 AI 知识库 pipeline 已实现 Collector → Analyzer → Organizer 数据流，但运行中出现了数据质量问题：
- `relevance_score` 超范围（8.40，正常应 0-1）
- `summary` 过短（仅 3 字）
- `tags` 为空数组
- 缺乏统一的格式校验和质量评估机制

这些问题的根源是 LLM 输出不够稳定，以及缺乏后置校验。

## Goals / Non-Goals

**Goals:**
- 实现 `validate_json.py` 对 article 和 raw JSON 进行结构校验
- 实现 `check_quality.py` 对 article JSON 进行五维度质量评分
- 提供清晰的错误报告，指出具体问题所在
- 作为 pipeline 后置检查，不修改原始数据

**Non-Goals:**
- 不自动修复错误（报错而非修正）
- 不修改 pipeline 核心逻辑
- 不实现自动化修复或重新分析

## Decisions

### 1. validate_json.py 校验规则

**Article 文件校验：**
```python
REQUIRED_ARTICLE_FIELDS = [
    "id", "title", "source", "source_id", "url",
    "summary", "tags", "relevance_score",
    "collected_at", "analyzed_at", "organized_at", "status"
]

VALIDATION_RULES = {
    "id": lambda v: v.startswith("kb-") and len(v) == 14,  # kb-YYYY-MM-DD-NNN
    "relevance_score": lambda v: 0.0 <= v <= 1.0,
    "tags": lambda v: isinstance(v, list) and len(v) > 0,
    "status": lambda v: v == "published",
    # 时间戳格式: ISO 8601
    "collected_at": is_iso8601,
    "analyzed_at": is_iso8601,
    "organized_at": is_iso8601,
}
```

**Raw 文件校验：**
```python
REQUIRED_RAW_FIELDS = ["source", "collected_at", "query", "count", "items"]

# items 中的每个 item 应有：id, title, description, url, stars
```

### 2. check_quality.py 五维度评分

```
┌──────────────────────────────────────────────────────────────┐
│  五维度评分（满分 100 分）                                      │
├──────────────────────────────────────────────────────────────┤
│  ① 摘要质量 (25分)                                            │
│     - 长度 40-100 字: 25分                                     │
│     - 长度 20-40 字: 15分                                      │
│     - 长度 <20 字: 0分                                         │
│                                                              │
│  ② 技术深度 (25分)                                            │
│     - relevance_score × 25                                    │
│                                                              │
│  ③ 格式规范 (20分)                                            │
│     - 必需字段齐全: 10分                                       │
│     - 时间戳格式正确: 5分                                      │
│     - url 格式正确: 5分                                        │
│                                                              │
│  ④ 标签精度 (15分)                                            │
│     - tags 数量 5-8 个: 15分                                  │
│     - tags 数量 3-4 或 9-10: 10分                             │
│     - tags 数量 <3 或 >10: 5分                                │
│                                                              │
│  ⑤ 空洞词检测 (15分)                                          │
│     - 检测摘要中的空洞词                                       │
│     - 无空洞词: 15分                                          │
│     - 1-2 个空洞词: 8分                                        │
│     - >2 个空洞词: 0分                                        │
└──────────────────────────────────────────────────────────────┘
```

### 3. 空洞词列表

```python
HOLLOW_WORDS = [
    "这个项目", "该项目", "很不错", "非常好", "很棒",
    "值得推荐", "强烈推荐", "一系列", "各种", "诸多",
    "相关", "有关", "涉及", "一些", "某些", "很重要",
    "非常有意义", "值得关注"
]
```

### 4. CLI 接口设计

```bash
# 校验 article 目录
python hooks/validate_json.py knowledge/articles/

# 校验 raw 目录
python hooks/validate_json.py knowledge/raw/

# 质量评分
python hooks/check_quality.py knowledge/articles/

# 指定单个文件
python hooks/validate_json.py knowledge/articles/2026-05-02-wepe-MachineLearning.json

# 输出 JSON 格式报告
python hooks/check_quality.py knowledge/articles/ --format json
```

### 5. 输出格式

**validate_json.py 输出：**
```json
{
  "passed": false,
  "errors": [
    {
      "file": "2026-05-02-wepe-MachineLearning.json",
      "field": "relevance_score",
      "expected": "0.0-1.0",
      "actual": 8.40
    },
    {
      "file": "2026-05-02-xxx.json",
      "field": "summary",
      "reason": "too short (3 chars)"
    }
  ],
  "summary": {
    "total_files": 50,
    "valid_files": 48,
    "invalid_files": 2
  }
}
```

**check_quality.py 输出：**
```json
{
  "total_score": 72,
  "passed": true,
  "breakdown": {
    "summary_quality": 15,
    "tech_depth": 13.75,
    "format": 20,
    "tag_accuracy": 15,
    "hollow_word_detection": 8
  },
  "issues": ["summary too short"]
}
```

## Risks / Trade-offs

- **[Risk] 空标签判断** → 当前规则要求 tags 非空，如果 AI 生成了空标签会报错
- **[Risk] 空洞词检测的准确性** → 基于关键词列表，可能有误判，但作为初步筛选足够

## Open Questions

1. 是否需要 `--fix` 参数自动修复可修复的问题？（如补全空 tags）
2. 是否需要 `--threshold` 参数调整质量评分阈值？