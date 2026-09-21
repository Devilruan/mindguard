# -*- coding: utf-8 -*-
"""
backend.api.admin_api
管理员后台 API：统计概览 / 会话列表 / 干预工单 / 预警推送 / 数据导出
"""
from __future__ import annotations
import csv
import io
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import func, desc, or_
from sqlalchemy.orm import Session

from backend.models.database import (
    SessionLocal, User, ScreeningSession, Intervention, get_db,
)

router = APIRouter()


# ──────────────────────────────────────────────
# Admin 路由保护依赖（引用共享模块，避免 main ↔ api 循环导入）
from config.admin_auth import require_admin_auth as _require_admin_auth


# ──────────────────────────────────────────────
# Pydantic 请求/响应模型
# ──────────────────────────────────────────────

class InterventionCreate(BaseModel):
    session_id: int
    status: str = 'pending'
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    risk_level: Optional[str] = None


class InterventionUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class AlertSend(BaseModel):
    session_ids: List[int]


# ──────────────────────────────────────────────
# 统计概览 Dashboard
# ──────────────────────────────────────────────

@router.get('/stats/overview')
def stats_overview(_: bool = Depends(_require_admin_auth), db: Session = Depends(get_db)):
    """仪表盘统计：总量 / 风险分布 / 近 7 天趋势 / 得分分布 / 年级分布"""

    total_sessions = db.query(ScreeningSession).count()
    total_users = db.query(User).count()

    # 近 7 天
    last_7 = datetime.utcnow() - timedelta(days=7)
    sessions_last_7 = db.query(ScreeningSession).filter(
        ScreeningSession.created_at >= last_7
    ).count()

    # 风险等级分布
    rows = db.query(
        ScreeningSession.overall_risk_level,
        func.count(ScreeningSession.id)
    ).group_by(ScreeningSession.overall_risk_level).all()
    risk_distribution = {r[0]: r[1] for r in rows}

    # PHQ-9 / GAD-7 得分分布（按分箱）
    phq9_dist = db.query(
        ScreeningSession.phq9_score,
        func.count(ScreeningSession.id)
    ).group_by(ScreeningSession.phq9_score).all()

    gad7_dist = db.query(
        ScreeningSession.gad7_score,
        func.count(ScreeningSession.id)
    ).group_by(ScreeningSession.gad7_score).all()

    # 综合风险分分布（按 10 分一档）
    rows2 = db.query(ScreeningSession.overall_risk_score).all()
    score_distribution = {}
    for (score,) in rows2:
        bucket = f'{int(score / 10) * 10}-{int(score / 10) * 10 + 9}'
        score_distribution[bucket] = score_distribution.get(bucket, 0) + 1

    # 年级分布
    rows3 = db.query(
        User.grade, func.count(ScreeningSession.id)
    ).outerjoin(ScreeningSession, ScreeningSession.user_id == User.id
    ).group_by(User.grade).all()
    grade_distribution = {g or '未填写': c for g, c in rows3}

    # 近 14 天筛查趋势
    trend = []
    for i in range(13, -1, -1):
        d = datetime.utcnow() - timedelta(days=i)
        count = db.query(ScreeningSession).filter(
            func.date(ScreeningSession.created_at) == d.date()
        ).count()
        trend.append({'date': d.strftime('%m-%d'), 'count': count})

    # 极高风险 pending 工单
    urgent_pending = db.query(Intervention).filter(
        Intervention.status == 'pending',
        Intervention.session_id.in_(
            db.query(ScreeningSession.id).filter(
                ScreeningSession.overall_risk_level == 'urgent'
            )
        )
    ).count()

    return {
        'total_sessions': total_sessions,
        'total_users': total_users,
        'sessions_last_7_days': sessions_last_7,
        'urgent_pending': urgent_pending,
        'risk_distribution': risk_distribution,
        'grade_distribution': grade_distribution,
        'score_distribution': score_distribution,
        'trend': trend,
    }


# ──────────────────────────────────────────────
# 筛查会话管理
# ──────────────────────────────────────────────

@router.get('/sessions')
def list_sessions(
    _: bool = Depends(_require_admin_auth),
    level: Optional[str] = Query(None, description='按风险等级筛选'),
    db: Session = Depends(get_db),
):
    """筛查会话列表（支持风险等级筛选）"""
    q = db.query(ScreeningSession).outerjoin(User, ScreeningSession.user_id == User.id)
    if level:
        q = q.filter(ScreeningSession.overall_risk_level == level)
    rows = q.order_by(desc(ScreeningSession.created_at)).limit(500).all()

    out = []
    for s, u in [(r, r.user) for r in rows]:
        activated = s.activated_rules
        if isinstance(activated, str):
            try:
                activated = json.loads(activated)
            except Exception:
                activated = []
        out.append({
            'id': s.id,
            'anon_id': u.anon_id if u else '未知',
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'phq9': s.phq9_score,
            'gad7': s.gad7_score,
            'risk_score': round(s.overall_risk_score, 1),
            'risk_level': s.overall_risk_level,
            'activation_count': len(activated or []),
        })

    return {'total': len(rows), 'rows': out}


@router.get('/sessions/{session_id}')
def session_detail(session_id: int, _: bool = Depends(_require_admin_auth), db: Session = Depends(get_db)):
    """单个会话详情（含完整推理链路 + 原始数据）"""
    s = db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail='会话不存在')

    u = s.user
    activated = s.activated_rules
    chain = s.explanation_chain
    features = s.features_json

    if isinstance(activated, str):
        try:
            activated = json.loads(activated)
        except Exception:
            activated = []
    if isinstance(chain, str):
        try:
            chain = json.loads(chain)
        except Exception:
            chain = []
    if isinstance(features, str):
        try:
            features = json.loads(features)
        except Exception:
            features = None

    # ── LLM 个性化建议（失败自动降级为固定模板） ──
    llm_suggestion = ''
    try:
        from backend.core.llm_client import generate_suggestion
        suicide_flag = (s.suicide_risk_score or 0) > 0
        llm_suggestion = generate_suggestion(
            level=s.overall_risk_level,
            score=s.overall_risk_score,
            depression=s.depression_score,
            anxiety=s.anxiety_score,
            suicide_flag=suicide_flag,
            activated_rules=activated,
        )
    except Exception:
        pass  # 静默降级

    # ── 危机分级 + RAG 知识检索（运行时计算，不存库） ──
    from backend.core.neuro_symbolic.engine import classify_crisis, retrieve_knowledge
    feat_for_crisis = (features or {}).get('text_suicide_risk', 0)
    crisis_level, crisis_hits = classify_crisis(
        s.open_text or '',
        suicide_feature=feat_for_crisis,
    )
    kb_level = s.overall_risk_level.upper() if s.overall_risk_level else 'LOW'
    if crisis_level == 'CRISIS':
        kb_level = 'URGENT'
    dimensions = []
    if s.open_text and any(k in s.open_text for k in ('学习', '考试', '论文', '作业')):
        dimensions.append('academic')
    if (s.depression_score or 0) > 50:
        dimensions.append('cognitive')
    knowledge_suggestions = retrieve_knowledge(kb_level, dimensions)

    return {
        'session': {
            'id': s.id,
            'anon_id': u.anon_id if u else None,
            'grade': u.grade if u else None,
            'major': u.major if u else None,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'phq9': s.phq9_score,
            'gad7': s.gad7_score,
            'risk_score': round(s.overall_risk_score, 2),
            'risk_level': s.overall_risk_level,
            'depression_score': round(s.depression_score, 2),
            'anxiety_score': round(s.anxiety_score, 2),
            'suicide_risk_score': round(s.suicide_risk_score, 2),
            'activated_rules': activated,
            'explanation_chain': chain,
            'features': features,
            'duration_sec': s.duration_sec,
            'phq9_answers': s.phq9_answers,
            'gad7_answers': s.gad7_answers,
            'open_text': s.open_text,
            'llm_suggestion': llm_suggestion,
            'crisis_level': crisis_level,
            'crisis_hits': crisis_hits,
            'knowledge_suggestions': knowledge_suggestions,
        }
    }


# ──────────────────────────────────────────────
# 干预工单 CRUD
# ──────────────────────────────────────────────

def serialize_iv(iv: Intervention) -> dict:
    return {
        'id': iv.id,
        'session_id': iv.session_id,
        'risk_level': iv.risk_level,
        'status': iv.status,
        'assigned_to': iv.assigned_to,
        'notes': iv.notes,
        'created_at': iv.created_at.isoformat() if iv.created_at else None,
        'updated_at': iv.updated_at.isoformat() if iv.updated_at else None,
    }


@router.get('/interventions')
def list_interventions(_: bool = Depends(_require_admin_auth), db: Session = Depends(get_db)):
    """干预工单列表（按创建时间倒序）"""
    rows = db.query(Intervention).order_by(desc(Intervention.created_at)).all()
    return [serialize_iv(iv) for iv in rows]


@router.post('/interventions')
def create_intervention(payload: InterventionCreate, _: bool = Depends(_require_admin_auth), db: Session = Depends(get_db)):
    """手动创建干预工单"""
    # 从关联筛查会话自动推断风险等级
    risk = payload.risk_level
    if not risk and payload.session_id:
        s = db.query(ScreeningSession).filter(ScreeningSession.id == payload.session_id).first()
        if s:
            risk = s.overall_risk_level

    iv = Intervention(
        session_id=payload.session_id,
        risk_level=risk,
        status=payload.status,
        assigned_to=payload.assigned_to,
        notes=payload.notes,
    )
    db.add(iv)
    db.commit()
    db.refresh(iv)
    return serialize_iv(iv)


@router.put('/interventions/{iv_id}')
def update_intervention(iv_id: int, payload: InterventionUpdate, _: bool = Depends(_require_admin_auth), db: Session = Depends(get_db)):
    """更新工单（认领 / 跟进 / 关闭）"""
    iv = db.query(Intervention).filter(Intervention.id == iv_id).first()
    if not iv:
        raise HTTPException(status_code=404, detail='工单不存在')

    if payload.status is not None:
        iv.status = payload.status
    if payload.assigned_to is not None:
        iv.assigned_to = payload.assigned_to
    if payload.notes is not None:
        iv.notes = payload.notes

    db.commit()
    db.refresh(iv)
    return serialize_iv(iv)


@router.delete('/interventions/{iv_id}')
def delete_intervention(iv_id: int, _: bool = Depends(_require_admin_auth), db: Session = Depends(get_db)):
    """删除工单"""
    iv = db.query(Intervention).filter(Intervention.id == iv_id).first()
    if not iv:
        raise HTTPException(status_code=404, detail='工单不存在')
    db.delete(iv)
    db.commit()
    return {'ok': True}


# ──────────────────────────────────────────────
# 预警推送
# ──────────────────────────────────────────────

@router.post('/alerts/send')
def send_alerts(payload: AlertSend, _: bool = Depends(_require_admin_auth), db: Session = Depends(get_db)):
    """为指定会话批量推送预警（自动创建干预工单）"""
    count = 0
    for sid in payload.session_ids:
        s = db.query(ScreeningSession).filter(ScreeningSession.id == sid).first()
        if not s:
            continue
        # 检查是否已有工单
        existing = db.query(Intervention).filter(
            Intervention.session_id == sid
        ).first()
        if existing:
            continue
        db.add(Intervention(
            session_id=sid,
            risk_level=s.overall_risk_level,
            status='pending',
            notes='系统自动推送预警',
        ))
        count += 1
    db.commit()
    return {'message': f'已推送预警，自动创建 {count} 条干预工单', 'created': count}


# ──────────────────────────────────────────────
# 数据导出（CSV / JSON）
# ──────────────────────────────────────────────

@router.get('/export/sessions')
def export_sessions(
    _: bool = Depends(_require_admin_auth),
    format: str = Query('json', description='csv / json'),
    db: Session = Depends(get_db),
):
    """导出全部筛查会话数据"""
    rows = db.query(ScreeningSession).order_by(ScreeningSession.id.asc()).all()

    def _j(x):
        if isinstance(x, str):
            try:
                return json.loads(x)
            except Exception:
                return x
        return x

    data = []
    columns = [
        'session_id', 'anon_id', 'grade', 'major', 'created_at',
        'phq9_score', 'gad7_score', 'phq9_answers', 'gad7_answers',
        'risk_score', 'risk_level', 'depression_score', 'anxiety_score',
        'suicide_risk_score', 'activated_rules', 'explanation_chain', 'duration_sec',
    ]
    for s in rows:
        u = db.query(User).filter(User.id == s.user_id).first() if s.user_id else None
        data.append({
            'session_id': s.id,
            'anon_id': u.anon_id if u else '未知',
            'grade': u.grade if u else None,
            'major': u.major if u else None,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'phq9_score': s.phq9_score,
            'gad7_score': s.gad7_score,
            'phq9_answers': _j(s.phq9_answers),
            'gad7_answers': _j(s.gad7_answers),
            'risk_score': round(s.overall_risk_score, 2),
            'risk_level': s.overall_risk_level,
            'depression_score': round(s.depression_score, 2),
            'anxiety_score': round(s.anxiety_score, 2),
            'suicide_risk_score': round(s.suicide_risk_score, 2),
            'activated_rules': _j(s.activated_rules),
            'explanation_chain': _j(s.explanation_chain),
            'duration_sec': s.duration_sec,
        })

    if format == 'json':
        content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type='application/json; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename=sessions_export.json'},
        )
    elif format == 'csv':
        if not data:
            return JSONResponse({'message': '暂无数据'})
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(columns)
        for row in data:
            writer.writerow([
                row.get(k) if not isinstance(row.get(k), (list, dict))
                else json.dumps(row.get(k), ensure_ascii=False)
                for k in columns
            ])
        content = buf.getvalue().encode('utf-8-sig')
        return StreamingResponse(
            io.BytesIO(content),
            media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename=sessions_export.csv'},
        )

    return JSONResponse({'error': 'format must be csv or json'})
