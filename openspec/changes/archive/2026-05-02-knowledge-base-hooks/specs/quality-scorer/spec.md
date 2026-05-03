## ADDED Requirements

### Requirement: 五维度质量评分

check_quality.py SHALL 对 article JSON 进行五维度质量评分，满分 100 分。

#### Scenario: 摘要质量评分 (25分)
- **WHEN** 计算摘要质量分数
- **THEN** 长度 40-100 字得 25分，20-40 字得 15分，<20 字得 0分

#### Scenario: 技术深度评分 (25分)
- **WHEN** 计算技术深度分数
- **THEN** 使用 relevance_score × 25

#### Scenario: 格式规范评分 (20分)
- **WHEN** 计算格式规范分数
- **THEN** 必需字段齐全得 10分，时间戳格式正确得 5分，url 格式正确得 5分

#### Scenario: 标签精度评分 (15分)
- **WHEN** 计算标签精度分数
- **THEN** tags 数量 5-8 个得 15分，3-4 或 9-10 个得 10分，<3 或 >10 个得 5分

#### Scenario: 空洞词检测 (15分)
- **WHEN** 检测摘要中的空洞词
- **THEN** 无空洞词得 15分，1-2 个空洞词得 8分，>2 个空洞词得 0分

### Requirement: 空洞词列表

check_quality.py SHALL 使用预定义的空洞词列表进行检测。

#### Scenario: 检测空洞词
- **WHEN** 分析摘要内容
- **THEN** 检测以下空洞词：
  - "这个项目"、"该项目"、"很不错"、"非常好"、"很棒"
  - "值得推荐"、"强烈推荐"、"一系列"、"各种"、"诸多"
  - "相关"、"有关"、"涉及"、"一些"、"某些"、"很重要"

### Requirement: 评分阈值

check_quality.py SHALL 使用 60 分作为质量阈值。

#### Scenario: 高质量文章
- **WHEN** 总分 >= 60
- **THEN** passed 字段为 true

#### Scenario: 需改进文章
- **WHEN** 总分 < 60
- **THEN** passed 字段为 false

### Requirement: 输出格式

check_quality.py SHALL 输出 JSON 格式的质量报告。

#### Scenario: 质量报告结构
- **WHEN** 生成质量报告
- **THEN** 输出包含 total_score, passed, breakdown, issues 的 JSON

#### Scenario: breakdown 结构
- **WHEN** 输出 breakdown
- **THEN** 包含 summary_quality, tech_depth, format, tag_accuracy, hollow_word_detection 各维度分数

### Requirement: 批量评分

check_quality.py SHALL 支持对整个目录进行批量评分。

#### Scenario: 批量评分
- **WHEN** 执行 `python hooks/check_quality.py knowledge/articles/`
- **THEN** 对目录下所有 article JSON 进行评分，输出每个文件的评分和汇总统计