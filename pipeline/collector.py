"""GitHub Trending 数据采集器"""
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests


QUERY = "AI OR LLM OR agent OR machine-learning OR deep-learning"


class Collector:
    """从 GitHub 获取 Trending 项目的采集器"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Content-Type": "application/json",
        }

    def fetch_trending(self, count: int = 50) -> list:
        """获取 GitHub Trending 项目

        Args:
            count: 获取项目数量，默认 50

        Returns:
            包含 repo 信息的列表
        """
        query = """
        query($searchQuery: String!, $count: Int!) {
          search(query: $searchQuery, type: REPOSITORY, first: $count) {
            nodes {
              ... on Repository {
                nameWithOwner
                name
                description
                url
                stargazerCount
                primaryLanguage {
                  name
                }
                repositoryTopics(first: 10) {
                  nodes {
                    topic {
                      name
                    }
                  }
                }
                createdAt
                updatedAt
              }
            }
          }
        }
        """

        variables = {"searchQuery": QUERY, "count": count}

        response = self._graphql_request(query, variables)
        repos = response["data"]["search"]["nodes"]

        return [self.format_repo(repo) for repo in repos]

    def _graphql_request(self, query: str, variables: dict) -> dict:
        """发送 GraphQL 请求到 GitHub API"""
        url = "https://api.github.com/graphql"

        for attempt in range(3):
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json={"query": query, "variables": variables},
                    timeout=30,
                )

                if response.status_code == 403:
                    raise RuntimeError("GitHub API rate limit exceeded. Consider adding GITHUB_TOKEN.")
                elif response.status_code != 200:
                    raise RuntimeError(f"GitHub API error: {response.status_code}")
                elif "errors" in response.json():
                    raise RuntimeError(f"GraphQL error: {response.json()['errors']}")

                return response.json()

            except requests.exceptions.RequestException as e:
                if attempt == 2:
                    raise RuntimeError(f"GitHub API request failed after 3 attempts: {e}")
                time.sleep(1)

    def format_repo(self, repo: dict) -> dict:
        """格式化 repo 数据结构"""
        topics = [node["topic"]["name"] for node in repo.get("repositoryTopics", {}).get("nodes", [])]

        return {
            "id": repo["nameWithOwner"],
            "title": repo["name"],
            "description": repo.get("description") or "",
            "url": repo["url"],
            "stars": repo["stargazerCount"],
            "language": repo.get("primaryLanguage", {}).get("name") if repo.get("primaryLanguage") else None,
            "topics": topics,
            "created_at": repo.get("createdAt"),
            "updated_at": repo.get("updatedAt"),
        }

    def append_to_raw(self, items: list, date: Optional[str] = None) -> str:
        """追加 items 到 raw 文件

        Args:
            items: repo 列表
            date: 日期字符串，默认为今天

        Returns:
            raw 文件路径
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        raw_dir = Path("knowledge/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)

        raw_file = raw_dir / f"github-trending-{date}.json"

        if raw_file.exists():
            with open(raw_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "source": "github-trending",
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "query": QUERY,
                "count": len(items),
                "items": [],
            }

        # 追加新 items，避免重复
        existing_ids = {item["id"] for item in data.get("items", [])}
        for item in items:
            if item["id"] not in existing_ids:
                data["items"].append(item)

        data["count"] = len(data["items"])
        data["collected_at"] = datetime.utcnow().isoformat() + "Z"

        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(raw_file)

    def collect(self, count: int = 50, date: Optional[str] = None) -> str:
        """执行完整采集流程

        Args:
            count: 获取项目数量
            date: 日期字符串

        Returns:
            raw 文件路径
        """
        print(f"[Collector] Fetching top {count} GitHub Trending AI projects...")

        repos = self.fetch_trending(count)
        print(f"[Collector] Fetched {len(repos)} repos")

        raw_file = self.append_to_raw(repos, date)
        print(f"[Collector] Saved to {raw_file}")

        time.sleep(1)  # 请求限流

        return raw_file