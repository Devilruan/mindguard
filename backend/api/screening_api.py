# -*- coding: utf-8 -*-
"""
backend.api.screening_api
筛查提交主入口：知情同意 / 题目获取 / 提交筛查 → 触发神经符号推理 → 生成报告
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.database import (
    SessionLocal, User, ScreeningSession, Intervention, get_db,
)
from backend.core.neuro_symbolic.engine import get_engine
from backend.core.feature_extraction import build_feature_vector, calc_phq9_score, calc_gad7_score
from config.settings import (
    PHQ9_QUESTIONS, GAD7_QUESTIONS, QUESTION_OPTIONS,
    CONSENT_TEXT,
)

log = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────────
# Pydantic 请求模型
# ──────────────────────────────────────────────

class ScreeningSubmit(BaseModel):
    anon_id: str
    grade: Optional[str] = None
    major: Optional[str] = None
    phq9_answers: List[int]
    gad7_answers: List[int]
    open_text: Optional[str] = None
    response_duration_sec: Optional[float] = None


# ──────────────────────────────────────────────
# 知情同意
# ──────────────────────────────────────────────

@router.get('/consent')
def get_consent():
    """返回知情同意文案"""
    return {'text': CONSENT_TEXT}


# ──────────────────────────────────────────────
# 题目列表
# ──────────────────────────────────────────────

@router.get('/questions')
def get_questions():
    """返回 PHQ-9 + GAD-7 全部题目 + 选项"""
    return {
        'phq9': PHQ9_QUESTIONS,
        'gad7': GAD7_QUESTIONS,
        'options': QUESTION_OPTIONS,
        'phq9_max': 27,
        'gad7_max': 21,
    }


# ──────────────────────────────────────────────
# 提交筛查（主入口）
# ──────────────────────────────────────────────

@router.post('/submit')
def submit(payload: ScreeningSubmit):
    """
    提交筛查表单，触发完整神经符号推理，返回风险评估报告。

    流程：
      ① Pydantic 校验 → ② 组装 RiskFeature → ③ NeuroSymbolicEngine.assess()
      ④ 写入数据库 → ⑤ 自动创建工单（高危） → ⑥ 返回报告
    """
    if len(payload.phq9_answers) != 9:
        raise HTTPException(status_code=400, detail='PHQ-9 需要 9 题答案')
    if len(payload.gad7_answers) != 7:
        raise HTTPException(status_code=400, detail='GAD-7 需要 7 题答案')

    log.info('筛查提交 anon=%s phq9=%s gad7=%s text_len=%d',
             payload.anon_id, payload.phq9_answers, payload.gad7_answers,
             len(payload.open_text or ''))

    features = build_feature_vector(
        phq9_answers=payload.phq9_answers,
        gad7_answers=payload.gad7_answers,
        open_text=payload.open_text,
        audio_path=None,
        response_duration_sec=payload.response_duration_sec,
    )

    engine = get_engine()
    assessment = engine.assess(features, open_text=payload.open_text)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.anon_id == payload.anon_id).first()
        if not user:
            user = User(
                anon_id=payload.anon_id,
                grade=payload.grade,
                major=payload.major,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        session = ScreeningSession(
            user_id=user.id,
            duration_sec=payload.response_duration_sec,
            phq9_answers=json.dumps(payload.phq9_answers),
            gad7_answers=json.dumps(payload.gad7_answers),
            open_text=payload.open_text,
            phq9_score=assessment.features_used['phq9_score'],
            gad7_score=assessment.features_used['gad7_score'],
            overall_risk_level=assessment.overall_risk_level,
            overall_risk_score=assessment.overall_risk_score,
            depression_score=assessment.depression_score,
            anxiety_score=assessment.anxiety_score,
            suicide_risk_score=assessment.suicide_risk_score,
            activated_rules=json.dumps(
                [{'rule_id': a.rule_id, 'explain': a.explain,
                  'priority': a.priority, 'met_conditions': a.met_conditions}
                 for a in assessment.activated_rules],
                ensure_ascii=False,
            ),
            explanation_chain=json.dumps(assessment.explanation_chain, ensure_ascii=False),
            features_json=json.dumps(assessment.features_used, ensure_ascii=False),
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        if assessment.overall_risk_level in ('high', 'urgent'):
            db.add(Intervention(
                session_id=session.id,
                risk_level=assessment.overall_risk_level,
                status='pending',
                notes='系统自动创建 - 高风险预警',
            ))
            db.commit()
            log.warning('高风险自动创建工单 session=%d level=%s',
                        session.id, assessment.overall_risk_level)

    finally:
        db.close()

    report = assessment.to_dict()
    report['session_id'] = session.id
    report['recommendation'] = assessment.recommendation

    log.info('筛查完成 session=%d level=%s score=%.1f',
             session.id, assessment.overall_risk_level, assessment.overall_risk_score)

    return report
