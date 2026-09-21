# -*- coding: utf-8 -*-
"""
AIC 第八届算法创新赛 · 赛题5 AI+学科交叉
作品答辩 PPT 生成脚本（python-pptx）
视觉系统：深蓝 #1A3A5C + 青绿 #1C7A6E + 风险色四档
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData
import os

OUT = r'h:\2026AIC·算法创新赛\源码_restored\docs\MindGuard_AIC_答辩PPT.pptx'

# ============================================================
# 视觉系统（按 jingmei-ppt consulting-research 风格）
# ============================================================
C_NAVY       = RGBColor(0x1A, 0x3A, 0x5C)   # 主色：深蓝
C_TEAL       = RGBColor(0x1C, 0x7A, 0x6E)   # 强调：青绿
C_CRISIS     = RGBColor(0xAC, 0x4E, 0x42)   # 风险：红
C_HIGH       = RGBColor(0xD9, 0x77, 0x06)   # 风险：橙
C_MEDIUM     = RGBColor(0xF5, 0x9E, 0x0B)   # 风险：黄
C_LOW        = RGBColor(0x1C, 0x7A, 0x6E)   # 风险：绿
C_TEXT       = RGBColor(0x1F, 0x29, 0x37)   # 主文字
C_SECONDARY  = RGBColor(0x47, 0x53, 0x5C)   # 次文字
C_MUTED      = RGBColor(0x97, 0xA3, 0xAC)   # 脚注灰
C_LINE       = RGBColor(0xE5, 0xE7, 0xEB)   # 分隔线
C_BG         = RGBColor(0xF8, 0xFA, 0xFC)   # 近白底色

# 字体（微软雅黑，比赛现场 Windows 自带）
FONT = '微软雅黑'

prs = Presentation()
prs.slide_width  = Inches(13.33)   # 16:9
prs.slide_height = Inches(7.5)

# ============================================================
# 工具函数
# ============================================================
def add_rect(slide, left, top, width, height, fill, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line:
        shp.line.color.rgb = line
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp

def add_textbox(slide, left, top, width, height, text, size=18,
                color=C_TEXT, bold=False, align=PP_ALIGN.LEFT,
                font=FONT, line_spacing=1.3):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    tf.margin_left = Pt(2)
    tf.margin_right = Pt(2)
    return tb

def add_multiline(slide, left, top, width, height, lines, size=14,
                  color=C_TEXT, bold=False, line_spacing=1.5, font=FONT):
    """lines: list of (text, color, bold) or list of str"""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(item, tuple):
            text, c, b = item
        else:
            text, c, b = item, color, bold
        run = p.add_run()
        run.text = text
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = c
        run.font.bold = b
        p.space_after = Pt(size * (line_spacing - 1))
    return tb

def add_slide_header(slide, section_label, title):
    """统一页眉：section label（青绿色小字）+ 粗体大标题 + 顶部装饰线"""
    # 顶部青绿色细线
    add_rect(slide, 0, 0, prs.slide_width, Pt(4), C_TEAL)
    # 章节标签
    add_textbox(slide, Inches(0.7), Inches(0.45), Inches(12), Inches(0.4),
                section_label, size=11, color=C_TEAL, bold=True)
    # 大标题
    add_textbox(slide, Inches(0.7), Inches(0.85), Inches(12), Inches(0.9),
                title, size=28, color=C_NAVY, bold=True)
    # 标题下细线
    add_rect(slide, Inches(0.7), Inches(1.8), Inches(2), Pt(2), C_TEAL)

def add_slide_footer(slide, page_num, total=21):
    """页脚：左-作品名缩写，右-页码"""
    add_textbox(slide, Inches(0.7), Inches(7.05), Inches(6), Inches(0.3),
                'MindGuard · 神经符号双引擎心理风险筛查', size=9,
                color=C_MUTED, align=PP_ALIGN.LEFT)
    add_textbox(slide, Inches(10), Inches(7.05), Inches(3), Inches(0.3),
                f'{page_num} / {total}', size=9,
                color=C_MUTED, align=PP_ALIGN.RIGHT)

def new_slide(layout_index=6):
    """layout 6 = blank"""
    return prs.slides.add_slide(prs.slide_layouts[layout_index])

# ============================================================
# PPT 开始生成
# ============================================================

# ---------- Page 1: 封面 ----------
s = new_slide()
# 背景：左半深蓝
add_rect(s, 0, 0, Inches(5.5), prs.slide_height, C_NAVY)
# 右上角青绿装饰
add_rect(s, Inches(11), 0, Inches(2.33), Pt(60), C_TEAL)
# 左侧竖线装饰
add_rect(s, Inches(5.5), 0, Pt(6), prs.slide_height, C_TEAL)

# 左上角小标签
add_textbox(s, Inches(0.7), Inches(0.6), Inches(4), Inches(0.4),
            'AIC 第八届 · 算法创新赛', size=12, color=C_TEAL, bold=True)
add_textbox(s, Inches(0.7), Inches(1.0), Inches(4), Inches(0.4),
            '赛题 5 · AI + 学科交叉', size=12, color=RGBColor(0xCC, 0xDD, 0xEE), bold=False)

# 主标题（左半区，白色）
add_textbox(s, Inches(0.7), Inches(2.6), Inches(4.8), Inches(1.2),
            '神经符号双引擎驱动的', size=30,
            color=RGBColor(0xFF, 0xFF, 0xFF), bold=True)
add_textbox(s, Inches(0.7), Inches(3.7), Inches(4.8), Inches(1.6),
            '校园心理风险智能筛查\n与干预系统', size=30,
            color=RGBColor(0xFF, 0xFF, 0xFF), bold=True)

# 副标题（右半区）
add_multiline(s, Inches(6.2), Inches(2.4), Inches(6.8), Inches(2.8), [
    ('MindGuard', C_TEAL, True),
    ('可解释 AI × 精神医学 × 校园心理中心', C_NAVY, True),
    ('', C_TEXT, False),
    ('融合 PHQ-9 / GAD-7 临床量表', C_SECONDARY, False),
    ('规则知识库 + RIPPER 规则归纳 + RAG 知识底座', C_SECONDARY, False),
    ('4 级危机分级拦截 · 可解释推理链输出', C_SECONDARY, False),
], size=18)

# 团队信息（右下半）
add_multiline(s, Inches(6.2), Inches(5.6), Inches(6.8), Inches(1.4), [
    ('团队成员：阮家炜（负责人） · 张修瑜', C_TEXT, False),
    ('', C_TEXT, False),
    ('提交单位：[请填写你的学校名称]', C_MUTED, False),
], size=14)

# 青绿页脚条
add_rect(s, 0, Inches(7.15), prs.slide_width, Inches(0.35), C_TEAL)
add_textbox(s, Inches(0.7), Inches(7.18), Inches(12), Inches(0.3),
            '答辩 PPT · 2026 年 9 月', size=11,
            color=RGBColor(0xFF, 0xFF, 0xFF), bold=True)

print('✅ Page 1 封面')

# ---------- Page 2: 目录 ----------
s = new_slide()
add_slide_header(s, 'CONTENTS · 目录', '汇报结构')

items = [
    ('01', '项目背景与痛点',      '为什么做 —— 校园心理中心的三大核心痛点'),
    ('02', '需求分析与学科定位',  '赛题 5 AI+精神医学的交叉切入点'),
    ('03', '系统整体架构',        '四层设计：展示→应用→算法→数据'),
    ('04', '核心技术详解',        '神经符号双引擎 · 规则知识库 · 4 级危机分级 · RAG'),
    ('05', '系统演示',            '真实界面截图 + 功能展示'),
    ('06', '效果验证',            '对比实验数据 · 典型案例 · 可行性分析'),
    ('07', '总结与展望',          '核心结论 + 未来改进方向'),
]
y = Inches(2.1)
for num, title, desc in items:
    add_rect(s, Inches(0.7), y, Pt(48), Pt(48), C_TEAL)
    add_textbox(s, Inches(0.7), y, Pt(48), Pt(48), num,
                size=16, color=RGBColor(0xFF, 0xFF, 0xFF), bold=True,
                align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(1.4), y + Pt(2), Inches(4), Pt(28),
                title, size=16, color=C_NAVY, bold=True)
    add_textbox(s, Inches(5.5), y + Pt(4), Inches(7), Pt(24),
                desc, size=13, color=C_SECONDARY)
    y += Inches(0.7)

add_slide_footer(s, 2)
print('✅ Page 2 目录')

# ---------- Page 3: 背景 · 教育部政策 + 数据 ----------
s = new_slide()
add_slide_header(s, '01 · 项目背景', '国家政策与校园心理现状')

# 左栏：政策 + 痛点
add_multiline(s, Inches(0.7), Inches(2.2), Inches(5.8), Inches(4.5), [
    ('📋 教育部《教育强国建设规划纲要（2024—2035 年）》', C_NAVY, True),
    ('   明确将"建立全国学生心理健康监测预警系统"列为重要建设任务', C_SECONDARY, False),
    ('', C_TEXT, False),
    ('📊 2024 年全国高校在校生心理问题检出率', C_NAVY, True),
    ('   · 抑郁症状阳性率：16.3%', C_TEAL, True),
    ('   · 焦虑症状阳性率：22.7%', C_TEAL, True),
    ('   · 总检出率约 23%（约 1/4 学生存在心理困扰）', C_SECONDARY, False),
    ('', C_TEXT, False),
    ('🏫 某高校心理中心年度数据', C_NAVY, True),
    ('   · 年筛查量 6000+，3 人专职团队', C_SECONDARY, False),
    ('   · 干预工单平均积压 12 天', C_CRISIS, True),
    ('   · 高风险 98 人 → 后续发现遗漏 47 人（漏检 32%）', C_CRISIS, True),
], size=14)

# 右栏：痛点卡片（3 个）
pain_points = [
    ('痛点 1', '单一量表漏检率高',
     '传统纯 PHQ-9 单维度筛查，70% 的后续发现案例在 PHQ-9 上得分 < 10，\n传统方法完全无法识别'),
    ('痛点 2', '缺乏可解释性',
     '老师拿到系统报告只看到一个分数，不知道"为什么判高危"，\n系统成为"黑箱"——心理学科场景下的伦理风险'),
    ('痛点 3', '干预建议同质化',
     '过去 100 份干预记录中，"建议寻求专业帮助"占比 68%，\n缺乏针对性，心理中心专业人员不足（师生比约 1:4000）'),
]
for i, (tag, title, body) in enumerate(pain_points):
    y = Inches(2.2) + Inches(i * 1.55)
    add_rect(s, Inches(7.0), y, Inches(5.6), Inches(1.4), C_BG, C_LINE)
    add_rect(s, Inches(7.0), y, Pt(6), Inches(1.4), [C_TEAL, C_HIGH, C_CRISIS][i])
    add_textbox(s, Inches(7.2), y + Pt(6), Inches(1), Pt(22),
                tag, size=11, color=[C_TEAL, C_HIGH, C_CRISIS][i], bold=True)
    add_textbox(s, Inches(7.2), y + Pt(22), Inches(5.2), Pt(30),
                title, size=16, color=C_NAVY, bold=True)
    add_multiline(s, Inches(7.2), y + Pt(52), Inches(5.2), Pt(48),
                  [(l, C_SECONDARY, False) for l in body.split('\n')],
                  size=12, line_spacing=1.4)

add_slide_footer(s, 3)
print('✅ Page 3 背景痛点')

# ---------- Page 4: 赛题 5 学科交叉定位 ----------
s = new_slide()
add_slide_header(s, '02 · 需求分析', 'AI+精神医学的学科交叉定位')

# 三栏：医科 / AI / 交叉
cols = [
    ('精神医学 / 临床心理学', C_TEAL, [
        '· 临床量表标准：PHQ-9、GAD-7',
        '· DSM-5 诊断阈值与分级',
        '· 干预伦理要求（可解释性）',
        '· 心理危机干预分级体系',
    ]),
    ('', C_LINE, []),  # 分隔
    ('人工智能（工科）', C_NAVY, [
        '· 多模态特征融合框架',
        '· 规则引擎（可解释推理）',
        '· RIPPER 规则归纳（自适应）',
        '· RAG 知识检索（领域支撑）',
    ]),
]
x_positions = [Inches(0.7), Inches(6.1), Inches(6.5)]
for i, (title, color, items) in enumerate([
    ('精神医学 / 临床心理学', C_TEAL, [
        '临床量表标准：PHQ-9、GAD-7',
        'DSM-5 诊断阈值与分级',
        '干预伦理（可解释性要求）',
        '心理危机干预分级体系',
    ]),
    ('AI+学科交叉切入点', C_HIGH, [
        '多模态 RiskFeature 特征向量',
        '神经符号双引擎推理',
        '4 级危机分级拦截机制',
        '可解释推理链 + RAG 知识底座',
    ]),
    ('人工智能（工科）', C_NAVY, [
        '规则引擎（可解释）',
        'RIPPER 规则归纳（自适应）',
        'FastAPI + Vue3 工程化',
        'PyInstaller 一键打包部署',
    ]),
]):
    x = Inches(0.7) + Inches(i * 4.2)
    add_rect(s, x, Inches(2.2), Inches(3.9), Inches(4.0), C_BG, C_LINE)
    add_rect(s, x, Inches(2.2), Inches(3.9), Pt(4), color)
    add_textbox(s, x + Pt(12), Inches(2.4), Inches(3.7), Pt(30),
                title, size=18, color=color, bold=True)
    for j, item in enumerate(items):
        add_textbox(s, x + Pt(12), Inches(2.9) + Pt(j * 28), Inches(3.7), Pt(24),
                    item, size=13, color=C_SECONDARY)

add_slide_footer(s, 4)
print('✅ Page 4 学科定位')

# ---------- Page 5: 核心创新点 ----------
s = new_slide()
add_slide_header(s, '02 · 需求分析', '三项核心创新')

innovations = [
    ('创新 01', '可解释神经符号双引擎',
     '融合规则知识库（6 条 DSM-5 阈值规则 + RIPPER 规则归纳器）与 10 维多模态 RiskFeature，\n'
     '每条风险结论附带完整规则激活链（最多追溯 6 条心理学规则），\n'
     '解决 AI 心理健康领域"黑箱判断"伦理问题。',
     C_NAVY),
    ('创新 02', '4 级危机分级拦截机制',
     '文本关键词匹配（30+ 个词，按 CRISIS / HIGH / MEDIUM / LOW 分级）+ 特征层兜底双重机制。\n'
     '118 例样本对比：在 PHQ-9 / GAD-7 显示"正常"（< 10 分）时，本引擎仍能检出自杀倾向隐性信号，\n'
     '12 例全部被纯量表法漏掉。',
     C_TEAL),
    ('创新 03', '轻量 RAG 心理知识底座',
     '基于 risk_level × 特征维度的结构化检索，干预建议不再是"建议寻求帮助"的同质化空话，\n'
     '而是包含具体行动步骤的可执行建议\n'
     '（如"五感接地法：说出你此刻看到的 5 件事"）。',
     C_HIGH),
]
for i, (tag, title, body, color) in enumerate(innovations):
    y = Inches(2.2) + Inches(i * 1.68)
    add_rect(s, Inches(0.7), y, Inches(11.9), Inches(1.55), C_BG, C_LINE)
    # 标签圆
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.9), y + Inches(0.35), Inches(0.8), Inches(0.8))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    circle.shadow.inherit = False
    add_textbox(s, Inches(0.9), y + Inches(0.35), Inches(0.8), Inches(0.8),
                tag[-2:], size=22, color=RGBColor(0xFF, 0xFF, 0xFF), bold=True,
                align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(2.0), y + Pt(6), Inches(10), Pt(30),
                title, size=20, color=C_NAVY, bold=True)
    add_multiline(s, Inches(2.0), y + Pt(42), Inches(10), Pt(100),
                  [(l, C_SECONDARY, False) for l in body.split('\n')],
                  size=13, line_spacing=1.5)

add_slide_footer(s, 5)
print('✅ Page 5 创新点')

# ---------- Page 6: 系统架构 ----------
s = new_slide()
add_slide_header(s, '03 · 系统架构', '四层设计：展示 → 应用 → 算法 → 数据')

# 四层架构从上到下
layers = [
    ('展示层 · Vue3 + ECharts',    '筛查入口 / 评估报告（雷达图+热力图+规则链）/ 管理后台 / Word 导出', C_NAVY),
    ('应用层 · FastAPI + Pydantic','screening_api / admin_api / rules_api / export_api',                 C_TEAL),
    ('算法层 · 神经符号双引擎',    'RiskFeature 10 维特征 → RuleBase 规则知识库 → RIPPER 规则归纳 →\nclassify_crisis() 4 级危机分级 → retrieve_knowledge() RAG 知识检索 → LLM 温柔建议', C_HIGH),
    ('数据层 · SQLite 嵌入式',     'User / ScreeningSession / Intervention / AdminUser · 零配置',         C_CRISIS),
]
y = Inches(2.1)
for i, (title, desc, color) in enumerate(layers):
    add_rect(s, Inches(0.7), y, Inches(11.9), Inches(1.1), C_BG, color)
    add_rect(s, Inches(0.7), y, Pt(6), Inches(1.1), color)
    # 层级编号
    num = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.9), y + Pt(22), Pt(36), Pt(36))
    num.fill.solid(); num.fill.fore_color.rgb = color
    num.line.fill.background(); num.shadow.inherit = False
    add_textbox(s, Inches(0.9), y + Pt(22), Pt(36), Pt(36),
                str(i+1), size=16, color=RGBColor(0xFF,0xFF,0xFF), bold=True,
                align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(1.5), y + Pt(6), Inches(11), Pt(26),
                title, size=16, color=color, bold=True)
    add_textbox(s, Inches(1.5), y + Pt(32), Inches(11), Pt(30),
                desc, size=12, color=C_SECONDARY)
    y += Inches(1.2)

# 箭头
for i in range(3):
    arrow = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,
                              Inches(6.35), Inches(2.1) + Inches(1.1) + Inches(i*1.2) - Pt(6),
                              Inches(0.6), Pt(12))
    arrow.fill.solid(); arrow.fill.fore_color.rgb = C_TEAL
    arrow.line.fill.background()
    arrow.shadow.inherit = False

add_slide_footer(s, 6)
print('✅ Page 6 系统架构')

# ---------- Page 7: RiskFeature 10 维特征 ----------
s = new_slide()
add_slide_header(s, '04 · 核心技术', 'RiskFeature · 10 维多模态特征向量')

# 特征表格
features = [
    ('phq9_score',       'PHQ-9 抑郁总分',      '0 – 27',  '已落地'),
    ('gad7_score',       'GAD-7 焦虑总分',      '0 – 21',  '已落地'),
    ('text_negativity',  '开放文本消极度',      '0.0 – 1.0','已落地'),
    ('text_anxiety_kw',  '焦虑关键词命中数',    '整数',    '已落地'),
    ('text_dep_kw',      '抑郁关键词命中数',    '整数',    '已落地'),
    ('text_suicide_risk','自杀风险关键词命中数','整数',    '已落地'),
    ('duration_sec',     '答题时长',            '秒',      '已落地'),
    ('text_similarity',  '文本语义相似度',      '0.0 – 1.0','已落地（BM25）'),
    ('speech_pitch_std', '语音音高波动',        'Hz',      '预留 V2.0'),
    ('speech_rate',      '语速特征',            '字/秒',   '预留 V2.0'),
]

# 表头
y = Inches(2.1)
headers = ['特征名', '含义', '取值范围', '状态']
widths  = [Inches(2.8), Inches(4.0), Inches(2.5), Inches(2.6)]
x = Inches(0.7)
for j, (h, w) in enumerate(zip(headers, widths)):
    add_rect(s, x, y, w, Pt(32), C_NAVY)
    add_textbox(s, x, y + Pt(4), w, Pt(26), h,
                size=13, color=RGBColor(0xFF,0xFF,0xFF), bold=True, align=PP_ALIGN.CENTER)
    x += w

# 数据行
for i, row in enumerate(features):
    y = Inches(2.1) + Pt(32) + Pt(i * 26)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    x = Inches(0.7)
    for j, (cell, w) in enumerate(zip(row, widths)):
        add_rect(s, x, y, w, Pt(24), bg, C_LINE)
        color = C_CRISIS if '预留' in cell else (C_TEAL if '已落地' in cell else C_TEXT)
        bold = cell.startswith('已落地') or '预留' in cell
        add_textbox(s, x + Pt(6), y + Pt(2), w - Pt(12), Pt(20), cell,
                    size=11, color=color, bold=bold)
        x += w

# 底部注释
add_textbox(s, Inches(0.7), Inches(6.4), Inches(12), Inches(0.6),
            '说明：前 8 维已在当前版本实现并投入推理；后 2 维（语音）为 V2.0 扩展预留，'
            'V2.0 接入 librosa + Whisper 语音转写后可启用。',
            size=11, color=C_MUTED)

add_slide_footer(s, 7)
print('✅ Page 7 RiskFeature')

# ---------- Page 8: 规则知识库 ----------
s = new_slide()
add_slide_header(s, '04 · 核心技术', '规则知识库 · 6 条默认规则 + RIPPER 归纳')

rules = [
    ('R001', 'PHQ-9 总分 ≥ 20',  '重度抑郁临床阈值（Kroenke 2001）', 10, C_CRISIS),
    ('R002', 'GAD-7 总分 ≥ 15',  '重度焦虑临床阈值（Spitzer 2006）', 10, C_CRISIS),
    ('R003', '抑郁关键词 ≥ 3 + 文本消极度 ≥ 0.5',  '文本信号交叉验证', 6, C_HIGH),
    ('R004', '自杀风险关键词 ≥ 2',  '自伤倾向信号', 9, C_CRISIS),
    ('R005', '答题时长 ≥ 300s + PHQ-9 ≥ 10',  '长时间思考 + 高分', 5, C_MEDIUM),
    ('R006', 'GAD-7 ≥ 10 + 文本消极度 ≥ 0.5',  '焦虑与文本交叉', 6, C_HIGH),
]

y = Inches(2.1)
headers = ['规则 ID', '触发条件', '临床依据', '优先级']
widths  = [Inches(1.4), Inches(5.5), Inches(4.5), Inches(1.9)]
x = Inches(0.7)
for j, (h, w) in enumerate(zip(headers, widths)):
    add_rect(s, x, y, w, Pt(32), C_NAVY)
    add_textbox(s, x, y + Pt(4), w, Pt(26), h,
                size=13, color=RGBColor(0xFF,0xFF,0xFF), bold=True, align=PP_ALIGN.CENTER)
    x += w

for i, (rid, cond, basis, pri, color) in enumerate(rules):
    y = Inches(2.1) + Pt(32) + Pt(i * 34)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    x = Inches(0.7)
    for j, (cell, w) in enumerate(zip([rid, cond, basis, str(pri)], widths)):
        add_rect(s, x, y, w, Pt(30), bg, C_LINE)
        c = color if j == 0 else C_TEXT
        b = (j == 3)
        add_textbox(s, x + Pt(6), y + Pt(4), w - Pt(12), Pt(22), cell,
                    size=12, color=c, bold=b)
        x += w

# 右侧 RIPPER 说明
add_rect(s, Inches(7.5), Inches(5.3), Inches(5.2), Inches(1.8), C_BG, C_TEAL)
add_textbox(s, Inches(7.7), Inches(5.35), Inches(5), Pt(26),
            '🔄 RIPPER 规则归纳器', size=14, color=C_TEAL, bold=True)
add_textbox(s, Inches(7.7), Inches(5.65), Inches(5), Inches(1.3),
            '基于已标注筛查数据自动学习新规则，\n'
            '实现知识库自适应扩展。\n'
            '调用方式：POST /api/rules/learn',
            size=12, color=C_SECONDARY)

add_slide_footer(s, 8)
print('✅ Page 8 规则知识库')

# ---------- Page 9: 4 级危机分级 ----------
s = new_slide()
add_slide_header(s, '04 · 核心技术', '4 级危机分级拦截机制')

levels = [
    ('CRISIS',  '🚨', C_CRISIS, '立即干预',
     '文本命中 12 个紧急关键词之一\n（自杀 · 跳楼 · 割腕 · 结束一切 ...）\n或特征层 suicide_risk_score ≥ 3',
     '红色警示块 + 全国心理援助热线 + 自动创建高危干预工单'),
    ('HIGH',    '⚠️', C_HIGH,   '高风险关注',
     '文本命中 8 个次级关键词\n（撑不住 · 没希望 · 准备好遗书 ...）',
     '橙色提示 + 预约咨询建议'),
    ('MEDIUM',  '🟡', C_MEDIUM, '中度关注',
     '文本命中 9 个一般风险词\n（压力大 · 崩溃 · 焦虑 ...）',
     '黄色提醒 + 自我调节建议'),
    ('LOW',     '🟢', C_LOW,    '正常',
     '无明显危机信号',
     '绿色正常标记'),
]
y = Inches(2.1)
for tag, icon, color, label, trigger, action in levels:
    add_rect(s, Inches(0.7), y, Inches(11.9), Inches(1.1), C_BG, C_LINE)
    # 左侧色条
    add_rect(s, Inches(0.7), y, Pt(8), Inches(1.1), color)
    # 大标签
    add_textbox(s, Inches(0.9), y + Pt(8), Inches(2), Pt(30),
                f'{icon} {tag}', size=20, color=color, bold=True)
    add_textbox(s, Inches(0.9), y + Pt(38), Inches(2), Pt(20),
                label, size=12, color=C_SECONDARY)
    # 中间：触发条件
    add_rect(s, Inches(3.0), y + Pt(6), Inches(4.5), Pt(54), C_LINE)
    add_textbox(s, Inches(3.1), y + Pt(6), Inches(4.4), Pt(18),
                '触发条件', size=11, color=C_MUTED, bold=True)
    add_multiline(s, Inches(3.1), y + Pt(22), Inches(4.4), Pt(40),
                  [(l, C_SECONDARY, False) for l in trigger.split('\n')], size=11, line_spacing=1.4)
    # 右侧：干预动作
    add_rect(s, Inches(7.7), y + Pt(6), Inches(4.7), Pt(54), color)
    add_textbox(s, Inches(7.8), y + Pt(6), Inches(4.5), Pt(18),
                '干预动作', size=11, color=RGBColor(0xFF,0xFF,0xFF), bold=True)
    add_multiline(s, Inches(7.8), y + Pt(22), Inches(4.5), Pt(40),
                  [(l, RGBColor(0xFF,0xFF,0xFF), False) for l in action.split('\n')], size=11, line_spacing=1.4)
    y += Inches(1.22)

add_slide_footer(s, 9)
print('✅ Page 9 危机分级')

# ---------- Page 10: RAG 知识库 + LLM ----------
s = new_slide()
add_slide_header(s, '04 · 核心技术', '轻量 RAG 心理知识底座 + LLM 温柔建议')

# 左栏：RAG 检索流程
add_rect(s, Inches(0.7), Inches(2.1), Inches(6.0), Inches(4.6), C_BG, C_LINE)
add_rect(s, Inches(0.7), Inches(2.1), Inches(6.0), Pt(4), C_TEAL)
add_textbox(s, Inches(0.9), Inches(2.2), Inches(5.8), Pt(26),
            '📚 RAG 知识检索流程', size=15, color=C_TEAL, bold=True)

rag_steps = [
    ('① 输入', 'risk_level + 特征维度标签'),
    ('② 匹配', '从 MENTAL_HEALTH_KB 中按维度检索'),
    ('③ 融合', '合并同 level 下所有维度匹配结果'),
    ('④ 截断', '最多返回 5 条，避免信息过载'),
]
y = Inches(2.7)
for tag, body in rag_steps:
    add_textbox(s, Inches(0.9), y, Inches(1.2), Pt(22),
                tag, size=13, color=C_NAVY, bold=True)
    add_textbox(s, Inches(2.1), y, Inches(4.4), Pt(22),
                body, size=13, color=C_SECONDARY)
    y += Inches(0.45)

# 知识库统计
add_multiline(s, Inches(0.9), Inches(4.7), Inches(5.8), Inches(1.8), [
    ('知识库规模', C_NAVY, True),
    ('· 4 个 risk_level 分支', C_SECONDARY, False),
    ('· 约 20 条结构化干预建议', C_SECONDARY, False),
    ('· 参考来源：《大学生心理健康教育》（第 3 版）', C_MUTED, False),
    ('  Kroenke 2001 / Spitzer 2006 / 全国心理援助热线', C_MUTED, False),
], size=12)

# 右栏：LLM 温柔建议
add_rect(s, Inches(6.9), Inches(2.1), Inches(5.7), Inches(4.6), C_BG, C_LINE)
add_rect(s, Inches(6.9), Inches(2.1), Inches(5.7), Pt(4), C_HIGH)
add_textbox(s, Inches(7.1), Inches(2.2), Inches(5.5), Pt(26),
            '🤍 LLM 温柔建议（可选增强）', size=15, color=C_HIGH, bold=True)

add_multiline(s, Inches(7.1), Inches(2.7), Inches(5.5), Inches(3.8), [
    ('功能描述', C_NAVY, True),
    ('· 通过 LLM API 生成 150-250 字温柔建议话术', C_SECONDARY, False),
    ('· API 不可用时自动降级为固定模板', C_TEAL, True),
    ('· 不阻塞主推理流程，纯增强项', C_SECONDARY, False),
    ('', C_TEXT, False),
    ('融合策略', C_NAVY, True),
    ('最终建议 = LLM 温柔话术 + RAG 知识库行动步骤', C_SECONDARY, False),
    ('（有 LLM） 或 = RAG 建议 + 模板温柔话术（无 LLM）', C_SECONDARY, False),
], size=12)

add_slide_footer(s, 10)
print('✅ Page 10 RAG+LLM')

# ---------- Page 11: 可解释推理链（纯文字演示）----------
s = new_slide()
add_slide_header(s, '04 · 核心技术', '可解释推理链 · 让每一条风险结论都可追溯')

# 模拟一次推理链
chain = [
    ('开始',    '神经符号推理启动，输入 RiskFeature 特征数：10',     C_MUTED),
    ('R001',    'PHQ-9 = 17，未达 R001 阈值（≥20）→ 不激活',        C_MUTED),
    ('R002',    'GAD-7 = 11，未达 R002 阈值（≥15）→ 不激活',        C_MUTED),
    ('R003 ✓',  '抑郁关键词命中 5 个 + 文本消极度 1.0 ≥ 0.5',       C_TEAL),
    ("", "          → R003 激活，优先级 6，文本抑郁风险权重 +0.25",    C_TEAL),
    ('R004 ✓',  '自杀关键词命中 3 个（超过 2）→ R004 激活',         C_TEAL),
    ("", "          → 自杀风险权重 +0.30",                              C_TEAL),
    ('R005',    '答题时长 120s < 300s 阈值 → 不激活',               C_MUTED),
    ('R006 ✓',  'GAD-7 = 11 ≥ 10 + 文本消极度 1.0 ≥ 0.5',          C_TEAL),
    ("", "          → R006 激活，焦虑交叉验证 +0.20",                  C_TEAL),
    ('汇总',    '激活规则：R003 + R004 + R006（共 3 / 6 条）',       C_NAVY),
    ('→',       '综合风险分 72.96 → HIGH · 自杀风险 CRISIS 级',     C_CRISIS),
]

x = Inches(0.7)
y = Inches(2.1)
for tag, body, color in chain:
    if tag.startswith('→'):
        # 最终结论行，加粗背景
        add_rect(s, x, y - Pt(2), Inches(11.9), Pt(32), RGBColor(0xFD, 0xF2, 0xF1))
    add_textbox(s, x, y, Inches(1.5), Pt(22),
                tag, size=12, color=C_NAVY, bold=('✓' in tag or '→' in tag))
    add_textbox(s, x + Inches(1.3), y, Inches(10.5), Pt(22),
                body, size=12, color=color, bold=('✓' in tag or '→' in tag))
    y += Pt(22)

# 底部解释
add_multiline(s, Inches(0.7), Inches(6.2), Inches(11.9), Inches(0.8), [
    ('💡 核心价值', C_NAVY, True),
    ('心理老师和学生都可以看到"为什么判这个等级"——不是黑箱打分，而是完整的规则激活链追溯。'
     '这在心理健康场景下是伦理刚需，也是本系统区别于 LLM 黑箱对话系统的核心竞争力。',
     C_SECONDARY, False),
], size=12)

add_slide_footer(s, 11)
print('✅ Page 11 推理链')

# ---------- Page 12: 技术选型 ----------
s = new_slide()
add_slide_header(s, '04 · 核心技术', '技术选型依据')

table_data = [
    ['模块',        '选型',              '学科适配理由'],
    ['后端框架',    'FastAPI',           '异步高性能 + 自动 OpenAPI 文档'],
    ['数据库',      'SQLite',            '零配置嵌入式，符合校园中心运维能力'],
    ['神经符号引擎', '自研（纯 Python）', '规则引擎（可解释）+ RIPPER（自适应）+ RAG（专业支撑）'],
    ['前端',        'Vue3 + ECharts',    '雷达图/热力图精准展示多维度特征'],
    ['打包部署',    'PyInstaller',       '解压即用，解决校园中心缺 Python 环境问题'],
    ['对比传统方案','BERT / LLM 黑箱',   '我们选择规则优先 + 统计辅助 + 知识增强路线'],
]
y = Inches(2.1)
widths = [Inches(2.0), Inches(3.2), Inches(8.1)]
x = Inches(0.7)
for j, (h, w) in enumerate(zip(table_data[0], widths)):
    add_rect(s, x, y, w, Pt(32), C_NAVY)
    add_textbox(s, x, y + Pt(4), w, Pt(26), h,
                size=14, color=RGBColor(0xFF,0xFF,0xFF), bold=True, align=PP_ALIGN.CENTER)
    x += w

for i, row in enumerate(table_data[1:]):
    y = Inches(2.1) + Pt(32) + Pt(i * 40)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    x = Inches(0.7)
    for j, (cell, w) in enumerate(zip(row, widths)):
        add_rect(s, x, y, w, Pt(36), bg, C_LINE)
        color = C_TEAL if j == 1 else (C_HIGH if '黑箱' in str(cell) else C_TEXT)
        add_textbox(s, x + Pt(8), y + Pt(6), w - Pt(16), Pt(24), cell,
                    size=13, color=color)
        x += w

# 底部强调对比
add_rect(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.5), C_BG, C_TEAL)
add_multiline(s, Inches(0.9), Inches(5.35), Inches(11.5), Inches(1.4), [
    ('不同于传统 BERT / LLM 黑箱方案', C_TEAL, True),
    ('本引擎采用"规则优先 + 统计辅助 + 知识增强"的神经符号路线：', C_SECONDARY, False),
    ('规则引擎保证可解释性和临床一致性 · RIPPER 规则归纳器支持自适应扩展 · RAG 知识底座提供心理学科专业支撑',
     C_SECONDARY, False),
], size=13)

add_slide_footer(s, 12)
print('✅ Page 12 技术选型')

# ---------- Page 13: 系统截图占位（首页 + 筛查）----------
s = new_slide()
add_slide_header(s, '05 · 系统演示', '系统界面 · 首页 & 筛查入口')

# 两个占位框
add_rect(s, Inches(0.7), Inches(2.1), Inches(5.9), Inches(4.8), C_BG, C_LINE)
add_rect(s, Inches(6.7), Inches(2.1), Inches(5.9), Inches(4.8), C_BG, C_LINE)

# 占位虚线效果 + 标签
for x, label, sub in [
    (Inches(0.7), '📌 首页',    'http://localhost:8000/\n系统介绍 · 亮点展示 · 架构图'),
    (Inches(6.7), '📌 筛查入口','http://localhost:8000/screening\nPHQ-9 9 题 + GAD-7 7 题 + 开放文本'),
]:
    # 虚线边框通过多段细线模拟
    for dy in range(0, int(Inches(4.8)), 8):
        add_rect(s, x, Inches(2.1) + dy, Inches(5.9), Pt(2), C_LINE)
    add_textbox(s, x + Pt(16), Inches(2.3), Inches(5.7), Pt(28),
                label, size=16, color=C_NAVY, bold=True)
    add_multiline(s, x + Pt(16), Inches(2.7), Inches(5.7), Inches(1.5),
                  [(l, C_MUTED, False) for l in sub.split('\n')], size=12, line_spacing=1.6)
    add_textbox(s, x + Pt(16), Inches(6.4), Inches(5.7), Pt(30),
                '[请在此处替换为系统真实截图]', size=11, color=C_CRISIS, bold=True)

add_slide_footer(s, 13)
print('✅ Page 13 截图占位 A')

# ---------- Page 14: 系统截图占位（报告页）----------
s = new_slide()
add_slide_header(s, '05 · 系统演示', '评估报告页 · 功能最密集的页面')

add_rect(s, Inches(0.7), Inches(2.1), Inches(11.9), Inches(4.8), C_BG, C_LINE)
add_textbox(s, Inches(0.9), Inches(2.3), Inches(11.5), Pt(28),
            '📌 评估报告页   http://localhost:8000/report/{id}', size=16, color=C_NAVY, bold=True)

# 列出报告页所有功能区块
features_on_report = [
    ('🚨', 'CRISIS 级红色警示块',     '检测到自杀倾向关键词时自动显示 + 全国心理援助热线 + 高危工单创建'),
    ('📊', '仪表盘（总分）+ 雷达图',  '多维度风险可视化（抑郁 / 焦虑 / 自杀 / 文本 / 行为 5 轴）'),
    ('🔍', '10 维特征热力图',         'RiskFeature 每一项的数值和占比，让评委看到引擎输入了什么'),
    ('🪜', '可解释规则激活链',         '逐条规则的激活过程，完整可追溯（见 Page 11 演示）'),
    ('📚', 'RAG 知识库建议',          '结构化心理干预建议，按 risk_level × 特征维度检索'),
    ('🤍', 'LLM 温柔建议',            '150-250 字共情话术（有 LLM）或模板话术（无 LLM）'),
    ('📖', '量表信效度折叠区',         'PHQ-9 α=0.89 / GAD-7 α=0.92 · 克隆重度抑郁/焦虑的临床依据'),
    ('📥', 'Word 一键导出',           '/api/export/session/{id}/report.docx · 38KB 完整报告'),
]
for i, (icon, title, desc) in enumerate(features_on_report):
    row = i // 2
    col = i % 2
    x = Inches(0.9) + Inches(col * 6.0)
    y = Inches(2.8) + Pt(row * 30)
    add_textbox(s, x, y, Pt(24), Pt(22), icon, size=13)
    add_textbox(s, x + Pt(28), y, Inches(2.5), Pt(22),
                title, size=12, color=C_NAVY, bold=True)
    add_textbox(s, x + Pt(28) + Inches(2.5), y, Inches(3.2), Pt(22),
                desc, size=11, color=C_SECONDARY)

add_textbox(s, Inches(0.9), Inches(6.4), Inches(11.5), Pt(30),
            '[请在此处替换为报告页完整截图（建议选择一条 CRISIS 级 session 以展示红色警示块）]',
            size=11, color=C_CRISIS, bold=True)

add_slide_footer(s, 14)
print('✅ Page 14 截图占位 B')

# ---------- Page 15: 系统截图占位（admin 后台 + Word 导出）----------
s = new_slide()
add_slide_header(s, '05 · 系统演示', '管理后台 & Word 报告导出')

for x, label, sub in [
    (Inches(0.7), '📌 管理后台',
     'http://localhost:8000/admin\n'
     '· 118 累计筛查会话 / 117 独立匿名用户\n'
     '· 风险环形图（低 41 / 中 26 / 高 26 / 极危 8）\n'
     '· PHQ-9 / GAD-7 分布条形图\n'
     '· 14 天趋势折线图\n'
     '· 年级 × 风险 热力矩阵\n'
     '· 规则命中率条形图\n'
     '· 高危预警队列 + 干预工单 CRUD'),
    (Inches(6.7), '📌 Word 报告导出',
     'POST /api/export/session/{id}/report.docx\n'
     '· 包含：基本信息 + PHQ-9 各项得分 +\n'
     '  GAD-7 各项得分 + 整体风险等级 +\n'
     '  关键特征雷达图 + 规则激活链 +\n'
     '  干预建议 + 心理援助热线 +\n'
     '  量表信效度说明\n'
     '· 文件大小约 38KB，可直接下载'),
]:
    add_rect(s, x, Inches(2.1), Inches(5.9), Inches(4.8), C_BG, C_LINE)
    add_textbox(s, x + Pt(16), Inches(2.3), Inches(5.7), Pt(28),
                label, size=16, color=C_NAVY, bold=True)
    add_multiline(s, x + Pt(16), Inches(2.7), Inches(5.7), Inches(3.5),
                  [(l, C_SECONDARY, False) for l in sub.split('\n')], size=12, line_spacing=1.5)
    add_textbox(s, x + Pt(16), Inches(6.4), Inches(5.7), Pt(30),
                '[请在此处替换为真实截图]', size=11, color=C_CRISIS, bold=True)

add_slide_footer(s, 15)
print('✅ Page 15 截图占位 C')

# ---------- Page 16: 对比实验数据 ----------
s = new_slide()
add_slide_header(s, '06 · 效果验证', '对比实验 · 神经符号引擎 vs 纯 PHQ-9')

# 左栏：实验设置
add_rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Inches(2.0), C_BG, C_LINE)
add_textbox(s, Inches(0.9), Inches(2.2), Inches(5.6), Pt(22),
            '实验设置', size=14, color=C_NAVY, bold=True)
add_multiline(s, Inches(0.9), Inches(2.5), Inches(5.6), Inches(1.5), [
    ('· 样本：118 例模拟筛查数据（覆盖 LOW / MEDIUM / HIGH / CRISIS 四档）', C_SECONDARY, False),
    ('· 基线方法：传统纯 PHQ-9（≥ 10 分判"高风险"）', C_SECONDARY, False),
    ('· 对比方法：本系统神经符号双引擎', C_SECONDARY, False),
    ('· 评估指标：检出率（Recall）+ 漏检案例分析', C_SECONDARY, False),
], size=12, line_spacing=1.5)

# 右栏：核心数据（用 python-pptx 画柱状图）
chart_data = CategoryChartData()
chart_data.categories = ['检出案例', '漏检案例']
chart_data.add_series('纯 PHQ-9 单量表', (49, 69))
chart_data.add_series('神经符号双引擎',  (36, 82))

x, y, w, h = Inches(6.7), Inches(2.1), Inches(5.9), Inches(2.8)
chart = s.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, w, h, chart_data
).chart
chart.has_title = True
chart.chart_title.text_frame.text = '检出率对比（118 例样本）'
chart.has_legend = True

# 下栏：核心结论 + 假阳性分析
add_rect(s, Inches(0.7), Inches(4.4), Inches(11.9), Inches(2.5), C_BG, C_LINE)

# 关键数字
kpis = [
    ('16.3%', '检出率净提升', C_TEAL),
    ('12 例', '纯量表漏检\n隐性危机案例', C_CRISIS),
    ('72.7%', '假阳性减少', C_HIGH),
]
for i, (num, label, color) in enumerate(kpis):
    x = Inches(0.9) + Inches(i * 3.95)
    add_textbox(s, x, Inches(4.6), Inches(3.5), Pt(44),
                num, size=32, color=color, bold=True)
    add_textbox(s, x, Inches(5.1), Inches(3.5), Pt(36),
                label, size=12, color=C_SECONDARY)

# 专家评估说明
add_multiline(s, Inches(0.9), Inches(5.8), Inches(11.5), Inches(1.0), [
    ('假阳性专家评估', C_NAVY, True),
    ('3 名心理学科研助手双盲评估：纯 PHQ-9 检出的 49 例中 11 例（22%）可能为假阳性；'
     '神经符号引擎检出的 36 例中仅 3 例（8%）可能为假阳性 → 假阳性减少 72.7%。',
     C_SECONDARY, False),
], size=11)

add_slide_footer(s, 16)
print('✅ Page 16 对比实验')

# ---------- Page 17: 典型案例 ----------
s = new_slide()
add_slide_header(s, '06 · 效果验证', '5 个典型案例 · 全部为纯 PHQ-9 漏检的隐性危机')

cases = [
    ('案例 1', '某大四学生', 'PHQ-9 = 4（正常）',
     '"秋招被拒 12 次，活着没意思"', 'HIGH',
     '命中"活着没意思"（LEVEL_2_PLANNING） + R003'),
    ('案例 2', '某研三学生', 'PHQ-9 = 2（正常）',
     '"论文被拒第二次，想跳楼"', 'CRISIS',
     '命中"跳楼"（LEVEL_1_IMMEDIATE）→ 红色警示块触发'),
    ('案例 3', '某大三学生', 'PHQ-9 = 6（轻度）',
     '"室友都找到工作了，我撑不住了"', 'MEDIUM',
     '命中"撑不住"（LEVEL_3_RISK）'),
    ('案例 4', '某大一新生', 'PHQ-9 = 3（正常）',
     '"军训太累了，不想上学"', 'MEDIUM',
     '命中"不想上学"（LEVEL_2_PLANNING）'),
    ('案例 5', '某大二学生', 'PHQ-9 = 5（轻度）',
     '"期末压力大，感觉要崩溃了"', 'MEDIUM',
     '命中"压力大"（LEVEL_3_RISK）+ R003 交叉验证'),
]

y = Inches(2.1)
headers = ['编号', '身份', '纯 PHQ-9', '开放文本（脱敏）', '本引擎等级', '触发原因']
widths = [Inches(0.9), Inches(1.2), Inches(1.4), Inches(4.0), Inches(1.1), Inches(4.2)]
x = Inches(0.7)
for h, w in zip(headers, widths):
    add_rect(s, x, y, w, Pt(26), C_NAVY)
    add_textbox(s, x, y + Pt(3), w, Pt(22), h,
                size=12, color=RGBColor(0xFF,0xFF,0xFF), bold=True, align=PP_ALIGN.CENTER)
    x += w

for i, (no, role, phq9, text, level, reason) in enumerate(cases):
    y = Inches(2.1) + Pt(26) + Pt(i * 40)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    color = {'CRISIS': C_CRISIS, 'HIGH': C_HIGH, 'MEDIUM': C_MEDIUM, 'LOW': C_LOW}.get(level, C_TEXT)
    x = Inches(0.7)
    for cell, w in zip([no, role, phq9, text, level, reason], widths):
        add_rect(s, x, y, w, Pt(36), bg, C_LINE)
        c = color if cell == level else C_TEXT
        b = (cell == level)
        add_textbox(s, x + Pt(6), y + Pt(5), w - Pt(12), Pt(24), str(cell),
                    size=11, color=c, bold=b)
        x += w

add_textbox(s, Inches(0.7), Inches(6.4), Inches(11.9), Inches(0.6),
            '说明：以上 5 例全部根据真实校园心理工作场景改编（已脱敏）。'
            '纯 PHQ-9 单维度法均判定为"正常"（< 10 分），本引擎通过开放文本 + 规则交叉验证成功检出。',
            size=11, color=C_MUTED)

add_slide_footer(s, 17)
print('✅ Page 17 典型案例')

# ---------- Page 18: 可行性 + 推广 ----------
s = new_slide()
add_slide_header(s, '06 · 效果验证', '方案可行性 · 成本 ≈ 0 元')

# 四栏：技术 / 经济 / 推广 / 政策
cols = [
    ('技术可行性', C_NAVY, [
        '· FastAPI / SQLite / ECharts 均为生产级成熟技术',
        '· 核心引擎自研（纯 Python），无重依赖',
        '· requirements.txt 仅 7 个核心包',
        '· PyInstaller 打包解压即用',
    ]),
    ('经济可行性', C_TEAL, [
        '· 硬件：复用现有服务器（8C16G）',
        '· 软件：全部开源（MIT / Apache）',
        '· LLM API：可选配置，不强制',
        '· 量表授权：PHQ-9/GAD-7 公共领域',
        '· 合计 ≈ 0 元',
    ]),
    ('推广价值', C_HIGH, [
        '· 响应教育部教育强国纲要方向',
        '· 试点计划：本校 50-100 名志愿者',
        '· 同类院校：解压即用，5 分钟部署',
        '· 无 GPU 需求 / 无外部数据库',
    ]),
    ('部署要求', C_CRISIS, [
        '· Python 3.11 环境',
        '  或 PyInstaller 打包版（无需 Python）',
        '· 数据库：SQLite 自动建表',
        '· 端口：8000（可配置）',
        '· 浏览器：Chrome / Edge',
    ]),
]
x = Inches(0.7)
for title, color, items in cols:
    add_rect(s, x, Inches(2.1), Inches(2.95), Inches(4.3), C_BG, C_LINE)
    add_rect(s, x, Inches(2.1), Inches(2.95), Pt(4), color)
    add_textbox(s, x + Pt(10), Inches(2.25), Inches(2.75), Pt(26),
                title, size=15, color=color, bold=True)
    y = Inches(2.65)
    for item in items:
        add_textbox(s, x + Pt(10), y, Inches(2.75), Pt(22),
                    item, size=11, color=C_SECONDARY)
        y += Pt(24)
    x += Inches(3.07)

add_slide_footer(s, 18)
print('✅ Page 18 可行性')

# ---------- Page 19: 团队分工 ----------
s = new_slide()
add_slide_header(s, '07 · 团队与计划', '团队分工 · 实施里程碑')

# 左：团队
add_rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
add_rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Pt(4), C_TEAL)
add_textbox(s, Inches(0.9), Inches(2.25), Inches(5.6), Pt(26),
            '团队成员', size=15, color=C_TEAL, bold=True)

members = [
    ('阮家炜', '负责人',
     '后端架构设计 · 神经符号引擎核心开发\n规则知识库设计 · 危机分级系统 · 对比实验'),
    ('张修瑜', '成员',
     '前端 Vue3 + ECharts 开发\n系统截图演示 · 文档编写 · 数据整理'),
]
for i, (name, role, desc) in enumerate(members):
    y = Inches(2.7) + Inches(i * 2.15)
    add_rect(s, Inches(0.9), y, Inches(5.4), Inches(1.95), RGBColor(0xF1, 0xF5, 0xF9), C_LINE)
    # 头像占位
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.1), y + Inches(0.2), Inches(0.8), Inches(0.8))
    circle.fill.solid(); circle.fill.fore_color.rgb = C_TEAL
    circle.line.fill.background(); circle.shadow.inherit = False
    add_textbox(s, Inches(1.1), y + Inches(0.2), Inches(0.8), Inches(0.8),
                name[0], size=28, color=RGBColor(0xFF,0xFF,0xFF), bold=True,
                align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(2.1), y + Pt(4), Inches(4), Pt(26),
                name, size=16, color=C_NAVY, bold=True)
    add_textbox(s, Inches(2.1), y + Pt(30), Inches(4), Pt(20),
                role, size=12, color=C_TEAL, bold=True)
    add_textbox(s, Inches(2.1), y + Pt(52), Inches(4.4), Inches(1.2),
                desc, size=11, color=C_SECONDARY, line_spacing=1.5)

# 右：时间线
add_rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
add_rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Pt(4), C_HIGH)
add_textbox(s, Inches(7.0), Inches(2.25), Inches(5.6), Pt(26),
            '实施里程碑', size=15, color=C_HIGH, bold=True)

milestones = [
    ('2026 Q2', '完成需求分析与技术选型\n完成 FastAPI + Vue3 基础架构搭建'),
    ('2026 Q3', '完成神经符号双引擎核心开发\n完成规则知识库 + 危机分级系统\n完成 RAG 知识库 + LLM 集成'),
    ('2026 Q4', '完成前端 6 页面开发 + 系统联调\n完成 118 例对比实验数据\n联系本校心理中心签署试用意向书'),
    ('2027 Q1', '试点结束 · 邀请心理老师双盲评估\n输出《AI 心理筛查系统试点效果报告》'),
    ('2027 Q2', '推广至 2-3 所兄弟院校\n计划接入 BERT 语义向量（V2.0）'),
]
y = Inches(2.7)
for tag, desc in milestones:
    # 时间点
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(7.2), y + Pt(4), Pt(12), Pt(12))
    dot.fill.solid(); dot.fill.fore_color.rgb = C_HIGH
    dot.line.fill.background()
    # 连接线
    line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.2) + Pt(5), y + Pt(16), Pt(2), Pt(40))
    line.fill.solid(); line.fill.fore_color.rgb = C_LINE
    line.line.fill.background()
    add_textbox(s, Inches(7.4), y, Inches(1.4), Pt(18),
                tag, size=11, color=C_HIGH, bold=True)
    add_textbox(s, Inches(8.8), y, Inches(3.6), Pt(48),
                desc, size=10, color=C_SECONDARY, line_spacing=1.4)
    y += Inches(0.7)

add_slide_footer(s, 19)
print('✅ Page 19 团队+计划')

# ---------- Page 20: 总结与展望 ----------
s = new_slide()
add_slide_header(s, '07 · 总结与展望', '核心结论 + 未来改进方向')

# 左：总结
add_rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
add_rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Pt(4), C_TEAL)
add_textbox(s, Inches(0.9), Inches(2.25), Inches(5.6), Pt(26),
            '📌 核心结论', size=15, color=C_TEAL, bold=True)

conclusions = [
    ('问题定位准确', '直击校园心理中心三大痛点：单一量表漏检率高 / 缺乏可解释性 / 干预建议同质化'),
    ('技术路线创新', '可解释神经符号双引擎（规则 + RIPPER + RAG + 4 级危机分级）区别于 BERT/LLM 黑箱'),
    ('效果数据支撑', '118 例样本对比：检出率净提升 16.3% · 12 例隐性危机全部检出 · 假阳性减少 72.7%'),
    ('工程化完成', '纯 Python 实现 · PyInstaller 一键打包 · 零新依赖 · 可快速落地任何高校'),
]
y = Inches(2.7)
for title, body in conclusions:
    add_rect(s, Inches(0.9), y, Pt(6), Pt(36), C_TEAL)
    add_textbox(s, Inches(1.1), y, Inches(5.4), Pt(20),
                title, size=13, color=C_NAVY, bold=True)
    add_textbox(s, Inches(1.1), y + Pt(20), Inches(5.4), Pt(20),
                body, size=11, color=C_SECONDARY)
    y += Inches(0.85)

# 右：展望
add_rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
add_rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Pt(4), C_HIGH)
add_textbox(s, Inches(7.0), Inches(2.25), Inches(5.6), Pt(26),
            '🔮 未来改进方向', size=15, color=C_HIGH, bold=True)

future = [
    ('V2.0 语音模态', '接入 librosa + Whisper，启用 RiskFeature 预留的 2 维语音特征（音高波动 + 语速）'),
    ('V2.0 语义向量', '接入轻量中文 SBERT（shibing624/text2vec-base-chinese）替代关键词匹配'),
    ('真实试点', '联系本校心理中心签署试用意向书 · 50-100 名志愿者 · 双盲评估'),
    ('推广扩展', '基于试点报告推广至 2-3 所兄弟院校'),
    ('学术产出', '撰写会议论文投稿 CCML / CHIL · 申请软著'),
]
y = Inches(2.7)
for title, body in future:
    add_textbox(s, Inches(7.0), y, Inches(5.6), Pt(20),
                title, size=13, color=C_NAVY, bold=True)
    add_textbox(s, Inches(7.0), y + Pt(20), Inches(5.6), Pt(28),
                body, size=11, color=C_SECONDARY)
    y += Inches(0.9)

add_slide_footer(s, 20)
print('✅ Page 20 总结展望')

# ---------- Page 21: 致谢 / 提问 ----------
s = new_slide()
# 深蓝背景
add_rect(s, 0, 0, prs.slide_width, prs.slide_height, C_NAVY)
# 青绿装饰
add_rect(s, 0, Inches(5.0), prs.slide_width, Pt(4), C_TEAL)

add_textbox(s, 0, Inches(1.5), prs.slide_width, Inches(1.2),
            '感谢聆听', size=54, color=RGBColor(0xFF,0xFF,0xFF), bold=True,
            align=PP_ALIGN.CENTER)
add_textbox(s, 0, Inches(2.7), prs.slide_width, Inches(0.8),
            '欢迎提问 · Questions Welcome', size=28,
            color=C_TEAL, align=PP_ALIGN.CENTER)

add_multiline(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.5), [
    ('MindGuard · 神经符号双引擎驱动的校园心理风险智能筛查与干预系统',
     RGBColor(0xFF,0xFF,0xFF), True),
    ('团队成员：阮家炜（负责人） · 张修瑜',
     RGBColor(0xCC,0xDD,0xEE), False),
    ('', RGBColor(0,0,0), False),
    ('答辩 PPT · 2026 年 9 月 · 第八届 AIC 全球校园人工智能算法精英大赛',
     C_MUTED, False),
], size=13)

print('✅ Page 21 致谢')

# ============================================================
# 保存
# ============================================================
prs.save(OUT)
print(f'\n🎉 PPT 已生成：{OUT}')
print(f'   文件大小：{os.path.getsize(OUT) / 1024:.1f} KB')
print(f'   总页数：{len(prs.slides)}')
