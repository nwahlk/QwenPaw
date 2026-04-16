"""
M1-QA 投研问答助手 — 百炼 DashScope Provider
对齐: 08 §4 三级降级编排（第 2 级）
"""
import requests
import config


class BailianProvider:
    """百炼 DashScope 调用，超时 120s，失败返回 None 静默降级"""

    ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def __init__(self):
        self.api_key = config.DASHSCOPE_API_KEY
        self.model = config.DASHSCOPE_MODEL
        self.timeout = config.DASHSCOPE_TIMEOUT

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def ask(self, query: str) -> dict | None:
        """
        调用百炼 DashScope 获取答案。
        成功返回 {answer, source, llm_used, model}，失败返回 None。
        """
        if not self.is_configured:
            return None

        try:
            resp = requests.post(
                self.ENDPOINT,
                json={
                    "model": self.model,
                    "input": {"messages": [{"role": "user", "content": query}]},
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                text = (
                    data.get("output", {})
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                if not text:
                    text = data.get("output", {}).get("text", "")
                return {
                    "answer": text,
                    "answer_source": "bailian",
                    "llm_used": True,
                    "model": self.model,
                }
        except Exception:
            pass
        return None
