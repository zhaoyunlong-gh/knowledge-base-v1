"""LLM 分析器 - 对 repo 进行 AI 分析"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from pipeline.model_client import ModelClient


class Analyzer:
    """使用 LLM 分析 GitHub repo 的分析器"""

    def __init__(self, model_client: Optional[ModelClient] = None):
        self.model_client = model_client or ModelClient()

    def analyze_repo(self, repo_info: dict) -> dict:
        """调用 LLM 分析单个 repo

        Args:
            repo_info: 包含 repo 信息的字典

        Returns:
            包含分析结果的字典
        """
        try:
            result = self.model_client.analyze(repo_info)
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to analyze repo {repo_info.get('id', 'unknown')}: {e}")

    def update_raw_with_insights(self, raw_file: str, repo_id: str, insights: dict) -> None:
        """将分析结果追加到 raw 文件中对应 item

        Args:
            raw_file: raw 文件路径
            repo_id: repo id
            insights: 分析结果
        """
        with open(raw_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("items", []):
            if item.get("id") == repo_id:
                item.update(insights)
                break

        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def analyze_all(self, raw_file: str) -> int:
        """批量处理 raw 文件中的所有 items

        Args:
            raw_file: raw 文件路径

        Returns:
            分析的 item 数量
        """
        with open(raw_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data.get("items", [])
        analyzed_count = 0

        for i, item in enumerate(items):
            # 跳过已有 analyzed_at 的 item（增量分析）
            if item.get("analyzed_at"):
                continue

            print(f"[Analyzer] Analyzing {i + 1}/{len(items)}: {item.get('id', 'unknown')}")

            try:
                insights = self.analyze_repo(item)
                self.update_raw_with_insights(raw_file, item["id"], insights)
                analyzed_count += 1
            except Exception as e:
                print(f"[Analyzer] Error analyzing {item.get('id')}: {e}")
                raise  # abort

            time.sleep(1)  # 请求间隔

        return analyzed_count

    def analyze(self, raw_file: str) -> int:
        """执行分析流程

        Args:
            raw_file: raw 文件路径

        Returns:
            分析的 item 数量
        """
        print(f"[Analyzer] Starting analysis of {raw_file}...")

        count = self.analyze_all(raw_file)

        print(f"[Analyzer] Completed. Analyzed {count} repos.")

        return count