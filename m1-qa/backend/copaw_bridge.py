"""
M1-QA 投研问答助手 — CoPaw 桥接 Provider
对齐: 08 §4 三级降级编排（第 1 级）
"""
import requests
import config


class CoPawProvider:
    """CoPaw 桥接调用，超时 20s，失败返回 None 静默降级"""

    def __init__(self):
        self.app_url = config.COPAW_APP_URL
        self.api_key = config.COPAW_API_KEY
        self.timeout = config.COPAW_TIMEOUT

    @property
    def is_configured(self) -> bool:
        return bool(self.app_url) and bool(self.api_key)

    def ask(self, query: str) -> dict | None:
        """
        调用 CoPaw 桥接获取答案。
        成功返回 {answer, source, llm_used, model}，失败返回 None。
        """
        if not self.is_configured:
            return None

        try:
            resp = requests.post(
                self.app_url,
                json={"query": query},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "answer": data.get("answer", data.get("response", "")),
                    "answer_source": "copaw",
                    "llm_used": True,
                    "model": data.get("model", "copaw-bridge"),
                }
        except Exception:
            pass
        return None
