## 1. validate_json.py 实现

- [x] 1.1 创建 `hooks/` 目录结构
- [x] 1.2 实现 `load_json_file(path)` 加载 JSON 文件
- [x] 1.3 实现 `validate_article(data)` 校验 article 必需字段和数据类型
- [x] 1.4 实现 `validate_raw(data)` 校验 raw 必需字段和数据类型
- [x] 1.5 实现 `is_iso8601(dt_str)` 时间戳格式校验
- [x] 1.6 实现 `validate_id_format(id_str)` id 格式校验（kb-YYYY-MM-DD-NNN）
- [x] 1.7 实现 `batch_validate(directory)` 批量校验目录下的 JSON 文件
- [x] 1.8 实现 `output_report(errors, summary)` 输出 JSON 格式报告

## 2. check_quality.py 实现

- [x] 2.1 创建 `hooks/check_quality.py`
- [x] 2.2 定义 `HOLLOW_WORDS` 空洞词列表
- [x] 2.3 实现 `calc_summary_quality(summary)` 摘要质量评分 (25分)
- [x] 2.4 实现 `calc_tech_depth(relevance_score)` 技术深度评分 (25分)
- [x] 2.5 实现 `calc_format_score(data)` 格式规范评分 (20分)
- [x] 2.6 实现 `calc_tag_accuracy(tags)` 标签精度评分 (15分)
- [x] 2.7 实现 `detect_hollow_words(summary)` 空洞词检测 (15分)
- [x] 2.8 实现 `score_article(file_path)` 单个 article 评分
- [x] 2.9 实现 `batch_score(directory)` 批量评分目录下的 article
- [x] 2.10 实现 `output_report(scores)` 输出 JSON 格式报告

## 3. 测试和验证

- [x] 3.1 运行 `python hooks/validate_json.py knowledge/articles/` 验证现有数据
- [x] 3.2 运行 `python hooks/validate_json.py knowledge/raw/` 验证 raw 文件
- [x] 3.3 运行 `python hooks/check_quality.py knowledge/articles/` 验证质量评分
- [x] 3.4 确认错误报告清晰可读