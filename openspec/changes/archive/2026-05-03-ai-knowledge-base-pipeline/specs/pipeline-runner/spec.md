## ADDED Requirements

### Requirement: 手动触发入口

PipelineRunner SHALL 提供 CLI 入口，允许用户手动触发完整流程。

#### Scenario: 运行 pipeline
- **WHEN** 用户执行 `python -m pipeline.run`
- **THEN** 依次执行 Collector -> Analyzer -> Organizer

#### Scenario: 指定日期
- **WHEN** 用户执行 `python -m pipeline.run --date 2026-03-17`
- **THEN** 使用指定日期生成 raw 文件和 article 文件

### Requirement: 日志记录

PipelineRunner SHALL 在控制台输出运行日志，记录每个步骤的进度和结果。

#### Scenario: 输出运行日志
- **WHEN** pipeline 运行中
- **THEN** 打印 Collector 获取 N 个项目，Analyzer 分析进度，Organizer 生成 N 个 article

### Requirement: 失败时 abort

PipelineRunner SHALL 在任何步骤失败时 abort 整个流程，记录错误日志并以非零状态码退出。

#### Scenario: 步骤失败
- **WHEN** Collector / Analyzer / Organizer 抛出异常
- **THEN** 打印错误日志，流程终止，程序以状态码 1 退出

### Requirement: 配置验证

PipelineRunner SHALL 在启动时验证所有必需配置（LLM_API_KEY, LLM_BASE_URL, LLM_MODEL）是否存在。

#### Scenario: 配置完整
- **WHEN** 所有配置存在
- **THEN** 开始运行 pipeline

#### Scenario: 配置缺失
- **WHEN** 缺少必需配置
- **THEN** 打印错误信息并以状态码 1 退出