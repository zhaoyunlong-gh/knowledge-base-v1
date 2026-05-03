# CLAUDE.md - AI 知识库

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AI 相关知识的采集，分析，整理。采集来自 GitHub Trending、Hacker News 等源数据，进行分析，并整理为结构化，可检索的知识条目。

## 项目价值

- 每日自动采集 AI Agent/Claude Code/SDD 等相关技术文章和开源项目
- 通过 AI Agent 完成采集，分析，整理三阶段流水线
- 输出格式统一的 json 的知识条目，以便于后续检索

## 目录结构

```
knowledge/
├── raw/                              # 原始采集数据
│   ├── github-trending-{date}.json  # GitHub Trending 原始数据
│   └── filtered-{date}.json          # 过滤日志
├── articles/                         # 知识条目（已整理）
│   ├── {date}-{slug}.json           # 单个知识条目
│   └── index.json                    # 知识库索引
└── agents/                           # Agent 定义
│   ├── collector.md                  # 采集 Agent
│    ├── analyzer.md                   # 分析 Agent
│    └── organizer.md                  # 整理 Agent
├── pipeline/
│   ├── model_client.py          ← 统一 LLM 客户端
│   ├── pipeline.py              ← 四步流水线
│   └── rss_sources.yaml         ← RSS 源配置
├── hooks/
│   ├── validate_json.py         ← JSON 校验脚本
│   └── check_quality.py         ← 质量评分脚本
```

## Agent 角色

### @collector — 内容采集员

- **职责**：从 GitHub、RSS、技术博客等渠道采集 AI 领域内容
- **触发**：`@collector 采集本周 AI 热点` 或 `@collector 搜索 MCP 相关项目`
- **定义文件**：`.opencode/agents/collector.md`
- **关联 Skill**：`collect-articles`

### @analyzer — 内容分析师

- **职责**：对采集的内容进行摘要、打分、分类
- **触发**：`@analyzer 分析这篇文章的技术价值` 或 `@analyzer 对比这两个框架`
- **定义文件**：`.opencode/agents/analyzer.md`
- **关联 Skill**：`analyze-content`

### @organizer — 内容整理

- **职责**：格式化、去重、质量把关，输出标准化 JSON
- **触发**：`@organizer 整理今天采集的内容` 或 `@organizer 检查文章格式`
- **定义文件**：`.opencode/agents/organizer.md`
- **关联 Skill**：`format-output`