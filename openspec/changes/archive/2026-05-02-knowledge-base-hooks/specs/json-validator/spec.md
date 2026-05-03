## ADDED Requirements

### Requirement: Article JSON 校验

validate_json.py SHALL 对 `knowledge/articles/` 下的每个 JSON 文件进行结构校验。

#### Scenario: 必需字段缺失
- **WHEN** article 文件缺少必需字段（如 id, title, summary）
- **THEN** 报告错误：缺少字段名

#### Scenario: relevance_score 超出范围
- **WHEN** relevance_score 不在 0.0-1.0 范围内
- **THEN** 报告错误：字段值超出范围

#### Scenario: tags 为空
- **WHEN** tags 字段为空数组
- **THEN** 报告错误：tags 不能为空

#### Scenario: id 格式错误
- **WHEN** id 不符合 kb-YYYY-MM-DD-NNN 格式
- **THEN** 报告错误：id 格式不正确

#### Scenario: status 不是 published
- **WHEN** status 字段值不是 "published"
- **THEN** 报告错误：status 应为 published

#### Scenario: 时间戳格式错误
- **WHEN** 时间戳字段不符合 ISO 8601 格式
- **THEN** 报告错误：时间戳格式不正确

### Requirement: Raw JSON 校验

validate_json.py SHALL 对 `knowledge/raw/` 下的每个 JSON 文件进行结构校验。

#### Scenario: 必需字段缺失
- **WHEN** raw 文件缺少 source, collected_at, query, count, items 字段
- **THEN** 报告错误：缺少必需字段

#### Scenario: items 中 item 字段不完整
- **WHEN** items 数组中的 item 缺少 id, title, description, url, stars
- **THEN** 报告错误：item 字段不完整

### Requirement: 批量校验

validate_json.py SHALL 支持对整个目录进行批量校验，输出汇总报告。

#### Scenario: 批量校验 articles
- **WHEN** 执行 `python hooks/validate_json.py knowledge/articles/`
- **THEN** 检查目录下所有 .json 文件，输出错误列表和汇总统计

#### Scenario: 批量校验 raw
- **WHEN** 执行 `python hooks/validate_json.py knowledge/raw/`
- **THEN** 检查目录下所有 .json 文件，输出错误列表和汇总统计

### Requirement: 错误报告格式

validate_json.py SHALL 输出 JSON 格式的错误报告。

#### Scenario: 错误报告结构
- **WHEN** 校验发现错误
- **THEN** 输出包含 passed, errors, summary 的 JSON 报告

#### Scenario: 无错误时
- **WHEN** 所有文件校验通过
- **THEN** 输出 passed: true 的 JSON 报告