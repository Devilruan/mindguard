# -*- coding: utf-8 -*-
"""
backend.api.analytics_api
智能分析 API：规则命中率 / 热力矩阵 / 趋势预测 / 高危预警队列 / 心理资源
"""
from __future__ import annotations
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from backend.models.database import (
    SessionLocal, User, ScreeningSession, Intervention, get_db,
)

router = APIRouter()


# ──────────────────────────────────────────────
# 心理自助资源（硬编码 + 前端 resources.html 展示）
# ──────────────────────────────────────────────

HELP_LINES = [
    {
        'name': '全国24小时心理援助热线',
        'number': '12356',
        'desc': '全国统一热线，全年无休',
        'tag': '通用',
    },
    {
        'name': '北京市心理危机研究与干预中心',
        'number': '010-82951332',
        'desc': '危机干预（24小时）',
        'tag': '危机干预',
    },
    {
        'name': '青少年心理咨询与维权热线',
        'number': '12355',
        'desc': '青少年群体（工作日 9:00-21:00）',
        'tag': '青少年',
    },
]

SELF_HELP_TECHNIQUES = [
    {
        'title': '情绪急救「4-7-8 呼吸法」',
        'content': '吸气 4 秒 → 屏息 7 秒 → 缓慢呼气 8 秒。重复 4 轮，可快速平复急性焦虑。',
        'category': '呼吸调节',
    },
    {
        'title': '「着陆技术」回到当下',
        'content': '焦虑时：说出你看到的 5 样东西 → 3 种声音 → 1 种触摸感受，将注意力拉回现实。',
        'category': '认知调节',
    },
    {
        'title': '情绪日记记录法',
        'content': '每天睡前用 5 分钟记录「发生了什么-我的感受-我的应对」，逐步识别情绪模式。',
        'category': '自我觉察',
    },
    {
        'title': '渐进式肌肉放松',
        'content': '从脚趾开始，依次收紧-放松全身各部位肌肉群（每个 5-10 秒），配合深呼吸。',
        'category': '躯体调节',
    },
]


# ──────────────────────────────────────────────
# 规则命中率分析
# ──────────────────────────────────────────────

@router.get('/rule-hits')
def rule_hits(db: Session = Depends(get_db)):
    """统计每条规则被触发的次数，用于评估规则有效性"""
    rows = db.query(ScreeningSession).all()

    hits = {}
    total = len(rows)
    for s in rows:
        rules = s.activated_rules
        if isinstance(rules, str):
            try:
                rules = json.loads(rules)
            except Exception:
                rules = []
        if not rules:
            continue
        for r in rules:
            rid = r.get('rule_id', 'unknown') if isinstance(r, dict) else str(r)
            hits[rid] = hits.get(rid, 0) + 1

    # 按命中次数排序
    result = []
    for rid, count in sorted(hits.items(), key=lambda x: -x[1]):
        result.append({
            'rule_id': rid,
            'hit_count': count,
            'hit_rate': round(count / max(total, 1) * 100, 1),
        })

    return {'total_sessions': total, 'rule_hits': result}


# ──────────────────────────────────────────────
# 年级 × 风险等级 热力矩阵
# ──────────────────────────────────────────────

@router.get('/grade-matrix')
def grade_matrix(db: Session = Depends(get_db)):
    """年级 × 风险等级的交叉统计，用于热力图"""
    levels = ['low', 'medium', 'high', 'urgent']

    # 聚合查询
    rows = db.query(
        User.grade, ScreeningSession.overall_risk_level, func.count(ScreeningSession.id)
    ).outerjoin(ScreeningSession, ScreeningSession.user_id == User.id
    ).filter(ScreeningSession.id != None
    ).group_by(User.grade, ScreeningSession.overall_risk_level).all()

    matrix = {}
    grades_set = set()
    for grade, level, cnt in rows:
        grade_label = grade or '未填写'
        grades_set.add(grade_label)
        if grade_label not in matrix:
            matrix[grade_label] = {l: 0 for l in levels}
        matrix[grade_label][level or 'low'] = cnt

    return {
        'grades': sorted(grades_set),
        'levels': levels,
        'matrix': matrix,
    }


# ──────────────────────────────────────────────
# 专业分布
# ──────────────────────────────────────────────

@router.get('/major-dist')
def major_dist(db: Session = Depends(get_db)):
    """参与筛查者的专业分布"""
    rows = db.query(
        User.major, func.count(ScreeningSession.id)
    ).outerjoin(ScreeningSession, ScreeningSession.user_id == User.id
    ).filter(ScreeningSession.id != None
    ).group_by(User.major).all()

    result = []
    for major, cnt in rows:
        result.append({'major': major or '未填写', 'count': cnt})
    result.sort(key=lambda x: -x['count'])

    return result[:20]  # TOP 20


# ──────────────────────────────────────────────
# 近 14 天趋势 + 未来 7 天预测（线性外推）
# ──────────────────────────────────────────────

@router.get('/trend-forecast')
def trend_forecast(db: Session = Depends(get_db)):
    """筛查量趋势 + 简易线性外推预测"""
    # 近 14 天实际数据
    actual = []
    today = datetime.utcnow().date()
    counts = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        c = db.query(ScreeningSession).filter(
            func.date(ScreeningSession.created_at) == d
        ).count()
        counts.append(c)
        actual.append({'date': d.strftime('%m-%d'), 'count': c})

    # 线性回归：y = ax + b
    n = len(counts)
    if n >= 2 and sum(counts) > 0:
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(counts) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, counts))
        den = sum((x - mean_x) ** 2 for x in xs)
        a = num / den if den else 0
        b = mean_y - a * mean_x

        forecast = []
        for i in range(1, 8):
            pred = max(0, round(a * (n - 1 + i) + b))
            fd = today + timedelta(days=i)
            forecast.append({'date': fd.strftime('%m-%d'), 'count': pred})
    else:
        forecast = []

    return {'actual': actual, 'forecast': forecast}


# ──────────────────────────────────────────────
# 高危预警队列
# ──────────────────────────────────────────────

@router.get('/urgent-queue')
def urgent_queue(db: Session = Depends(get_db)):
    """high + urgent 风险的筛查会话队列（含自杀风险标记）"""
    rows = db.query(ScreeningSession).filter(
        ScreeningSession.overall_risk_level.in_(['high', 'urgent'])
    ).order_by(desc(ScreeningSession.overall_risk_score)).all()

    out = []
    for s in rows:
        u = s.user
        features = s.features_json
        suicide_flag = False
        if isinstance(features, str):
            try:
                features = json.loads(features)
            except Exception:
                features = None
        if features and features.get('text_suicide_risk', 0) > 0:
            suicide_flag = True

        # 触发的规则 ID 列表（供后台预警队列展示）
        triggered = []
        if s.activated_rules:
            try:
                rules = json.loads(s.activated_rules) if isinstance(s.activated_rules, str) else s.activated_rules
                triggered = [r.get('rule_id', '') for r in rules if isinstance(r, dict) and r.get('rule_id')]
            except Exception:
                triggered = []
        # 干预工单状态
        iv_status = None
        if s.intervention_id:
            try:
                iv = db.query(Intervention).filter(Intervention.id == s.intervention_id).first()
                iv_status = iv.status if iv else None
            except Exception:
                iv_status = None

        out.append({
            'session_id': s.id,
            'anon_id': u.anon_id if u else None,
            'grade': u.grade if u else None,
            'risk_level': s.overall_risk_level,
            'risk_score': round(s.overall_risk_score, 1),
            'suicide_risk': s.suicide_risk_score or 0,
            'suicide_flag': suicide_flag,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'duration_sec': s.duration_sec,
            'triggered_rules': triggered,
            'has_intervention': s.intervention_id is not None,
            'intervention_status': iv_status,
        })

    return out


# ──────────────────────────────────────────────
# 个人历史趋势
# ──────────────────────────────────────────────

@router.get('/history/{anon_id}')
def history(anon_id: str, db: Session = Depends(get_db)):
    """指定匿名用户的历史筛查趋势"""
    u = db.query(User).filter(User.anon_id == anon_id).first()
    if not u:
        raise HTTPException(status_code=404, detail='未找到该匿名用户')

    sessions = db.query(ScreeningSession).filter(
        ScreeningSession.user_id == u.id
    ).order_by(ScreeningSession.created_at.asc()).all()

    trend = []
    for s in sessions:
        trend.append({
            'session_id': s.id,
            'date': s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else None,
            'phq9': s.phq9_score,
            'gad7': s.gad7_score,
            'risk_score': round(s.overall_risk_score, 1),
            'risk_level': s.overall_risk_level,
            'depression_score': round(s.depression_score, 1),
            'anxiety_score': round(s.anxiety_score, 1),
        })

    return {
        'anon_id': anon_id,
        'grade': u.grade,
        'major': u.major,
        'count': len(sessions),
        'trend': trend,
    }


# ──────────────────────────────────────────────
# 心理自助资源
# ──────────────────────────────────────────────

@router.get('/resources')
def resources():
    """返回心理援助热线 + 自助技巧（兼容前端字段名）"""
    hotlines = [
        {
            'name': h['name'],
            'number': h['number'],
            'scope': h['desc'] + ' · ' + h['tag'],
        }
        for h in HELP_LINES
    ]
    tips = [
        {
            'title': t['title'],
            'content': t['content'],
        }
        for t in SELF_HELP_TECHNIQUES
    ]
    guidance = [
        {'title': '筛查结果能代替专业诊断吗？',
         'content': '不能。筛查量表用于风险初筛与持续观察，不能作为临床诊断。若量表分数持续偏高或主观困扰明显，请前往校医院/精神专科就诊，由专业医师评估。'},
        {'title': '我的筛查数据安全吗？',
         'content': '系统采用匿名标识存储，不记录真实身份；筛查数据本地保存在校内服务器，仅相关心理老师可按流程查看，符合个人信息保护要求。'},
        {'title': '发现同学有危险信号时我该怎么做？',
         'content': '先陪伴倾听，不评判；鼓励其联系心理咨询或拨打 12356 / 12355 热线；紧急情况（如自伤风险）请立即告知辅导员并拨打 120/110，不独自承担。'},
    ]
    return {
        'help_lines': HELP_LINES,
        'self_help_techniques': SELF_HELP_TECHNIQUES,
        'hotlines': hotlines,
        'tips': tips,
        'guidance': guidance,
    }
