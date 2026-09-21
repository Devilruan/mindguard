# -*- coding: utf-8 -*-
"""把技术方案.md 转为规范排版 docx（宋体/小四/标题层级），供转 PDF 使用"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import re, os

SRC = r'H:\2026AIC·算法创新赛\源码_restored\docs\技术方案.md'
OUT = r'C:\Users\24974\AppData\Local\Temp\tech_plan_s5.docx'

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# 页面设置：A4，页边距 2.5/2.5/3/3
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.5)
sec.left_margin = sec.right_margin = Cm(3.0)

def set_font(run, size=12, bold=False, cn_font='宋体'):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), cn_font)

def add_para(text, style='body', size=12):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text)
    if style == 'h1':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_font(r, 16, True, '黑体')
    elif style == 'h2':
        set_font(r, 14, True, '黑体')
    elif style == 'h3':
        set_font(r, 12, True, '黑体')
    elif style == 'body':
        set_font(r, size, False, '宋体')
    elif style == 'note':
        set_font(r, 10, False, '楷体')
    return p

def add_table(rows):
    """rows: list of list[str]"""
    tbl = doc.add_table(rows=len(rows), cols=len(rows[0]))
    tbl.style = 'Table Grid'
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            c = tbl.cell(i, j)
            c.text = ''
            p = c.paragraphs[0]
            r = p.add_run(str(cell))
            set_font(r, 10, i == 0, '宋体')
            if i == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return tbl

import unicodedata

def clean_xml(s):
    """去掉 XML 非法控制字符"""
    return ''.join(ch for ch in s if ch == '\n' or ch == '\t' or unicodedata.category(ch) != 'Cc' and (ord(ch) >= 32 or ch in '\n\t'))

with open(SRC, encoding='utf-8') as f:
    raw = f.read()
# 读取时已有部分控制字符损坏（如 \b 显示为 ackend），修正明显的
raw = raw.replace('\u0008', 'b').replace('\u000b', '\n').replace('\u000c', '\n')
lines = [clean_xml(l) for l in raw.split('\n')]
# 修复退格符导致的单词损坏（ackend→backend, etrieve→retrieve, 等）
fixed_lines = []
for l in lines:
    l2 = l.replace('ackend/core', 'backend/core')
    l2 = l2.replace('etrieve_knowledge', 'retrieve_knowledge')
    l2 = l2.replace('ackend', 'backend')
    l2 = l2.replace('etrieve', 'retrieve')
    # 清理孤立控制残留
    l2 = ''.join(ch for ch in l2 if ch == '\n' or ch == '\t' or ord(ch) >= 32)
    fixed_lines.append(l2)
lines = fixed_lines

# 打开表格后继续处理
i = 0
in_code = False
while i < len(lines):
    line = lines[i].rstrip()
    s = line.strip()

    if s.startswith('```'):
        in_code = not in_code
        if in_code:
            add_para('代码区：', 'note')
        i += 1
        continue
    if in_code:
        p = doc.add_paragraph()
        r = p.add_run(s)
        set_font(r, 9, False, 'Consolas')
        p.paragraph_format.space_after = Pt(0)
        i += 1
        continue

    # 表格：连续 | 行
    if s.startswith('|') and s.endswith('|') and i + 1 < len(lines) and '---' in lines[i+1]:
        header = [c.strip() for c in s.strip('|').split('|')]
        rows = [header]
        i += 2  # 跳过分隔行
        while i < len(lines) and lines[i].strip().startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            rows.append(cells)
            i += 1
        if len(rows) > 1:
            add_table(rows)
        i -= 1
        i += 1
        continue

    if not s:
        i += 1
        continue

    if s.startswith('## '):
        add_para(s[3:], 'h2')
    elif s.startswith('### '):
        add_para(s[4:], 'h3')
    elif s.startswith('# '):
        add_para(s[2:], 'h1')
    elif s.startswith('- '):
        add_para(s[2:], 'body', 11)
    elif re.match(r'^\d+\.\s', s):
        add_para(s, 'body', 11)
    elif s.startswith('|'):
        pass  # 单行表格忽略
    else:
        add_para(s, 'body')
    i += 1

doc.save(OUT)
print(f'✅ 技术方案 docx 已生成: {OUT} ({os.path.getsize(OUT)} bytes)')
print(f'   段落数约 {len(doc.paragraphs)}')