## Context

AI 知识库需要从 GitHub Trending 采集 AI 相关项目，经 LLM 分析后整理成结构化知识条目。当前系统缺乏自动化的采集 pipeline，纯手动整理无法规模化。

**当前状态：**
- 目录结构已建立 (`knowledge/raw/`, `knowledge/articles/`)
- 无任何 Python 代码
- 无现有的 LLM 集成

**约束：**
- Python 3.x
- 手动触发（非定时）
- 依赖 OpenAI 兼容 API（通过 .env 配置）
- 失败时 abort 并记录日志

**利益相关方：**
- 知识库维护者（手动触发 pipeline）
- 知识库消费者（读取 articles/ 下的 JSON 文件）

## Goals / Non-Goals

**Goals:**
- 实现完整的 Collector → Analyzer → Organizer 数据流
- 支持配置多个 LLM Provider（DeepSeek / Qwen / OpenAI）
- 生成符合统一 schema 的 article JSON 文件
- 维护 article 索引（index.json）

**Non-Goals:**
- 不实现定时自动运行（手动触发即可）
- 不实现 Web UI 或 API
- 不实现知识条的更新/删除（只新增）
- 不实现全文搜索（索引文件仅维护元数据）

## Decisions

### 1. 使用 GitHub GraphQL API 而非 REST

**决定：** 使用 GitHub GraphQL API 获取 Trending 数据

**理由：**
- GraphQL 可以一次请求获取 repo 的 name、description、stars、topics 等多字段
- 避免 REST 多次请求的开销

**备选：** 使用 github-trending-api 第三方库 → 放弃，因为不稳定

### 2. raw 文件追加模式，不覆盖

**决定：** Collector 运行结果追加到 `raw/github-trending-{date}.json`，Analyzer 在同一文件追加分析结果

**理由：**
- 多次运行不丢失历史数据
- Analyzer 可以在已有 raw 数据上增量分析

**格式：**
```json
{
  "source": "github-trending",
  "collected_at": "2026-03-17T10:30:00Z",
  "query": "AI OR LLM OR agent, past 7 days, sorted by stars",
  "count": 50,
  "items": [
    { /* repo 数据 */ },
    { /* repo 数据 + analyzer 追加字段 */ }
  ]
}
```

### 3. LLM 调用使用 JSON Mode + 结构化输出

**决定：** Analyzer 调用 LLM 时使用 JSON Mode，prompt 要求输出结构化 JSON

**理由：**
- 避免解析自然语言回复的不确定性
- 确保输出字段完整

**Prompt 设计：**
```
你是一个 AI 技术分析师。分析以下 GitHub repo，返回 JSON：

{
  "summary": "项目一句话描述",
  "relevance_score": 0.0-1.0,
  "score_breakdown": {
    "tech_depth": 0.0-1.0,
    "practical_value": 0.0-1.0,
    "timeliness": 0.0-1.0,
    "community_heat": 0.0-1.0,
    "domain_match": 0.0-1.0
  },
  "tags": ["tag1", "tag2", ...]
}

Repo 信息：
name: {name}
description: {description}
stars: {stars}
topics: {topics}
```

### 4. model_client 统一封装

**决定：** 所有 LLM 调用通过 `pipeline/model_client.py` 统一客户端

**理由：**
- 统一错误处理、重试逻辑、超时配置
- 切换 provider 无需修改业务代码

**接口设计：**
```python
class ModelClient:
    def __init__(self, api_key, base_url, model)
    def analyze(self, repo_info: dict) -> dict  # 返回分析结果
```

### 5. Organizer 生成 article 时生成 slug

**决定：** slug 从 repo 名派生（`openai/agents-sdk` → `openai-agents-sdk`）

**理由：**
- 避免文件名冲突
- 保持与 source_id 的关联性

**Article 文件命名：** `{date}-{slug}.json`（如 `2026-03-17-openai-agents-sdk.json`）

### 6. index.json 由 Organizer 维护

**决定：** 每次生成 article 时，更新 `knowledge/articles/index.json`

**index.json 格式：**
```json
{
  "updated_at": "2026-03-17T12:00:00Z",
  "count": 150,
  "articles": [
    { "id": "kb-2026-03-17-001", "slug": "openai-agents-sdk", "path": "2026-03-17-openai-agents-sdk.json" },
    ...
  ]
}
```

## Risks / Trade-offs

- **[Risk] GitHub API 限流** → Mitigation：添加请求间隔（sleep 1s），超过限流时 abort 并提示用户
- **[Risk] LLM API 超时或失败** → Mitigation：abort 整个流程，日志记录失败项目和错误信息
- **[Risk] 重复运行生成重复 article** → Mitigation：index.json 检查 slug 是否已存在，存在则跳过
- **[Risk] GitHub trending 数据每日变化** → Trade-off：不处理历史 trending，只采集当天数据

## Open Questions

1. GitHub API 是否需要认证 token？未认证是否有足够配额？
2. LLM temperature 设置多少合适？（建议 0.3 保持一致性）
3. score_breakdown 的五个维度（tech_depth, practical_value, timeliness, community_heat, domain_match）是否需要可配置？
4. 如果某个 repo 分析失败，是跳过该 repo 还是整个流程 abort？（当前决策：abort）