## 1. 项目初始化

- [x] 1.1 创建 `pipeline/` 目录结构
- [x] 1.2 添加 `requirements.txt`（python-dotenv, requests）
- [x] 1.3 创建 `.env.example`（LLM_API_KEY, LLM_BASE_URL, LLM_MODEL）
- [x] 1.4 创建 `pipeline/__init__.py`

## 2. ModelClient 实现

- [x] 2.1 创建 `pipeline/model_client.py`，实现 `ModelClient` 类
- [x] 2.2 实现 `__init__` 从环境变量读取配置
- [x] 2.3 实现 `analyze(repo_info)` 方法，调用 OpenAI 兼容 API
- [x] 2.4 实现错误处理和重试逻辑（最多 3 次，间隔 2s）
- [x] 2.5 实现 `load_env()` 从 .env 文件加载配置

## 3. Collector 实现

- [x] 3.1 创建 `pipeline/collector.py`
- [x] 3.2 实现 `fetch_trending(count=50)` 调用 GitHub GraphQL API
- [x] 3.3 实现 `append_to_raw(items, date)` 追加写入 raw 文件
- [x] 3.4 实现 `format_repo(repo)` 格式化 repo 数据结构
- [x] 3.5 添加请求限流（sleep 1s）

## 4. Analyzer 实现

- [x] 4.1 创建 `pipeline/analyzer.py`
- [x] 4.2 实现 `analyze_repo(repo_info, model_client)` 调用 LLM 分析
- [x] 4.3 实现 `update_raw_with_insights(raw_file, insights)` 追加分析结果到 raw 文件
- [x] 4.4 实现 `analyze_all(raw_file_path, model_client)` 批量处理所有 items
- [x] 4.5 添加请求间隔（sleep 1s）

## 5. Organizer 实现

- [x] 5.1 创建 `pipeline/organizer.py`
- [x] 5.2 实现 `generate_slug(repo_id)` 从 repo id 生成 slug
- [x] 5.3 实现 `generate_id(date, seq)` 生成 kb-{date}-{seq} 格式 id
- [x] 5.4 实现 `create_article(item, date)` 生成 article JSON
- [x] 5.5 实现 `save_article(article, slug, date)` 保存到 `knowledge/articles/`
- [x] 5.6 实现 `check_duplicate(slug)` 检查 index.json 是否已存在
- [x] 5.7 实现 `update_index(article)` 更新 index.json
- [x] 5.8 实现 `organize_all(raw_file_path)` 处理所有已分析的 items

## 6. Pipeline 入口

- [x] 6.1 创建 `pipeline/run.py` 作为 CLI 入口
- [x] 6.2 实现 `--date` 参数解析
- [x] 6.3 实现 `validate_config()` 配置验证
- [x] 6.4 实现日志输出（print 进度信息）
- [x] 6.5 实现异常处理和 abort

## 7. 集成测试

- [x] 7.1 运行 `python -m pipeline.run` 测试完整流程
- [x] 7.2 验证 raw 文件生成正确
- [x] 7.3 验证 article 文件生成正确
- [x] 7.4 验证 index.json 维护正确