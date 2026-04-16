"""
M1-QA ComplianceService 单元测试 — scan_text 全覆盖 (L1 Unit)
TC 编号：TC-M01-C01 ~ TC-M01-C68
对齐: compliance_service.py scan_text 函数
"""
import pytest
from compliance_service import scan_text


# ---------------------------------------------------------------------------
# 公共规则常量
# ---------------------------------------------------------------------------

RULE_G01 = {"id": "R-G01", "label": "投资操作"}
RULE_G02 = {"id": "R-G02", "label": "收益承诺"}
RULE_G03 = {"id": "R-G03", "label": "风险提示缺失"}
ALL_RULES = [RULE_G01, RULE_G02, RULE_G03]


# ---------------------------------------------------------------------------
# 公共 fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rule_g01():
    """仅包含 R-G01（投资操作表述）的规则列表"""
    return [RULE_G01]


@pytest.fixture
def rule_g02():
    """仅包含 R-G02（收益承诺）的规则列表"""
    return [RULE_G02]


@pytest.fixture
def all_rules():
    """同时包含 R-G01、R-G02、R-G03 的完整规则列表"""
    return list(ALL_RULES)


# ===========================================================================
# 正向测试：R-G01 — 投资操作表述
# ===========================================================================

class TestScanTextG01Keywords:
    """R-G01 每个关键词单独命中测试"""

    @pytest.mark.parametrize(
        "keyword",
        ["全仓", "清仓", "买入", "卖出", "加仓", "减仓", "调仓"],
        ids=lambda k: f"R-G01-{k}",
    )
    def test_scan_text_g01_single_keyword_hit(self, keyword, rule_g01):
        """TC-M01-C01~C07 · L1 · R-G01 的每个关键词单独出现时应命中"""
        text = f"建议您{keyword}该股票"
        hits = scan_text(text, rule_g01)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G01"

    @pytest.mark.parametrize(
        "keyword",
        ["全仓", "清仓", "买入", "卖出", "加仓", "减仓", "调仓"],
        ids=lambda k: f"R-G01-long-{k}",
    )
    def test_scan_text_g01_keyword_in_long_text(self, keyword, rule_g01):
        """TC-M01-C08~C14 · L1 · R-G01 关键词嵌套在长文本中间时仍应命中"""
        text = (
            f"根据市场分析，综合考虑多方因素，我们认为投资者可以考虑"
            f"{keyword}操作，请谨慎评估风险后再做决定。"
        )
        hits = scan_text(text, rule_g01)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G01"


# ===========================================================================
# 正向测试：R-G02 — 收益承诺
# ===========================================================================

class TestScanTextG02Keywords:
    """R-G02 每个关键词单独命中测试"""

    @pytest.mark.parametrize(
        "keyword",
        ["保证收益", "稳赚", "无风险", "保本"],
        ids=lambda k: f"R-G02-{k}",
    )
    def test_scan_text_g02_single_keyword_hit(self, keyword, rule_g02):
        """TC-M01-C15~C18 · L1 · R-G02 的每个关键词单独出现时应命中"""
        text = f"该产品{keyword}，欢迎购买。"
        hits = scan_text(text, rule_g02)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G02"

    @pytest.mark.parametrize(
        "keyword",
        ["保证收益", "稳赚", "无风险", "保本"],
        ids=lambda k: f"R-G02-long-{k}",
    )
    def test_scan_text_g02_keyword_in_long_text(self, keyword, rule_g02):
        """TC-M01-C19~C22 · L1 · R-G02 关键词嵌套在长文本中间时仍应命中"""
        text = (
            f"经过专业团队严格筛选，本期产品{keyword}，"
            f"年化回报可观，详情请咨询客服。"
        )
        hits = scan_text(text, rule_g02)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G02"


# ===========================================================================
# 正向测试：同时命中 R-G01 和 R-G02
# ===========================================================================

class TestScanTextMultipleRules:
    """多规则同时命中的场景"""

    def test_scan_text_g01_g02_both_hit(self, all_rules):
        """TC-M01-C23 · L2 · 文本同时包含 R-G01 和 R-G02 关键词时，两条规则均应命中"""
        text = "建议全仓买入，保证收益不亏损。"
        hits = scan_text(text, all_rules)
        rule_ids = [h["rule_id"] for h in hits]
        assert "R-G01" in rule_ids
        assert "R-G02" in rule_ids
        # 文本不含金融产品词（基金/理财/投资/股票/债券），R-G03 不触发
        assert len(hits) == 2

    def test_scan_text_g01_g02_different_keywords(self, all_rules):
        """TC-M01-C24 · L2 · 不同关键词组合同时触发 R-G01 和 R-G02"""
        text = "稳赚不赔，立刻调仓获取高收益！"
        hits = scan_text(text, all_rules)
        rule_ids = [h["rule_id"] for h in hits]
        assert "R-G01" in rule_ids
        assert "R-G02" in rule_ids

    def test_scan_text_all_three_rules_hit(self, all_rules):
        """TC-M01-C69 · L2 · 文本同时触发 R-G01、R-G02、R-G03 三条规则"""
        text = "建议全仓买入该基金，保证收益绝对安全！"
        hits = scan_text(text, all_rules)
        rule_ids = {h["rule_id"] for h in hits}
        assert rule_ids == {"R-G01", "R-G02", "R-G03"}
        assert len(hits) == 3

    def test_scan_text_g01_g03_hit_g02_miss(self, all_rules):
        """TC-M01-C70 · L2 · 触发 R-G01 + R-G03，但不触发 R-G02"""
        text = "建议买入该股票，配置价值较高。"
        hits = scan_text(text, all_rules)
        rule_ids = {h["rule_id"] for h in hits}
        assert "R-G01" in rule_ids
        assert "R-G03" in rule_ids
        assert "R-G02" not in rule_ids


# ===========================================================================
# 反向测试：不应命中的文本
# ===========================================================================

class TestScanTextNoHit:
    """不含敏感词的文本不应产生任何命中"""

    def test_scan_text_normal_text_no_hit(self, all_rules):
        """TC-M01-C25 · L1 · 正常的投研分析文本不应触发任何规则"""
        text = "该公司基本面良好，市盈率处于合理区间，长期价值值得关注。"
        hits = scan_text(text, all_rules)
        assert hits == []

    def test_scan_text_empty_string_no_hit(self, all_rules):
        """TC-M01-C26 · L1 · 空字符串不应触发任何规则"""
        hits = scan_text("", all_rules)
        assert hits == []

    def test_scan_text_similar_purchase_not_sensitive(self, all_rules):
        """TC-M01-C27 · L1 · '购买' 与 '买入' 形似但不应触发 R-G01"""
        text = "您可以通过官网购买该产品，投资有风险。"
        hits = scan_text(text, all_rules)
        rule_ids = [h["rule_id"] for h in hits]
        assert "R-G01" not in rule_ids
        assert hits == []

    def test_scan_text_profit_word_alone_no_hit(self, all_rules):
        """TC-M01-C28 · L1 · '收益' 单独出现不触发 R-G02，须为完整词组 '保证收益'"""
        text = "该产品历史收益表现优异，但不代表未来。"
        hits = scan_text(text, all_rules)
        rule_ids = [h["rule_id"] for h in hits]
        assert "R-G02" not in rule_ids

    def test_scan_text_risk_word_alone_no_hit(self, all_rules):
        """TC-M01-C29 · L1 · '风险' 单独出现不触发 R-G02，须为完整词组 '无风险'"""
        text = "投资有风险，请充分了解产品后谨慎决策。"
        hits = scan_text(text, all_rules)
        rule_ids = [h["rule_id"] for h in hits]
        assert "R-G02" not in rule_ids

    def test_scan_text_whitespace_only_no_hit(self, all_rules):
        """TC-M01-C30 · L1 · 纯空白字符不应触发任何规则"""
        hits = scan_text("   \t\n  ", all_rules)
        assert hits == []


# ===========================================================================
# 边界测试：规则列表变体
# ===========================================================================

class TestScanTextEdgeCases:
    """边界条件测试"""

    def test_scan_text_empty_rules_no_hit(self):
        """TC-M01-C31 · L2 · rules 为空列表时，即使文本含敏感词也不命中"""
        text = "建议全仓买入，保证收益。"
        hits = scan_text(text, [])
        assert hits == []

    def test_scan_text_only_g01_rule_ignores_g02_keywords(self, rule_g01):
        """TC-M01-C32 · L2 · 只传入 R-G01 规则时，R-G02 关键词不应产生命中"""
        text = "该产品保证收益，稳赚不赔。"
        hits = scan_text(text, rule_g01)
        rule_ids = [h["rule_id"] for h in hits]
        assert "R-G02" not in rule_ids
        # 文本中无 R-G01 关键词，结果应为空
        assert hits == []

    def test_scan_text_only_g02_rule_ignores_g01_keywords(self, rule_g02):
        """TC-M01-C33 · L2 · 只传入 R-G02 规则时，R-G01 关键词不应产生命中"""
        text = "建议全仓买入该股票。"
        hits = scan_text(text, rule_g02)
        rule_ids = [h["rule_id"] for h in hits]
        assert "R-G01" not in rule_ids
        # 文本中无 R-G02 关键词，结果应为空
        assert hits == []

    def test_scan_text_only_g01_rule_hits_correctly(self, rule_g01):
        """TC-M01-C34 · L2 · 只传入 R-G01 规则，且文本含 R-G01 关键词时应正常命中"""
        text = "建议您买入该股票。"
        hits = scan_text(text, rule_g01)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G01"

    def test_scan_text_only_g02_rule_hits_correctly(self, rule_g02):
        """TC-M01-C35 · L2 · 只传入 R-G02 规则，且文本含 R-G02 关键词时应正常命中"""
        text = "该产品无风险，欢迎认购。"
        hits = scan_text(text, rule_g02)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G02"

    def test_scan_text_g01_multiple_keywords_hit_only_once(self, rule_g01):
        """TC-M01-C36 · L2 · 文本含多个 R-G01 关键词时，R-G01 规则只应命中一次"""
        text = "建议全仓买入，同时加仓减仓调仓操作。"
        hits = scan_text(text, rule_g01)
        g01_hits = [h for h in hits if h["rule_id"] == "R-G01"]
        assert len(g01_hits) == 1

    def test_scan_text_g02_multiple_keywords_hit_only_once(self, rule_g02):
        """TC-M01-C37 · L2 · 文本含多个 R-G02 关键词时，R-G02 规则只应命中一次"""
        text = "保证收益、稳赚不赔、无风险、保本产品。"
        hits = scan_text(text, rule_g02)
        g02_hits = [h for h in hits if h["rule_id"] == "R-G02"]
        assert len(g02_hits) == 1

    def test_scan_text_unknown_rule_id_ignored(self):
        """TC-M01-C38 · L2 · 传入未知 rule_id 的规则时，应被忽略，不产生命中"""
        text = "建议全仓买入，保证收益。"
        hits = scan_text(text, [{"id": "R-UNKNOWN"}])
        assert hits == []


# ===========================================================================
# 返回值结构验证
# ===========================================================================

class TestScanTextReturnStructure:
    """验证返回值的字段完整性与内容正确性"""

    def test_scan_text_g01_hit_has_required_fields(self, rule_g01):
        """TC-M01-C39 · L1 · R-G01 命中结果应包含 rule_id、span、message 三个字段"""
        hits = scan_text("建议买入该股票。", rule_g01)
        assert len(hits) == 1
        hit = hits[0]
        assert "rule_id" in hit, "缺少 rule_id 字段"
        assert "span" in hit, "缺少 span 字段"
        assert "message" in hit, "缺少 message 字段"

    def test_scan_text_g02_hit_has_required_fields(self, rule_g02):
        """TC-M01-C40 · L1 · R-G02 命中结果应包含 rule_id、span、message 三个字段"""
        hits = scan_text("该产品保本保收益。", rule_g02)
        assert len(hits) == 1
        hit = hits[0]
        assert "rule_id" in hit, "缺少 rule_id 字段"
        assert "span" in hit, "缺少 span 字段"
        assert "message" in hit, "缺少 message 字段"

    def test_scan_text_g01_rule_id_value(self, rule_g01):
        """TC-M01-C41 · L1 · R-G01 命中结果的 rule_id 值应为 'R-G01'"""
        hits = scan_text("卖出操作", rule_g01)
        assert hits[0]["rule_id"] == "R-G01"

    def test_scan_text_g02_rule_id_value(self, rule_g02):
        """TC-M01-C42 · L1 · R-G02 命中结果的 rule_id 值应为 'R-G02'"""
        hits = scan_text("稳赚产品", rule_g02)
        assert hits[0]["rule_id"] == "R-G02"

    def test_scan_text_g01_span_value(self, rule_g01):
        """TC-M01-C43 · L1 · R-G01 命中结果的 span 应为 'investment_ops'"""
        hits = scan_text("建议加仓。", rule_g01)
        assert hits[0]["span"] == "investment_ops"

    def test_scan_text_g02_span_value(self, rule_g02):
        """TC-M01-C44 · L1 · R-G02 命中结果的 span 应为 'return_promise'"""
        hits = scan_text("无风险投资。", rule_g02)
        assert hits[0]["span"] == "return_promise"

    def test_scan_text_g01_message_content(self, rule_g01):
        """TC-M01-C45 · L1 · R-G01 命中结果的 message 应包含 '投资操作' 相关描述"""
        hits = scan_text("建议清仓。", rule_g01)
        assert "投资操作" in hits[0]["message"]

    def test_scan_text_g02_message_content(self, rule_g02):
        """TC-M01-C46 · L1 · R-G02 命中结果的 message 应包含 '收益承诺' 相关描述"""
        hits = scan_text("保证收益产品。", rule_g02)
        assert "收益承诺" in hits[0]["message"]

    def test_scan_text_return_type_is_list(self, all_rules):
        """TC-M01-C47 · L1 · scan_text 返回值类型应为 list"""
        result = scan_text("普通文本", all_rules)
        assert isinstance(result, list)

    def test_scan_text_each_hit_is_dict(self, all_rules):
        """TC-M01-C48 · L1 · 命中列表中每个元素类型应为 dict"""
        hits = scan_text("建议全仓买入，保证收益。", all_rules)
        for hit in hits:
            assert isinstance(hit, dict)


# ===========================================================================
# 正向测试：R-G03 — 风险提示缺失检测
# ===========================================================================

@pytest.fixture
def rule_g03():
    """仅包含 R-G03（风险提示缺失）的规则列表"""
    return [RULE_G03]


class TestScanTextG03MissingRiskWarning:
    """R-G03 风险提示缺失检测：含金融产品词但缺少风险提示时应命中"""

    @pytest.mark.parametrize(
        "keyword",
        ["基金", "理财", "投资", "股票", "债券"],
        ids=lambda k: f"R-G03-{k}",
    )
    def test_g03_missing_risk_warning_hit(self, keyword, rule_g03):
        """TC-M01-C49~C53 · L1 · 含金融产品词但无风险提示应触发 R-G03"""
        text = f"推荐这只{keyword}产品收益不错"
        hits = scan_text(text, rule_g03)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G03"
        assert hits[0]["span"] == "missing_risk_warning"

    @pytest.mark.parametrize(
        "keyword",
        ["基金", "理财", "投资", "股票", "债券"],
        ids=lambda k: f"R-G03-long-{k}",
    )
    def test_g03_missing_risk_in_long_text(self, keyword, rule_g03):
        """TC-M01-C54~C58 · L1 · 长文本中含金融产品词但无风险提示也应触发"""
        text = (
            f"经过深入研究，我们认为该{keyword}产品具有较高的配置价值，"
            f"建议适当关注并考虑纳入资产组合。"
        )
        hits = scan_text(text, rule_g03)
        assert len(hits) == 1
        assert hits[0]["rule_id"] == "R-G03"


class TestScanTextG03WithRiskWarningNoHit:
    """R-G03 反向测试：含金融产品词且有风险提示时不应命中"""

    @pytest.mark.parametrize(
        "disclaimer",
        ["投资有风险", "市场有风险", "风险自担", "不代表未来"],
        ids=lambda d: f"disclaimer-{d}",
    )
    def test_g03_with_disclaimer_no_hit(self, disclaimer, rule_g03):
        """TC-M01-C59~C62 · L1 · 含金融产品词但附带风险提示不应触发 R-G03"""
        text = f"推荐这只基金产品收益不错，{disclaimer}，入市需谨慎。"
        hits = scan_text(text, rule_g03)
        assert hits == []

    def test_g03_no_financial_keyword_no_hit(self, rule_g03):
        """TC-M01-C63 · L1 · 不含金融产品词的文本不应触发 R-G03"""
        text = "今天天气很好，适合出去散步。"
        hits = scan_text(text, rule_g03)
        assert hits == []

    def test_g03_empty_text_no_hit(self, rule_g03):
        """TC-M01-C64 · L2 · 空文本不应触发 R-G03"""
        assert scan_text("", rule_g03) == []


class TestScanTextG03ReturnStructure:
    """R-G03 返回值结构验证"""

    def test_g03_hit_has_required_fields(self, rule_g03):
        """TC-M01-C65 · L1 · R-G03 命中结果应包含 rule_id、span、message 三个字段"""
        hits = scan_text("推荐该基金产品", rule_g03)
        assert len(hits) == 1
        hit = hits[0]
        assert "rule_id" in hit
        assert "span" in hit
        assert "message" in hit

    def test_g03_span_value(self, rule_g03):
        """TC-M01-C66 · L1 · R-G03 命中结果 span 应为 'missing_risk_warning'"""
        hits = scan_text("推荐该理财产品", rule_g03)
        assert hits[0]["span"] == "missing_risk_warning"

    def test_g03_message_content(self, rule_g03):
        """TC-M01-C67 · L1 · R-G03 命中结果 message 应包含 '风险提示' 相关描述"""
        hits = scan_text("推荐该股票", rule_g03)
        assert "风险提示" in hits[0]["message"]

    def test_g03_multiple_financial_keywords_hit_once(self, rule_g03):
        """TC-M01-C68 · L2 · 文本含多个金融产品词时，R-G03 只命中一次"""
        text = "推荐基金和股票以及债券产品"
        hits = scan_text(text, rule_g03)
        g03_hits = [h for h in hits if h["rule_id"] == "R-G03"]
        assert len(g03_hits) == 1
