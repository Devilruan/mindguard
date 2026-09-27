# -*- coding: utf-8 -*-
"""
backend.api.features_api
新增功能 API：每日一句、心情打卡、CBT 认知扭曲、风险预测、PDF 报告、紧急联系人
"""
from __future__ import annotations
import json
import math
import random
import io
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.database import (
    SessionLocal, User, ScreeningSession, Intervention,
    MoodJournal, EmergencyContact, get_db,
)

log = logging.getLogger(__name__)
router = APIRouter()


# ══════════════════════════════════════════════
# #2 每日一句心理格言
# ══════════════════════════════════════════════

DAILY_AFFIRMATIONS = [
    ('你今天的感受是真实的，也是重要的。', '自我接纳'),
    ('情绪没有对错，它只是你内心的一个信号。', '情绪觉察'),
    ('慢慢来，你不需要一下子解决所有问题。', '减压'),
    ('已经撑到今天了，这本身就很了不起。', '自我肯定'),
    ('允许自己偶尔休息，不是偷懒，是必要的充电。', '自我关怀'),
    ('你不需要对所有人的情绪负责，只对自己的负责就好。', '边界'),
    ('困难的日子不代表永远困难，它只是今天很难。', '希望'),
    ('找一件今天发生的小事，哪怕很小，让它成为你继续的理由。', '积极行动'),
    ('深呼吸，你此刻是安全的。', '接地技术'),
    ('承认自己的脆弱，比假装坚强更需要勇气。', '勇气'),
    ('你值得被好好对待，包括被你自己好好对待。', '自我价值'),
    ('不完美不是你的缺陷，它是让你成为你的独特之处。', '自我接纳'),
    ('有时候，允许自己"什么都不做"就是最好的自愈。', '休息'),
    ('焦虑是身体在提醒你需要照顾自己了，不是你的敌人。', '情绪理解'),
    ('你不必独自承担一切，寻求帮助是智慧，不是软弱。', '求助'),
    ('今天的你比昨天多了解了自己一点，这就是进步。', '成长'),
    ('没有哪一种情绪会永远持续，包括现在让你难受的这个。', '希望'),
    ('你存在本身就有意义，不需要用成就来证明。', '自我价值'),
    ('把"我应该"换成"我可以"，世界会轻松很多。', '认知重构'),
    ('允许自己不被所有人喜欢，这是自由的开始。', '边界'),
    ('哭不是软弱，是内心在清理空间。', '情绪释放'),
    ('你正在经历的，许多人也经历过，你不是孤单的。', '连接感'),
    ('一小步行动胜过一千句焦虑的想法。', '行动'),
    ('善待自己就像善待一个你在乎的朋友。', '自我关怀'),
    ('今天，我选择对自己温柔一点。', '自我接纳'),
]


@router.get('/daily-affirmation')
def get_daily_affirmation(date: Optional[str] = None):
    """返回基于日期哈希的"每日一句"，同一天所有人看到相同的，第二天自动刷新。"""
    if not date:
        date = datetime.utcnow().strftime('%Y-%m-%d')
    seed = hash(date) % 10000
    idx = seed % len(DAILY_AFFIRMATIONS)
    text, category = DAILY_AFFIRMATIONS[idx]
    return {
        'date': date,
        'text': text,
        'category': category,
    }


# ══════════════════════════════════════════════
# #4 心情快速打卡 / 日记
# ══════════════════════════════════════════════

class MoodEntry(BaseModel):
    anon_id: str
    mood_score: float          # 1-10
    emotion: str                # happy/calm/anxious/sad/angry/empty
    text: Optional[str] = None


@router.post('/mood-journal')
def add_mood(payload: MoodEntry, db: Session = Depends(get_db)):
    entry = MoodJournal(
        anon_id=payload.anon_id,
        mood_score=payload.mood_score,
        emotion=payload.emotion,
        text=payload.text,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {'id': entry.id, 'created_at': entry.created_at.isoformat()}


@router.get('/mood-journal/{anon_id}')
def get_moods(anon_id: str, limit: int = 60, db: Session = Depends(get_db)):
    entries = (
        db.query(MoodJournal)
        .filter(MoodJournal.anon_id == anon_id)
        .order_by(MoodJournal.created_at.desc())
        .limit(limit)
        .all()
    )
    records = [
        {
            'id': e.id,
            'mood_score': e.mood_score,
            'emotion': e.emotion,
            'text': e.text,
            'created_at': e.created_at.isoformat(),
        }
        for e in entries
    ]
    # 趋势预测：线性回归
    trend = None
    if len(records) >= 3:
        recent = records[:14]
        xs = list(range(len(recent)))
        ys = [r['mood_score'] for r in reversed(recent)]
        trend = _linear_regression_predict(xs, ys)
    return {'records': records, 'prediction': trend}


def _linear_regression_predict(xs, ys, days_ahead: int = 7):
    """最小二乘线性回归，返回未来 N 天的预测分数。"""
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if den == 0:
        return None
    slope = num / den
    intercept = mean_y - slope * mean_x
    predictions = []
    for i in range(n, n + days_ahead):
        score = intercept + slope * i
        score = max(1.0, min(10.0, score))
        predictions.append(round(score, 1))
    direction = 'improving' if slope > 0.05 else ('worsening' if slope < -0.05 else 'stable')
    return {'predictions': predictions, 'direction': direction, 'slope': round(slope, 3)}


# ══════════════════════════════════════════════
# #6 认知扭曲检测 + CBT 重塑建议
# ══════════════════════════════════════════════

COGNITIVE_DISTORTIONS = [
    {
        'name': '全或无思维 (All-or-Nothing)',
        'patterns': ['总是', '从来', '每次', '所有', '完全', '百分之百', '没有一个', '无一例外'],
        'example': '我总是失败',
        'reframe': '事实：我有成功也有失败。"总是/从来"是极端化想法，大部分时候事情处于中间地带。',
    },
    {
        'name': '灾难化思维 (Catastrophizing)',
        'patterns': ['完蛋', '毁了', '彻底', '没救', '天塌', '死定', '一切都完'],
        'example': '这次考试没考好，我的人生毁了',
        'reframe': '事实：一次失败不等于人生毁灭。"灾难化"让焦虑指数级放大，但很少真的发生。',
    },
    {
        'name': '情绪推理 (Emotional Reasoning)',
        'patterns': ['我感觉我', '我觉得我', '感觉自己', '觉得自己'],
        'example': '我感觉我是个没人爱的人',
        'reframe': '事实：情绪不等于事实。"感觉"是主观的，可以改变；"事实"是客观的。',
    },
    {
        'name': '读心术 (Mind Reading)',
        'patterns': ['他们一定', '他们肯定', '他们就是', '所有人都觉得', '大家都在背后'],
        'example': '大家肯定都在背后议论我',
        'reframe': '事实：我无法知道别人在想什么。与其猜测，不如直接问——大多数人其实没那么关注我。',
    },
    {
        'name': '应该思维 (Should Statement)',
        'patterns': ['我应该', '我必须', '我一定要', '我得', '我不得不'],
        'example': '我应该完美，不应该犯任何错误',
        'reframe': '事实：把"我应该"换成"我可以试试"。高标准变成要求，就会产生自责和焦虑。',
    },
    {
        'name': '过度概括 (Overgeneralization)',
        'patterns': ['每次都', '一直都', '永远都', '全都'],
        'example': '永远没有人会真的理解我',
        'reframe': '事实：一个/几个例子不能代表全部。换一个环境、换一个时间，结果可能完全不同。',
    },
    {
        'name': '标签化 (Labeling)',
        'patterns': ['我就是个', '我是一个没用', '失败者', '废物', '没用的人', '永远不会成功'],
        'example': '我就是个失败者',
        'reframe': '事实：我做了一些失败的事 ≠ 我是一个失败者。行为可以改变，标签是永远的诅咒。',
    },
    {
        'name': '个人化 (Personalization)',
        'patterns': ['都是我的错', '因为我', '要不是我', '全怪我'],
        'example': '朋友不开心一定是因为我做错了什么',
        'reframe': '事实：别人的情绪主要是他们自己的事。我无法控制任何人的感受，只需要做好自己。',
    },
]


@router.post('/cbt-analysis')
def cbt_analysis(payload: dict):
    """对一段自由文本进行认知扭曲检测 + CBT 重塑建议。"""
    text = (payload.get('text') or '').strip()
    if not text or len(text) < 5:
        return {'distortions': [], 'summary': '请先写一句话说说你现在的感受，比如"我觉得所有人都在背后议论我"。'}

    found = []
    for d in COGNITIVE_DISTORTIONS:
        matched = [p for p in d['patterns'] if p in text]
        if matched:
            found.append({
                'name': d['name'],
                'matched_keywords': matched,
                'example': d['example'],
                'reframe': d['reframe'],
            })

    summary = ''
    if not found:
        summary = '没有检测到明显的认知扭曲，你的表达看起来比较客观。继续保持这种觉察力！'
    elif len(found) == 1:
        summary = f'检测到 {len(found)} 种可能的认知扭曲：{found[0]["name"]}。试试右边的重塑建议。'
    else:
        summary = f'检测到 {len(found)} 种可能的认知扭曲。一个一个来处理，先挑最触动你的那个开始。'

    return {
        'distortions': found,
        'summary': summary,
        'original_text': text,
    }


# ══════════════════════════════════════════════
# #3 风险等级 → 干预资源智能匹配
# ══════════════════════════════════════════════

INTERVENTION_MAP = {
    'urgent': {
        'title': '⚠️ 极高风险 · 立即行动',
        'color': '#AC4E42',
        'icon': '🚨',
        'resources': [
            {'type': 'hotline', 'name': '全国24小时心理援助热线', 'number': '12356', 'action': '立即拨打'},
            {'type': 'hotline', 'name': '北京心理危机研究与干预中心', 'number': '010-82951332', 'action': '立即拨打'},
            {'type': 'action', 'name': '告诉一个你信任的人', 'desc': '老师/朋友/家人，说一句"我需要你"就够了'},
            {'type': 'action', 'name': '3-3-3 接地练习', 'desc': '说出 3 个你看到的东西 → 3 种声音 → 3 种触摸'},
        ],
        'suggestion': '你此刻可能很痛苦，但请相信——这种痛苦是可以改变的，而且你不需要独自面对。请拨打上方热线，或者立刻联系身边的一个人。',
    },
    'high': {
        'title': '🔴 高风险 · 尽快关注',
        'color': '#C97B3A',
        'icon': '🟠',
        'resources': [
            {'type': 'hotline', 'name': '全国24小时心理援助热线', 'number': '12356', 'action': '随时拨打'},
            {'type': 'technique', 'name': '4-7-8 呼吸法', 'desc': '吸气 4 秒 → 屏息 7 秒 → 呼气 8 秒，重复 4 轮'},
            {'type': 'action', 'name': '预约学校心理咨询', 'desc': '告诉自己"这不是软弱，是在主动照顾自己"'},
            {'type': 'journal', 'name': '写下来', 'desc': '现在打开心情日记，用一句话描述此刻感受'},
        ],
        'suggestion': '你的情绪负担已经比较重了。主动寻求专业帮助是非常勇敢的决定——找一个咨询师聊聊，或者先从呼吸练习开始。',
    },
    'medium': {
        'title': '🟡 中风险 · 值得留意',
        'color': '#E6A817',
        'icon': '🟡',
        'resources': [
            {'type': 'technique', 'name': '5-4-3-2-1 接地练习', 'desc': '5个所见 → 4个所触 → 3个所听 → 2个所嗅 → 1个所尝'},
            {'type': 'action', 'name': '动一动', 'desc': '起身走 5 分钟，让身体的紧张释放'},
            {'type': 'journal', 'name': '情绪日记', 'desc': '写 3 句话：发生了什么/我感到什么/我需要什么'},
            {'type': 'breathing', 'name': '引导式呼吸', 'desc': '去呼吸训练页，跟着做 2 分钟'},
        ],
        'suggestion': '你最近可能压力不小。不需要"解决一切"，先选上面一件小事去做——哪怕只是深呼吸 2 分钟。',
    },
    'low': {
        'title': '🟢 低风险 · 继续保持',
        'color': '#1C7A6E',
        'icon': '🟢',
        'resources': [
            {'type': 'action', 'name': '每天 5 分钟觉察', 'desc': '睡前花 5 分钟记录今天最值得感恩的一件小事'},
            {'type': 'technique', 'name': '身体扫描', 'desc': '从头到脚觉察每一块肌肉，哪里紧就放松哪里'},
            {'type': 'social', 'name': '联系一个朋友', 'desc': '发条消息："最近好吗？想你了"'},
            {'type': 'habit', 'name': '规律作息', 'desc': '睡眠是情绪最好的调节器，尽量固定上床时间'},
        ],
        'suggestion': '你的心理状态目前稳定。把自我觉察变成习惯——定期回来测一测，了解自己的情绪规律。',
    },
}


@router.get('/intervention-plan/{risk_level}')
def get_intervention_plan(risk_level: str):
    """根据风险等级返回匹配的干预方案。"""
    plan = INTERVENTION_MAP.get(risk_level)
    if not plan:
        raise HTTPException(400, 'Invalid risk level')
    return plan


# ══════════════════════════════════════════════
# #14 PDF 报告下载
# ══════════════════════════════════════════════

@router.get('/pdf-report/{session_id}')
def get_pdf_report(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
    if not session:
        raise HTTPException(404, 'Session not found')
    user = db.query(User).filter(User.id == session.user_id).first()

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # 注册中文字体（如果可用）
        font_name = 'Helvetica'
        cn_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Noto Sans CJK SC']
        for cf in cn_fonts:
            try:
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                pdfmetrics.registerFont(UnicodeCIDFont(cf))
                font_name = cf
                break
            except Exception:
                continue

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('title', parent=styles['Title'], fontName=font_name, fontSize=20, spaceAfter=20, textColor=colors.HexColor('#1C7A6E'))
        h2_style = ParagraphStyle('h2', parent=styles['Heading2'], fontName=font_name, fontSize=14, spaceBefore=15, spaceAfter=8, textColor=colors.HexColor('#203248'))
        body_style = ParagraphStyle('body', parent=styles['Normal'], fontName=font_name, fontSize=11, leading=18)

        level_cn = {'urgent': '极高风险', 'high': '高风险', 'medium': '中风险', 'low': '低风险'}.get(session.overall_risk_level, session.overall_risk_level)
        level_color = {'urgent': '#AC4E42', 'high': '#C97B3A', 'medium': '#E6A817', 'low': '#1C7A6E'}.get(session.overall_risk_level, '#666')

        story = []
        story.append(Paragraph('MindGuard 心理健康风险筛查报告', title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1C7A6E')))
        story.append(Spacer(1, 20))

        # 基本信息表
        info_data = [
            ['匿名标识', user.anon_id if user else '-'],
            ['筛查时间', session.created_at.strftime('%Y-%m-%d %H:%M')],
            ['年级 / 专业', f"{user.grade or '-'} / {user.major or '-'}" if user else '-'],
            ['风险等级', f'<font color="{level_color}"><b>{level_cn}</b></font>'],
            ['综合风险分', f'{session.overall_risk_score:.2f}'],
        ]
        info_table = Table(info_data, colWidths=[120, 350])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F8F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D9E0E5')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))

        # 得分详情
        story.append(Paragraph('📊 心理测评得分', h2_style))
        score_data = [
            ['量表', '得分', '满分', '说明'],
            ['PHQ-9 抑郁', f'{session.phq9_score:.1f}', '27', '≥10 提示有抑郁症状'],
            ['GAD-7 焦虑', f'{session.gad7_score:.1f}', '21', '≥10 提示有焦虑症状'],
            ['自杀风险', f'{session.suicide_risk_score:.2f}', '1.00', '>0.5 需重点关注'],
            ['综合风险', f'{session.overall_risk_score:.2f}', '1.00', '神经符号引擎综合评估'],
        ]
        score_table = Table(score_data, colWidths=[100, 60, 60, 250])
        score_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1C7A6E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D9E0E5')),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 15))

        # 神经符号推理
        if session.activated_rules:
            story.append(Paragraph('🧠 神经符号推理触发规则', h2_style))
            try:
                rules = json.loads(session.activated_rules)
                for r in rules[:10]:
                    story.append(Paragraph(f'• {r}', body_style))
            except Exception:
                story.append(Paragraph(str(session.activated_rules)[:500], body_style))
            story.append(Spacer(1, 10))

        # 干预建议
        plan = INTERVENTION_MAP.get(session.overall_risk_level, {})
        story.append(Paragraph('💡 个性化干预建议', h2_style))
        if plan.get('suggestion'):
            story.append(Paragraph(plan['suggestion'], body_style))
        if plan.get('resources'):
            story.append(Spacer(1, 5))
            for r in plan['resources']:
                emoji = {'hotline': '📞', 'technique': '🧘', 'action': '✨', 'journal': '📝', 'breathing': '🌬️', 'social': '💬', 'habit': '⏰'}.get(r['type'], '•')
                story.append(Paragraph(f'{emoji} <b>{r.get("name","")}</b> — {r.get("desc","")}', body_style))

        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="50%", thickness=1, color=colors.HexColor('#D9E0E5')))
        story.append(Spacer(1, 10))
        story.append(Paragraph('咨询师签名：__________________　　日期：______________', ParagraphStyle('sign', parent=body_style, fontSize=10, textColor=colors.gray)))
        story.append(Paragraph('本报告由 MindGuard 神经符号推理引擎自动生成，仅供参考，不能替代专业诊断。', ParagraphStyle('footer', parent=body_style, fontSize=9, textColor=colors.gray, alignment='center')))

        doc.build(story)
        buf.seek(0)
        filename = f'mindguard_report_{session.id}_{session.created_at.strftime("%Y%m%d")}.pdf'
        return StreamingResponse(
            buf,
            media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        log.error('PDF generation failed: %s', e, exc_info=True)
        raise HTTPException(500, f'PDF 生成失败: {e}')


# ══════════════════════════════════════════════
# #13 紧急联系人 / 安全代理
# ══════════════════════════════════════════════

class ContactForm(BaseModel):
    anon_id: str
    contact_name: str
    contact_phone: str
    relation: Optional[str] = '朋友'
    notify_threshold: Optional[str] = 'urgent'


@router.post('/emergency-contact')
def save_contact(payload: ContactForm, db: Session = Depends(get_db)):
    existing = db.query(EmergencyContact).filter(
        EmergencyContact.anon_id == payload.anon_id
    ).first()
    if existing:
        existing.contact_name = payload.contact_name
        existing.contact_phone = payload.contact_phone
        existing.relation = payload.relation
        existing.notify_threshold = payload.notify_threshold
    else:
        db.add(EmergencyContact(
            anon_id=payload.anon_id,
            contact_name=payload.contact_name,
            contact_phone=payload.contact_phone,
            relation=payload.relation,
            notify_threshold=payload.notify_threshold,
        ))
    db.commit()
    return {'status': 'ok'}


@router.get('/emergency-contact/{anon_id}')
def get_contact(anon_id: str, db: Session = Depends(get_db)):
    c = db.query(EmergencyContact).filter(EmergencyContact.anon_id == anon_id).first()
    if not c:
        return {'configured': False}
    return {
        'configured': True,
        'contact_name': c.contact_name,
        'contact_phone': c.contact_phone,
        'relation': c.relation,
        'notify_threshold': c.notify_threshold,
    }


# ══════════════════════════════════════════════
# 我的档案：查询当前匿名用户的测评历史
# ══════════════════════════════════════════════

RISK_LEVEL_CN = {
    'low': '🟢 低风险',
    'medium': '🟡 中风险',
    'high': '🟠 高风险',
    'urgent': '🔴 极高风险',
}


@router.get('/my-records')
def my_records(request: Request, anon_id: Optional[str] = None,
               db: Session = Depends(get_db)):
    """
    返回当前匿名用户的测评历史（按时间倒序）。
    身份来源：query 参数 anon_id → 浏览器 cookie anon_id（自适应测评开始时写入）。
    """
    aid = (anon_id or '').strip()
    if not aid:
        aid = (request.cookies.get('anon_id') or '').strip()
    if not aid:
        return {'records': [], 'identity': None}

    sessions = (
        db.query(ScreeningSession)
        .join(User, ScreeningSession.user_id == User.id)
        .filter(User.anon_id == aid)
        .order_by(ScreeningSession.created_at.desc())
        .all()
    )

    records = []
    for s in sessions:
        answered = None
        if s.features_json:
            try:
                answered = json.loads(s.features_json).get('answered_count')
            except Exception:
                answered = None
        records.append({
            'session_id': s.id,
            'risk_level': s.overall_risk_level,
            'risk_level_cn': RISK_LEVEL_CN.get(s.overall_risk_level, s.overall_risk_level),
            'created_at': (s.created_at + timedelta(hours=8)).isoformat() if s.created_at else None,
            'overall_score': round(s.overall_risk_score or 0, 1),
            'total_answered': answered,
            'phq9_score': round(s.phq9_score or 0, 1),
            'gad7_score': round(s.gad7_score or 0, 1),
        })
    return {'records': records, 'identity': aid}


# ══════════════════════════════════════════════
# 首页实时统计
# ══════════════════════════════════════════════

@router.get('/home-stats')
def home_stats(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    return {
        'total_sessions': db.query(ScreeningSession).count(),
        'today_sessions': db.query(ScreeningSession).filter(ScreeningSession.created_at >= today_start).count(),
        'total_users': db.query(User).count(),
        'urgent_count': db.query(ScreeningSession).filter(
            ScreeningSession.overall_risk_level == 'urgent').count(),
    }