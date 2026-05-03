## ADDED Requirements

### Requirement: 配置读取

ModelClient SHALL 从环境变量读取 LLM 配置：LLM_API_KEY, LLM_BASE_URL, LLM_MODEL。

#### Scenario: 读取环境变量
- **WHEN** ModelClient 初始化
- **THEN** 从 os.environ 或 .env 文件读取 API_KEY, BASE_URL, MODEL

#### Scenario: 缺少必需配置
- **WHEN** 缺少 LLM_API_KEY
- **THEN** 抛出 ValueError 并提示 "LLM_API_KEY is required"

### Requirement: 统一的 chat 接口

ModelClient SHALL 提供 analyze(repo_info: dict) -> dict 方法，封装 LLM API 调用。

#### Scenario: 成功调用
- **WHEN** 调用 model_client.analyze({"name": "...", "description": "...", ...})
- **THEN** 返回 LLM 分析结果字典

#### Scenario: API 返回非 JSON
- **WHEN** LLM API 返回无法解析的响应
- **THEN** 抛出异常，日志记录原始响应

### Requirement: 错误处理和重试

ModelClient SHALL 处理 API 错误，实现基本的重试逻辑（最多 3 次）。

#### Scenario: 请求失败重试
- **WHEN** API 返回 5xx 错误
- **THEN** 等待 2 秒后重试，最多 3 次

#### Scenario: 认证失败
- **WHEN** API 返回 401/403
- **THEN** 抛出异常，不再重试