"""
M1-QA 投研问答助手 — Agent 编排层（三级降级）
对齐: 08 §4 三级降级编排, 07 §1.2 降级策略
"""
import time

from copaw_bridge import CoPawProvider
from bailian_qa import BailianProvider
import config


class CoPawAgent:
    """
    三级降级编排：CoPaw → 百炼 → Demo
    降级链不可跳级、静默执行（对齐 07 §1.2）
    """

    def __init__(self):
        self.copaw = CoPawProvider()
        self.bailian = BailianProvider()

    def ask(
        self,
        query: str,
        session_id: str,
        use_reports: bool = False,
        report_ids: list = None,
        report_storage=None,
    ) -> dict:
        """
        按 CoPaw → 百炼 → Demo 顺序尝试，返回统一结果。
        对齐: 08 §4, 07 §1.2
    
        :param query: 用户问题
        :param session_id: 会话 ID
        :param use_reports: 是否启用研报知识库增强（默认 False，保持向后兼容）
        :param report_ids: 可选，指定使用哪些研报 ID；为 None 时检索全部研报
        :param report_storage: 研报存储实例（当 use_reports=True 时必需传入）
        :return: {answer, llm_used, model, response_time_ms, answer_source,
                  sources: list[{id, title}]}  # sources 为引用的研报列表
        """
        start = time.time()
    
        # 研报上下文检索与构建
        sources = []  # 引用的研报列表
        enhanced_query = query  # 默认使用原始问题
    
        if use_reports and report_storage is not None:
            context_text, sources = self._build_report_context(
                query, report_storage, report_ids
            )
            if context_text:
                # 将研报上下文与用户问题拼接为增强 prompt
                enhanced_query = self._build_enhanced_prompt(query, context_text)
    
        # 第 1 级：CoPaw 桥接
        result = self.copaw.ask(enhanced_query)
        if result:
            result["response_time_ms"] = int((time.time() - start) * 1000)
            result["sources"] = sources
            return result
    
        # 第 2 级：百炼 DashScope
        result = self.bailian.ask(enhanced_query)
        if result:
            result["response_time_ms"] = int((time.time() - start) * 1000)
            result["sources"] = sources
            return result
    
        # 第 3 级：Demo 模式（始终可用）
        elapsed = int((time.time() - start) * 1000)
        demo_answer = (
            f"[离线演示] 关于「{query}」的回答：这是一条演示回复。"
            f"在实际使用中，系统会通过 CoPaw 或百炼大模型生成专业的投诺分析。"
            f"当前处于离线演示模式，您可以配置 LLM API Key 以获取真实回答。"
        )
        return {
            "answer": demo_answer,
            "answer_source": "demo",
            "llm_used": False,
            "model": None,
            "response_time_ms": elapsed,
            "sources": sources,
        }

    def get_capabilities(self) -> dict:
        """
        返回当前 LLM 能力配置状态。
        对齐: 09 §1 端点 1, 05 US-005
        """
        return {
            "copaw_configured": self.copaw.is_configured,
            "bailian_configured": self.bailian.is_configured,
            "model": self.bailian.model if self.bailian.is_configured else None,
        }

    def _build_report_context(
        self, query: str, report_storage, report_ids: list = None
    ) -> tuple:
        """
        构建研报上下文，检索相关研报并汇总相关内容。

        :param query: 用户问题
        :param report_storage: 研报存储实例
        :param report_ids: 可选，指定研报 ID 列表
        :return: (context_text, sources_list)
            - context_text: 拼接后的研报上下文文本
            - sources_list: 引用的研报列表 [{id, title}, ...]
        """
        import config

        top_k = config.REPORT_SEARCH_TOP_K
        excerpt_max_len = config.REPORT_EXCERPT_MAX_LENGTH
        context_max_len = config.MAX_REPORT_CONTEXT_LENGTH

        # 调用 report_storage 的检索方法
        try:
            results = report_storage.search_reports(
                query=query,
                top_k=top_k,
                report_ids=report_ids,
                excerpt_max_length=excerpt_max_len,
            )
        except Exception:
            # 检索失败时静默降级，不注入上下文
            return "", []

        if not results:
            return "", []

        # 构建上下文文本
        context_parts = []
        sources = []
        total_len = 0

        for item in results:
            excerpt = item.get("excerpt", "")
            if not excerpt:
                continue

            # 检查总长度限制
            part_len = len(excerpt) + 50  # 预留标题和格式开销
            if total_len + part_len > context_max_len:
                break

            title = item.get("title", "未知研报")
            rid = item.get("id", "")

            context_parts.append(f"【研报：{title}】\n{excerpt}")
            sources.append({"id": rid, "title": title})
            total_len += part_len

        context_text = "\n\n".join(context_parts)
        return context_text, sources

    def _build_enhanced_prompt(self, query: str, context_text: str) -> str:
        """
        构建增强 Prompt，将研报上下文与用户问题拼接。

        :param query: 用户原始问题
        :param context_text: 研报上下文文本
        :return: 增强后的完整 prompt 字符串
        """
        return (
            f"以下是与用户问题相关的研报内容摘录，请基于这些内容回答：\n\n"
            f"{context_text}\n\n"
            f"用户问题：{query}\n\n"
            f"请基于以上研报内容回答，如果研报中没有相关信息，请明确说明。"
            f"回答中请标注信息来源（引用哪份研报）。"
        )

    def compare_reports(self, report_a: dict, report_b: dict, focus_areas: list) -> dict:
        """
        对比两份研报，返回分析结果。
        复用三级降级：CoPaw → 百炼 → Demo
        
        :param report_a: 第一份研报，包含 title 和 text_content 字段
        :param report_b: 第二份研报，包含 title 和 text_content 字段
        :param focus_areas: 对比关注维度列表
        :return: {compare_result, llm_used, model, response_time_ms}
        """
        import json
        import config

        start = time.time()

        # 构建 Prompt
        system_prompt = self._build_compare_system_prompt()
        user_prompt = self._build_compare_user_prompt(report_a, report_b, focus_areas)

        # 第 1 级：CoPaw 桥接
        result = self._call_compare_copaw(system_prompt, user_prompt)
        if result:
            result["response_time_ms"] = int((time.time() - start) * 1000)
            return result

        # 第 2 级：百炼 DashScope
        result = self._call_compare_bailian(system_prompt, user_prompt)
        if result:
            result["response_time_ms"] = int((time.time() - start) * 1000)
            return result

        # 第 3 级：Demo 模式（始终可用）
        return self._generate_demo_compare(report_a, report_b, start)

    def _build_compare_system_prompt(self) -> str:
        """  构建对比分析的 System Prompt  """
        return (
            "你是一位专业的投研分析师，擅长对比分析不同投资研究报告的异同点。\n\n"
            "你的任务是根据用户提供的两份研报内容，进行深入对比分析，输出结构化的分析结果。\n\n"
            "分析要点：\n"
            "1. 识别两份报告的核心观点差异\n"
            "2. 找出共识和共同结论\n"
            "3. 分析差异背后的原因（方法论、数据源、立场等）\n"
            "4. 给出综合投资建议\n\n"
            "输出要求：\n"
            "- 客观中立，不带主观偏见\n"
            "- 论点需有论据支撑\n"
            "- 结构清晰，便于阅读\n"
            "- 使用专业但易懂的语言"
        )

    def _build_compare_user_prompt(
        self, report_a: dict, report_b: dict, focus_areas: list
    ) -> str:
        """  构建对比分析的 User Prompt  """
        import config

        max_len = config.MAX_COMPARE_TEXT_LENGTH // 2  # 每份研报分配一半长度

        content_a = self._truncate_text(report_a.get("text_content", ""), max_len)
        content_b = self._truncate_text(report_b.get("text_content", ""), max_len)
        title_a = report_a.get("title", "报告 A")
        title_b = report_b.get("title", "报告 B")

        # 构建关注点段落
        if focus_areas:
            focus_section = f"请重点关注以下维度：{', '.join(focus_areas)}"
        else:
            focus_section = "请自行识别关键对比维度"

        return (
            f"请对比分析以下两份投研报告：\n\n"
            f"【报告 A】标题：{title_a}\n"
            f"---\n{content_a}\n---\n\n"
            f"【报告 B】标题：{title_b}\n"
            f"---\n{content_b}\n---\n\n"
            f"{focus_section}\n\n"
            f'请按以下 JSON 格式输出分析结果（仅输出 JSON，不要其他内容）：\n'
            f'{{{"\n"}'
            '  "summary": "两份研报的整体对比总结（200字以内）",\n'
            '  "differences": [\n'
            '    {\n'
            '      "aspect": "对比维度名称",\n'
            '      "report_a_view": "报告 A 的观点",\n'
            '      "report_b_view": "报告 B 的观点",\n'
            '      "analysis": "差异分析"\n'
            '    }\n'
            '  ],\n'
            '  "commonalities": ["共识点1", "共识点2"],\n'
            '  "recommendation": "综合投资建议（150字以内）"\n'
            '}'
        )

    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        """  截断过长文本，保留开头和结尾  """
        if len(text) <= max_length:
            return text
        head = text[: max_length // 2]
        tail = text[-(max_length // 2) :]
        return f"{head}\n\n...[中间部分已省略]...\n\n{tail}"

    def _call_compare_copaw(self, system_prompt: str, user_prompt: str) -> dict | None:
        """
        通过 CoPaw 尝试对比分析。
        拉取 CoPaw 的 ask 接口，将 system+user 拼接传入。
        成功返回 {compare_result, llm_used, model}，失败返回 None。
        """
        import json

        if not self.copaw.is_configured:
            return None
        # 将 system prompt 和 user prompt 拼接作为单一输入
        full_query = f"{system_prompt}\n\n{user_prompt}"
        raw = self.copaw.ask(full_query)
        if not raw:
            return None
        try:
            compare_result = self._parse_compare_json(raw.get("answer", ""))
            return {
                "compare_result": compare_result,
                "llm_used": True,
                "model": raw.get("model", "copaw-bridge"),
            }
        except Exception:
            return None

    def _call_compare_bailian(self, system_prompt: str, user_prompt: str) -> dict | None:
        """
        通过百炼 DashScope 尝试对比分析。
        成功返回 {compare_result, llm_used, model}，失败返回 None。
        """
        import json
        import requests
        import config

        if not self.bailian.is_configured:
            return None
        try:
            resp = requests.post(
                self.bailian.ENDPOINT,
                json={
                    "model": self.bailian.model,
                    "input": {
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ]
                    },
                },
                headers={
                    "Authorization": f"Bearer {self.bailian.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.bailian.timeout,
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
                compare_result = self._parse_compare_json(text)
                return {
                    "compare_result": compare_result,
                    "llm_used": True,
                    "model": self.bailian.model,
                }
        except Exception:
            pass
        return None

    @staticmethod
    def _parse_compare_json(text: str) -> dict:
        """
        从 LLM 输出中解析 JSON 格式的对比结果。
        如果解析失败，返回包含原始文本的备用结果。
        """
        import json
        import re

        # 尝试提取 JSON 块（去掉可能的 Markdown 代码块标记）
        text = text.strip()
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if json_match:
            text = json_match.group(1).strip()

        try:
            result = json.loads(text)
            # 确保必要字段存在
            return {
                "summary": result.get("summary", ""),
                "differences": result.get("differences", []),
                "commonalities": result.get("commonalities", []),
                "recommendation": result.get("recommendation", ""),
            }
        except (json.JSONDecodeError, ValueError):
            # 解析失败，将原始文本作为总结返回
            return {
                "summary": text[:500] if text else "对比分析已完成，请查看原始结果。",
                "differences": [],
                "commonalities": [],
                "recommendation": "",
            }

    def _generate_demo_compare(self, report_a: dict, report_b: dict, start: float) -> dict:
        """
        Demo 模式：无法调用真实 LLM 时的备用对比结果。
        返回 {compare_result, llm_used, model, response_time_ms}。
        """
        import time

        elapsed = int((time.time() - start) * 1000)
        title_a = report_a.get("title", "报告 A")
        title_b = report_b.get("title", "报告 B")
        return {
            "compare_result": {
                "summary": (
                    f"[离线演示] 已对《{title_a}》和《{title_b}》进行对比分析。"
                    f"在实际使用中，系统会通过 CoPaw 或百炼大模型生成专业对比分析。"
                    f"当前处于离线演示模式。"
                ),
                "differences": [
                    {
                        "aspect": "行业观点",
                        "report_a_view": f"《{title_a}》的行业观点（演示）",
                        "report_b_view": f"《{title_b}》的行业观点（演示）",
                        "analysis": "请配置 LLM API Key 以获取真实对比分析。",
                    }
                ],
                "commonalities": ["这是离线演示模式，请配置 LLM API Key"],
                "recommendation": "当前处于离线演示模式，配置 LLM API Key 后可获取真实的投资建议。",
            },
            "llm_used": False,
            "model": None,
            "response_time_ms": elapsed,
        }

    def get_health(self, storage) -> dict:
        """
        返回系统健康状态。
        对齐: 09 §9, 05 US-004
        """
        from wsgi import get_start_time

        storage_ok = storage.is_data_dir_writable()
        llm_ok = self.copaw.is_configured or self.bailian.is_configured

        status = "healthy" if storage_ok else "degraded"

        return {
            "status": status,
            "uptime": int(time.time() - get_start_time()),
            "components": {
                "storage": "ok" if storage_ok else "error",
                "llm": "ok" if llm_ok else "unavailable",
            },
        }
