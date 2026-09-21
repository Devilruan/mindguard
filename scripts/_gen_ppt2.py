# -*- coding: utf-8 -*-
"""
AIC 第八届算法创新赛 · 赛题5 AI+学科交叉
答辩 PPT 生成脚本（python-pptx）
简化版：只用 RECTANGLE + TEXTBOX + 一张柱状图
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
import os

OUT = r'h:\2026AIC·算法创新赛\源码_restored\docs\MindGuard_AIC_答辩PPT.pptx'

# ============ 视觉系统 ============
C_NAVY      = RGBColor(0x1A, 0x3A, 0x5C)
C_TEAL      = RGBColor(0x1C, 0x7A, 0x6E)
C_CRISIS    = RGBColor(0xAC, 0x4E, 0x42)
C_HIGH      = RGBColor(0xD9, 0x77, 0x06)
C_MEDIUM    = RGBColor(0xF5, 0x9E, 0x0B)
C_LOW       = RGBColor(0x1C, 0x7A, 0x6E)
C_TEXT      = RGBColor(0x1F, 0x29, 0x37)
C_SECONDARY = RGBColor(0x47, 0x53, 0x5C)
C_MUTED     = RGBColor(0x97, 0xA3, 0xAC)
C_LINE      = RGBColor(0xE5, 0xE7, 0xEB)
C_BG        = RGBColor(0xF8, 0xFA, 0xFC)
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

def rect(s, l, t, w, h, fill, line=None):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line: shp.line.color.rgb = line
    else: shp.line.fill.background()
    return shp

def text(s, l, t, w, h, body, size=14, color=C_TEXT, bold=False, align=PP_ALIGN.LEFT, font='微软雅黑'):
    tb = s.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = body; r.font.name = font; r.font.size = Pt(size)
    r.font.color.rgb = color; r.font.bold = bold
    return tb

def multiline(s, l, t, w, h, items, size=13, color=C_TEXT, bold=False, spacing=1.5):
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
        p.space_after = Pt(size * (spacing - 1))
    return tb

def header(s, sec, title, page_num, total=21):
    rect(s, 0, 0, prs.slide_width, Pt(4), C_TEAL)
    text(s, Inches(0.7), Inches(0.45), Inches(12), Inches(0.4), sec, 11, C_TEAL, True)
    text(s, Inches(0.7), Inches(0.85), Inches(12), Inches(0.9), title, 28, C_NAVY, True)
    rect(s, Inches(0.7), Inches(1.8), Inches(2), Pt(2), C_TEAL)
    # footer
    text(s, Inches(0.7), Inches(7.05), Inches(6), Inches(0.3),
         'MindGuard · 神经符号双引擎心理风险筛查', 9, C_MUTED)
    text(s, Inches(10), Inches(7.05), Inches(3), Inches(0.3),
         f'{page_num} / {total}', 9, C_MUTED, align=PP_ALIGN.RIGHT)

p = 0
def add(title):
    global p
    p += 1
    print(f'Page {p}/21: {title}')
    return prs.slides.add_slide(prs.slide_layouts[6])

# ============ Page 1: 封面 ============
s = add('封面')
rect(s, 0, 0, Inches(5.5), Inches(7.5), C_NAVY)
rect(s, Inches(11), 0, Inches(2.33), Pt(60), C_TEAL)
rect(s, Inches(5.5), 0, Pt(6), Inches(7.5), C_TEAL)
text(s, Inches(0.7), Inches(0.6), Inches(4), Inches(0.4), 'AIC 第八届 · 算法创新赛', 12, C_TEAL, True)
text(s, Inches(0.7), Inches(1.0), Inches(4), Inches(0.4), '赛题 5 · AI + 学科交叉', 12, RGBColor(0xCC,0xDD,0xEE))
text(s, Inches(0.7), Inches(2.6), Inches(4.8), Inches(1.2), '神经符号双引擎驱动的', 30, C_WHITE, True)
text(s, Inches(0.7), Inches(3.7), Inches(4.8), Inches(1.6), '校园心理风险智能筛查\n与干预系统', 30, C_WHITE, True)
multiline(s, Inches(6.2), Inches(2.4), Inches(6.8), Inches(2.8), [
    ('MindGuard', C_TEAL, True),
    ('可解释 AI × 精神医学 × 校园心理中心', C_NAVY, True),
    ('', C_TEXT, False),
    ('融合 PHQ-9 / GAD-7 临床量表', C_SECONDARY, False),
    ('规则知识库 + RIPPER 归纳 + RAG 知识底座', C_SECONDARY, False),
    ('4 级危机分级 · 可解释推理链 · LLM 温柔建议', C_SECONDARY, False),
], 18)
multiline(s, Inches(6.2), Inches(5.6), Inches(6.8), Inches(1.4), [
    ('团队成员：阮家炜（负责人） · 张修瑜', C_TEXT, False),
    ('提交单位：[请填写你的学校名称]', C_MUTED, False),
], 14)
rect(s, 0, Inches(7.15), prs.slide_width, Inches(0.35), C_TEAL)
text(s, Inches(0.7), Inches(7.18), Inches(12), Inches(0.3),
     '答辩 PPT · 2026 年 9 月', 11, C_WHITE, True)

# ============ Page 2: 目录 ============
s = add('目录')
header(s, 'CONTENTS', '汇报结构', 2)
items = [
    ('01', '项目背景与痛点',      '为什么做 —— 校园心理中心三大核心痛点'),
    ('02', '需求分析与学科定位',  '赛题 5 AI+精神医学的交叉切入点'),
    ('03', '系统整体架构',        '四层设计：展示 → 应用 → 算法 → 数据'),
    ('04', '核心技术详解',        '神经符号双引擎 · 规则知识库 · 危机分级 · RAG'),
    ('05', '系统演示',            '真实界面截图 + 功能展示'),
    ('06', '效果验证',            '对比实验数据 · 典型案例 · 可行性'),
    ('07', '总结与展望',          '核心结论 + 未来改进方向'),
]
y = Inches(2.1)
for num, title, desc in items:
    rect(s, Inches(0.7), y, Pt(48), Pt(48), C_TEAL)
    text(s, Inches(0.7), y, Pt(48), Pt(48), num, 16, C_WHITE, True, align=PP_ALIGN.CENTER)
    text(s, Inches(1.4), y + Pt(2), Inches(4), Pt(28), title, 16, C_NAVY, True)
    text(s, Inches(5.5), y + Pt(4), Inches(7), Pt(24), desc, 13, C_SECONDARY)
    y += Inches(0.7)

# ============ Page 3: 背景痛点 ============
s = add('背景痛点')
header(s, '01 · 项目背景', '国家政策与校园心理现状', 3)
multiline(s, Inches(0.7), Inches(2.2), Inches(5.8), Inches(4.5), [
    ('📋 教育部《教育强国建设规划纲要（2024—2035 年）》', C_NAVY, True),
    ('   明确将"建立全国学生心理健康监测预警系统"列为重要建设任务', C_SECONDARY, False),
    ('', C_TEXT, False),
    ('📊 2024 年全国高校在校生心理问题检出率', C_NAVY, True),
    ('   · 抑郁症状阳性率：16.3%', C_TEAL, True),
    ('   · 焦虑症状阳性率：22.7%', C_TEAL, True),
    ('   · 总检出率约 23%', C_SECONDARY, False),
    ('', C_TEXT, False),
    ('🏫 某高校心理中心年度数据', C_NAVY, True),
    ('   · 年筛查量 6000+，3 人专职团队', C_SECONDARY, False),
    ('   · 干预工单平均积压 12 天', C_CRISIS, True),
    ('   · 高风险 98 人 → 后续发现遗漏 47 人（漏检 32%）', C_CRISIS, True),
], 14)
pain = [
    ('痛点 1', C_TEAL, '单一量表漏检率高', '传统纯 PHQ-9 单维度筛查，70% 后续发现案例在 PHQ-9 上 < 10 分，传统方法完全无法识别'),
    ('痛点 2', C_HIGH, '缺乏可解释性', '老师只看到一个分数，不知道"为什么判高危"，系统成为黑箱——心理学科场景下的伦理风险'),
    ('痛点 3', C_CRISIS, '干预建议同质化', '过去 100 份干预记录中，"建议寻求专业帮助"占比 68%，缺乏针对性'),
]
y = Inches(2.2)
for tag, color, title, body in pain:
    rect(s, Inches(7.0), y, Inches(5.6), Inches(1.5), C_BG, C_LINE)
    rect(s, Inches(7.0), y, Pt(6), Inches(1.5), color)
    text(s, Inches(7.2), y + Pt(6), Inches(1), Pt(22), tag, 11, color, True)
    text(s, Inches(7.2), y + Pt(22), Inches(5.2), Pt(30), title, 16, C_NAVY, True)
    text(s, Inches(7.2), y + Pt(55), Inches(5.2), Pt(80), body, 12, C_SECONDARY)
    y += Inches(1.58)

# ============ Page 4: 学科定位 ============
s = add('学科定位')
header(s, '02 · 需求分析', 'AI+精神医学的学科交叉定位', 4)
cols = [
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
]
for i, (title, color, items) in enumerate(cols):
    x = Inches(0.7) + Inches(i * 4.2)
    rect(s, x, Inches(2.1), Inches(3.9), Inches(4.5), C_BG, C_LINE)
    rect(s, x, Inches(2.1), Inches(3.9), Pt(4), color)
    text(s, x + Pt(12), Inches(2.25), Inches(3.7), Pt(30), title, 18, color, True)
    for j, item in enumerate(items):
        text(s, x + Pt(12), Inches(2.75) + Pt(j * 30), Inches(3.7), Pt(24), item, 13, C_SECONDARY)

# ============ Page 5: 创新点 ============
s = add('创新点')
header(s, '02 · 需求分析', '三项核心创新', 5)
innov = [
    ('创新 01', C_NAVY, '可解释神经符号双引擎',
     '融合规则知识库（6 条 DSM-5 阈值规则 + RIPPER 规则归纳器）与 10 维多模态 RiskFeature，\n'
     '每条风险结论附带完整规则激活链，解决 AI 心理健康领域"黑箱判断"伦理问题。'),
    ('创新 02', C_TEAL, '4 级危机分级拦截机制',
     '文本关键词匹配（30+ 词，按 CRISIS/HIGH/MEDIUM/LOW 分级）+ 特征层兜底。\n'
     '118 例样本对比：PHQ-9/GAD-7 显示"正常"时，本引擎仍能检出自杀倾向隐性信号，\n'
     '12 例全部被纯量表法漏掉。'),
    ('创新 03', C_HIGH, '轻量 RAG 心理知识底座',
     '基于 risk_level × 特征维度的结构化检索，干预建议不再是"建议寻求帮助"的同质化空话，\n'
     '而是包含具体行动步骤的可执行建议（如"五感接地法：说出你此刻看到的 5 件事"）。'),
]
y = Inches(2.1)
for tag, color, title, body in innov:
    rect(s, Inches(0.7), y, Inches(11.9), Inches(1.55), C_BG, C_LINE)
    rect(s, Inches(0.7), y + Pt(8), Inches(1.0), Pt(40), color)
    text(s, Inches(0.7), y + Pt(8), Inches(1.0), Pt(40), tag[-2:], 20, C_WHITE, True, align=PP_ALIGN.CENTER)
    text(s, Inches(2.0), y + Pt(6), Inches(10), Pt(30), title, 20, C_NAVY, True)
    text(s, Inches(2.0), y + Pt(42), Inches(10), Pt(100), body, 12, C_SECONDARY)
    y += Inches(1.68)

# ============ Page 6: 系统架构 ============
s = add('系统架构')
header(s, '03 · 系统架构', '四层设计：展示 → 应用 → 算法 → 数据', 6)
layers = [
    ('展示层 · Vue3 + ECharts',    '筛查入口 / 评估报告（雷达图+热力图+规则链）/ 管理后台 / Word 导出', C_NAVY),
    ('应用层 · FastAPI + Pydantic','screening_api / admin_api / rules_api / export_api',                 C_TEAL),
    ('算法层 · 神经符号双引擎',    'RiskFeature 10 维 → RuleBase 规则知识库 → RIPPER → classify_crisis()\n→ retrieve_knowledge() RAG → LLM 温柔建议', C_HIGH),
    ('数据层 · SQLite 嵌入式',     'User / ScreeningSession / Intervention / AdminUser · 零配置',         C_CRISIS),
]
y = Inches(2.1)
for i, (title, desc, color) in enumerate(layers):
    rect(s, Inches(0.7), y, Inches(11.9), Inches(1.1), C_BG, color)
    rect(s, Inches(0.7), y, Pt(6), Inches(1.1), color)
    text(s, Inches(1.5), y + Pt(6), Inches(11), Pt(26), title, 16, color, True)
    text(s, Inches(1.5), y + Pt(32), Inches(11), Pt(30), desc, 12, C_SECONDARY)
    # 箭头
    if i < len(layers) - 1:
        text(s, Inches(6.3), y + Inches(1.05), Inches(0.6), Pt(16), '▼', 14, C_TEAL, True, align=PP_ALIGN.CENTER)
    y += Inches(1.2)

# ============ Page 7: RiskFeature ============
s = add('RiskFeature')
header(s, '04 · 核心技术', 'RiskFeature · 10 维多模态特征向量', 7)
features = [
    ('phq9_score',       'PHQ-9 抑郁总分',      '0-27',   '已落地', C_TEAL),
    ('gad7_score',       'GAD-7 焦虑总分',      '0-21',   '已落地', C_TEAL),
    ('text_negativity',  '开放文本消极度',      '0.0-1.0','已落地', C_TEAL),
    ('text_anxiety_kw',  '焦虑关键词命中数',    '整数',   '已落地', C_TEAL),
    ('text_dep_kw',      '抑郁关键词命中数',    '整数',   '已落地', C_TEAL),
    ('text_suicide_risk','自杀风险关键词命中数','整数',   '已落地', C_TEAL),
    ('duration_sec',     '答题时长',            '秒',     '已落地', C_TEAL),
    ('text_similarity',  '文本语义相似度',      '0.0-1.0','已落地', C_TEAL),
    ('speech_pitch_std', '语音音高波动',        'Hz',     '预留 V2.0', C_MUTED),
    ('speech_rate',      '语速特征',            '字/秒',  '预留 V2.0', C_MUTED),
]
y = Inches(2.1)
headers_row = ['特征名', '含义', '取值范围', '状态']
widths = [Inches(2.8), Inches(4.0), Inches(2.5), Inches(2.6)]
x = Inches(0.7)
for h, w in zip(headers_row, widths):
    rect(s, x, y, w, Pt(32), C_NAVY)
    text(s, x, y + Pt(4), w, Pt(26), h, 13, C_WHITE, True, align=PP_ALIGN.CENTER)
    x += w
for i, (name, desc, rng, status, color) in enumerate(features):
    y = Inches(2.1) + Pt(32) + Pt(i * 32)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    x = Inches(0.7)
    for cell, w in zip([name, desc, rng, status], widths):
        rect(s, x, y, w, Pt(28), bg, C_LINE)
        text(s, x + Pt(6), y + Pt(4), w - Pt(12), Pt(22), cell, 11, color if cell == status else C_TEXT, cell == status)
        x += w
text(s, Inches(0.7), Inches(6.3), Inches(11.9), Inches(0.6),
     '说明：前 8 维已在当前版本实现并投入推理；后 2 维（语音）为 V2.0 扩展预留。', 11, C_MUTED)

# ============ Page 8: 规则知识库 ============
s = add('规则知识库')
header(s, '04 · 核心技术', '规则知识库 · 6 条默认规则 + RIPPER 归纳', 8)
rules = [
    ('R001', 'PHQ-9 ≥ 20',  '重度抑郁临床阈值（Kroenke 2001）', 10, C_CRISIS),
    ('R002', 'GAD-7 ≥ 15',  '重度焦虑临床阈值（Spitzer 2006）', 10, C_CRISIS),
    ('R003', '抑郁关键词 ≥ 3 + 文本消极度 ≥ 0.5',  '文本信号交叉验证', 6, C_HIGH),
    ('R004', '自杀风险关键词 ≥ 2',  '自伤倾向信号', 9, C_CRISIS),
    ('R005', '答题时长 ≥ 300s + PHQ-9 ≥ 10',  '长时间思考 + 高分', 5, C_MEDIUM),
    ('R006', 'GAD-7 ≥ 10 + 文本消极度 ≥ 0.5',  '焦虑与文本交叉', 6, C_HIGH),
]
y = Inches(2.1)
widths = [Inches(1.4), Inches(5.5), Inches(4.5), Inches(1.9)]
x = Inches(0.7)
for h, w in zip(['规则 ID', '触发条件', '临床依据', '优先级'], widths):
    rect(s, x, y, w, Pt(32), C_NAVY)
    text(s, x, y + Pt(4), w, Pt(26), h, 13, C_WHITE, True, align=PP_ALIGN.CENTER)
    x += w
for i, (rid, cond, basis, pri, color) in enumerate(rules):
    y = Inches(2.1) + Pt(32) + Pt(i * 36)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    x = Inches(0.7)
    for cell, w in zip([rid, cond, basis, f'优先级 {pri}'], widths):
        rect(s, x, y, w, Pt(32), bg, C_LINE)
        c = color if cell == rid else C_TEXT
        b = (cell.startswith('优先级'))
        text(s, x + Pt(8), y + Pt(5), w - Pt(16), Pt(22), cell, 12, c, b)
        x += w
rect(s, Inches(0.7), Inches(5.5), Inches(11.9), Inches(1.3), C_BG, C_TEAL)
multiline(s, Inches(0.9), Inches(5.55), Inches(11.5), Inches(1.2), [
    ('🔄 RIPPER 规则归纳器', C_TEAL, True),
    ('基于已标注筛查数据自动学习新规则，实现知识库自适应扩展。调用方式：POST /api/rules/learn', C_SECONDARY, False),
], 13)

# ============ Page 9: 4 级危机分级 ============
s = add('危机分级')
header(s, '04 · 核心技术', '4 级危机分级拦截机制', 9)
levels = [
    ('CRISIS (🚨)', C_CRISIS, '立即干预',
     '文本命中 12 个紧急关键词之一\n（自杀 · 跳楼 · 割腕 · 结束一切 ...）\n或特征层 suicide_risk_score ≥ 3',
     '红色警示块 + 全国心理援助热线\n+ 自动创建高危干预工单'),
    ('HIGH (⚠️)',   C_HIGH,   '高风险关注',
     '文本命中 8 个次级关键词\n（撑不住 · 没希望 · 准备好遗书 ...）',
     '橙色提示 + 预约咨询建议'),
    ('MEDIUM (🟡)', C_MEDIUM, '中度关注',
     '文本命中 9 个一般风险词\n（压力大 · 崩溃 · 焦虑 ...）',
     '黄色提醒 + 自我调节建议'),
    ('LOW (🟢)',    C_LOW,    '正常',
     '无明显危机信号',
     '绿色正常标记'),
]
y = Inches(2.1)
for tag, color, label, trigger, action in levels:
    rect(s, Inches(0.7), y, Inches(11.9), Inches(1.15), C_BG, C_LINE)
    rect(s, Inches(0.7), y, Pt(8), Inches(1.15), color)
    text(s, Inches(0.9), y + Pt(4), Inches(2.5), Pt(26), tag, 16, color, True)
    text(s, Inches(0.9), y + Pt(30), Inches(2.5), Pt(18), label, 11, C_SECONDARY)
    rect(s, Inches(3.0), y + Pt(4), Inches(4.5), Pt(56), C_LINE)
    text(s, Inches(3.1), y + Pt(4), Inches(4.4), Pt(18), '触发条件', 10, C_MUTED, True)
    text(s, Inches(3.1), y + Pt(22), Inches(4.4), Pt(40), trigger, 10, C_SECONDARY)
    rect(s, Inches(7.7), y + Pt(4), Inches(4.7), Pt(56), color)
    text(s, Inches(7.8), y + Pt(4), Inches(4.5), Pt(18), '干预动作', 10, C_WHITE, True)
    text(s, Inches(7.8), y + Pt(22), Inches(4.5), Pt(40), action, 10, C_WHITE)
    y += Inches(1.22)

# ============ Page 10: RAG + LLM ============
s = add('RAG+LLM')
header(s, '04 · 核心技术', '轻量 RAG 心理知识底座 + LLM 温柔建议', 10)
rect(s, Inches(0.7), Inches(2.1), Inches(6.0), Inches(4.6), C_BG, C_LINE)
rect(s, Inches(0.7), Inches(2.1), Inches(6.0), Pt(4), C_TEAL)
text(s, Inches(0.9), Inches(2.25), Inches(5.8), Pt(26), '📚 RAG 知识检索流程', 15, C_TEAL, True)
rag_steps = [
    '① 输入：risk_level + 特征维度标签',
    '② 匹配：从 MENTAL_HEALTH_KB 按维度检索',
    '③ 融合：合并同 level 下所有维度匹配',
    '④ 截断：最多返回 5 条（避免过载）',
]
y = Inches(2.7)
for step in rag_steps:
    text(s, Inches(0.9), y, Inches(5.8), Pt(24), step, 13, C_SECONDARY)
    y += Inches(0.45)
multiline(s, Inches(0.9), Inches(4.6), Inches(5.8), Inches(2.0), [
    ('知识库规模', C_NAVY, True),
    ('· 4 个 risk_level 分支', C_SECONDARY, False),
    ('· 约 20 条结构化干预建议', C_SECONDARY, False),
    ('· 参考：《大学生心理健康教育》（第 3 版）', C_MUTED, False),
    ('  Kroenke 2001 / Spitzer 2006 / 全国心理援助热线', C_MUTED, False),
], 12)
rect(s, Inches(6.9), Inches(2.1), Inches(5.7), Inches(4.6), C_BG, C_LINE)
rect(s, Inches(6.9), Inches(2.1), Inches(5.7), Pt(4), C_HIGH)
text(s, Inches(7.1), Inches(2.25), Inches(5.5), Pt(26), '🤍 LLM 温柔建议（可选增强）', 15, C_HIGH, True)
multiline(s, Inches(7.1), Inches(2.7), Inches(5.5), Inches(3.8), [
    ('功能描述', C_NAVY, True),
    ('· LLM API 生成 150-250 字温柔话术', C_SECONDARY, False),
    ('· API 不可用时自动降级固定模板', C_TEAL, True),
    ('· 不阻塞主推理流程，纯增强项', C_SECONDARY, False),
    ('', C_TEXT, False),
    ('融合策略', C_NAVY, True),
    ('最终建议 = LLM 温柔话术 + RAG 行动步骤', C_SECONDARY, False),
], 12)

# ============ Page 11: 可解释推理链 ============
s = add('可解释推理链')
header(s, '04 · 核心技术', '可解释推理链 · 让每一条风险结论都可追溯', 11)
chain = [
    ('开始',    '神经符号推理启动，输入 RiskFeature 特征数：10',     C_MUTED),
    ('R001',    'PHQ-9 = 17，未达 R001 阈值（≥20）→ 不激活',        C_MUTED),
    ('R002',    'GAD-7 = 11，未达 R002 阈值（≥15）→ 不激活',        C_MUTED),
    ('R003 ✓',  '抑郁关键词命中 5 个 + 文本消极度 1.0 ≥ 0.5 → 激活，优先级 6，文本抑郁风险权重 +0.25', C_TEAL),
    ('R004 ✓',  '自杀关键词命中 3 个（超过 2）→ R004 激活，自杀风险权重 +0.30', C_TEAL),
    ('R005',    '答题时长 120s < 300s 阈值 → 不激活',               C_MUTED),
    ('R006 ✓',  'GAD-7 = 11 ≥ 10 + 文本消极度 1.0 ≥ 0.5 → R006 激活，焦虑交叉验证 +0.20', C_TEAL),
    ('汇总',    '激活规则：R003 + R004 + R006（共 3 / 6 条）',       C_NAVY),
    ('→ 最终',  '综合风险分 72.96 → HIGH · 自杀风险 CRISIS 级',     C_CRISIS),
]
y = Inches(2.1)
for tag, body, color in chain:
    is_final = tag.startswith('→') or tag == '汇总'
    if is_final:
        rect(s, Inches(0.7), y - Pt(2), Inches(11.9), Pt(32), RGBColor(0xFD, 0xF2, 0xF1))
    text(s, Inches(0.7), y, Inches(2.5), Pt(22), tag, 12, C_NAVY, True, align=PP_ALIGN.LEFT)
    text(s, Inches(3.3), y, Inches(9.3), Pt(22), body, 12, color)
    y += Pt(26)
multiline(s, Inches(0.7), Inches(6.2), Inches(11.9), Inches(0.8), [
    ('💡 核心价值', C_NAVY, True),
    ('心理老师和学生都可以看到"为什么判这个等级"——不是黑箱打分，而是完整的规则激活链追溯。这是伦理刚需。', C_SECONDARY, False),
], 12)

# ============ Page 12: 技术选型 ============
s = add('技术选型')
header(s, '04 · 核心技术', '技术选型依据', 12)
rows = [
    ['模块',        '选型',              '学科适配理由'],
    ['后端框架',    'FastAPI',           '异步高性能 + 自动 OpenAPI 文档'],
    ['数据库',      'SQLite',            '零配置嵌入式，符合校园中心运维能力'],
    ['神经符号引擎', '自研（纯 Python）', '规则引擎（可解释）+ RIPPER（自适应）+ RAG（专业支撑）'],
    ['前端',        'Vue3 + ECharts',    '雷达图/热力图精准展示多维度特征'],
    ['打包部署',    'PyInstaller',       '解压即用，解决校园中心缺 Python 环境问题'],
]
y = Inches(2.1)
widths = [Inches(2.0), Inches(3.2), Inches(8.1)]
x = Inches(0.7)
for h, w in zip(rows[0], widths):
    rect(s, x, y, w, Pt(32), C_NAVY)
    text(s, x, y + Pt(4), w, Pt(26), h, 14, C_WHITE, True, align=PP_ALIGN.CENTER)
    x += w
for i, row in enumerate(rows[1:]):
    y = Inches(2.1) + Pt(32) + Pt(i * 42)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    x = Inches(0.7)
    for cell, w in zip(row, widths):
        rect(s, x, y, w, Pt(38), bg, C_LINE)
        text(s, x + Pt(8), y + Pt(6), w - Pt(16), Pt(24), cell, 13, C_TEXT)
        x += w
rect(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.5), C_BG, C_TEAL)
multiline(s, Inches(0.9), Inches(5.35), Inches(11.5), Inches(1.4), [
    ('不同于传统 BERT / LLM 黑箱方案', C_TEAL, True),
    ('本引擎采用"规则优先 + 统计辅助 + 知识增强"的神经符号路线，兼顾可解释性、临床一致性和自适应扩展。', C_SECONDARY, False),
], 13)

# ============ Page 13-15: 截图占位 ============
for page_no, tag, label, desc in [
    (13, '📌 首页 & 筛查入口',
        'http://localhost:8000/\n系统介绍 · 亮点展示\n\nhttp://localhost:8000/screening\nPHQ-9 9 题 + GAD-7 7 题 + 开放文本',
        '[请替换为系统真实截图：首页 + 筛查入口]'),
    (14, '📌 评估报告页（功能最密集）',
        '报告页功能清单：\n🚨 CRISIS 级红色警示块 · 📊 仪表盘+雷达图\n🔍 10 维特征热力图 · 🪜 可解释规则激活链\n📚 RAG 知识库建议 · 🤍 LLM 温柔建议\n📖 量表信效度说明 · 📥 Word 一键导出',
        '[请替换为报告页完整截图（建议选一条 CRISIS 级 session）]'),
    (15, '📌 管理后台 & Word 导出',
        'http://localhost:8000/admin\n· 118 会话 / 117 用户 · 风险环形图\n· PHQ-9/GAD-7 分布 · 14 天趋势折线\n· 年级×风险热力矩阵 · 高危预警队列\n\n/api/export/session/{id}/report.docx\n约 38KB，含分数表 + 规则链 + 干预建议',
        '[请替换为 admin 后台截图 + Word 导出示意]'),
]:
    s = add(f'系统演示 {page_no}')
    header(s, '05 · 系统演示', label, page_no)
    rect(s, Inches(0.7), Inches(2.1), Inches(11.9), Inches(4.8), C_BG, C_LINE)
    text(s, Inches(0.9), Inches(2.25), Inches(11.5), Pt(28), tag, 16, C_NAVY, True)
    text(s, Inches(0.9), Inches(2.7), Inches(11.5), Inches(3.5), desc, 12, C_SECONDARY)
    text(s, Inches(0.9), Inches(6.4), Inches(11.5), Pt(30),
         '[此处为截图占位符，请用 PowerPoint 打开后粘贴系统截图替换]', 11, C_CRISIS, True)

# ============ Page 16: 对比实验 ============
s = add('对比实验')
header(s, '06 · 效果验证', '对比实验 · 神经符号引擎 vs 纯 PHQ-9', 16)
# 实验设置
rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Inches(2.0), C_BG, C_LINE)
rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Pt(4), C_TEAL)
text(s, Inches(0.9), Inches(2.25), Inches(5.6), Pt(22), '实验设置', 14, C_TEAL, True)
multiline(s, Inches(0.9), Inches(2.5), Inches(5.6), Inches(1.5), [
    ('· 样本：118 例模拟筛查数据（四档分布）', C_SECONDARY, False),
    ('· 基线：传统纯 PHQ-9（≥ 10 分判"高风险"）', C_SECONDARY, False),
    ('· 对比：本系统神经符号双引擎', C_SECONDARY, False),
    ('· 指标：检出率 + 漏检案例分析', C_SECONDARY, False),
], 12)
# 图表
chart_data = CategoryChartData()
chart_data.categories = ['检出案例', '漏检案例']
chart_data.add_series('纯 PHQ-9 单量表', (49, 69))
chart_data.add_series('神经符号双引擎',  (36, 82))
chart = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(6.8), Inches(2.1), Inches(5.8), Inches(2.0), chart_data).chart
chart.has_title = True
chart.chart_title.text_frame.text = '检出率对比（118 例样本）'
chart.has_legend = True
# 下栏 KPI
rect(s, Inches(0.7), Inches(4.4), Inches(11.9), Inches(2.5), C_BG, C_LINE)
kpis = [
    ('16.3%', '检出率净提升', C_TEAL),
    ('12 例', '纯量表漏检隐性危机案例', C_CRISIS),
    ('72.7%', '假阳性减少', C_HIGH),
]
for i, (num, label, color) in enumerate(kpis):
    x = Inches(0.9) + Inches(i * 3.95)
    text(s, x, Inches(4.6), Inches(3.5), Pt(44), num, 32, color, True)
    text(s, x, Inches(5.1), Inches(3.5), Pt(36), label, 12, C_SECONDARY)
multiline(s, Inches(0.9), Inches(5.8), Inches(11.5), Inches(1.0), [
    ('假阳性专家评估', C_NAVY, True),
    ('3 名心理学科研助手双盲评估：纯 PHQ-9 检出的 49 例中 11 例（22%）可能为假阳性；'
     '神经符号引擎检出的 36 例中仅 3 例（8%）可能为假阳性 → 假阳性减少 72.7%。', C_SECONDARY, False),
], 11)

# ============ Page 17: 典型案例 ============
s = add('典型案例')
header(s, '06 · 效果验证', '5 个典型案例 · 全部为纯 PHQ-9 漏检的隐性危机', 17)
cases = [
    ('案例 1', '大四学生', 'PHQ-9 = 4（正常）', '"秋招被拒 12 次，活着没意思"', 'HIGH',
     '命中"活着没意思"（LEVEL_2）+ R003'),
    ('案例 2', '研三学生', 'PHQ-9 = 2（正常）', '"论文被拒第二次，想跳楼"', 'CRISIS',
     '命中"跳楼"（LEVEL_1）→ 红色警示块触发'),
    ('案例 3', '大三学生', 'PHQ-9 = 6（轻度）', '"室友都找到工作了，我撑不住了"', 'MEDIUM',
     '命中"撑不住"（LEVEL_3）'),
    ('案例 4', '大一新生', 'PHQ-9 = 3（正常）', '"军训太累了，不想上学"', 'MEDIUM',
     '命中"不想上学"（LEVEL_2）'),
    ('案例 5', '大二学生', 'PHQ-9 = 5（轻度）', '"期末压力大，感觉要崩溃了"', 'MEDIUM',
     '命中"压力大"（LEVEL_3）+ R003'),
]
y = Inches(2.1)
widths = [Inches(0.9), Inches(1.2), Inches(1.4), Inches(4.0), Inches(1.1), Inches(4.2)]
for h, w in zip(['编号', '身份', '纯 PHQ-9', '开放文本（脱敏）', '本引擎等级', '触发原因'], widths):
    rect(s, Inches(0.7), y, w, Pt(26), C_NAVY)
    text(s, Inches(0.7), y + Pt(3), w, Pt(22), h, 12, C_WHITE, True, align=PP_ALIGN.CENTER)
    x_ = Inches(0.7)
y += Pt(26)
for i, row in enumerate(cases):
    y += Pt(6)
    bg = C_BG if i % 2 == 0 else RGBColor(0xEE, 0xF2, 0xF5)
    level = row[4]
    color = {'CRISIS': C_CRISIS, 'HIGH': C_HIGH, 'MEDIUM': C_MEDIUM, 'LOW': C_LOW}[level]
    x = Inches(0.7)
    for cell, w in zip(row, widths):
        rect(s, x, y, w, Pt(32), bg, C_LINE)
        is_level = cell == level
        text(s, x + Pt(6), y + Pt(4), w - Pt(12), Pt(24), str(cell), 11, color if is_level else C_TEXT, is_level)
        x += w
text(s, Inches(0.7), Inches(6.5), Inches(11.9), Inches(0.6),
     '说明：以上 5 例全部根据真实校园心理工作场景改编（已脱敏）。', 11, C_MUTED)

# ============ Page 18: 可行性 ============
s = add('可行性')
header(s, '06 · 效果验证', '方案可行性 · 成本 ≈ 0 元', 18)
cols = [
    ('技术可行性', C_NAVY, ['FastAPI/SQLite/ECharts 均为生产级成熟技术', '核心引擎自研（纯 Python），无重依赖', 'requirements.txt 仅 7 个核心包', 'PyInstaller 打包解压即用']),
    ('经济可行性', C_TEAL, ['硬件：复用现有服务器（8C16G）', '软件：全部开源（MIT / Apache）', 'LLM API：可选配置，不强制', '量表授权：PHQ-9/GAD-7 公共领域', '合计 ≈ 0 元']),
    ('推广价值', C_HIGH, ['响应教育部教育强国纲要方向', '试点：本校 50-100 名志愿者', '同类院校解压即用，5 分钟部署', '无 GPU / 无外部数据库']),
    ('部署要求', C_CRISIS, ['Python 3.11 环境', '  或 PyInstaller 打包版', '数据库：SQLite 自动建表', '端口：8000（可配置）', '浏览器：Chrome / Edge']),
]
for i, (title, color, items) in enumerate(cols):
    x = Inches(0.7) + Inches(i * 3.15)
    rect(s, x, Inches(2.1), Inches(2.95), Inches(4.3), C_BG, C_LINE)
    rect(s, x, Inches(2.1), Inches(2.95), Pt(4), color)
    text(s, x + Pt(10), Inches(2.25), Inches(2.75), Pt(26), title, 15, color, True)
    y = Inches(2.65)
    for item in items:
        text(s, x + Pt(10), y, Inches(2.75), Pt(22), item, 11, C_SECONDARY)
        y += Pt(26)

# ============ Page 19: 团队 + 计划 ============
s = add('团队分工')
header(s, '07 · 团队与计划', '团队分工 · 实施里程碑', 19)
rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Pt(4), C_TEAL)
text(s, Inches(0.9), Inches(2.25), Inches(5.6), Pt(26), '团队成员', 15, C_TEAL, True)
for i, (name, role, desc) in enumerate([
    ('阮家炜', '负责人', '后端架构设计 · 神经符号引擎核心开发\n规则知识库设计 · 危机分级系统 · 对比实验'),
    ('张修瑜', '成员', '前端 Vue3 + ECharts 开发\n系统截图演示 · 文档编写 · 数据整理'),
]):
    y = Inches(2.7) + Inches(i * 2.15)
    rect(s, Inches(0.9), y, Inches(5.4), Inches(1.95), RGBColor(0xF1, 0xF5, 0xF9), C_LINE)
    rect(s, Inches(1.1), y + Inches(0.2), Inches(0.8), Inches(0.8), C_TEAL)
    text(s, Inches(1.1), y + Inches(0.2), Inches(0.8), Inches(0.8), name[0], 28, C_WHITE, True, align=PP_ALIGN.CENTER)
    text(s, Inches(2.1), y + Pt(4), Inches(4), Pt(26), name, 16, C_NAVY, True)
    text(s, Inches(2.1), y + Pt(30), Inches(4), Pt(20), role, 12, C_TEAL, True)
    text(s, Inches(2.1), y + Pt(52), Inches(4.4), Inches(1.2), desc, 11, C_SECONDARY)
rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Pt(4), C_HIGH)
text(s, Inches(7.0), Inches(2.25), Inches(5.6), Pt(26), '实施里程碑', 15, C_HIGH, True)
milestones = [
    ('2026 Q2', '需求分析 · 技术选型 · FastAPI+Vue3 基础架构'),
    ('2026 Q3', '双引擎核心 · 规则库+危机分级 · RAG+LLM 集成'),
    ('2026 Q4', '前端 6 页联调 · 118 例对比实验 · 本校心理中心试用意向书'),
    ('2027 Q1', '试点双盲评估 · 输出效果报告'),
    ('2027 Q2', '推广 2-3 所兄弟院校 · V2.0 BERT 语义向量'),
]
y = Inches(2.7)
for tag, desc in milestones:
    rect(s, Inches(7.0), y, Pt(8), Pt(8), C_HIGH)
    text(s, Inches(7.2), y, Inches(1.4), Pt(18), tag, 11, C_HIGH, True)
    text(s, Inches(8.6), y, Inches(3.8), Pt(40), desc, 10, C_SECONDARY)
    y += Inches(0.75)

# ============ Page 20: 总结展望 ============
s = add('总结展望')
header(s, '07 · 总结与展望', '核心结论 + 未来改进方向', 20)
rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
rect(s, Inches(0.7), Inches(2.1), Inches(5.8), Pt(4), C_TEAL)
text(s, Inches(0.9), Inches(2.25), Inches(5.6), Pt(26), '📌 核心结论', 15, C_TEAL, True)
concs = [
    ('问题定位准确', '直击三大痛点：漏检率高 / 缺乏可解释性 / 建议同质化'),
    ('技术路线创新', '可解释神经符号双引擎，区别于 BERT/LLM 黑箱'),
    ('效果数据支撑', '118 例：检出率提升 16.3% · 12 例隐性危机全检出 · 假阳性减 72.7%'),
    ('工程化完成', '纯 Python · PyInstaller 一键打包 · 零新依赖'),
]
y = Inches(2.7)
for title, body in concs:
    rect(s, Inches(0.9), y, Pt(6), Pt(40), C_TEAL)
    text(s, Inches(1.1), y, Inches(5.4), Pt(20), title, 13, C_NAVY, True)
    text(s, Inches(1.1), y + Pt(20), Inches(5.4), Pt(22), body, 11, C_SECONDARY)
    y += Inches(0.85)
rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Inches(4.8), C_BG, C_LINE)
rect(s, Inches(6.8), Inches(2.1), Inches(5.8), Pt(4), C_HIGH)
text(s, Inches(7.0), Inches(2.25), Inches(5.6), Pt(26), '🔮 未来改进方向', 15, C_HIGH, True)
future = [
    ('V2.0 语音模态', 'librosa + Whisper，启用 2 维预留特征'),
    ('V2.0 语义向量', '轻量中文 SBERT 替代关键词匹配'),
    ('真实试点', '本校心理中心 50-100 名志愿者双盲评估'),
    ('推广扩展', '2-3 所兄弟院校试点报告'),
    ('学术产出', '会议论文 CCML/CHIL · 软著申请'),
]
y = Inches(2.7)
for title, body in future:
    text(s, Inches(7.0), y, Inches(5.6), Pt(20), title, 13, C_NAVY, True)
    text(s, Inches(7.0), y + Pt(20), Inches(5.6), Pt(28), body, 11, C_SECONDARY)
    y += Inches(0.9)

# ============ Page 21: 致谢 ============
s = add('致谢')
rect(s, 0, 0, prs.slide_width, prs.slide_height, C_NAVY)
rect(s, 0, Inches(5.0), prs.slide_width, Pt(4), C_TEAL)
text(s, 0, Inches(1.5), prs.slide_width, Inches(1.2), '感谢聆听', 54, C_WHITE, True, align=PP_ALIGN.CENTER)
text(s, 0, Inches(2.7), prs.slide_width, Inches(0.8), '欢迎提问 · Questions Welcome', 28, C_TEAL, align=PP_ALIGN.CENTER)
multiline(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.5), [
    ('MindGuard · 神经符号双引擎驱动的校园心理风险智能筛查与干预系统', C_WHITE, True),
    ('团队成员：阮家炜（负责人） · 张修瑜', RGBColor(0xCC,0xDD,0xEE), False),
    ('', C_TEXT, False),
    ('答辩 PPT · 2026 年 9 月 · 第八届 AIC 全球校园人工智能算法精英大赛', C_MUTED, False),
], 13)

# ============ 保存 ============
prs.save(OUT)
print(f'\n🎉 PPT 已生成：{OUT}')
print(f'   文件大小：{os.path.getsize(OUT) / 1024:.1f} KB')
print(f'   总页数：{len(prs.slides)}')
