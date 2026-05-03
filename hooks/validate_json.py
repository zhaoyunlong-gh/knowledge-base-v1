"""JSON 结构校验脚本 - 校验 article 和 raw JSON 文件"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


# 必需字段定义
REQUIRED_ARTICLE_FIELDS = [
    "id", "title", "source", "source_id", "url",
    "summary", "tags", "relevance_score",
    "collected_at", "analyzed_at", "organized_at", "status"
]

REQUIRED_RAW_FIELDS = ["source", "collected_at", "query", "count", "items"]

REQUIRED_ITEM_FIELDS = ["id", "title", "description", "url", "stars"]

# 空洞词列表
HOLLOW_WORDS = [
    "这个项目", "该项目", "很不错", "非常好", "很棒",
    "值得推荐", "强烈推荐", "一系列", "各种", "诸多",
    "相关", "有关", "涉及", "一些", "某些", "很重要",
    "非常有意义", "值得关注"
]


def is_iso8601(dt_str: str) -> bool:
    """检查字符串是否符合 ISO 8601 格式"""
    if not isinstance(dt_str, str):
        return False
    # 支持格式: 2026-05-02T14:14:21.610155Z, 2026-05-02T14:14:21Z
    patterns = [
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$",
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$",
    ]
    return any(re.match(p, dt_str) for p in patterns)


def validate_id_format(id_str: str) -> bool:
    """验证 id 格式: kb-YYYY-MM-DD-NNN"""
    if not isinstance(id_str, str):
        return False
    return bool(re.match(r"^kb-\d{4}-\d{2}-\d{2}-\d{3}$", id_str))


def load_json_file(path: str) -> Tuple[Dict[str, Any], str]:
    """加载 JSON 文件，返回 (data, error_message)"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), ""
    except json.JSONDecodeError as e:
        return {}, f"Invalid JSON: {e}"
    except Exception as e:
        return {}, f"Error reading file: {e}"


def validate_article(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """校验 article JSON 数据，返回错误列表"""
    errors = []

    # 检查必需字段
    for field in REQUIRED_ARTICLE_FIELDS:
        if field not in data:
            errors.append({
                "field": field,
                "reason": "field missing"
            })

    if errors:
        return errors

    # 校验 id 格式
    if not validate_id_format(data.get("id", "")):
        errors.append({
            "field": "id",
            "reason": "invalid format (expected: kb-YYYY-MM-DD-NNN)"
        })

    # 校验 relevance_score 范围
    score = data.get("relevance_score")
    if not isinstance(score, (int, float)):
        errors.append({
            "field": "relevance_score",
            "reason": "should be number"
        })
    elif not (0.0 <= score <= 1.0):
        errors.append({
            "field": "relevance_score",
            "reason": f"out of range (expected 0.0-1.0, got {score})"
        })

    # 校验 tags
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        errors.append({
            "field": "tags",
            "reason": "should be array"
        })
    elif len(tags) == 0:
        errors.append({
            "field": "tags",
            "reason": "tags cannot be empty"
        })

    # 校验 status
    if data.get("status") != "published":
        errors.append({
            "field": "status",
            "reason": f"should be 'published', got '{data.get('status')}'"
        })

    # 校验时间戳格式
    for ts_field in ["collected_at", "analyzed_at", "organized_at"]:
        ts = data.get(ts_field)
        if ts and not is_iso8601(ts):
            errors.append({
                "field": ts_field,
                "reason": f"invalid ISO 8601 format: {ts}"
            })

    # 校验 url 格式
    url = data.get("url", "")
    if url and not url.startswith(("http://", "https://")):
        errors.append({
            "field": "url",
            "reason": f"invalid URL format: {url}"
        })

    return errors


def validate_raw(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """校验 raw JSON 数据，返回错误列表"""
    errors = []

    # 检查必需字段
    for field in REQUIRED_RAW_FIELDS:
        if field not in data:
            errors.append({
                "field": field,
                "reason": "field missing"
            })

    if errors:
        return errors

    # 校验 items
    items = data.get("items", [])
    if not isinstance(items, list):
        errors.append({
            "field": "items",
            "reason": "should be array"
        })
    else:
        for i, item in enumerate(items):
            for field in REQUIRED_ITEM_FIELDS:
                if field not in item:
                    errors.append({
                        "field": f"items[{i}].{field}",
                        "reason": "field missing"
                    })

    return errors


def batch_validate(directory: str) -> Dict[str, Any]:
    """批量校验目录下所有 JSON 文件"""
    dir_path = Path(directory)
    if not dir_path.exists():
        return {
            "passed": False,
            "errors": [],
            "summary": {"total_files": 0, "valid_files": 0, "invalid_files": 0},
            "fatal_error": f"Directory not found: {directory}"
        }

    # 判断是 article 还是 raw 目录
    is_article_dir = "articles" in str(dir_path)

    all_errors = []
    valid_count = 0
    invalid_count = 0

    json_files = [f for f in dir_path.glob("*.json") if f.name != "index.json"]

    for json_file in json_files:
        data, load_error = load_json_file(str(json_file))

        if load_error:
            all_errors.append({
                "file": json_file.name,
                "field": "_root",
                "reason": load_error
            })
            invalid_count += 1
            continue

        # 选择校验函数
        validator = validate_article if is_article_dir else validate_raw
        errors = validator(data)

        if errors:
            for err in errors:
                err["file"] = json_file.name
            all_errors.extend(errors)
            invalid_count += 1
        else:
            valid_count += 1

    # 记录失败文件
    if invalid_count > 0:
        log_file = dir_path / "validation_failed.log"
        with open(log_file, "w", encoding="utf-8") as f:
            for err in all_errors:
                f.write(f"{err.get('file', 'unknown')}: {err.get('field', '?')} - {err.get('reason', '?')}\n")

    return {
        "passed": invalid_count == 0,
        "errors": all_errors,
        "summary": {
            "total_files": len(json_files),
            "valid_files": valid_count,
            "invalid_files": invalid_count
        }
    }


def output_report(report: Dict[str, Any]) -> None:
    """输出 JSON 格式报告"""
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_json.py <directory_or_file>")
        sys.exit(1)

    target = sys.argv[1]
    target_path = Path(target)

    if target_path.is_dir():
        # 批量校验目录
        report = batch_validate(target)
    elif target_path.is_file():
        # 单文件校验
        data, load_error = load_json_file(target)

        if load_error:
            report = {
                "passed": False,
                "errors": [{"file": target_path.name, "field": "_root", "reason": load_error}],
                "summary": {"total_files": 1, "valid_files": 0, "invalid_files": 1}
            }
        else:
            # 判断是 article 还是 raw
            is_article = "articles" in str(target_path)
            validator = validate_article if is_article else validate_raw
            errors = validator(data)

            for err in errors:
                err["file"] = target_path.name

            report = {
                "passed": len(errors) == 0,
                "errors": errors,
                "summary": {
                    "total_files": 1,
                    "valid_files": 0 if errors else 1,
                    "invalid_files": 1 if errors else 0
                }
            }
    else:
        report = {
            "passed": False,
            "errors": [],
            "summary": {"total_files": 0, "valid_files": 0, "invalid_files": 0},
            "fatal_error": f"Path not found: {target}"
        }

    output_report(report)


if __name__ == "__main__":
    main()