"""
M1-QA 投研问答助手 — 研报存储层（JSON 文件 CRUD）
遵循 storage.py 的 RMW 模式（全量读入 → 修改 → 全量写回）
"""
import json
import os
import time
from datetime import datetime, timezone


class ReportStorage:
    """
    研报 JSON 文件存储引擎 — RMW 模式。
    管理 reports.json（研报元数据）和 compares.json（对比报告）。
    """

    def __init__(self, data_dir: str):
        """
        初始化存储，自动创建数据目录和空 JSON 文件。
        :param data_dir: data 目录绝对路径
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._reports_path = os.path.join(data_dir, "reports.json")
        self._compares_path = os.path.join(data_dir, "compares.json")

        # 初始化空文件（若不存在）
        if not os.path.exists(self._reports_path):
            self._write_json(self._reports_path, [])
        if not os.path.exists(self._compares_path):
            self._write_json(self._compares_path, [])

    # ── 内部 IO ──

    @staticmethod
    def _read_json(path: str) -> list:
        """读取 JSON 文件，返回列表"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(path: str, data: list):
        """全量写回 JSON 文件"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _now_iso() -> str:
        """返回当前 UTC 时间的 ISO 8601 格式字符串"""
        return datetime.now(timezone.utc).isoformat()

    # ── 研报管理 ──

    def create_report(self, report_dict: dict) -> dict:
        """
        写入新研报元数据记录。
        :param report_dict: 研报数据，必须包含全部必填字段
        :return: 写入的研报记录
        """
        reports = self._read_json(self._reports_path)
        reports.append(report_dict)
        self._write_json(self._reports_path, reports)
        return report_dict

    def get_reports(self, status: str = None, page: int = 1, page_size: int = 20) -> dict:
        """
        获取研报列表，支持状态过滤和分页。
        :param status: 状态过滤（ready/parsing/error），None 表示不过滤
        :param page: 页码，从 1 开始
        :param page_size: 每页条数，最大 100
        :return: {items: list, total: int}
        """
        reports = self._read_json(self._reports_path)

        # 状态过滤
        if status:
            reports = [r for r in reports if r.get("status") == status]

        # 按上传时间倒序排列
        reports.sort(key=lambda r: r.get("upload_time", ""), reverse=True)

        total = len(reports)
        # 分页切片
        page_size = min(page_size, 100)
        start = (page - 1) * page_size
        end = start + page_size
        items = reports[start:end]

        return {"items": items, "total": total}

    def get_report_by_id(self, report_id: str) -> dict | None:
        """
        按研报 ID 查找单条记录。
        :param report_id: 研报 ID（格式：rpt_xxx）
        :return: 研报记录或 None
        """
        reports = self._read_json(self._reports_path)
        for r in reports:
            if r.get("id") == report_id:
                return r
        return None

    def delete_report(self, report_id: str) -> dict:
        """
        删除研报元数据记录，返回被删除的记录。
        :param report_id: 研报 ID
        :raises KeyError: 研报不存在时抛出
        :return: 被删除的研报记录
        """
        reports = self._read_json(self._reports_path)
        target = None
        new_reports = []
        for r in reports:
            if r.get("id") == report_id:
                target = r
            else:
                new_reports.append(r)

        if target is None:
            raise KeyError(f"Report {report_id} not found")

        self._write_json(self._reports_path, new_reports)
        return target

    # ── 对比报告管理 ──

    def create_compare(self, compare_dict: dict) -> dict:
        """
        写入新对比报告记录。
        :param compare_dict: 对比报告数据，必须包含全部必填字段
        :return: 写入的对比报告记录
        """
        compares = self._read_json(self._compares_path)
        compares.append(compare_dict)
        self._write_json(self._compares_path, compares)
        return compare_dict

    def get_compare_by_id(self, compare_id: str) -> dict | None:
        """
        按对比报告 ID 查找单条记录。
        :param compare_id: 对比报告 ID（格式：cmp_xxx）
        :return: 对比报告记录或 None
        """
        compares = self._read_json(self._compares_path)
        for c in compares:
            if c.get("id") == compare_id:
                return c
        return None

    # ── 研报内容检索 ──

    def search_reports(
        self,
        query: str,
        top_k: int = 3,
        report_ids: list = None,
        excerpt_max_length: int = 1000,
    ) -> list:
        """
        基于关键词匹配搜索研报相关内容，返回最相关的研报片段。

        实现思路：
        1. 将用户问题分词（中文按字切割，英文按空格分词）
        2. 对每份编号为 ready 状态且有 text_content 的研报，计算关键词命中数
        3. 按命中数降序取 top_k 份
        4. 从每份研报提取最相关的段落作为摘录

        :param query: 用户问题文本
        :param top_k: 返回最相关研报数量
        :param report_ids: 如果指定，只检索这些 ID 对应的研报；为 None 时检索全部
        :param excerpt_max_length: 每份研报提取的最大字符数
        :return: [
            {
                "id": str,
                "title": str,
                "excerpt": str,   # 最相关的段落摘录
                "score": int,     # 关键词命中数得分
            },
            ...
        ]
        """
        if not query or not query.strip():
            return []

        # 读取全部研报
        reports = self._read_json(self._reports_path)

        # 按状态过滤：只检索状态为 ready 的研报
        reports = [r for r in reports if r.get("status") == "ready"]

        # 如果指定了 report_ids，只保留对应 ID 的研报
        if report_ids:
            id_set = set(report_ids)
            reports = [r for r in reports if r.get("id") in id_set]

        # 将查询进行分词：先拆分英文单词，再提取长度≥2 的中文子串
        keywords = self._extract_keywords(query)
        if not keywords:
            return []

        # 计算每份研报的相关度得分
        scored = []
        for report in reports:
            text_content = report.get("text_content", "")
            if not text_content:
                continue
            score = self._calc_keyword_score(keywords, text_content)
            if score > 0:
                scored.append((score, report))

        # 按得分降序排序，取 top_k 份
        scored.sort(key=lambda x: x[0], reverse=True)
        top_reports = scored[:top_k]

        # 构建返回结果，提取最相关段落
        results = []
        for score, report in top_reports:
            excerpt = self._extract_best_excerpt(
                keywords,
                report.get("text_content", ""),
                excerpt_max_length,
            )
            results.append({
                "id": report["id"],
                "title": report.get("title", ""),
                "excerpt": excerpt,
                "score": score,
            })

        return results

    @staticmethod
    def _extract_keywords(query: str) -> list:
        """
        从查询字符串中提取关键词列表。
        - 英文单词：按空格分割，去除长度小于 2 的单词
        - 中文：提取长度 ≥ 2 的子串（滑动窗口，长度 2~4）
        :param query: 用户问题字符串
        :return: 关键词列表（已去重、小写）
        """
        import re

        keywords = set()

        # 提取英文单词（长度>=2）
        en_words = re.findall(r"[a-zA-Z]+", query)
        for w in en_words:
            if len(w) >= 2:
                keywords.add(w.lower())

        # 提取中文字符序列（滑动窗口，长度 2~4）
        # 只对中文字符进行提取
        zh_chars = re.sub(r"[^\u4e00-\u9fff]", "", query)
        for length in range(2, 5):
            for i in range(len(zh_chars) - length + 1):
                keywords.add(zh_chars[i: i + length])

        return list(keywords)

    @staticmethod
    def _calc_keyword_score(keywords: list, text: str) -> int:
        """
        计算关键词在文本中的命中得分。
        得分算法：每个关键词命中次数的加权和，较长的关键词权重更大
        :param keywords: 关键词列表
        :param text: 研报文本内容
        :return: 得分整数
        """
        text_lower = text.lower()
        score = 0
        for kw in keywords:
            count = text_lower.count(kw.lower())
            if count > 0:
                # 较长关键词权重更高（长度乘以命中次数）
                score += len(kw) * count
        return score

    @staticmethod
    def _extract_best_excerpt(
        keywords: list, text: str, max_length: int
    ) -> str:
        """
        从研报文本中提取最相关的段落，汇聚关键词密度最高的文本片段。

        算法：
        1. 按换行分割文本为段落
        2. 为每个段落计算关键词得分
        3. 按得分降序排序，贪心选取直到达到字符限制

        :param keywords: 关键词列表
        :param text: 研报全文
        :param max_length: 摘录最大字符数
        :return: 返回拼接后的昨步内容
        """
        if not text:
            return ""

        # 按换行将文本拆分为段落，过滤空段落
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        if not paragraphs:
            return text[:max_length]

        # 计算每个段落的关键词得分
        para_scores = []
        text_lower = text.lower()
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            score = 0
            for kw in keywords:
                count = para_lower.count(kw.lower())
                if count > 0:
                    score += len(kw) * count
            para_scores.append((score, i, para))

        # 按得分降序排序
        para_scores.sort(key=lambda x: x[0], reverse=True)

        # 贪心选取段落直到达到字符限制
        selected_indices = set()
        total_len = 0
        for score, idx, para in para_scores:
            if score == 0:
                break  # 得分为 0 的段落不选入
            if total_len + len(para) + 1 <= max_length:
                selected_indices.add(idx)
                total_len += len(para) + 1
            else:
                # 剩余空间装入部分内容
                remaining = max_length - total_len
                if remaining > 50:  # 至少装入 50 字符才有意义
                    selected_indices.add(idx)
                break

        # 如果没有任何段落被选中（所有得分都为 0），直接返回文本头部
        if not selected_indices:
            return text[:max_length]

        # 按序号顺序拼接选中的段落（保持阅读流畅性）
        sorted_indices = sorted(selected_indices)
        excerpts = []
        for idx in sorted_indices:
            excerpts.append(paragraphs[idx])

        result = "\n".join(excerpts)
        # 确保不超出最大长度
        return result[:max_length]
