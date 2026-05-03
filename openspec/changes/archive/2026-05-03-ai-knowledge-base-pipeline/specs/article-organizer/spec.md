## ADDED Requirements

### Requirement: 生成 Article JSON

Organizer SHALL 读取 raw 文件，为每个有 analyzed_at 字段的 item 生成对应的 article JSON 文件。

#### Scenario: 生成 article 文件
- **WHEN** raw 文件包含已分析的 items
- **THEN** 为每个 item 创建 `knowledge/articles/{date}-{slug}.json`

#### Scenario: slug 生成
- **WHEN** 处理 item with id = "openai/agents-sdk"
- **THEN** 生成 slug = "openai-agents-sdk"

#### Scenario: id 生成
- **WHEN** 生成 article id
- **THEN** 使用格式 "kb-{date}-{seq}"，如 "kb-2026-03-17-001"

### Requirement: Article Schema 字段

Article JSON SHALL 包含完整字段：id, title, source, source_id, url, summary, tags, relevance_score, collected_at, analyzed_at, organized_at, status。

#### Scenario: 完整字段写入
- **WHEN** 生成 article JSON
- **THEN** 写入所有字段，status 固定为 "published"，organized_at 为当前时间

### Requirement: 避免重复

Organizer SHALL 检查 index.json，若 slug 已存在则跳过该 article。

#### Scenario: slug 已存在
- **WHEN** 处理 slug = "openai-agents-sdk"
- **THEN** 检查 index.json 中 articles 是否已存在相同 slug，若存在则跳过

### Requirement: 维护 index.json

Organizer SHALL 在每次生成 article 后更新 `knowledge/articles/index.json`。

#### Scenario: 更新 index.json
- **WHEN** 生成新的 article
- **THEN** 更新 index.json 的 updated_at, count 和 articles 数组

#### Scenario: index.json 不存在
- **WHEN** 生成第一个 article 且 index.json 不存在
- **THEN** 创建 index.json 并初始化 articles 数组