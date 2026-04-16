import re
from typing import Any


def scan_text(text: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:

    hits: list[dict[str, Any]] = [ ]

    for r in rules:
        rid = r.get("id", "")
        if rid == "R-G01" and re.search(r"(全仓|清仓|买入|卖出|加仓|减仓|调仓)", text):
            hits.append({"rule_id": rid, "span": "investment_ops", "message": "疑似个性化投资操作表述"})
        if rid == "R-G02" and re.search(r"(保证收益|稳赚|无风险|保本)", text):
            hits.append({"rule_id": rid, "span": "return_promise", "message": "疑似收益承诺"})
        if rid == "R-G03" and re.search(r"(基金|理财|投资|股票|债券)", text) and not re.search(r"(投资有风险|市场有风险|风险自担|不代表未来)", text):
            hits.append({"rule_id": rid, "span": "missing_risk_warning", "message": "疑似缺少风险提示"})
    return hits