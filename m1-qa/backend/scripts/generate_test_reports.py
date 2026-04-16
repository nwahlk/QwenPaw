# -*- coding: utf-8 -*-
"""
生成测试用模拟研报 PDF 文件
用于研报上传与对比功能的集成测试
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_reports")


def create_styles():
    """创建文档样式"""
    styles = getSampleStyleSheet()
    
    # 尝试注册中文字体（如果失败则使用默认字体）
    try:
        pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
        chinese_font = 'SimHei'
    except:
        chinese_font = 'Helvetica'
    
    # 标题样式
    title_style = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Title'],
        fontName=chinese_font,
        fontSize=18,
        spaceAfter=20,
        alignment=1,  # 居中
    )
    
    # 一级标题
    h1_style = ParagraphStyle(
        'ChineseH1',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.darkblue,
    )
    
    # 二级标题
    h2_style = ParagraphStyle(
        'ChineseH2',
        parent=styles['Heading2'],
        fontName=chinese_font,
        fontSize=12,
        spaceBefore=10,
        spaceAfter=8,
        textColor=colors.darkslategray,
    )
    
    # 正文样式
    body_style = ParagraphStyle(
        'ChineseBody',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=10,
        leading=16,
        spaceAfter=8,
    )
    
    return title_style, h1_style, h2_style, body_style


def create_semiconductor_report():
    """创建半导体行业研报"""
    output_path = os.path.join(OUTPUT_DIR, "test_report_semiconductor_2024.pdf")
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    title_style, h1_style, h2_style, body_style = create_styles()
    story = []
    
    # 标题
    story.append(Paragraph("2024年半导体行业深度研究报告", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 一、行业概述
    story.append(Paragraph("一、行业概述", h1_style))
    story.append(Paragraph(
        "半导体行业作为现代信息技术的基石，在2024年呈现出复杂的发展态势。全球半导体市场规模预计达到6,520亿美元，"
        "同比增长11.5%。其中，逻辑芯片和存储芯片是两大主要细分市场，分别占据市场总额的35%和28%。",
        body_style
    ))
    story.append(Paragraph(
        "从产业链角度看，半导体行业可分为设计、制造、封测三大环节。台积电、三星等晶圆代工厂在先进制程领域持续领先，"
        "而中国大陆企业在成熟制程领域竞争力不断增强。设备材料领域仍被美日欧企业主导，国产替代空间广阔。",
        body_style
    ))
    
    # 二、核心观点
    story.append(Paragraph("二、核心观点", h1_style))
    story.append(Paragraph("2.1 周期拐点已现，行业进入复苏通道", h2_style))
    story.append(Paragraph(
        "经历了2023年的深度调整后，半导体行业库存周期已接近底部。全球主要芯片厂商库存周转天数从2023年高点的180天"
        "下降至2024年一季度的120天，接近健康水平。手机、PC等消费电子需求回暖，汽车电子和工业控制需求保持稳定增长，"
        "行业整体进入复苏通道。",
        body_style
    ))
    
    story.append(Paragraph("2.2 AI驱动高端芯片需求爆发", h2_style))
    story.append(Paragraph(
        "人工智能技术的突破性进展带动高端GPU、HBM存储需求爆发式增长。英伟达H100/A100系列GPU供不应求，"
        "SK海力士HBM产能已被预订至2025年。预计AI芯片市场2024年增速将超过50%，成为半导体行业增长的主要驱动力。",
        body_style
    ))
    
    story.append(Paragraph("2.3 国产替代进入深水区", h2_style))
    story.append(Paragraph(
        "在美国出口管制持续收紧的背景下，半导体设备、材料、EDA工具等领域的国产替代进程加速。"
        "中微公司刻蚀设备已进入台积电供应链，北方华创平台型设备布局日趋完善，但高端光刻机、先进制程光刻胶等"
        "核心环节仍存在较大差距。",
        body_style
    ))
    
    # 三、投资建议
    story.append(Paragraph("三、投资建议", h1_style))
    story.append(Paragraph(
        "建议重点关注以下投资主线：1）AI算力芯片产业链，包括高端GPU、HBM存储、先进封装等环节；"
        "2）半导体设备国产替代，重点关注刻蚀、薄膜沉积、量测检测等细分领域龙头；"
        "3）汽车电子和工业控制芯片，受益于新能源车渗透率提升和工业4.0进程。",
        body_style
    ))
    text1 = '个股推荐：中微公司（688012）、北方华创（002371）、寒武纪（688256）、澜起科技（688008）。给予半导体行业"强于大市"评级。'
    story.append(Paragraph(text1, body_style))
    
    # 四、风险提示
    story.append(Paragraph("四、风险提示", h1_style))
    story.append(Paragraph(
        "1）宏观经济下行风险：全球经济衰退可能导致消费电子需求持续疲软；"
        "2）技术迭代风险：技术路线变化可能导致现有投资失效；"
        "3）地缘政治风险：美国出口管制政策可能进一步收紧；"
        "4）估值风险：部分个股估值处于历史高位，存在回调压力。",
        body_style
    ))
    
    # 五、财务数据
    story.append(Paragraph("五、重点公司财务数据", h1_style))
    
    table_data = [
        ['公司名称', '股票代码', '市值(亿)', 'PE(TTM)', '评级'],
        ['中微公司', '688012', '850', '65x', '买入'],
        ['北方华创', '002371', '1,200', '58x', '买入'],
        ['寒武纪', '688256', '620', '-', '增持'],
        ['澜起科技', '688008', '580', '42x', '买入'],
    ]
    
    table = Table(table_data, colWidths=[3*cm, 2.5*cm, 2*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    
    doc.build(story)
    print(f"已生成: {output_path}")
    return output_path


def create_newenergy_report():
    """创建新能源行业研报"""
    output_path = os.path.join(OUTPUT_DIR, "test_report_newenergy_2024.pdf")
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    title_style, h1_style, h2_style, body_style = create_styles()
    story = []
    
    # 标题
    story.append(Paragraph("2024年新能源汽车行业研究报告", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 一、行业概述
    story.append(Paragraph("一、行业概述", h1_style))
    story.append(Paragraph(
        "新能源汽车行业在2024年继续保持高速增长态势。全球新能源车销量预计达到1,850万辆，渗透率突破20%。"
        "中国作为全球最大的新能源汽车市场，年销量有望突破1,000万辆，占全球市场份额的54%以上。",
        body_style
    ))
    story.append(Paragraph(
        "产业链上游为锂、钴、镍等原材料，中游为动力电池、电机、电控等核心零部件，下游为整车制造和充电基础设施。"
        "动力电池成本占整车成本的30%-40%，是产业链的核心环节。宁德时代、比亚迪占据全球动力电池市场65%以上份额。",
        body_style
    ))
    
    # 二、核心观点
    story.append(Paragraph("二、核心观点", h1_style))
    story.append(Paragraph("2.1 价格战趋缓，行业格局优化", h2_style))
    story.append(Paragraph(
        "经历了2023年的激烈价格战后，新能源汽车行业竞争格局趋于稳定。头部企业市场份额持续提升，"
        "比亚迪、特斯拉、理想、问界等品牌形成第一梯队。二三线品牌加速出清，行业集中度不断提升。"
        "预计2024年行业价格战强度将显著下降，企业盈利能力有望改善。",
        body_style
    ))
    
    story.append(Paragraph("2.2 电池技术路线分化明显", h2_style))
    story.append(Paragraph(
        "动力电池技术路线呈现多元化发展趋势。磷酸铁锂电池凭借成本优势在入门级和中端车型占据主导，"
        "市场份额超过60%；三元锂电池在高端车型和长续航车型中保持优势；固态电池、钠离子电池等新技术"
        "逐步进入产业化阶段。4680大圆柱电池产能爬坡，有望成为新一代主流技术路线。",
        body_style
    ))
    
    story.append(Paragraph("2.3 智能化成为核心竞争点", h2_style))
    story.append(Paragraph(
        "智能驾驶和智能座舱成为新能源汽车差异化竞争的核心。华为、小鹏、理想等企业在NOA（导航辅助驾驶）"
        "领域持续迭代，城市NOA功能已覆盖全国主要城市。预计2024年L3级别自动驾驶将实现量产落地，"
        "智能化功能将成为消费者购车的重要考量因素。",
        body_style
    ))
    
    # 三、投资建议
    story.append(Paragraph("三、投资建议", h1_style))
    story.append(Paragraph(
        "建议关注以下投资主线：1）动力电池龙头及优质二线厂商，受益于行业量利齐升；"
        "2）汽车智能化产业链，包括域控制器、传感器、车载软件等环节；"
        "3）充电桩产业链，受益于快充网络加速建设。",
        body_style
    ))
    text2 = '个股推荐：宁德时代（300750）、比亚迪（002594）、德赛西威（002920）、拓普集团（601689）。给予新能源汽车行业"强于大市"评级。'
    story.append(Paragraph(text2, body_style))
    
    # 四、风险提示
    story.append(Paragraph("四、风险提示", h1_style))
    story.append(Paragraph(
        "1）行业竞争加剧风险：新进入者持续增加，价格战可能再度升级；"
        "2）原材料价格波动风险：锂价大幅波动影响电池厂商盈利；"
        "3）政策支持力度减弱风险：补贴退坡可能影响需求；"
        "4）技术路线不确定性风险：新技术迭代可能改变竞争格局。",
        body_style
    ))
    
    # 五、财务数据
    story.append(Paragraph("五、重点公司财务数据", h1_style))
    
    table_data = [
        ['公司名称', '股票代码', '市值(亿)', 'PE(TTM)', '评级'],
        ['宁德时代', '300750', '8,500', '22x', '买入'],
        ['比亚迪', '002594', '6,200', '28x', '买入'],
        ['德赛西威', '002920', '680', '45x', '增持'],
        ['拓普集团', '601689', '520', '32x', '买入'],
    ]
    
    table = Table(table_data, colWidths=[3*cm, 2.5*cm, 2*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkgreen),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    
    doc.build(story)
    print(f"已生成: {output_path}")
    return output_path


def create_ai_report():
    """创建AI行业研报"""
    output_path = os.path.join(OUTPUT_DIR, "test_report_ai_2024.pdf")
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    title_style, h1_style, h2_style, body_style = create_styles()
    story = []
    
    # 标题
    story.append(Paragraph("2024年人工智能行业深度研究报告", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 一、行业概述
    story.append(Paragraph("一、行业概述", h1_style))
    story.append(Paragraph(
        "人工智能行业在2024年进入爆发式增长阶段。以ChatGPT为代表的大语言模型技术突破，"
        "推动了AI应用的全面普及。全球AI市场规模预计达到5,200亿美元，同比增长38%。"
        "生成式AI成为最热门的细分赛道，市场规模增速超过100%。",
        body_style
    ))
    story.append(Paragraph(
        "AI产业链可分为三层：基础层（算力芯片、云计算基础设施）、技术层（算法模型、开发平台）、"
        "应用层（垂直行业解决方案、消费级应用）。英伟达在AI芯片领域占据绝对主导地位，"
        "OpenAI、Google、Meta等在模型领域竞争激烈，应用层呈现百花齐放态势。",
        body_style
    ))
    
    # 二、核心观点
    story.append(Paragraph("二、核心观点", h1_style))
    story.append(Paragraph("2.1 算力需求持续高景气", h2_style))
    story.append(Paragraph(
        "大模型训练和推理对算力的需求呈指数级增长。GPT-4训练消耗约25,000张A100 GPU算力，"
        "而GPT-5的训练规模预计将是GPT-4的5-10倍。全球AI芯片市场预计2024年增长52%，"
        "达到900亿美元规模。英伟达H100/H200系列供不应求，预计供需紧张将持续至2025年。",
        body_style
    ))
    
    story.append(Paragraph("2.2 大模型竞争白热化", h2_style))
    story.append(Paragraph(
        "大语言模型领域竞争进入白热化阶段。GPT-4、Claude 3、Gemini等闭源模型持续迭代，"
        "Llama 3、Mistral等开源模型快速追赶。国产大模型取得显著进展，"
        "通义千问、文心一言、智谱GLM等已达到接近GPT-3.5的水平。模型参数规模进入万亿时代，"
        "训练成本和推理成本持续攀升。",
        body_style
    ))
    
    story.append(Paragraph("2.3 B端应用加速落地", h2_style))
    story.append(Paragraph(
        "AI在企业端的应用场景加速落地。智能客服、代码生成、内容创作、数据分析等场景已产生明确ROI。"
        "金融、医疗、教育、法律等专业领域的AI应用快速渗透。预计到2026年，"
        "超过70%的企业将部署AI助手，AI将成为企业数字化转型的核心驱动力。",
        body_style
    ))
    
    # 三、投资建议
    story.append(Paragraph("三、投资建议", h1_style))
    story.append(Paragraph(
        "建议关注以下投资主线：1）AI算力产业链，包括GPU、光模块、服务器等；"
        "2）AI应用落地，重点关注金融、教育、医疗等垂直领域；"
        "3）AI数据要素，数据标注、高质量语料库需求爆发。",
        body_style
    ))
    text3 = '个股推荐：科大讯飞（002230）、金山办公（688111）、光云科技（300771）、寒武纪（688256）。给予AI行业"强于大市"评级。'
    story.append(Paragraph(text3, body_style))
    
    # 四、风险提示
    story.append(Paragraph("四、风险提示", h1_style))
    story.append(Paragraph(
        "1）技术迭代风险：AI技术快速迭代可能导致现有投资失效；"
        "2）监管政策风险：AI安全监管可能限制应用场景；"
        "3）估值风险：部分AI概念股估值过高，存在回调风险；"
        "4）商业化不确定性风险：部分应用场景商业化进程可能不及预期。",
        body_style
    ))
    
    # 五、财务数据
    story.append(Paragraph("五、重点公司财务数据", h1_style))
    
    table_data = [
        ['公司名称', '股票代码', '市值(亿)', 'PE(TTM)', '评级'],
        ['科大讯飞', '002230', '920', '85x', '增持'],
        ['金山办公', '688111', '1,100', '72x', '买入'],
        ['光云科技', '300771', '85', '-', '观望'],
        ['寒武纪', '688256', '620', '-', '增持'],
    ]
    
    table = Table(table_data, colWidths=[3*cm, 2.5*cm, 2*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkorange),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    
    doc.build(story)
    print(f"已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    print("开始生成测试研报 PDF 文件...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    create_semiconductor_report()
    create_newenergy_report()
    create_ai_report()
    
    print("\n所有测试研报已生成完成！")
    print(f"文件位置: {os.path.abspath(OUTPUT_DIR)}")
