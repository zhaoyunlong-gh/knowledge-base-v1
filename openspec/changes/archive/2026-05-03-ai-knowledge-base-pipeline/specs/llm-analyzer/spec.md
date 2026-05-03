## ADDED Requirements

### Requirement: LLM 分析 Repo 生成洞见

Analyzer SHALL 对每个 repo 调用 LLM API 生成结构化分析，包含 summary, relevance_score, score_breakdown, tags。

#### Scenario: 成功分析 Repo
- **WHEN** 调用 analyze_repo(repo_info)
- **THEN** 返回包含 summary, relevance_score, score_breakdown, tags, analyzed_at 的字典

#### Scenario: 分析结果写入 raw 文件
- **WHEN** 分析完成一个 repo
- **THEN** 将分析结果追加到 raw 文件对应 item 的 insights 字段

#### Scenario: LLM API 超时
- **WHEN** LLM API 请求超时（30s）
- **THEN** 抛出异常，流程 abort，日志记录失败 repo

#### Scenario: LLM API 返回错误
- **WHEN** LLM API 返回非 200 状态码
- **THEN** 抛出异常，流程 abort，日志记录错误详情

### Requirement: relevance_score 计算

Analyzer SHALL 计算 0.0-1.0 的 relevance_score，综合考虑 tech_depth, practical_value, timeliness, community_heat, domain_match。

#### Scenario: 综合评分
- **WHEN** 完成 repo 分析
- **THEN** relevance_score = weighted_average(score_breakdown 各维度)

### Requirement: tags 生成

Analyzer SHALL 生成 3-8 个标签，反映项目的主要技术栈、应用场景和特性。

#### Scenario: 生成有效标签
- **WHEN** 分析 repo 完成
- **THEN** 生成 3-8 个 tags，如 ["agent-framework", "multi-agent", "python", "openai"]

### Requirement: 批量处理

Analyzer SHALL 按顺序处理 raw 文件中的所有 items，每个处理完成后追加结果。

#### Scenario: 批量处理所有 items
- **WHEN** 调用 analyze_all(raw_file_path)
- **THEN** 遍历所有 items，逐一调用 LLM 分析并更新 raw 文件

### Requirement: 请求间隔

Analyzer SHALL 在每个 LLM 请求间添加 1 秒延迟，避免触发限流。

#### Scenario: 请求间隔
- **WHEN** 完成一个 repo 分析
- **THEN** sleep 1 秒后再处理下一个