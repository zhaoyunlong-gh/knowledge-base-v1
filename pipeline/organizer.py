"""Article 整理器 - 将分析结果转换为 article 并维护索引"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class Organizer:
    """将分析结果整理成 article 的整理器"""

    def __init__(self):
        self.articles_dir = Path("knowledge/articles")
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.articles_dir / "index.json"

    def generate_slug(self, repo_id: str) -> str:
        """从 repo id 生成 slug

        Args:
            repo_id: repo id，如 "openai/agents-sdk"

        Returns:
            slug 字符串，如 "openai-agents-sdk"
        """
        return repo_id.replace("/", "-")

    def generate_id(self, date: str, seq: int) -> str:
        """生成 article id

        Args:
            date: 日期字符串，如 "2026-03-17"
            seq: 序号

        Returns:
            id 字符串，如 "kb-2026-03-17-001"
        """
        return f"kb-{date}-{seq:03d}"

    def create_article(self, item: dict, date: str, seq: int) -> dict:
        """从 raw item 生成 article

        Args:
            item: raw 文件中的 item
            date: 日期字符串
            seq: 序号

        Returns:
            article 字典
        """
        slug = self.generate_slug(item["id"])

        article = {
            "id": self.generate_id(date, seq),
            "title": item.get("title", item["id"].split("/")[-1]),
            "source": "github-trending",
            "source_id": item["id"],
            "url": item.get("url", f"https://github.com/{item['id']}"),
            "summary": item.get("summary", ""),
            "tags": item.get("tags", []),
            "relevance_score": item.get("relevance_score", 0.0),
            "collected_at": item.get("created_at"),
            "analyzed_at": item.get("analyzed_at"),
            "organized_at": datetime.utcnow().isoformat() + "Z",
            "status": "published",
        }

        return article

    def save_article(self, article: dict, slug: str, date: str) -> str:
        """保存 article 到文件

        Args:
            article: article 字典
            slug: slug 字符串
            date: 日期字符串

        Returns:
            文件路径
        """
        filename = f"{date}-{slug}.json"
        filepath = self.articles_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def load_index(self) -> dict:
        """加载 index.json，如果不存在则返回空结构"""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"updated_at": None, "count": 0, "articles": []}

    def save_index(self, index: dict) -> None:
        """保存 index.json"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def check_duplicate(self, slug: str) -> bool:
        """检查 slug 是否已存在

        Args:
            slug: slug 字符串

        Returns:
            是否已存在
        """
        index = self.load_index()
        existing_slugs = {article["slug"] for article in index.get("articles", [])}
        return slug in existing_slugs

    def update_index(self, article: dict, slug: str) -> None:
        """更新 index.json

        Args:
            article: article 字典
            slug: slug 字符串
        """
        index = self.load_index()

        # 添加到 articles 数组
        index["articles"].append({
            "id": article["id"],
            "slug": slug,
            "path": f"{article['organized_at'][:10]}-{slug}.json",
        })

        # 更新元数据
        index["updated_at"] = datetime.utcnow().isoformat() + "Z"
        index["count"] = len(index["articles"])

        self.save_index(index)

    def organize_all(self, raw_file: str) -> int:
        """处理 raw 文件中所有已分析的 items

        Args:
            raw_file: raw 文件路径

        Returns:
            处理的 article 数量
        """
        with open(raw_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data.get("items", [])
        date = datetime.now().strftime("%Y-%m-%d")

        # 获取当前 index 中的数量，用于序号
        index = self.load_index()
        start_seq = index.get("count", 0) + 1

        article_count = 0

        for i, item in enumerate(items):
            # 只处理有 analyzed_at 字段的 item
            if not item.get("analyzed_at"):
                continue

            slug = self.generate_slug(item["id"])

            # 检查是否重复
            if self.check_duplicate(slug):
                print(f"[Organizer] Skipping duplicate: {slug}")
                continue

            seq = start_seq + article_count
            article = self.create_article(item, date, seq)

            filepath = self.save_article(article, slug, date)
            print(f"[Organizer] Created {filepath}")

            self.update_index(article, slug)
            article_count += 1

        return article_count

    def organize(self, raw_file: str) -> int:
        """执行整理流程

        Args:
            raw_file: raw 文件路径

        Returns:
            处理的 article 数量
        """
        print(f"[Organizer] Starting organization of {raw_file}...")

        count = self.organize_all(raw_file)

        print(f"[Organizer] Completed. Created {count} articles.")

        return count