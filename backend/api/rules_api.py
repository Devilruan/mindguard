# -*- coding: utf-8 -*-
"""
backend.api.rules_api
规则引擎管理：列表 / 添加 / 删除 / RIPPER 自动学习 / 恢复默认
"""
from __future__ import annotations
import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from backend.core.neuro_symbolic.engine import (
    get_engine, Rule, RuleLearner, RuleBase,
)
from backend.models.database import SessionLocal, RuleVersion
from config.settings import DEFAULT_RULES

router = APIRouter()


# Admin 路由保护依赖（引用共享模块，避免 main ↔ api 循环导入）
from config.admin_auth import require_admin_auth as _require_admin_auth


# ──────────────────────────────────────────────
# Pydantic 请求模型
# ──────────────────────────────────────────────

class RuleCondition(BaseModel):
    feat: str
    op: str            # '>=' / '>' / '<=' / '<' / '=='
    thr: float


class RuleAdd(BaseModel):
    rule_id: str
    priority: int = 5
    consequence: str = ''
    explain: str = ''
    conditions: List[RuleCondition]


# ──────────────────────────────────────────────
# 规则列表
# ──────────────────────────────────────────────

@router.get('/list')
def list_rules(_: bool = Depends(_require_admin_auth)):
    """获取当前生效的全部规则"""
    engine = get_engine()
    return {
        'rules': [
            {
                'id': r.id,
                'priority': r.priority,
                'consequence': r.consequence,
                'explain': r.explain,
                'conditions': [
                    {'feat': c[0], 'op': c[1], 'thr': c[2]} for c in r.conditions
                ],
            }
            for r in engine.rule_base.rules
        ],
        'total': len(engine.rule_base.rules),
    }


# ──────────────────────────────────────────────
# 添加规则
# ──────────────────────────────────────────────

@router.post('/add')
def add_rule(payload: RuleAdd, _: bool = Depends(_require_admin_auth)):
    """手动添加一条新规则"""
    engine = get_engine()

    # 检查 ID 重复
    if any(r.id == payload.rule_id for r in engine.rule_base.rules):
        raise HTTPException(status_code=400, detail=f'规则 {payload.rule_id} 已存在')

    rule = Rule(
        id=payload.rule_id,
        priority=payload.priority,
        consequence=payload.consequence,
        explain=payload.explain,
        conditions=[(c.feat, c.op, c.thr) for c in payload.conditions],
    )
    engine.rule_base.add_rule(rule)

    # 记录版本
    db = SessionLocal()
    try:
        db.add(RuleVersion(
            version=f'custom-{payload.rule_id}',
            rules_json=json.dumps([r.__dict__ for r in engine.rule_base.rules], ensure_ascii=False, default=str),
            updated_by='admin',
        ))
        db.commit()
    finally:
        db.close()

    return {'ok': True, 'rule_id': payload.rule_id}


# ──────────────────────────────────────────────
# 删除规则
# ──────────────────────────────────────────────

@router.delete('/{rule_id}')
def remove_rule(rule_id: str, _: bool = Depends(_require_admin_auth)):
    """删除指定规则"""
    engine = get_engine()
    before = len(engine.rule_base.rules)
    engine.rule_base.remove_rule(rule_id)

    if len(engine.rule_base.rules) == before:
        raise HTTPException(status_code=404, detail=f'规则 {rule_id} 不存在')

    # 版本记录
    db = SessionLocal()
    try:
        db.add(RuleVersion(
            version=f'remove-{rule_id}',
            rules_json=json.dumps([r.__dict__ for r in engine.rule_base.rules], ensure_ascii=False, default=str),
            updated_by='admin',
        ))
        db.commit()
    finally:
        db.close()

    return {'ok': True}


# ──────────────────────────────────────────────
# RIPPER 自动学习
# ──────────────────────────────────────────────

@router.post('/learn')
def learn_rules(_: bool = Depends(_require_admin_auth)):
    """
    基于历史筛查数据运行 RIPPER 规则学习。

    步骤：
      1. 从数据库读取所有已完成的筛查会话
      2. 提取特征矩阵（n × 10）+ 风险标签（high/urgent → 1, 其他 → 0）
      3. 调用 wittgenstein.Ripper 训练
      4. 将学习到的新规则加入规则库
    """
    from backend.models.database import SessionLocal, ScreeningSession
    from config.settings import FEATURE_NAMES

    db = SessionLocal()
    try:
        sessions = db.query(ScreeningSession).all()
    finally:
        db.close()

    if len(sessions) < 10:
        raise HTTPException(status_code=400, detail='样本量不足（至少需要 10 条已完成筛查数据）')

    # 构建特征矩阵和标签
    X, y = [], []
    for s in sessions:
        features = s.features_json
        if isinstance(features, str):
            try:
                features = json.loads(features)
            except Exception:
                continue
        if not features:
            continue
        row = [features.get(f, 0) for f in FEATURE_NAMES]
        X.append(row)
        y.append(1 if s.overall_risk_level in ('high', 'urgent') else 0)

    if not X:
        raise HTTPException(status_code=400, detail='无有效特征数据')

    # 运行 RIPPER
    learner = RuleLearner()
    learned = learner.fit(X, y, FEATURE_NAMES)

    # 加入规则库（不覆盖已有）
    engine = get_engine()
    added = 0
    for r in learned:
        if not any(x.id == r.id for x in engine.rule_base.rules):
            engine.rule_base.add_rule(r)
            added += 1

    # 版本记录
    db = SessionLocal()
    try:
        db.add(RuleVersion(
            version=f'learned-{len(learned)}-new-{added}',
            rules_json=json.dumps([r.__dict__ for r in engine.rule_base.rules], ensure_ascii=False, default=str),
            updated_by='RIPPER',
        ))
        db.commit()
    finally:
        db.close()

    return {
        'total_samples': len(X),
        'learned_rules': len(learned),
        'newly_added': added,
        'learner_available': learner.available,
    }


# ──────────────────────────────────────────────
# 恢复默认
# ──────────────────────────────────────────────

@router.post('/reset-defaults')
def reset_defaults(_: bool = Depends(_require_admin_auth)):
    """恢复 6 条默认心理学规则"""
    engine = get_engine()
    engine.rule_base = RuleBase()  # 重建（自动加载 DEFAULT_RULES）

    # 版本记录
    db = SessionLocal()
    try:
        db.add(RuleVersion(
            version='v1.0-default-reset',
            rules_json=json.dumps(DEFAULT_RULES, ensure_ascii=False),
            updated_by='admin',
        ))
        db.commit()
    finally:
        db.close()

    return {'ok': True, 'restored': len(engine.rule_base.rules)}

