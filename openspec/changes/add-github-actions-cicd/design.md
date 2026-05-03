## Context

项目当前依赖手动运行 `pipeline/run.py` 采集 AI 知识内容。为实现自动化，在 GitHub Actions 上构建 CI/CD 流水线，支持每日定时和手动触发采集。

**当前状态：**
- `pipeline/run.py`: 串联 Collector → Analyzer → Organizer
- `hooks/validate_json.py` + `hooks/check_quality.py`: 输出校验
- `requirements.txt`: python-dotenv, requests

**约束：**
- 环境变量（API keys）通过 GitHub Secrets 管理，不直接暴露在 workflow 文件中
- GitHub Actions runner 使用 ubuntu-latest，包含 Python 3.11

## Goals / Non-Goals

**Goals:**
- 每日自动采集 AI 热点内容（GitHub Trending）
- 支持手动触发采集
- 采集完成后自动校验并提交结果到仓库

**Non-Goals:**
- 不实现 PR review 或部署到生产环境
- 不支持除 ubuntu-latest 以外的其他 runner

## Decisions

**1. 触发方式：schedule + workflow_dispatch**
- `schedule`: 定时每日 UTC 00:00 运行（北京时间 08:00）
- `workflow_dispatch`: 支持手动在 GitHub Actions 页面触发
- 选择 cron 表达式而非第三方定时服务，零额外依赖

**2. 依赖安装使用 pip（而非 Poetry/Conda）**
- 项目依赖简单（仅 2 个 pip 包）
- Actions 的 `actions/setup-python@v5` 内置 pip 缓存
- 无需额外配置文件

**3. 使用 `fetch-depth: 0` 全量拉取 git 历史**
- 目的：支持 commit 阶段计算 diff
- 替代方案：单独 checkout specific SHA 或使用 `persist-credentials: false`
- 选择全量拉取，因 workflow 运行频次低（每日一次），开销可接受

**4. commit message 使用 `[skip ci]` 标记**
- 目的：避免 CI 循环触发（commit 触发新 workflow）
- 实际场景：commit 由 workflow 完成，`[skip ci]` 不会生效，但作为最佳实践保留

## Risks / Trade-offs

- **[Risk]** GitHub Token 权限不足导致 push 失败 → **Mitigation**: 确保 token 有 `contents: write` 权限（默认 repo scope 包含）
- **[Risk]** LLM API 调用失败导致 pipeline 中断 → **Mitigation**: `pipeline/run.py` 有异常捕获，返回 exit code 1，CI 会标记为失败
- **[Trade-off]** 定时任务可能与高峰期撞车 → 选 UTC 00:00 避开北京时间白天，但 API 限流风险由调用方（LLM API）承担

## Migration Plan

1. 合并 `.github/workflows/daily-collect.yml` 到 main 分支
2. 在 GitHub 仓库 Settings → Secrets 添加 4 个环境变量
3. 手动触发一次 `workflow_dispatch` 验证流程
4. 确认 `knowledge/` 目录正确更新并自动 commit

**回滚：** 若发现问题，在 GitHub Actions 页面禁用 workflow 或删除 `.github/` 目录。

## Open Questions

- 是否需要添加失败通知（如 Slack/Email）？
- 是否需要在 commit 前运行测试？