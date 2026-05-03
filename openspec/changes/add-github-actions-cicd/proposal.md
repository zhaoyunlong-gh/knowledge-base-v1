## Why

目前项目依赖手动运行 `pipeline/run.py` 采集 AI 知识内容，缺乏自动化机制。通过 GitHub Actions 实现定时 + 手动触发，确保知识库每日更新。

## What Changes

- 新增 `.github/workflows/daily-collect.yml` — GitHub Actions 工作流
- 触发条件：`schedule` (每日 UTC 00:00) + `workflow_dispatch` (手动触发)
- 执行步骤：安装依赖 → 运行采集 pipeline → 运行 hooks 校验 → 自动提交结果
- 环境变量通过 GitHub Secrets 管理（LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, GITHUB_TOKEN）

## Capabilities

### New Capabilities
- `github-actions-pipeline`: GitHub Actions 自动化流水线，支持定时和手动触发，执行采集→分析→整理全流程

### Modified Capabilities
<!-- 无现有 spec 需要修改 -->

## Impact

- 新增 `.github/workflows/daily-collect.yml`
- 依赖 `requirements.txt` 中的 `python-dotenv` 和 `requests`
- 需要在 GitHub 仓库配置 4 个 Secrets
- `knowledge/` 目录将在每次 CI 后自动更新并提交