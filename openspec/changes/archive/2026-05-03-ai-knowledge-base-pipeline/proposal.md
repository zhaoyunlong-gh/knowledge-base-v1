## Why

当前缺乏自动化的 AI 知识采集系统。需要从 GitHub Trending 采集 AI 相关项目，经 AI 分析提炼洞见，整理成结构化的知识条目，以便后续检索和使用。手动整理耗时且难以规模化。

## What Changes

- 新增 `pipeline/` 目录，包含 Collector、Analyzer、Organizer 三个模块
- **Collector**: 获取 GitHub Trending Top 50 AI 相关项目，输出到 `raw/github-trending-{date}.json`
- **Analyzer**: 对每个项目调用 LLM 分析，追加 summary、relevance_score、score_breakdown、tags 到 raw 文件
- **Organizer**: 读取 raw 文件，生成 `knowledge/articles/{slug}.json`，维护 `knowledge/articles/index.json`
- 手动触发运行，支持配置 LLM API（DeepSeek / Qwen / OpenAI）
- 失败时 abort 并记录日志

## Capabilities

### New Capabilities

- `github-collector`: 从 GitHub GraphQL API 获取 Trending 项目，支持 Top N 过滤
- `llm-analyzer`: 调用 OpenAI 兼容 API 对项目进行分析，输出结构化洞见
- `article-organizer`: 将分析结果转换为统一 article schema，维护索引文件
- `model-client`: 统一的 LLM 客户端，支持 API Key / Base URL / Model 配置
- `pipeline-runner`: 串联三个模块的手动触发入口

### Modified Capabilities

（无）

## Impact

- 新增 `pipeline/` 目录结构
- 依赖 `python-dotenv` 读取环境变量
- 依赖 `requests` 调用 GitHub API 和 LLM API
- 输出到 `knowledge/raw/` 和 `knowledge/articles/` 目录