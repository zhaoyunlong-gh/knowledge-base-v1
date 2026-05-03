# AI 知识库

AI 相关知识的采集、分析、整理系统。从 GitHub Trending 等渠道采集内容，通过 LLM 分析，输出结构化知识条目。

## 业务流程

```
Collector → Analyzer → Organizer → Hooks
  采集        分析       整理       校验
```

1. **Collector** - 从 GitHub Trending 采集 AI 相关项目
2. **Analyzer** - 调用 LLM 分析项目，生成摘要、评分、标签
3. **Organizer** - 整理为标准化 JSON 格式，更新索引
4. **Hooks** - JSON 校验 + 质量检查

## 目录结构

```
.
├── knowledge/
│   ├── raw/                      # 原始采集数据
│   │   └── github-trending-*.json
│   └── articles/                 # 知识条目（已整理）
│       ├── *.json               # 单个知识条目
│       ├── index.json           # 知识库索引
│       ├── validation_failed.log
│       └── quality_failed.log
├── pipeline/
│   ├── collector.py             # GitHub Trending 采集器
│   ├── analyzer.py              # LLM 分析器
│   ├── organizer.py             # 文章整理器
│   ├── model_client.py          # 统一 LLM 客户端
│   └── run.py                   # CLI 入口
├── hooks/
│   ├── validate_json.py         # JSON 结构校验
│   └── check_quality.py         # 质量评分
├── openspec/                    # OpenSpec 工作流
└── requirements.txt
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 等配置
```

### 3. 运行完整流程

```bash
python3 pipeline/run.py
```

### 4. 运行 Hooks 校验

```bash
python3 hooks/validate_json.py knowledge/articles/
python3 hooks/check_quality.py knowledge/articles/
```

## 知识条目格式

```json
{
  "id": "kb-2026-05-02-009",
  "title": "MachineLearningNotebooks",
  "source": "github-trending",
  "source_id": "Azure/MachineLearningNotebooks",
  "url": "https://github.com/Azure/MachineLearningNotebooks",
  "summary": "微软官方Azure机器学习Python SDK的Jupyter笔记本示例集",
  "tags": ["azure", "machine-learning", "python"],
  "relevance_score": 0.71,
  "collected_at": "2018-08-17T17:29:14Z",
  "analyzed_at": "2026-05-02T14:35:30.690519Z",
  "organized_at": "2026-05-02T15:43:19.471399Z",
  "status": "published"
}
```

## Pipeline 模块

### Collector

从 GitHub GraphQL API 获取 Trending 项目，支持：
- 按编程语言过滤
- 按时间范围过滤（daily/weekly/monthly）
- 自动跳过已处理项目（增量采集）

### Analyzer

使用 LLM 分析每个项目，生成：
- `summary` - 中文摘要
- `relevance_score` - 相关性评分 (0.0-1.0)
- `score_breakdown` - 五维评分
- `tags` - 标签数组

### Organizer

- 从 raw 数据生成标准化 article
- 去重检查
- 更新 index.json 索引

## Hooks

### validate_json.py

校验知识条目的 JSON 结构：
- 必需字段完整性
- `relevance_score` 范围 (0.0-1.0)
- 时间戳格式 (ISO 8601)
- ID 格式 (`kb-YYYY-MM-DD-NNN`)

### check_quality.py

五维质量评分：
- summary_quality - 摘要质量
- tech_depth - 技术深度
- format - 格式规范
- tag_accuracy - 标签准确度
- hollow_word_detection - 空洞词检测

## LLM 配置

支持 OpenAI 兼容 API（DeepSeek / Qwen / OpenAI）：

```bash
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4o-mini
```

## License

MIT
