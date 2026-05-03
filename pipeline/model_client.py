"""统一的 LLM 客户端，支持 OpenAI 兼容 API（DeepSeek / Qwen / OpenAI）"""
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class ModelConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 30


class ModelClient:
    """统一的 LLM 客户端"""

    def __init__(self, config: Optional[ModelConfig] = None):
        if config is None:
            config = self.load_config()
        self.config = config

    @staticmethod
    def load_config() -> ModelConfig:
        """从环境变量或 .env 文件加载配置"""
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.environ.get("LLM_API_KEY")
        base_url = os.environ.get("LLM_BASE_URL")
        model = os.environ.get("LLM_MODEL")

        if not api_key:
            raise ValueError("LLM_API_KEY is required")

        return ModelConfig(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1/chat/completions",
            model=model or "gpt-4o-mini",
        )

    def analyze(self, repo_info: dict) -> dict:
        """调用 LLM 分析单个 repo，返回结构化洞见

        Args:
            repo_info: 包含 name, description, stars, topics 等字段的 dict

        Returns:
            包含 summary, relevance_score, score_breakdown, tags, analyzed_at 的 dict
        """
        prompt = self._build_prompt(repo_info)
        response = self._call_llm(prompt)
        return self._parse_response(response)

    def _build_prompt(self, repo_info: dict) -> str:
        """构建分析 prompt"""
        name = repo_info.get("name", "")
        description = repo_info.get("description", "")
        stars = repo_info.get("stars", 0)
        topics = repo_info.get("topics", [])

        return f"""分析这个 GitHub 项目，返回 JSON：

项目名: {name}
描述: {description}
Stars: {stars}
Topics: {topics}

只返回 JSON，不要其他内容。格式：{{"summary":"...","relevance_score":0.0,"score_breakdown":{{"tech_depth":0.0,"practical_value":0.0,"timeliness":0.0,"community_heat":0.0,"domain_match":0.0}},"tags":["tag1","tag2"]}}"""

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API，实现重试逻辑"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self._make_request(prompt)
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM API failed after {max_retries} attempts: {e}")
                time.sleep(retry_delay)

    def _make_request(self, prompt: str) -> str:
        """发送 HTTP 请求到 LLM API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        response = requests.post(
            self.config.base_url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout,
        )

        if response.status_code == 401 or response.status_code == 403:
            raise RuntimeError(f"LLM API authentication failed: {response.status_code}")
        elif response.status_code >= 500:
            raise RuntimeError(f"LLM API server error: {response.status_code}")
        elif response.status_code != 200:
            raise RuntimeError(f"LLM API error: {response.status_code} - {response.text}")

        return response.json()["choices"][0]["message"]["content"]

    def _parse_response(self, response: str) -> dict:
        """解析 LLM 返回的 JSON 响应"""
        import re

        # 移除 <think>... 标签
        cleaned = re.sub(r"<think>.*?", "", response, flags=re.DOTALL).strip()

        # 找到 "summary": 的位置
        summary_idx = cleaned.find('"summary":')
        if summary_idx == -1:
            print(f"[ModelClient] No summary found. Preview: {cleaned[:200]}...")
            raise ValueError(f"No summary field found in response")

        # 往前找 {
        brace_idx = cleaned.rfind("{", 0, summary_idx)
        if brace_idx == -1:
            raise ValueError(f"No JSON found in response")

        # 从 brace_idx 开始，尝试不同的结束位置
        for end_offset in range(1, len(cleaned) - brace_idx + 1):
            end_pos = brace_idx + end_offset
            candidate = cleaned[brace_idx:end_pos]
            try:
                result = json.loads(candidate)
                if all(k in result for k in ["summary", "relevance_score", "score_breakdown", "tags"]):
                    from datetime import datetime

                    result["analyzed_at"] = datetime.utcnow().isoformat() + "Z"
                    return result
            except json.JSONDecodeError:
                continue

        print(f"[ModelClient] Failed to parse. Brace at {brace_idx}, summary at {summary_idx}")
        print(f"[ModelClient] Region: {cleaned[brace_idx:brace_idx + 300]}...")
        raise ValueError(f"No valid JSON found in response")