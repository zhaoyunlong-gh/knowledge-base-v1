## ADDED Requirements

### Requirement: GitHub Collector 获取 Trending 项目

Collector SHALL 从 GitHub GraphQL API 获取 Trending 项目列表。获取项目包括：name, description, stars, topics, created_at, updated_at。

#### Scenario: 成功获取 Top 50 项目
- **WHEN** 调用 Collector.fetch_trending(count=50)
- **THEN** 返回包含 50 个项目的列表，每个项目包含 id, title, description, url, stars, language, topics, created_at, updated_at 字段

#### Scenario: GitHub API 限流时
- **WHEN** GitHub API 返回 403 限流错误
- **THEN** 抛出异常并记录日志，流程 abort

#### Scenario: 网络错误时
- **WHEN** GitHub API 请求超时或网络错误
- **THEN** 抛出异常并记录日志，流程 abort

### Requirement: raw 文件追加写入

Collector SHALL 将获取的数据追加到 `raw/github-trending-{date}.json` 文件。文件不存在时创建，存在时读取并追加 items。

#### Scenario: 新文件创建
- **WHEN** raw 文件不存在
- **THEN** 创建文件并写入包含 source, collected_at, query, count, items 的 JSON

#### Scenario: 已有文件追加
- **WHEN** raw 文件已存在
- **THEN** 读取现有 JSON，将新 items 追加到 items 数组，写回文件

### Requirement: 过滤 AI 相关项目

Collector SHOULD 使用 GitHub search 过滤 AI/ML/LLM/Agent 相关项目。查询条件：AI OR LLM OR agent OR machine-learning OR deep-learning。

#### Scenario: 使用 GraphQL search 过滤
- **WHEN** 调用 fetch_trending
- **THEN** 使用 GraphQL search API 查询符合关键词的 repos

### Requirement: 按 stars 排序

Collector SHALL 按 stars 数量降序返回项目。

#### Scenario: 结果按 stars 排序
- **WHEN** 获取项目列表
- **THEN** 结果按 stars 降序排列