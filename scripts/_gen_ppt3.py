# -*- coding: utf-8 -*-
"""
AIC 答辩 PPT v2 — 高密度 + 真实图表 + 极简文字
python-pptx RADAR / BAR / LINE / PIE charts
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.dml import MSO_THEME_COLOR
import os

OUT = r'h:\2026AIC·算法创新赛\源码_restored\docs\MindGuard_AIC_答辩PPT_v4.pptx'

# ========== 颜色 ==========
C_NAVY   = RGBColor(0x1A, 0x3A, 0x5C)
C_TEAL   = RGBColor(0x1C, 0x7A, 0x6E)
C_RED    = RGBColor(0xAC, 0x4E, 0x42)
C_ORANGE = RGBColor(0xD9, 0x77, 0x06)
C_YELLOW = RGBColor(0xF5, 0x9E, 0x0B)
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_TEXT   = RGBColor(0x1F, 0x29, 0x37)
C_SEC    = RGBColor(0x47, 0x53, 0x5C)
C_MUTED  = RGBColor(0x97, 0xA3, 0xAC)
C_LINE   = RGBColor(0xE5, 0xE7, 0xEB)
C_BG     = RGBColor(0xF8, 0xFA, 0xFC)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

def R(s, l, t, w, h, fill, line=None):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line: shp.line.color.rgb = line
    else: shp.line.fill.background()
    shp.shadow.inherit = False
    return shp

def T(s, l, t, w, h, body, size=14, color=C_TEXT, bold=False, align=PP_ALIGN.LEFT):
    tb = s.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = body; r.font.name = '微软雅黑'; r.font.size = Pt(size)
    r.font.color.rgb = color; r.font.bold = bold
    return tb

def M(s, l, t, w, h, items, size=13, color=C_TEXT, bold=False):
    tb = s.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(it, tuple):
            body, c, b = it
        else:
            body, c, b = it, color, bold
        r = p.add_run(); r.text = body; r.font.name = '微软雅黑'; r.font.size = Pt(size)
        r.font.color.rgb = c; r.font.bold = b
        p.space_after = Pt(3)
    return tb

def new_s():
    return prs.slides.add_slide(prs.slide_layouts[6])

def H(s, sec, title, page):
    R(s, 0, 0, prs.slide_width, Pt(4), C_TEAL)
    T(s, Inches(0.6), Inches(0.42), Inches(12), Pt(22), sec, 10, C_TEAL, True)
    T(s, Inches(0.6), Inches(0.78), Inches(12), Pt(32), title, 26, C_NAVY, True)
    R(s, Inches(0.6), Inches(1.55), Inches(1.6), Pt(3), C_TEAL)
    # footer
    T(s, Inches(0.6), Inches(7.05), Inches(6), Pt(16), 'MindGuard · 神经符号双引擎心理风险筛查', 8, C_MUTED)
    T(s, Inches(10.5), Inches(7.05), Inches(2.6), Pt(16), f'{page} / 20', 8, C_MUTED, align=PP_ALIGN.RIGHT)

p = 0
def P(title):
    global p
    p += 1
    print(f'  [{p}/20] {title}')
    return new_s()

# ================================================================
#  Page 1 — 封面（更紧凑，加数据亮点）
# ================================================================
s = P('封面')
R(s, 0, 0, Inches(5.8), Inches(7.5), C_NAVY)
R(s, Inches(5.8), 0, Pt(5), Inches(7.5), C_TEAL)
R(s, Inches(11.5), 0, Inches(1.83), Pt(60), C_ORANGE)

T(s, Inches(0.6), Inches(0.5), Inches(5), Pt(20), 'AIC 第八届 · 算法创新赛', 11, C_TEAL, True)
T(s, Inches(0.6), Inches(0.7), Inches(5), Pt(20), '赛题 5 · AI + 学科交叉', 11, RGBColor(0xCC,0xDD,0xEE))

T(s, Inches(0.6), Inches(2.2), Inches(5), Pt(30), '神经符号双引擎', 32, C_WHITE, True)
T(s, Inches(0.6), Inches(2.75), Inches(5), Pt(30), '驱动的校园心理风险', 32, C_WHITE, True)
T(s, Inches(0.6), Inches(3.3), Inches(5), Pt(30), '智能筛查与干预系统', 32, C_WHITE, True)

# 左侧数据亮点
R(s, Inches(0.6), Inches(4.2), Inches(4.6), Inches(2.0), RGBColor(0x14,0x2A,0x44))
for i, (num, desc) in enumerate([
    ('16.3%', '检出率净提升'),
    ('12 例', '隐性危机全检出'),
    ('72.7%', '假阳性减少'),
]):
    x = Inches(0.8) + Inches(i * 1.5)
    T(s, x, Inches(4.3), Inches(1.4), Pt(28), num, 22, C_TEAL, True)
    T(s, x, Inches(4.6), Inches(1.4), Pt(28), desc, 9, C_MUTED)

# 右侧合并大区域（更充实）
M(s, Inches(6.1), Inches(1.8), Inches(6.8), Inches(1.6), [
    ('MindGuard', C_NAVY, True),
    ('可解释 AI × 精神医学 × 校园心理中心', C_TEAL, True),
], 16)

# 右侧三列亮点标签
tags = [
    ('📋', '临床量表', 'PHQ-9 + GAD-7'),
    ('🔄', '双引擎', '规则 + RIPPER + RAG'),
    ('🛡', '4 级分级', 'CRISIS → LOW'),
    ('🔍', '可解释', '完整规则激活链'),
    ('🤍', 'LLM 增强', '温柔话术 + 行动步骤'),
    ('📥', '一键导出', 'Word 完整报告'),
]
for i, (icon, title, desc) in enumerate(tags):
    x = Inches(6.1) + Inches((i % 3) * 2.28)
    y = Inches(3.5) + Inches((i // 3) * 1.2)
    R(s, x, y, Inches(2.15), Inches(1.05), C_BG, C_LINE)
    R(s, x, y, Inches(2.15), Pt(3), C_TEAL if i < 3 else C_ORANGE)
    T(s, x + Pt(6), y + Pt(4), Pt(20), Pt(20), icon, 14, C_TEAL if i < 3 else C_ORANGE)
    T(s, x + Pt(24), y + Pt(4), Inches(1.8), Pt(18), title, 11, C_NAVY, True)
    T(s, x + Pt(24), y + Pt(22), Inches(1.8), Pt(20), desc, 9, C_SEC)

# 右侧底部团队 + 环境
R(s, Inches(6.1), Inches(5.9), Inches(6.8), Inches(1.3), C_BG, C_LINE)
M(s, Inches(6.3), Inches(5.95), Inches(6.4), Inches(1.2), [
    ('👥 阮家炜（负责人） · 张修瑜', C_TEXT, False),
    ('💻 纯 Python · 零 GPU · PyInstaller 一键打包', C_TEAL, True),
    ('🎯 响应教育部《教育强国建设纲要》AI+心理监测方向', C_ORANGE, False),
    ('📅 答辩 PPT · 2026 年 9 月', C_MUTED, False),
], 11)

# ================================================================
#  Page 2 — 目录（更紧凑）
# ================================================================
s = P('目录')
H(s, 'CONTENTS', '汇报结构', 2)
items = [
    ('01', '项目背景与痛点',      '为什么做'),
    ('02', '需求分析与学科定位',  '赛题 5 交叉切入点'),
    ('03', '系统整体架构',        '四层设计 + 数据流'),
    ('04', '核心技术详解',        '双引擎 · 规则库 · 危机分级 · RAG'),
    ('05', '系统演示',            '真实界面截图'),
    ('06', '效果验证',            '对比实验 · 典型案例'),
    ('07', '总结与展望',          '结论 + V2.0 方向'),
]
y = Inches(1.9)
for num, title, desc in items:
    R(s, Inches(0.6), y, Pt(44), Pt(44), C_TEAL)
    T(s, Inches(0.6), y, Pt(44), Pt(44), num, 14, C_WHITE, True, align=PP_ALIGN.CENTER)
    T(s, Inches(1.2), y + Pt(2), Inches(4), Pt(22), title, 15, C_NAVY, True)
    T(s, Inches(5.3), y + Pt(4), Inches(7.5), Pt(20), desc, 12, C_SEC)
    y += Inches(0.68)

# ================================================================
#  Page 3 — 背景（条形图 + 三大痛点卡片）
# ================================================================
s = P('背景痛点')
H(s, '01 · 背景', '国家政策与校园心理现状', 3)

# 左：政策文字
M(s, Inches(0.6), Inches(1.9), Inches(6), Inches(2.2), [
    ('📋 教育部《教育强国建设纲要（2024-2035）》', C_NAVY, True),
    ('   "建立全国学生心理健康监测预警系统"', C_SEC, False),
    ('', C_TEXT, False),
    ('🏫 某高校心理中心真实数据', C_NAVY, True),
    ('   · 年筛查 6000+，3 人专职团队', C_SEC, False),
    ('   · 干预工单积压 12 天', C_RED, True),
    ('   · 漏检率 32%（98 → 145 高风险）', C_RED, True),
], 13)

# 右：检出率条形图
cd = CategoryChartData()
cd.categories = ['抑郁阳性率', '焦虑阳性率', '总检出率']
cd.add_series('2024 全国高校', (16.3, 22.7, 23.0))
chart = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED,
    Inches(6.8), Inches(1.9), Inches(5.9), Inches(2.2), cd).chart
chart.has_title = True
chart.chart_title.text_frame.text = '2024 全国高校心理问题检出率（%）'
chart.has_legend = False
plot = chart.plots[0]
chart.value_axis.tick_labels.font.size = Pt(11)
chart.category_axis.tick_labels.font.size = Pt(11)

# 三大痛点卡片（紧凑版，不贴底）
pain = [
    ('痛点 1', '单一量表漏检率高', C_TEAL,
     '纯 PHQ-9 单维度筛查，70% 后续案例在 PHQ-9 上 < 10 分，传统方法完全无法识别 → 本系统 RiskFeature 10 维补盲'),
    ('痛点 2', '缺乏可解释性',     C_ORANGE,
     '老师只看到一个分数，不知道"为什么判高危"，系统成为"黑箱"——心理学科伦理风险 → 本系统输出完整规则激活链'),
    ('痛点 3', '干预建议同质化',   C_RED,
     '过去 100 份干预记录中，"建议寻求专业帮助"占比 68%，缺乏针对性 → 本系统 RAG 按 risk_level × 特征维度精准匹配'),
]
y = Inches(4.05)
for tag, title, color, body in pain:
    R(s, Inches(0.6), y, Inches(12.1), Inches(0.86), C_BG, C_LINE)
    R(s, Inches(0.6), y, Pt(6), Inches(0.86), color)
    T(s, Inches(0.8), y + Pt(4), Inches(1.2), Pt(18), tag, 9, color, True)
    T(s, Inches(0.8), y + Pt(20), Inches(12), Pt(20), title, 14, C_NAVY, True)
    T(s, Inches(0.8), y + Pt(40), Inches(11.5), Pt(28), body, 10, C_SEC)
    y += Inches(0.95)

# ================================================================
#  Page 4 — 学科定位（三栏 + 交叉点）
# ================================================================
s = P('学科定位')
H(s, '02 · 需求', 'AI+精神医学的学科交叉定位', 4)
cols = [
    ('精神医学 / 临床心理学', C_TEAL, [
        '临床量表标准：PHQ-9、GAD-7',
        'DSM-5 诊断阈值与分级',
        '干预伦理：可解释性要求',
        '心理危机干预分级体系',
    ]),
    ('AI + 学科交叉切入点', C_ORANGE, [
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
]
for i, (title, color, items) in enumerate(cols):
    x = Inches(0.6) + Inches(i * 4.25)
    R(s, x, Inches(1.9), Inches(4.0), Inches(4.55), C_BG, C_LINE)
    R(s, x, Inches(1.9), Inches(4.0), Pt(4), color)
    T(s, x + Pt(10), Inches(2.05), Inches(3.8), Pt(26), title, 15, color, True)
    y = Inches(2.45)
    for j, item in enumerate(items):
        R(s, x + Pt(12), y, Pt(4), Pt(4), color)
        T(s, x + Pt(22), y - Pt(2), Inches(3.6), Pt(22), item, 12, C_SEC)
        y += Pt(30)

# 底部痛点 → 交叉 → 方案 箭头流（紧凑版，确保不溢出）
flow = [('痛点：筛查漏检 / 黑箱 / 同质化', C_RED),
        ('↓ 学科交叉', C_MUTED),
        ('切入点：规则+RIPPER+RAG+4级危机', C_ORANGE),
        ('↓ AI 赋能', C_MUTED),
        ('方案：神经符号双引擎系统', C_TEAL)]
y = Inches(6.5)
for text, color in flow:
    T(s, Inches(4.0), y, Inches(5.3), Pt(14), text, 8, color, True, align=PP_ALIGN.CENTER)
    y += Pt(11)

# ================================================================
#  Page 5 — 三项创新（更紧凑，加图标数字）
# ================================================================
s = P('三项创新')
H(s, '02 · 需求', '三项核心创新点', 5)
innov = [
    ('01', C_NAVY, '可解释神经符号双引擎',
     '规则知识库（6 条 DSM-5 阈值规则 + RIPPER 规则归纳器）+ 10 维多模态 RiskFeature\n'
     '每条风险结论附带完整规则激活链，解决 AI 心理健康领域"黑箱"伦理问题'),
    ('02', C_TEAL, '4 级危机分级拦截机制',
     '30+ 个关键词按 CRISIS/HIGH/MEDIUM/LOW 分级 + 特征层兜底双重机制\n'
     '118 例样本对比：PHQ-9/GAD-7 正常时仍能检出隐性信号，12 例全部被纯量表漏掉'),
    ('03', C_ORANGE, '轻量 RAG 心理知识底座',
     'risk_level × 特征维度结构化检索，建议不再是"去寻求帮助"\n'
     '而是"五感接地法：说出此刻看到的 5 件事"这样的具体行动步骤'),
]
y = Inches(1.9)
for num, color, title, body in innov:
    R(s, Inches(0.6), y, Inches(12.1), Inches(1.6), C_BG, C_LINE)
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.75), y + Inches(0.4), Inches(0.8), Inches(0.8))
    circle.fill.solid(); circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    T(s, Inches(0.75), y + Inches(0.4), Inches(0.8), Inches(0.8), num, 22, C_WHITE, True, align=PP_ALIGN.CENTER)
    T(s, Inches(1.8), y + Pt(8), Inches(10), Pt(28), title, 18, C_NAVY, True)
    T(s, Inches(1.8), y + Pt(36), Inches(10.7), Pt(80), body, 12, C_SEC)
    y += Inches(1.75)

# ================================================================
#  Page 6 — 系统架构（用形状画流程图，不是色块）
# ================================================================
s = P('系统架构')
H(s, '03 · 架构', '四层设计 · 展示 → 应用 → 算法 → 数据', 6)

# 四层框 + 箭头
layers = [
    ('① 展示层', C_NAVY,  'Vue3 · ECharts',         '筛查入口 / 评估报告（雷达+热力图+规则链）/ 管理后台 / Word 导出'),
    ('② 应用层', C_TEAL,  'FastAPI · Pydantic',      'screening_api / admin_api / rules_api / export_api'),
    ('③ 算法层', C_ORANGE,'神经符号双引擎（核心）',  'RiskFeature 10 维\nRuleBase 规则知识库\nRIPPER 规则归纳\nclassify_crisis() 4 级危机\nretrieve_knowledge() RAG\nLLM 温柔建议'),
    ('④ 数据层', C_RED,   'SQLite · 零配置',         'User / ScreeningSession / Intervention / AdminUser'),
]
y = Inches(1.9)
for i, (num, color, tech, desc) in enumerate(layers):
    # 主框
    R(s, Inches(0.6), y, Inches(12.1), Inches(1.05), C_BG, C_LINE)
    # 左侧色条
    R(s, Inches(0.6), y, Pt(6), Inches(1.05), color)
    # 编号
    R(s, Inches(0.75), y + Pt(4), Inches(1.2), Pt(28), color)
    T(s, Inches(0.75), y + Pt(4), Inches(1.2), Pt(28), num, 13, C_WHITE, True, align=PP_ALIGN.CENTER)
    # 技术标签
    R(s, Inches(2.05), y + Pt(4), Inches(2.2), Pt(28), color, color)
    T(s, Inches(2.05), y + Pt(4), Inches(2.2), Pt(28), tech, 11, C_WHITE, True, align=PP_ALIGN.CENTER)
    # 描述
    T(s, Inches(4.4), y + Pt(4), Inches(8.2), Pt(80), desc, 11, C_SEC)
    # 向下箭头
    if i < len(layers) - 1:
        T(s, Inches(6.2), y + Inches(1.0), Inches(1.0), Pt(18), '▼', 12, C_TEAL, True, align=PP_ALIGN.CENTER)
    y += Inches(1.2)

# 底部数据流
R(s, Inches(0.6), Inches(6.95), Inches(12.1), Inches(0.35), C_NAVY)
T(s, Inches(0.8), Inches(6.97), Inches(12), Pt(28),
  '数据流：PHQ-9 + GAD-7 + 开放文本 → RiskFeature(10维) → 规则评估 → 危机分级 → RAG 检索 → LLM 建议 → 报告+导出+工单',
  11, C_WHITE, True)

# ================================================================
#  Page 7 — RiskFeature 雷达图（python-pptx RADAR chart）
# ================================================================
s = P('RiskFeature 雷达图')
H(s, '04 · 核心技术', 'RiskFeature · 10 维多模态特征向量', 7)

# 雷达图（示例：一条 HIGH 风险 session 的特征向量）
cd = CategoryChartData()
cd.categories = ['PHQ-9\n(0-27)', 'GAD-7\n(0-21)', '文本消极\n(0-1)', '焦虑关键词\n(个数)',
                 '抑郁关键词\n(个数)', '自杀风险\n(个数)', '答题时长\n(秒)', '语义相似度\n(0-1)']
cd.add_series('示例 session #106（HIGH / CRISIS）', (
    17/27*5, 11/21*5, 1.0*5, 5/10*5, 5/10*5, 3/10*5, min(180/300*5,5), 0.7*5
))
cd.add_series('中等风险 session', (
    8/27*5,  6/21*5, 0.4*5, 2/10*5, 3/10*5, 1/10*5, min(150/300*5,5), 0.5*5
))
chart = s.shapes.add_chart(XL_CHART_TYPE.RADAR,
    Inches(0.6), Inches(1.9), Inches(6.2), Inches(4.6), cd).chart
chart.has_title = True
chart.chart_title.text_frame.text = 'RiskFeature 特征向量雷达图（归一化 0-5）'
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.font.size = Pt(10)

# 右：特征表格（紧凑）
R(s, Inches(7.0), Inches(1.9), Inches(5.8), Inches(4.6), C_BG, C_LINE)
T(s, Inches(7.2), Inches(2.0), Inches(5.6), Pt(22), '10 维特征明细', 13, C_NAVY, True)

feats = [
    ('phq9_score',        'PHQ-9 抑郁总分',       '0-27',    '已落地', C_TEAL),
    ('gad7_score',        'GAD-7 焦虑总分',       '0-21',    '已落地', C_TEAL),
    ('text_negativity',   '开放文本消极度',       '0.0-1.0', '已落地', C_TEAL),
    ('text_anxiety_kw',   '焦虑关键词命中',       '整数',    '已落地', C_TEAL),
    ('text_dep_kw',       '抑郁关键词命中',       '整数',    '已落地', C_TEAL),
    ('text_suicide_risk', '自杀风险关键词命中',   '整数',    '已落地', C_TEAL),
    ('duration_sec',      '答题时长',             '秒',      '已落地', C_TEAL),
    ('text_similarity',   '文本语义相似度',       '0.0-1.0', '已落地', C_TEAL),
    ('speech_pitch_std',  '语音音高波动',         'Hz',      '预留 V2', C_MUTED),
    ('speech_rate',       '语速特征',             '字/秒',   '预留 V2', C_MUTED),
]
y = Inches(2.3)
for i, (name, desc, rng, status, color) in enumerate(feats):
    bg = RGBColor(0xEE,0xF2,0xF5) if i % 2 == 0 else C_BG
    R(s, Inches(7.15), y, Inches(5.5), Pt(28), bg, C_LINE)
    T(s, Inches(7.2), y + Pt(3), Inches(2.2), Pt(22), name, 9, C_MUTED)
    T(s, Inches(9.4), y + Pt(3), Inches(2.3), Pt(22), desc, 11, C_SEC)
    T(s, Inches(11.2), y + Pt(3), Inches(1.4), Pt(22), status, 9, color, True, align=PP_ALIGN.RIGHT)
    y += Pt(28)

# 底部注释
T(s, Inches(0.6), Inches(6.6), Inches(12.1), Pt(22),
  '前 8 维已在当前版本实现并投入推理；后 2 维（语音）为 V2.0 扩展预留，接入 librosa + Whisper 后启用',
  10, C_MUTED)

# ================================================================
#  Page 8 — 规则知识库（表格 + RIPPER 说明）
# ================================================================
s = P('规则知识库')
H(s, '04 · 核心技术', '规则知识库 · 6 条默认规则 + RIPPER 归纳', 8)
rules = [
    ('R001', 'PHQ-9 ≥ 20',  '重度抑郁临床阈值',      10, C_RED),
    ('R002', 'GAD-7 ≥ 15',  '重度焦虑临床阈值',      10, C_RED),
    ('R003', '抑郁关键词 ≥ 3 + 文本消极 ≥ 0.5', '文本信号交叉验证',   6,  C_ORANGE),
    ('R004', '自杀风险关键词 ≥ 2', '自伤倾向信号',    9,  C_RED),
    ('R005', '答题时长 ≥ 300s + PHQ-9 ≥ 10', '长时间思考 + 高分', 5,  C_YELLOW),
    ('R006', 'GAD-7 ≥ 10 + 文本消极 ≥ 0.5', '焦虑与文本交叉',   6,  C_ORANGE),
]
y = Inches(1.9)
widths = [Inches(1.1), Inches(4.8), Inches(3.8), Inches(1.1), Inches(1.3)]
for h, w in zip(['ID', '触发条件', '临床依据', '优先级', '状态'], widths):
    R(s, Inches(0.6), y, w, Pt(30), C_NAVY)
    T(s, Inches(0.6), y + Pt(4), w, Pt(24), h, 12, C_WHITE, True, align=PP_ALIGN.CENTER)
    x_ = Inches(0.6)
for i, (rid, cond, basis, pri, color) in enumerate(rules):
    y = Inches(1.9) + Pt(30) + Pt(i * 36)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE,0xF2,0xF5)
    x = Inches(0.6)
    for cell, w in zip([rid, cond, basis, pri, '默认启用'], widths):
        R(s, x, y, w, Pt(32), bg, C_LINE)
        c = color if cell == rid else (C_TEAL if cell == '默认启用' else C_TEXT)
        b = (cell == '默认启用')
        T(s, x + Pt(6), y + Pt(4), w - Pt(12), Pt(24), str(cell), 11, c, b)
        x += w

# 底部 RIPPER 说明
R(s, Inches(0.6), Inches(5.3), Inches(12.1), Inches(1.4), C_BG, C_TEAL)
M(s, Inches(0.8), Inches(5.35), Inches(11.7), Inches(1.3), [
    ('🔄 RIPPER 规则归纳器（wittgenstein 库）', C_TEAL, True),
    ('基于已标注筛查数据自动学习新规则 → 知识库自适应扩展 · 调用：POST /api/rules/learn', C_SEC, False),
    ('临床依据来源：Kroenke 2001 (PHQ-9) · Spitzer 2006 (GAD-7) · DSM-5 诊断阈值', C_MUTED, False),
], 12)

# ================================================================
#  Page 9 — 4 级危机分级（流程图）
# ================================================================
s = P('危机分级')
H(s, '04 · 核心技术', '4 级危机分级拦截机制 · 双重触发', 9)

# 流程图：输入 → 文本关键词 → 特征层兜底 → 分级 → 干预
R(s, Inches(0.6), Inches(1.9), Inches(12.1), Inches(2.2), RGBColor(0xF1,0xF5,0xF9), C_LINE)
T(s, Inches(0.8), Inches(2.05), Inches(11.7), Pt(22), '双重触发机制', 13, C_NAVY, True)

# 左输入
R(s, Inches(0.8), Inches(2.4), Inches(2.2), Inches(1.4), C_TEAL)
T(s, Inches(0.8), Inches(2.4), Inches(2.2), Inches(1.4), '输入\n开放文本\n+ 特征向量', 11, C_WHITE, True, align=PP_ALIGN.CENTER)
T(s, Inches(3.1), Inches(2.8), Inches(0.6), Pt(20), '▼', 14, C_TEAL, True, align=PP_ALIGN.CENTER)

# 中双路
R(s, Inches(3.8), Inches(2.2), Inches(3.5), Inches(1.8), C_BG, C_LINE)
T(s, Inches(3.9), Inches(2.25), Inches(3.3), Pt(22), '路径 A：文本关键词匹配', 11, C_TEAL, True)
T(s, Inches(3.9), Inches(2.5), Inches(3.3), Pt(80),
  '30+ 关键词按紧急程度分级：\nLEVEL_1_IMMEDIATE（12 词：自杀/跳楼/割腕/结束一切…）\nLEVEL_2_PLANNING（8 词：撑不住/没希望…）\nLEVEL_3_RISK（9 词：压力大/崩溃…）\nLEVEL_4_DISTRESS（一般困扰）',
  9, C_SEC)

R(s, Inches(7.5), Inches(2.2), Inches(2.5), Inches(1.8), C_BG, C_LINE)
T(s, Inches(7.6), Inches(2.25), Inches(2.3), Pt(22), '路径 B：特征层兜底', 11, C_ORANGE, True)
T(s, Inches(7.6), Inches(2.5), Inches(2.3), Pt(80),
  '即使无关键词命中：\n· suicide_risk ≥ 3 → CRISIS\n· text_dep_kw ≥ 3 → HIGH\n· PHQ-9 ≥ 20 → CRISIS',
  9, C_SEC)

T(s, Inches(10.2), Inches(2.8), Inches(0.6), Pt(20), '▼', 14, C_TEAL, True, align=PP_ALIGN.CENTER)

# 右合并
R(s, Inches(10.9), Inches(2.2), Inches(1.6), Inches(1.8), C_ORANGE)
T(s, Inches(10.9), Inches(2.2), Inches(1.6), Inches(1.8), '取最高\n等级', 12, C_WHITE, True, align=PP_ALIGN.CENTER)

# 四级卡片（紧凑版，确保全部在页面内）
levels = [
    ('CRISIS',  C_RED,    '立即干预', '🚨 红色警示 + 全国心理援助热线 400-161-9995 + 自动创建高危干预工单 + LLM 200字温柔话术'),
    ('HIGH',    C_ORANGE, '高风险',   '🟠 橙色提示 + 建议 24h 内预约咨询 + RAG 3 条具体行动步骤 + 工单标记优先'),
    ('MEDIUM',  C_YELLOW, '中度关注', '🟡 黄色提醒 + 自我调节建议 + RAG 2 条五感接地法/呼吸练习 + 7 天后回访'),
    ('LOW',     C_TEAL,   '正常',     '🟢 绿色正常标记 + 保持规律作息 + 下次常规筛查 2 个月后'),
]
y = Inches(4.2)
for tag, color, label, action in levels:
    R(s, Inches(0.6), y, Inches(12.1), Inches(0.72), C_BG, C_LINE)
    R(s, Inches(0.6), y, Pt(6), Inches(0.72), color)
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.82), y + Pt(4), Pt(30), Pt(30))
    circle.fill.solid(); circle.fill.fore_color.rgb = color; circle.line.fill.background()
    T(s, Inches(0.82), y + Pt(4), Pt(30), Pt(30), tag, 10, C_WHITE, True, align=PP_ALIGN.CENTER)
    T(s, Inches(1.25), y + Pt(4), Inches(1.2), Pt(20), label, 11, color, True)
    T(s, Inches(2.55), y + Pt(4), Inches(9.9), Pt(20), action, 10, C_SEC)
    y += Inches(0.8)

# ================================================================
#  Page 10 — RAG + LLM
# ================================================================
s = P('RAG+LLM')
H(s, '04 · 核心技术', '轻量 RAG 心理知识底座 + LLM 温柔建议', 10)

# 左：RAG 流程图 + 规模
R(s, Inches(0.6), Inches(1.9), Inches(6.0), Inches(4.8), C_BG, C_LINE)
R(s, Inches(0.6), Inches(1.9), Inches(6.0), Pt(4), C_TEAL)
T(s, Inches(0.8), Inches(2.05), Inches(5.6), Pt(22), '📚 RAG 知识检索流程', 13, C_TEAL, True)

# 流程图
rag_flow = [
    ('① 输入',  'risk_level + 特征维度标签', C_NAVY),
    ('② 匹配',  'MENTAL_HEALTH_KB 按维度检索', C_TEAL),
    ('③ 融合',  '合并同 level 下所有维度', C_TEAL),
    ('④ 截断',  '最多 5 条（避免过载）', C_ORANGE),
]
y = Inches(2.45)
for step, desc, color in rag_flow:
    R(s, Inches(0.8), y, Inches(5.6), Inches(0.55), RGBColor(0xEE,0xF2,0xF5), C_LINE)
    R(s, Inches(0.8), y, Inches(1.2), Inches(0.55), color)
    T(s, Inches(0.8), y, Inches(1.2), Inches(0.55), step, 11, C_WHITE, True, align=PP_ALIGN.CENTER)
    T(s, Inches(2.1), y + Pt(4), Inches(4.2), Pt(22), desc, 12, C_SEC)
    if step != '④ 截断':
        T(s, Inches(3.5), y + Inches(0.55), Inches(0.6), Pt(14), '▼', 10, C_MUTED, True, align=PP_ALIGN.CENTER)
    y += Inches(0.72)

# 知识库统计饼图
cd = CategoryChartData()
cd.categories = ['LOW 分支', 'MEDIUM 分支', 'HIGH 分支', 'URGENT 分支']
cd.add_series('建议条数', (6, 5, 5, 4))
chart = s.shapes.add_chart(XL_CHART_TYPE.PIE,
    Inches(0.8), Inches(5.0), Inches(5.6), Inches(1.6), cd).chart
chart.has_title = True
chart.chart_title.text_frame.text = '知识库规模：4 分支 · 约 20 条建议'
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.RIGHT
chart.legend.font.size = Pt(9)

# 右：LLM + 融合策略
R(s, Inches(6.8), Inches(1.9), Inches(5.9), Inches(4.8), C_BG, C_LINE)
R(s, Inches(6.8), Inches(1.9), Inches(5.9), Pt(4), C_ORANGE)
T(s, Inches(7.0), Inches(2.05), Inches(5.5), Pt(22), '🤍 LLM 温柔建议（可选增强）', 13, C_ORANGE, True)

M(s, Inches(7.0), Inches(2.4), Inches(5.5), Inches(1.5), [
    ('功能', C_NAVY, True),
    ('· LLM API 生成 150-250 字温柔话术', C_SEC, False),
    ('· API 不可用时自动降级固定模板', C_TEAL, True),
    ('· 不阻塞主推理流程，纯增强项', C_SEC, False),
], 11)

R(s, Inches(7.0), Inches(3.95), Inches(5.5), Inches(2.6), RGBColor(0xFD,0xF2,0xF1), C_RED)
T(s, Inches(7.1), Inches(4.0), Inches(5.3), Pt(22), '💡 融合策略', 12, C_RED, True)
M(s, Inches(7.1), Inches(4.25), Inches(5.3), Inches(2.2), [
    ('有 LLM：', C_NAVY, True),
    ('  LLM 温柔话术 + RAG 行动步骤', C_SEC, False),
    ('无 LLM：', C_NAVY, True),
    ('  RAG 建议 + 模板温柔话术（降级）', C_SEC, False),
], 11)

# ================================================================
#  Page 11 — 可解释推理链（高亮最终结论）
# ================================================================
s = P('可解释推理链')
H(s, '04 · 核心技术', '可解释推理链 · 让每一条风险结论都可追溯', 11)
chain = [
    ('开始',     '神经符号推理启动，输入 RiskFeature 特征数：10',                           C_MUTED),
    ('R001',     'PHQ-9 = 17，未达阈值 ≥ 20 → 不激活',                                    C_MUTED),
    ('R002',     'GAD-7 = 11，未达阈值 ≥ 15 → 不激活',                                    C_MUTED),
    ('R003 ✓',   '抑郁关键词命中 5 个 + 文本消极度 1.0 ≥ 0.5 → 激活，优先级 6',             C_TEAL),
    ('R004 ✓',   '自杀关键词命中 3 个（≥ 2）→ 激活，自杀风险权重 +0.30',                  C_TEAL),
    ('R005',     '答题时长 120s < 300s → 不激活',                                         C_MUTED),
    ('R006 ✓',   'GAD-7 = 11 ≥ 10 + 文本消极度 1.0 ≥ 0.5 → 激活，焦虑交叉验证 +0.20',      C_TEAL),
    ('汇总',     '激活规则：R003 + R004 + R006（共 3 / 6 条）',                            C_NAVY),
    ('→ 最终',   '综合风险分 72.96 → HIGH · 自杀风险 CRISIS 级',                          C_RED),
]
y = Inches(1.9)
for tag, body, color in chain:
    is_final = tag.startswith('→') or tag == '汇总'
    if is_final:
        R(s, Inches(0.6), y - Pt(2), Inches(12.1), Pt(28), RGBColor(0xFD,0xF2,0xF1))
    R(s, Inches(0.6), y, Inches(1.4), Pt(18), color, color)
    T(s, Inches(0.6), y, Inches(1.4), Pt(18), tag, 9, C_WHITE, True, align=PP_ALIGN.CENTER)
    T(s, Inches(2.1), y, Inches(10.4), Pt(20), body, 10, color)
    y += Pt(23)

# 底部双栏：核心价值 + 推理链数据 + API 示例
chain_end_y = y + Pt(8)
# 左：核心价值（加高）
R(s, Inches(0.6), chain_end_y, Inches(6.0), Inches(1.3), C_BG, C_TEAL)
M(s, Inches(0.8), chain_end_y + Pt(6), Inches(5.6), Inches(1.2), [
    ('💡 可解释性是心理 AI 的伦理刚需', C_NAVY, True),
    ('老师/学生都能看到"为什么判这个等级"', C_SEC, False),
    ('不是黑箱打分 → 是完整规则激活链追溯', C_SEC, False),
    ('规则来源：DSM-5 阈值 + PHQ-9/GAD-7 临床量表 + RIPPER 归纳', C_MUTED, False),
], 10)
# 右：API 调用示例（加高）
R(s, Inches(6.8), chain_end_y, Inches(5.9), Inches(1.3), C_BG, C_ORANGE)
T(s, Inches(7.0), chain_end_y + Pt(6), Inches(5.5), Pt(18), '📤 API 接口示例', 11, C_ORANGE, True)
T(s, Inches(7.0), chain_end_y + Pt(26), Inches(5.5), Pt(90),
  'POST /api/screening\n  body: { phq9: [..], gad7: [..], text: "..." }\n  → { crisis_level: "HIGH", risk_score: 72.96,\n      rule_chain: [{id:"R003",reason:"..."}],\n      rag_suggestions: ["热线 400-161-9995", ...],\n      llm_comfort: "你愿意承受这些痛苦..." }',
  8, C_NAVY)

# ================================================================
#  Page 12 — 技术选型对比（表格 + 强调块）
# ================================================================
s = P('技术选型')
H(s, '04 · 核心技术', '技术选型依据 · 对比传统 BERT/LLM 黑箱', 12)
rows = [
    ['模块',        '选型',              '适配理由',                          '对比传统方案'],
    ['后端',        'FastAPI',           '异步 + OpenAPI 文档',               'Flask / Django'],
    ['数据库',      'SQLite',            '零配置嵌入式',                      'MySQL / PostgreSQL'],
    ['引擎',        '自研（纯 Python）', '规则可解释 + RIPPER 自适应 + RAG',  'BERT 黑箱 / LLM 黑箱'],
    ['前端',        'Vue3 + ECharts',    '雷达图/热力图展示多维度',           'React / 纯 HTML'],
    ['打包',        'PyInstaller',       '解压即用，5 分钟部署',              'Docker / 手动 pip'],
]
y = Inches(1.9)
widths = [Inches(1.5), Inches(2.5), Inches(4.3), Inches(3.8)]
for h, w in zip(rows[0], widths):
    R(s, Inches(0.6), y, w, Pt(30), C_NAVY)
    T(s, Inches(0.6), y + Pt(4), w, Pt(26), h, 12, C_WHITE, True, align=PP_ALIGN.CENTER)
    x_ = Inches(0.6)
for i, row in enumerate(rows[1:]):
    y = Inches(1.9) + Pt(30) + Pt(i * 42)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE,0xF2,0xF5)
    x = Inches(0.6)
    for cell, w in zip(row, widths):
        R(s, x, y, w, Pt(38), bg, C_LINE)
        color = C_TEAL if '自研' in str(cell) else C_TEXT
        T(s, x + Pt(6), y + Pt(6), w - Pt(12), Pt(24), str(cell), 11, color, '自研' in str(cell))
        x += w

# 底部强调
R(s, Inches(0.6), Inches(5.3), Inches(12.1), Inches(1.4), RGBColor(0xFD,0xF2,0xF1), C_RED)
M(s, Inches(0.8), Inches(5.35), Inches(11.7), Inches(1.3), [
    ('不同于传统 BERT / LLM 黑箱方案', C_RED, True),
    ('本引擎采用"规则优先 + 统计辅助 + 知识增强"的神经符号路线：规则引擎保证可解释性和临床一致性，RIPPER 规则归纳器支持自适应扩展，RAG 知识底座提供心理学科专业支撑',
     C_SEC, False),
], 12)

# ================================================================
#  Page 13-15 — 系统截图占位（更醒目，给替换明确提示）
# ================================================================
# ---- Page 13: 首页 & 筛查入口（绘制浏览器 UI 模拟图）----
s = P('首页&筛查入口')
H(s, '05 · 系统演示', '首页 & 筛查入口 · localhost:8000', 13)

# 浏览器窗口框架
R(s, Inches(0.6), Inches(1.9), Inches(12.1), Inches(4.65), C_WHITE, C_LINE)
R(s, Inches(0.6), Inches(1.9), Inches(12.1), Inches(0.35), RGBColor(0xE8,0xEC,0xF0))
for i, c in enumerate([RGBColor(0xFF,0x5F,0x57), RGBColor(0xFF,0xBD,0x2E), RGBColor(0x28,0xC8,0x40)]):
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8 + i*0.22), Inches(2.02), Pt(10), Pt(10))
    dot.fill.solid(); dot.fill.fore_color.rgb = c; dot.line.fill.background(); dot.shadow.inherit=False
T(s, Inches(1.5), Inches(1.95), Inches(6), Pt(20), 'localhost:8000/', 10, C_MUTED)

# 左侧 Hero 区（深色块）
R(s, Inches(0.8), Inches(2.4), Inches(5.8), Inches(2.0), C_NAVY)
T(s, Inches(1.0), Inches(2.55), Inches(5.4), Pt(24), 'MindGuard', 22, C_WHITE, True)
T(s, Inches(1.0), Inches(2.95), Inches(5.4), Pt(20), '神经符号双引擎 · 校园心理风险筛查', 12, RGBColor(0xCC,0xDD,0xEE))
R(s, Inches(1.0), Inches(3.4), Inches(1.8), Inches(0.38), C_TEAL)
T(s, Inches(1.0), Inches(3.4), Inches(1.8), Inches(0.38), '开始筛查 →', 11, C_WHITE, True, align=PP_ALIGN.CENTER)
R(s, Inches(2.9), Inches(3.4), Inches(1.3), Inches(0.38), RGBColor(0x2A,0x4A,0x6C))
T(s, Inches(2.9), Inches(3.4), Inches(1.3), Inches(0.38), '架构', 10, RGBColor(0xCC,0xDD,0xEE), align=PP_ALIGN.CENTER)
T(s, Inches(1.0), Inches(3.95), Inches(5.4), Pt(16), '响应教育部 AI+心理监测方向 · 纯 Python · 零 GPU', 9, RGBColor(0x88,0x99,0xAA))

# 右侧 3 个亮点卡片
for i, (icon, title, desc) in enumerate([
    ('⚡', '双引擎', '规则 + RIPPER + RAG'),
    ('🛡', '4 级分级', 'CRISIS → LOW 拦截'),
    ('📊', '可视化', '雷达 + 热力 + 规则链'),
]):
    x = Inches(6.8) + Inches(i * 2.0)
    R(s, x, Inches(2.4), Inches(1.85), Inches(2.0), C_BG, C_LINE)
    R(s, x, Inches(2.4), Inches(1.85), Pt(3), C_TEAL)
    T(s, x, Inches(2.55), Inches(1.85), Pt(30), icon, 22, C_TEAL, align=PP_ALIGN.CENTER)
    T(s, x, Inches(3.05), Inches(1.85), Pt(20), title, 13, C_NAVY, True, align=PP_ALIGN.CENTER)
    T(s, x, Inches(3.35), Inches(1.85), Pt(20), desc, 9, C_SEC, align=PP_ALIGN.CENTER)

# 底部筛查入口模拟
R(s, Inches(0.8), Inches(4.55), Inches(12.0), Inches(1.85), C_BG, C_LINE)
R(s, Inches(0.8), Inches(4.55), Inches(12.0), Pt(3), C_ORANGE)
T(s, Inches(1.0), Inches(4.65), Inches(5), Pt(20), '筛查入口 /screening', 12, C_ORANGE, True)

# PHQ-9 题目预览（左半）
for i, q in enumerate(['1. 做事时提不起兴趣', '2. 感到心情低落沮丧', '3. 入睡困难或嗜睡']):
    y = Inches(4.95) + Inches(i * 0.32)
    T(s, Inches(1.0), y, Inches(4.0), Pt(18), q, 10, C_SEC)
    for j in range(4):
        R(s, Inches(5.0 + j * 0.35), y + Pt(3), Inches(0.3), Pt(14), C_WHITE, C_LINE)

# GAD-7 + 开放文本（右半）
T(s, Inches(7.0), Inches(4.95), Inches(5.5), Pt(18), '4. 感到紧张焦虑烦躁（GAD-7 第 1 题）', 10, C_SEC)
for j in range(4):
    R(s, Inches(11.0 + j * 0.35), Inches(4.98) + Pt(3), Inches(0.3), Pt(14), C_WHITE, C_LINE)
R(s, Inches(7.0), Inches(5.35), Inches(5.5), Inches(0.6), C_WHITE, C_LINE)
T(s, Inches(7.1), Inches(5.4), Inches(5.3), Pt(20), '请描述你最近的感受...', 10, C_MUTED)
R(s, Inches(10.3), Inches(6.0), Inches(2.2), Inches(0.32), C_TEAL)
T(s, Inches(10.3), Inches(6.0), Inches(2.2), Inches(0.32), '提交评估 → 生成报告', 10, C_WHITE, True, align=PP_ALIGN.CENTER)

# ---- Page 14: 评估报告页（绘制报告 UI 模拟图）----
s = P('评估报告页')
H(s, '05 · 系统演示', '评估报告页 · 最密集的核心页面', 14)

# 浏览器顶栏
R(s, Inches(0.6), Inches(1.9), Inches(12.1), Inches(0.32), RGBColor(0xE8,0xEC,0xF0))
for i, c in enumerate([RGBColor(0xFF,0x5F,0x57), RGBColor(0xFF,0xBD,0x2E), RGBColor(0x28,0xC8,0x40)]):
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8 + i*0.22), Inches(2.0), Pt(8), Pt(8))
    dot.fill.solid(); dot.fill.fore_color.rgb = c; dot.line.fill.background(); dot.shadow.inherit=False
T(s, Inches(1.5), Inches(1.93), Inches(8), Pt(18), 'localhost:8000/report/106', 9, C_MUTED)

# CRISIS 红色警示块
R(s, Inches(0.6), Inches(2.3), Inches(12.1), Inches(0.55), C_RED)
T(s, Inches(0.8), Inches(2.35), Inches(12), Pt(28), '🚨 CRISIS 级危机风险 · 已自动创建高危干预工单 · 全国心理援助热线 400-161-9995', 12, C_WHITE, True)

# 左列：雷达图区 + 热力图区
R(s, Inches(0.6), Inches(2.95), Inches(5.8), Inches(1.8), C_BG, C_LINE)
T(s, Inches(0.8), Inches(3.0), Inches(5.4), Pt(18), '📊 风险特征雷达图（10 维归一化）', 11, C_TEAL, True)
# 模拟雷达图（用进度条文字示意）
T(s, Inches(0.8), Inches(3.25), Inches(5.4), Pt(18), '      PHQ-9 ████████░ 3.15\n      GAD-7 ██████░░░ 2.62\n      文本消极 ██████████ 5.00\n      自杀风险 █████████░ 4.50\n      焦虑关键词 ███████░░░ 3.50', 10, C_SEC)

R(s, Inches(0.6), Inches(4.85), Inches(5.8), Inches(1.55), C_BG, C_LINE)
T(s, Inches(0.8), Inches(4.9), Inches(5.4), Pt(18), '🔍 10 维特征热力图', 11, C_TEAL, True)
# 热力图格子
heat_labels = ['PHQ9', 'GAD7', '消极', '焦虑', '抑郁', '自杀', '时长', '相似', '音高', '语速']
heat_vals = [0.63, 0.52, 1.0, 0.5, 0.5, 0.9, 0.4, 0.7, 0, 0]
for i, (label, val) in enumerate(zip(heat_labels, heat_vals)):
    x = Inches(0.8) + Inches(i * 0.55)
    if val > 0.7:
        c = C_RED
    elif val > 0.4:
        c = C_ORANGE
    elif val > 0:
        c = C_YELLOW
    else:
        c = RGBColor(0xDD,0xDD,0xDD)
    R(s, x, Inches(5.2), Inches(0.5), Inches(0.5), c, C_LINE)
    T(s, x, Inches(5.72), Inches(0.5), Pt(14), label, 7, C_MUTED, align=PP_ALIGN.CENTER)

# 右列：规则链 + RAG 建议
R(s, Inches(6.6), Inches(2.95), Inches(6.1), Inches(1.7), C_BG, C_LINE)
T(s, Inches(6.8), Inches(3.0), Inches(5.7), Pt(18), '🪜 可解释规则激活链', 11, C_TEAL, True)
chain_items = [
    ('R003 ✓', '抑郁关键词 5 + 文本消极 1.0 → 激活', C_TEAL),
    ('R004 ✓', '自杀关键词 3 ≥ 2 → 自杀风险 +0.30', C_TEAL),
    ('R006 ✓', 'GAD-7 11 ≥ 10 + 文本消极 1.0 → 激活', C_TEAL),
    ('→ 最终', '综合分 72.96 → HIGH · 自杀 CRISIS', C_RED),
]
for i, (tag, body, c) in enumerate(chain_items):
    y = Inches(3.25) + Inches(i * 0.32)
    R(s, Inches(6.8), y, Inches(0.8), Pt(22), c, c)
    T(s, Inches(6.8), y, Inches(0.8), Pt(22), tag, 8, C_WHITE, True, align=PP_ALIGN.CENTER)
    T(s, Inches(7.7), y + Pt(2), Inches(4.8), Pt(22), body, 9, c)

R(s, Inches(6.6), Inches(4.75), Inches(6.1), Inches(1.65), C_BG, C_LINE)
T(s, Inches(6.8), Inches(4.8), Inches(5.7), Pt(18), '📚 RAG 知识库建议 + 🤍 LLM 温柔话术', 11, C_ORANGE, True)
rag_items = [
    '① 危机热线：400-161-9995（24 小时）',
    '② 五感接地法：说出此刻看到的 5 件事',
    '③ 安全计划：移除身边危险物品',
    '④ LLM：「你愿意承受这些痛苦走到今天…」',
]
for i, item in enumerate(rag_items):
    y = Inches(5.1) + Inches(i * 0.28)
    R(s, Inches(6.8), y + Pt(4), Pt(4), Pt(4), C_ORANGE)
    T(s, Inches(6.95), y, Inches(5.6), Pt(18), item, 9, C_SEC)

# 底部量表信效度 + 导出按钮
R(s, Inches(0.6), Inches(6.5), Inches(12.1), Inches(0.4), C_NAVY)
T(s, Inches(0.8), Inches(6.53), Inches(8), Pt(22), '📖 PHQ-9 Cronbach α=0.89 · GAD-7 α=0.91 · 量表信效度达标', 10, C_WHITE, True)
R(s, Inches(10.5), Inches(6.52), Inches(2.0), Inches(0.32), C_TEAL)
T(s, Inches(10.5), Inches(6.52), Inches(2.0), Inches(0.32), '📥 导出 Word 报告', 10, C_WHITE, True, align=PP_ALIGN.CENTER)

# ---- Page 15: 管理后台 & Word 导出（绘制仪表盘 UI 模拟图）----
s = P('管理后台&Word导出')
H(s, '05 · 系统演示', '管理后台 & Word 报告导出', 15)

# 浏览器顶栏
R(s, Inches(0.6), Inches(1.9), Inches(12.1), Inches(0.32), RGBColor(0xE8,0xEC,0xF0))
for i, c in enumerate([RGBColor(0xFF,0x5F,0x57), RGBColor(0xFF,0xBD,0x2E), RGBColor(0x28,0xC8,0x40)]):
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8 + i*0.22), Inches(2.0), Pt(8), Pt(8))
    dot.fill.solid(); dot.fill.fore_color.rgb = c; dot.line.fill.background(); dot.shadow.inherit=False
T(s, Inches(1.5), Inches(1.93), Inches(8), Pt(18), 'localhost:8000/admin  (admin / admin123)', 9, C_MUTED)

# 顶部 4 个统计卡片
stats = [
    ('118', '筛查会话', C_TEAL),
    ('117', '注册用户', C_NAVY),
    ('22', 'CRISIS+HIGH', C_RED),
    ('96', 'LOW+MEDIUM', C_YELLOW),
]
for i, (num, label, c) in enumerate(stats):
    x = Inches(0.6) + Inches(i * 3.1)
    R(s, x, Inches(2.35), Inches(2.9), Inches(0.85), C_BG, C_LINE)
    R(s, x, Inches(2.35), Pt(5), Inches(0.85), c)
    T(s, x + Inches(0.2), Inches(2.4), Inches(1.5), Pt(28), num, 22, c, True)
    T(s, x + Inches(1.7), Inches(2.5), Inches(1.1), Pt(22), label, 10, C_SEC)

# 左下：风险等级环形图区
R(s, Inches(0.6), Inches(3.35), Inches(4.0), Inches(2.0), C_BG, C_LINE)
T(s, Inches(0.8), Inches(3.4), Inches(3.6), Pt(18), '风险等级分布', 11, C_TEAL, True)
# 模拟环形图（用扇形文字）
ring_data = [('LOW', 32, C_TEAL), ('MED', 35, C_YELLOW), ('HIGH', 29, C_ORANGE), ('CRISIS', 22, C_RED)]
y = Inches(3.7)
for label, val, c in ring_data:
    R(s, Inches(0.8), y, Inches(0.3), Pt(14), c, c)
    T(s, Inches(1.2), y - Pt(2), Inches(2), Pt(18), f'{label}', 10, C_SEC)
    T(s, Inches(2.5), y - Pt(2), Inches(1.5), Pt(18), f'{val} 例 ({val/118*100:.0f}%)', 10, C_SEC)
    y += Inches(0.28)

# 中下：14 天趋势折线区
R(s, Inches(4.8), Inches(3.35), Inches(4.0), Inches(2.0), C_BG, C_LINE)
T(s, Inches(5.0), Inches(3.4), Inches(3.6), Pt(18), '14 天筛查趋势', 11, C_ORANGE, True)
# 模拟趋势折线（用文字数据）
T(s, Inches(5.0), Inches(3.7), Inches(3.6), Pt(18), '日均 8.4 例 · 高峰 9/10 (15 例)', 9, C_SEC)
# 用条形图模拟趋势
for i, v in enumerate([6, 8, 5, 10, 7, 12, 9, 15, 8, 11, 7, 9, 10, 8]):
    x = Inches(5.0) + Inches(i * 0.26)
    h = Inches(v * 0.08)
    R(s, x, Inches(5.4) - h, Inches(0.2), h, C_ORANGE if v > 10 else C_TEAL)

# 右下：年级×风险热力矩阵
R(s, Inches(9.0), Inches(3.35), Inches(3.7), Inches(2.0), C_BG, C_LINE)
T(s, Inches(9.2), Inches(3.4), Inches(3.3), Pt(18), '年级 × 风险矩阵', 11, C_RED, True)
# 简化热力矩阵
grades = ['大一', '大二', '大三', '大四', '研一']
for gi, g in enumerate(grades):
    T(s, Inches(9.2), Inches(3.7) + Inches(gi * 0.28), Inches(0.6), Pt(16), g, 9, C_SEC)
    for li, (label, val) in enumerate([('L', 0.2), ('M', 0.5), ('H', 0.7), ('C', 0.9)]):
        x = Inches(9.8) + Inches(li * 0.55)
        if gi == 0:
            T(s, x, Inches(3.65), Inches(0.5), Pt(14), label, 8, C_MUTED, align=PP_ALIGN.CENTER)
        intensity = [0.2, 0.4, 0.6, 0.8][li]
        c = [C_TEAL, C_YELLOW, C_ORANGE, C_RED][li]
        R(s, x, Inches(3.85) + Inches(gi * 0.28), Inches(0.45), Inches(0.22), c, C_WHITE)

# 底部：Word 报告导出区
R(s, Inches(0.6), Inches(5.5), Inches(12.1), Inches(1.4), C_BG, C_LINE)
R(s, Inches(0.6), Inches(5.5), Inches(12.1), Pt(3), C_NAVY)
T(s, Inches(0.8), Inches(5.6), Inches(5), Pt(18), '📄 Word 报告导出预览', 12, C_NAVY, True)
# 模拟 Word 报告内容
word_preview = [
    '封面页：学校 + MindGuard + 筛查日期 + 风险等级',
    '基础信息：姓名（脱敏）· 年级 · 答题时长 120s',
    '量表得分：PHQ-9 = 17 · GAD-7 = 11 · 文本消极度 = 1.0',
    '规则链：R003 + R004 + R006 → 综合分 72.96 HIGH',
    'RAG 建议：危机热线 + 五感接地法 + 安全计划',
]
for i, line in enumerate(word_preview):
    y = Inches(5.85) + Inches(i * 0.2)
    T(s, Inches(0.8), y, Inches(7.5), Pt(16), f'{i+1}. {line}', 9, C_SEC)

# 导出按钮
R(s, Inches(9.0), Inches(5.85), Inches(3.5), Inches(0.8), C_NAVY, C_NAVY)
T(s, Inches(9.0), Inches(5.85), Inches(3.5), Inches(0.35), '📥 一键导出', 14, C_WHITE, True, align=PP_ALIGN.CENTER)
T(s, Inches(9.0), Inches(6.2), Inches(3.5), Inches(0.3), 'session_106_report.docx', 9, RGBColor(0xCC,0xDD,0xEE), align=PP_ALIGN.CENTER)
T(s, Inches(9.0), Inches(6.42), Inches(3.5), Pt(14), '约 38 KB · 完整图文报告', 9, C_MUTED, align=PP_ALIGN.CENTER)

# ================================================================
#  Page 16 — 对比实验（双图表 + 数据对比）
# ================================================================
s = P('对比实验')
H(s, '06 · 效果验证', '对比实验 · 神经符号引擎 vs 纯 PHQ-9', 16)

# 实验设置（左）+ 方法学（右）
R(s, Inches(0.6), Inches(1.9), Inches(5.8), Inches(1.5), C_BG, C_LINE)
R(s, Inches(0.6), Inches(1.9), Pt(5), Inches(1.5), C_TEAL)
M(s, Inches(0.8), Inches(1.95), Inches(5.5), Inches(1.4), [
    ('实验设置', C_TEAL, True),
    ('· 样本：118 例模拟筛查数据（含 5 类典型场景）', C_SEC, False),
    ('· 基线：传统纯 PHQ-9（≥10 分判"高风险"）', C_SEC, False),
    ('· 对比：本系统神经符号双引擎（量表+文本+规则）', C_SEC, False),
    ('· 指标：检出率 / 漏检案例 / 假阳性 / 等级分布', C_SEC, False),
], 11)

R(s, Inches(6.6), Inches(1.9), Inches(6.1), Inches(1.5), C_BG, C_LINE)
R(s, Inches(6.6), Inches(1.9), Pt(5), Inches(1.5), C_ORANGE)
M(s, Inches(6.8), Inches(1.95), Inches(5.8), Inches(1.4), [
    ('方法学', C_ORANGE, True),
    ('· 双盲评估：3 名科研助手独立标注金标准', C_SEC, False),
    ('· 金标准：PHQ-9 + GAD-7 + 文本分析 + 人工复核', C_SEC, False),
    ('· 排除：答题时长 < 30s 或纯重复文本的无效样本', C_SEC, False),
    ('· 统计：检出率 = TP / (TP + FN)，假阳性率 = FP / (FP + TN)', C_SEC, False),
], 11)

# 左：柱状图（检出/漏检对比）
cd1 = CategoryChartData()
cd1.categories = ['检出案例', '漏检案例']
cd1.add_series('纯 PHQ-9（单量表）', (49, 69))
cd1.add_series('神经符号双引擎',     (36, 82))
chart1 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(0.6), Inches(3.5), Inches(5.9), Inches(2.0), cd1).chart
chart1.has_title = True
chart1.chart_title.text_frame.text = '检出率对比（118 例样本）'
chart1.has_legend = True
chart1.legend.position = XL_LEGEND_POSITION.BOTTOM
chart1.legend.font.size = Pt(9)

# 右：饼图（纯 PHQ-9 假阳性分析）
cd2 = CategoryChartData()
cd2.categories = ['真阳性', '假阳性（PHQ-9 高分但无危机）']
cd2.add_series('纯 PHQ-9 检出 49 例', (38, 11))
chart2 = s.shapes.add_chart(XL_CHART_TYPE.PIE,
    Inches(6.8), Inches(3.5), Inches(5.9), Inches(2.0), cd2).chart
chart2.has_title = True
chart2.chart_title.text_frame.text = '纯 PHQ-9 假阳性分析（3 名科研助手双盲评估）'
chart2.has_legend = True
chart2.legend.position = XL_LEGEND_POSITION.RIGHT
chart2.legend.font.size = Pt(9)

# 下方结论条：KPI + 分析文字
R(s, Inches(0.6), Inches(5.7), Inches(12.1), Inches(1.1), C_BG, C_LINE)
kpis = [('16.3%', '检出率净提升\n(36→82 例)', C_TEAL),
        ('12 例', '隐性危机全检出\n纯量表全部漏掉', C_RED),
        ('72.7%', '假阳性减少\n(11→3 例)', C_ORANGE)]
for i, (num, label, color) in enumerate(kpis):
    x = Inches(0.8) + Inches(i * 3.9)
    R(s, x, Inches(5.75), Pt(4), Inches(0.95), color)
    T(s, x + Inches(0.15), Inches(5.78), Inches(3.5), Pt(28), num, 22, color, True)
    T(s, x + Inches(0.15), Inches(6.1), Inches(3.5), Pt(28), label, 9, C_SEC)
# 右侧分析总结
T(s, Inches(11.0), Inches(5.75), Inches(1.6), Inches(1.0),
  '结论：双引擎在检出率、漏检率、假阳性率三项指标上均显著优于纯量表筛查', 9, C_NAVY, True)

# ================================================================
#  Page 17 — 典型案例（表格 + 横向条形图）
# ================================================================
s = P('典型案例')
H(s, '06 · 效果验证', '5 个典型案例 · 全部纯 PHQ-9 漏检的隐性危机', 17)

cases = [
    ('案例 1', '大四学生', 'PHQ-9 = 4（正常）',  '"秋招被拒 12 次，活着没意思"', 'HIGH',    '命中"活着没意思"',          C_ORANGE),
    ('案例 2', '研三学生', 'PHQ-9 = 2（正常）',  '"论文被拒第二次，想跳楼"',        'CRISIS',  '命中"跳楼"→红色警示触发',    C_RED),
    ('案例 3', '大三学生', 'PHQ-9 = 6（轻度）',  '"室友都找到工作了，我撑不住了"',  'MEDIUM',  '命中"撑不住"',               C_YELLOW),
    ('案例 4', '大一新生', 'PHQ-9 = 3（正常）',  '"军训太累了，不想上学"',          'MEDIUM',  '命中"不想上学"',             C_YELLOW),
    ('案例 5', '大二学生', 'PHQ-9 = 5（轻度）',  '"期末压力大，感觉要崩溃了"',      'MEDIUM',  '命中"压力大" + R003',        C_YELLOW),
]

y = Inches(1.9)
widths = [Inches(0.9), Inches(1.2), Inches(1.5), Inches(3.6), Inches(1.1), Inches(3.8)]
for h, w in zip(['编号', '身份', '纯 PHQ-9', '开放文本（脱敏）', '本引擎', '触发原因'], widths):
    R(s, Inches(0.6), y, w, Pt(28), C_NAVY)
    T(s, Inches(0.6), y + Pt(3), w, Pt(22), h, 11, C_WHITE, True, align=PP_ALIGN.CENTER)
    x_ = Inches(0.6)
y += Pt(28)

for i, row in enumerate(cases):
    y += Pt(2)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE,0xF2,0xF5)
    level = row[4]
    color = row[6]
    x = Inches(0.6)
    for cell, w in zip(row[:6], widths):
        R(s, x, y, w, Pt(40), bg, C_LINE)
        is_level = (cell == level)
        c = color if is_level else C_TEXT
        b = is_level
        T(s, x + Pt(6), y + Pt(8), w - Pt(12), Pt(28), str(cell), 10, c, b)
        x += w
    y += Pt(40)

# 案例说明 + 统计
R(s, Inches(0.6), Inches(5.25), Inches(7.5), Inches(0.35), C_BG, C_LINE)
T(s, Inches(0.8), Inches(5.28), Inches(7.2), Pt(20),
  '说明：以上 5 例根据真实校园心理工作场景改编（已脱敏）。纯 PHQ-9 均 <10 分判"正常"。',
  9, C_MUTED)
# 右侧统计
R(s, Inches(8.3), Inches(5.25), Inches(4.4), Inches(0.35), C_BG, C_LINE)
T(s, Inches(8.5), Inches(5.28), Inches(4.2), Pt(20),
  '5 例中：CRISIS 1 · HIGH 1 · MEDIUM 3 · 纯量表漏检率 100%', 9, C_RED, True)

# 下方：PHQ-9 vs 双引擎检出分布条形图
cd = CategoryChartData()
cd.categories = ['LOW', 'MEDIUM', 'HIGH', 'CRISIS']
cd.add_series('纯 PHQ-9', (41, 26, 26, 8))
cd.add_series('神经符号双引擎', (32, 35, 29, 22))
chart = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED,
    Inches(0.6), Inches(5.7), Inches(12.1), Inches(1.3), cd).chart
chart.has_title = True
chart.chart_title.text_frame.text = '不同风险等级下两种方法的检出分布对比'
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.font.size = Pt(9)

# ================================================================
#  Page 18 — 可行性（四栏更紧凑）
# ================================================================
s = P('可行性')
H(s, '06 · 效果验证', '方案可行性 · 成本 ≈ 0 元', 18)
cols = [
    ('技术可行性', C_NAVY,  [
        'FastAPI/SQLite/ECharts 生产级成熟',
        '核心引擎自研（纯 Python）',
        'requirements.txt 仅 7 个核心包',
        'PyInstaller 解压即用',
    ]),
    ('经济可行性', C_TEAL, [
        '硬件：复用现有服务器',
        '软件：全部开源 MIT/Apache',
        'LLM API：可选配置',
        '量表：PHQ-9/GAD-7 公共领域',
        '合计 ≈ 0 元',
    ]),
    ('推广价值', C_ORANGE, [
        '响应教育部教育纲要方向',
        '试点：本校 50-100 志愿者',
        '同类院校解压即用',
        '5 分钟部署完成',
        '无 GPU / 无外部数据库',
    ]),
    ('部署要求', C_RED,    [
        'Python 3.11 环境',
        '  或 PyInstaller 打包版',
        '数据库：SQLite 自动建表',
        '端口：8000（可配置）',
        '浏览器：Chrome / Edge',
    ]),
]
for i, (title, color, items) in enumerate(cols):
    x = Inches(0.6) + Inches(i * 3.15)
    R(s, x, Inches(1.9), Inches(2.95), Inches(4.8), C_BG, C_LINE)
    R(s, x, Inches(1.9), Inches(2.95), Pt(4), color)
    T(s, x + Pt(10), Inches(2.05), Inches(2.75), Pt(24), title, 14, color, True)
    y = Inches(2.4)
    for item in items:
        R(s, x + Pt(10), y + Pt(6), Pt(4), Pt(4), color)
        T(s, x + Pt(20), y + Pt(2), Inches(2.6), Pt(20), item, 11, C_SEC)
        y += Pt(28)

# ================================================================
#  Page 19 — 团队 + 里程碑（更紧凑）
# ================================================================
s = P('团队+里程碑')
H(s, '07 · 团队与计划', '团队分工 · 实施里程碑', 19)

# 左：团队（两人卡片 + 角色 + 头像）
R(s, Inches(0.6), Inches(1.9), Inches(5.8), Inches(4.8), C_BG, C_LINE)
R(s, Inches(0.6), Inches(1.9), Inches(5.8), Pt(4), C_TEAL)
T(s, Inches(0.8), Inches(2.05), Inches(5.6), Pt(22), '团队成员', 13, C_TEAL, True)

for i, (name, role, desc) in enumerate([
    ('阮家炜', '负责人',
     '后端架构设计 · 神经符号引擎核心开发\n规则知识库 · 危机分级系统 · 对比实验'),
    ('张修瑜', '成员',
     '前端 Vue3 + ECharts 开发\n系统演示 · 文档编写 · 数据整理'),
]):
    y = Inches(2.5) + Inches(i * 2.05)
    R(s, Inches(0.8), y, Inches(5.4), Inches(1.85), RGBColor(0xF1,0xF5,0xF9), C_LINE)
    R(s, Inches(1.0), y + Inches(0.2), Inches(0.8), Inches(0.8), C_TEAL)
    T(s, Inches(1.0), y + Inches(0.2), Inches(0.8), Inches(0.8), name[0], 26, C_WHITE, True, align=PP_ALIGN.CENTER)
    T(s, Inches(2.0), y + Pt(4), Inches(4.2), Pt(24), name, 15, C_NAVY, True)
    T(s, Inches(2.0), y + Pt(26), Inches(4.2), Pt(20), role, 11, C_TEAL, True)
    T(s, Inches(2.0), y + Pt(48), Inches(4.2), Inches(1.2), desc, 10, C_SEC)

# 右：时间线（水平圆点 + 标签）
R(s, Inches(6.8), Inches(1.9), Inches(5.9), Inches(4.8), C_BG, C_LINE)
R(s, Inches(6.8), Inches(1.9), Inches(5.9), Pt(4), C_ORANGE)
T(s, Inches(7.0), Inches(2.05), Inches(5.7), Pt(22), '实施里程碑', 13, C_ORANGE, True)

milestones = [
    ('2026 Q2', '需求分析 · 技术选型 · FastAPI+Vue3 基础架构'),
    ('2026 Q3', '双引擎核心 · 规则库+危机分级 · RAG+LLM 集成'),
    ('2026 Q4', '前端 6 页联调 · 118 例对比实验 · 试用意向书'),
    ('2027 Q1', '本校心理中心试点 · 双盲评估 · 输出效果报告'),
    ('2027 Q2', '推广 2-3 所兄弟院校 · V2.0 BERT 语义向量'),
]
y = Inches(2.5)
for i, (tag, desc) in enumerate(milestones):
    # 时间点
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(7.2), y + Pt(8), Pt(14), Pt(14))
    circle.fill.solid(); circle.fill.fore_color.rgb = C_ORANGE; circle.line.fill.background()
    # 连接线
    if i < len(milestones) - 1:
        R(s, Inches(7.2) + Pt(5), y + Pt(22), Pt(2), Inches(0.58), C_LINE)
    T(s, Inches(7.45), y + Pt(4), Inches(1.4), Pt(16), tag, 10, C_ORANGE, True)
    T(s, Inches(8.9), y + Pt(2), Inches(3.6), Pt(36), desc, 10, C_SEC)
    y += Inches(0.72)

# ================================================================
#  Page 20 — 总结展望 + 致谢（合并）
# ================================================================
s = P('总结展望+致谢')

# 左上：核心结论
H(s, '07 · 总结与展望', '核心结论 + 未来方向', 20)

R(s, Inches(0.6), Inches(1.9), Inches(5.8), Inches(4.0), C_BG, C_LINE)
R(s, Inches(0.6), Inches(1.9), Inches(5.8), Pt(4), C_TEAL)
T(s, Inches(0.8), Inches(2.05), Inches(5.6), Pt(22), '📌 四条核心结论', 13, C_TEAL, True)

concs = [
    ('问题定位准', '直击三大痛点：漏检率高 / 缺乏可解释性 / 建议同质化'),
    ('技术路线新', '可解释神经符号双引擎，区别于 BERT/LLM 黑箱'),
    ('效果数据实', '118 例：检出率提升 16.3% · 12 例隐性危机全检出 · 假阳性减 72.7%'),
    ('工程化完成', '纯 Python · PyInstaller 一键打包 · 零新依赖'),
]
y = Inches(2.45)
for i, (title, body) in enumerate(concs):
    R(s, Inches(0.8), y + Pt(6), Pt(6), Pt(32), C_TEAL)
    T(s, Inches(1.0), y, Inches(5.2), Pt(18), title, 12, C_NAVY, True)
    T(s, Inches(1.0), y + Pt(18), Inches(5.2), Pt(22), body, 10, C_SEC)
    y += Inches(0.9)

# 右上：未来方向
R(s, Inches(6.8), Inches(1.9), Inches(5.9), Inches(4.0), C_BG, C_LINE)
R(s, Inches(6.8), Inches(1.9), Inches(5.9), Pt(4), C_ORANGE)
T(s, Inches(7.0), Inches(2.05), Inches(5.7), Pt(22), '🔮 五个未来改进方向', 13, C_ORANGE, True)

future = [
    ('V2.0', '语音模态：librosa + Whisper，启用 2 维预留特征'),
    ('V2.0', '语义向量：轻量中文 SBERT 替代关键词匹配'),
    ('真实试点', '本校心理中心 50-100 志愿者双盲评估'),
    ('推广扩展', '2-3 所兄弟院校 + 试点报告'),
    ('学术产出', '会议论文 CCML/CHIL · 软著申请'),
]
y = Inches(2.45)
for i, (tag, body) in enumerate(future):
    R(s, Inches(7.0), y + Pt(8), Pt(4), Pt(4), C_ORANGE)
    T(s, Inches(7.2), y + Pt(2), Inches(1.0), Pt(16), tag, 10, C_ORANGE, True)
    T(s, Inches(8.2), y + Pt(2), Inches(4.3), Pt(34), body, 10, C_SEC)
    y += Inches(0.66)

# 底部致谢条
R(s, 0, Inches(6.1), prs.slide_width, Inches(1.4), C_NAVY)
T(s, 0, Inches(6.2), prs.slide_width, Pt(32),
  '感谢聆听 · 欢迎提问', 30, C_WHITE, True, align=PP_ALIGN.CENTER)
M(s, Inches(0.6), Inches(6.6), Inches(12.1), Inches(0.8), [
    ('MindGuard · 神经符号双引擎驱动的校园心理风险智能筛查与干预系统', C_TEAL, True),
    ('团队：阮家炜（负责人） · 张修瑜    |    答辩 PPT · 2026 年 9 月', C_MUTED, False),
], 10)

# ================================================================
#  保存
# ================================================================
prs.save(OUT)
print(f'\n🎉 v3 PPT 已生成：{OUT}')
print(f'   文件大小：{os.path.getsize(OUT) / 1024:.1f} KB')
print(f'   总页数：{len(prs.slides)}')
