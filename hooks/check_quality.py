"""质量评分脚本 - 五维度评估 article JSON 质量"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


# 空洞词列表
HOLLOW_WORDS = [
    "这个项目", "该项目", "很不错", "非常好", "很棒",
    "值得推荐", "强烈推荐", "一系列", "各种", "诸多",
    "相关", "有关", "涉及", "一些", "某些", "很重要",
    "非常有意义", "值得关注"
]

# 质量阈值
QUALITY_THRESHOLD = 60

# 必需字段
REQUIRED_ARTICLE_FIELDS = [
    "id", "title", "source", "source_id", "url",
    "summary", "tags", "relevance_score",
    "collected_at", "analyzed_at", "organized_at", "status"
]


def is_iso8601(dt_str: str) -> bool:
    """检查字符串是否符合 ISO 8601 格式"""
    if not isinstance(dt_str, str):
        return False
    patterns = [
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$",
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$",
    ]
    return any(re.match(p, dt_str) for p in patterns)


def calc_summary_quality(summary: str) -> Tuple[int, List[str]]:
    """计算摘要质量分数 (25分)"""
    issues = []
    length = len(summary)

    if length >= 40 and length <= 100:
        score = 25
    elif length >= 20:
        score = 15
    else:
        score = 0
        if length < 20:
            issues.append(f"summary too short ({length} chars)")

    return score, issues


def calc_tech_depth(relevance_score: float) -> Tuple[int, List[str]]:
    """计算技术深度分数 (25分)"""
    issues = []
    score = round(relevance_score * 25, 2)

    if relevance_score < 0.3:
        issues.append(f"low relevance_score ({relevance_score})")

    return score, issues


def calc_format_score(data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """计算格式规范分数 (20分)"""
    issues = []
    score = 0

    # 必需字段齐全: 10分
    missing_fields = [f for f in REQUIRED_ARTICLE_FIELDS if f not in data]
    if missing_fields:
        issues.append(f"missing fields: {', '.join(missing_fields)}")
    else:
        score += 10

    # 时间戳格式正确: 5分
    ts_ok = all(is_iso8601(data.get(f, "")) for f in ["collected_at", "analyzed_at", "organized_at"])
    if ts_ok:
        score += 5
    else:
        issues.append("invalid timestamp format")

    # url 格式正确: 5分
    url = data.get("url", "")
    if url and url.startswith(("http://", "https://")):
        score += 5
    elif url:
        issues.append(f"invalid URL format: {url}")

    return score, issues


def calc_tag_accuracy(tags: List[str]) -> Tuple[int, List[str]]:
    """计算标签精度分数 (15分)"""
    issues = []
    count = len(tags)

    if 5 <= count <= 8:
        score = 15
    elif 3 <= count <= 4 or 9 <= count <= 10:
        score = 10
    else:
        score = 5
        if count < 3:
            issues.append(f"too few tags ({count})")
        elif count > 10:
            issues.append(f"too many tags ({count})")

    return score, issues


def detect_hollow_words(summary: str) -> Tuple[int, List[str]]:
    """检测空洞词 (15分)"""
    issues = []
    detected = []

    for word in HOLLOW_WORDS:
        if word in summary:
            detected.append(word)

    count = len(detected)
    if count == 0:
        score = 15
    elif count <= 2:
        score = 8
        issues.append(f"hollow words detected: {', '.join(detected)}")
    else:
        score = 0
        issues.append(f"too many hollow words: {', '.join(detected)}")

    return score, issues


def score_article(file_path: str) -> Dict[str, Any]:
    """对单个 article 文件进行评分"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {
            "file": Path(file_path).name,
            "total_score": 0,
            "passed": False,
            "breakdown": {},
            "issues": [f"failed to load: {e}"]
        }

    summary = data.get("summary", "")
    tags = data.get("tags", [])
    relevance_score = data.get("relevance_score", 0)

    # 计算各维度分数
    summary_score, s_issues = calc_summary_quality(summary)
    tech_score, t_issues = calc_tech_depth(relevance_score)
    format_score, f_issues = calc_format_score(data)
    tag_score, tag_issues = calc_tag_accuracy(tags)
    hollow_score, h_issues = detect_hollow_words(summary)

    # 汇总
    total_score = summary_score + tech_score + format_score + tag_score + hollow_score

    all_issues = s_issues + t_issues + f_issues + tag_issues + h_issues

    return {
        "file": Path(file_path).name,
        "total_score": round(total_score, 2),
        "passed": total_score >= QUALITY_THRESHOLD,
        "breakdown": {
            "summary_quality": summary_score,
            "tech_depth": tech_score,
            "format": format_score,
            "tag_accuracy": tag_score,
            "hollow_word_detection": hollow_score
        },
        "issues": all_issues
    }


def batch_score(directory: str) -> Dict[str, Any]:
    """批量评分目录下所有 article 文件"""
    dir_path = Path(directory)

    if not dir_path.exists():
        return {
            "scores": [],
            "summary": {"total_files": 0, "passed": 0, "failed": 0},
            "fatal_error": f"Directory not found: {directory}"
        }

    json_files = [f for f in dir_path.glob("*.json") if f.name != "index.json"]
    scores = []
    passed_count = 0

    for json_file in json_files:
        result = score_article(str(json_file))
        scores.append(result)
        if result["passed"]:
            passed_count += 1

    # 记录失败文件
    failed_count = len(json_files) - passed_count
    if failed_count > 0:
        log_file = dir_path / "quality_failed.log"
        with open(log_file, "w", encoding="utf-8") as f:
            for result in scores:
                if not result["passed"]:
                    f.write(f"{result['file']}: score={result['total_score']} - {', '.join(result['issues'])}\n")

    return {
        "scores": scores,
        "summary": {
            "total_files": len(json_files),
            "passed": passed_count,
            "failed": failed_count
        }
    }


def output_report(report: Dict[str, Any]) -> None:
    """输出 JSON 格式报告"""
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_quality.py <directory_or_file>")
        sys.exit(1)

    target = sys.argv[1]
    target_path = Path(target)

    if target_path.is_dir():
        report = batch_score(target)
    elif target_path.is_file():
        result = score_article(target)
        report = {
            "scores": [result],
            "summary": {
                "total_files": 1,
                "passed": 1 if result["passed"] else 0,
                "failed": 0 if result["passed"] else 1
            }
        }
    else:
        report = {
            "scores": [],
            "summary": {"total_files": 0, "passed": 0, "failed": 0},
            "fatal_error": f"Path not found: {target}"
        }

    output_report(report)


if __name__ == "__main__":
    main()