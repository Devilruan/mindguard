# -*- coding: utf-8 -*-
"""
backend.core.neuro_symbolic.engine
神经符号双引擎核心：规则知识库 + RIPPER 规则学习 + 可解释推理

设计思想：
  输入层 → 神经感知（BERT/关键词/语音等多模态） → 10 维 RiskFeature
  推理层 → 规则引擎（RuleBase）逐条评估 → 收集激活规则
  输出层 → 综合风险分 + 分维度分 + 完整推理链 + LLM 个性化建议
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import json
import logging
import os
import time

log = logging.getLogger(__name__)

# wittgenstein 可选依赖（未安装时降级为启发式规则）
try:
    import wittgenstein
    from wittgenstein import Ripper
    _HAS_RIPPER_IMPORT = True
except Exception:
    _HAS_RIPPER_IMPORT = False
    wittgenstein = None
    Ripper = None

from config.settings import (
    DEFAULT_RULES,
    FEATURE_NAMES,
    RULES_DIR,
)

# RIPPER 可用性标记（真实实例化测试，避免假阳性）
try:
    _test = Ripper()
    HAS_RIPPER = True
except Exception:
    HAS_RIPPER = False


# ──────────────────────────────────────────────
# 数据类：特征向量 / 规则 / 激活 / 评估结果
# ──────────────────────────────────────────────

@dataclass
class RiskFeature:
    """多模态特征向量：10 维，来自神经感知层。

    与 config.settings.FEATURE_NAMES 字段一一对应。
    """
    phq9_score: float
    gad7_score: float
    text_negativity: float
    text_anxiety_keywords: int
    text_depression_keywords: int
    text_suicide_risk: int
    speech_pitch_std: float
    speech_speaking_rate: float
    speech_jitter: float
    response_duration_sec: float

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}

    def to_vector(self) -> List[float]:
        return [getattr(self, f) for f in FEATURE_NAMES]


@dataclass
class Rule:
    """一条可解释规则：conditions → consequence。

    conditions 格式示例：
        [('phq9_score', '>=', 20), ('text_negativity', '>', 0.5)]
    """
    id: str
    priority: int = 5
    conditions: List[Tuple[str, str, Any]] = None
    consequence: str = ''
    explain: str = ''

    def __post_init__(self) -> None:
        if self.conditions is None:
            self.conditions = []

    def evaluate(self, features: Dict[str, float]) -> Tuple[bool, List[bool]]:
        """逐条检查条件是否满足。返回 (是否全部满足, 每条条件的满足情况)。"""
        met: List[bool] = []
        for feat, op, thr in self.conditions:
            val = features.get(feat, 0)
            if op == '>=':
                met.append(val >= thr)
            elif op == '>':
                met.append(val > thr)
            elif op == '<=':
                met.append(val <= thr)
            elif op == '<':
                met.append(val < thr)
            elif op == '==':
                met.append(val == thr)
            else:
                met.append(False)
        return all(met), met


@dataclass
class RuleActivation:
    """一次筛查中被激活的规则及其证据。"""
    rule_id: str
    explain: str
    priority: int
    met_conditions: List[bool]
    condition_details: Optional[List[str]] = None


@dataclass
class RiskAssessment:
    """最终评估结果：分数 + 依据链 + 个性化建议。"""
    overall_risk_level: str
    overall_risk_score: float
    depression_score: float
    anxiety_score: float
    suicide_risk_score: float
    activated_rules: List[RuleActivation]
    features_used: Dict[str, Any]
    explanation_chain: List[str]
    recommendation: str = ''
    llm_suggestion: str = ''
    # ── 新增：危机分级 + RAG 知识检索结果 ──
    crisis_level: str = 'LOW'
    crisis_hits: List[str] = field(default_factory=list)
    knowledge_suggestions: List[str] = field(default_factory=list)
    elapsed_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall_risk_level': self.overall_risk_level,
            'overall_risk_score': round(self.overall_risk_score, 2),
            'depression_score': round(self.depression_score, 2),
            'anxiety_score': round(self.anxiety_score, 2),
            'suicide_risk_score': round(self.suicide_risk_score, 2),
            'activated_rules': [
                {'rule_id': r.rule_id, 'explain': r.explain,
                 'priority': r.priority, 'met_conditions': r.met_conditions}
                for r in self.activated_rules
            ],
            'features_used': self.features_used,
            'explanation_chain': self.explanation_chain,
            'recommendation': self.recommendation,
            'llm_suggestion': self.llm_suggestion,
            'crisis_level': self.crisis_level,
            'crisis_hits': self.crisis_hits,
            'knowledge_suggestions': self.knowledge_suggestions,
            'elapsed_ms': round(self.elapsed_ms, 1),
        }


# ──────────────────────────────────────────────
# 规则知识库（可热更新、可 RIPPER 学习）
# ──────────────────────────────────────────────

class RuleBase:
    """心理学规则知识库 + 可学习规则管理。

    规则优先级越高越先评估；RuleLearner 可从标注数据中学习新规则。
    """

    def __init__(self) -> None:
        self.rules: List[Rule] = []
        self._load_defaults()

    def _load_defaults(self) -> None:
        """从 config.DEFAULT_RULES 加载 6 条默认规则。"""
        for rdata in DEFAULT_RULES:
            self.add_rule(Rule(**rdata))

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, rule_id: str) -> None:
        self.rules = [r for r in self.rules if r.id != rule_id]

    def save(self, path: Optional[str] = None) -> None:
        """将当前规则库持久化到 JSON 文件。"""
        path = path or os.path.join(RULES_DIR, 'active_rules.json')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([r.__dict__ for r in self.rules], f, ensure_ascii=False, indent=2)
        log.info('规则库已保存到 %s（%d 条）', path, len(self.rules))

    def load(self, path: Optional[str] = None) -> None:
        """从 JSON 文件恢复规则库（会覆盖当前）。"""
        path = path or os.path.join(RULES_DIR, 'active_rules.json')
        if not os.path.exists(path):
            return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.rules = [Rule(**d) for d in data]
        log.info('从 %s 恢复规则库（%d 条）', path, len(self.rules))


# ──────────────────────────────────────────────
# RIPPER 规则学习器
# ──────────────────────────────────────────────

class RuleLearner:
    """用 RIPPER 规则归纳算法从标注数据中学习新规则。

    依赖 wittgenstein 库；未安装时自动降级为基于心理学阈值的启发式规则。
    """

    def __init__(self) -> None:
        self.model = None
        self.available = HAS_RIPPER

    def fit(self, X: List[List[float]], y: List[int],
            feature_names: List[str]) -> List[Rule]:
        """
        从特征矩阵 + 二值标签中学习规则。

        Parameters
        ----------
        X : 特征矩阵 (n_samples, n_features)
        y : 风险标签 (0=安全, 1=高风险)
        feature_names : 每列对应的特征名

        Returns
        -------
        List[Rule]  学习得到的规则列表
        """
        if self.available:
            try:
                log.info('使用 RIPPER 训练 %d 条样本...', len(X))
                t0 = time.time()
                self.model = Ripper()
                self.model.fit(X, y)
                rules = self._extract_rules_from_wittgenstein(self.model, feature_names)
                log.info('RIPPER 训练完成 (%.0fms)，学习到 %d 条规则',
                         (time.time() - t0) * 1000, len(rules))
                return rules
            except Exception as e:
                log.warning('RIPPER 训练失败，降级为启发式规则: %s', e)

        return self._heuristic_rules(feature_names)

    def _extract_rules_from_wittgenstein(self, model,
                                         feature_names: List[str]) -> List[Rule]:
        """将 wittgenstein.Ripper 模型输出转换为 Rule 列表。"""
        rules: List[Rule] = []
        idx_by_name = {name: i for i, name in enumerate(feature_names)}
        try:
            raw = str(model)
        except Exception:
            return self._heuristic_rules(feature_names)

        for i, line in enumerate(raw.split('\n')):
            line = line.strip()
            if not line or '→' not in line:
                continue
            try:
                lhs, _, _ = line.partition('→')
                conditions: List[Tuple[str, str, Any]] = []
                for token in lhs.split('&'):
                    token = token.strip()
                    parts = token.split()
                    if len(parts) >= 3:
                        feat, op, thr = parts[0], parts[1], float(parts[2])
                        # 可能是特征索引名（f_0, f_1...）也可能是原始名
                        feat_name = feature_names[int(feat[2:])] if feat.startswith('f_') else feat
                        conditions.append((feat_name, op, thr))
                if conditions:
                    rules.append(Rule(
                        id=f'LEARNED_{i:03d}',
                        priority=4,
                        conditions=conditions,
                        consequence='learned_risk_signal',
                        explain='RIPPER 从历史数据学习得到的规则',
                    ))
            except Exception:
                continue

        return rules or self._heuristic_rules(feature_names)

    def _heuristic_rules(self, feature_names: List[str]) -> List[Rule]:
        """无 RIPPER 时的启发式规则（基于临床心理学阈值）。"""
        return [
            Rule(id='LEARNED_H1', priority=4,
                 conditions=[('phq9_score', '>=', 12)],
                 consequence='learned_risk_signal',
                 explain='启发式：PHQ-9 ≥ 12 提示潜在抑郁风险'),
            Rule(id='LEARNED_H2', priority=4,
                 conditions=[('text_negativity', '>=', 0.5), ('gad7_score', '>=', 10)],
                 consequence='learned_risk_signal',
                 explain='启发式：文本消极 + GAD-7 升高交叉提示焦虑风险'),
        ]


# ──────────────────────────────────────────────
# 神经符号引擎（核心）
# ──────────────────────────────────────────────

class NeuroSymbolicEngine:
    """
    神经符号双引擎推理：

    1. 接收多模态特征（来自神经感知层）
    2. 依次评估规则库中的每条规则，收集激活的规则
    3. 根据激活规则计算各维度风险分数（0-100）
    4. 综合得出风险等级 + 生成人类可读的"推理链路"
    5. （可选）调用 LLM 生成个性化安慰建议

    输出 RiskAssessment，包含完整可追溯的依据链。
    """

    def __init__(self, rule_base: Optional[RuleBase] = None) -> None:
        self.rule_base = rule_base or RuleBase()
        self.learner = RuleLearner()

    def assess(self, features: RiskFeature,
               generate_llm_suggestion: bool = True,
               open_text: Optional[str] = None) -> RiskAssessment:
        """
        执行一次完整评估。

        Parameters
        ----------
        features : RiskFeature
            10 维特征向量（来自 build_feature_vector）
        generate_llm_suggestion : bool
            是否调用 LLM 生成个性化建议（默认 True，失败自动降级）
        open_text : Optional[str]
            用户开放文本，用于危机分级匹配关键词

        Returns
        -------
        RiskAssessment  分数 + 推理链 + 建议 + 危机分级 + 知识库建议
        """
        t0 = time.time()
        feat_dict = features.to_dict()

        # ── 0. 危机分级（基于开放文本关键词 + 已计算的自杀风险特征） ──
        crisis_level, crisis_hits = classify_crisis(
            open_text or '',
            suicide_feature=feat_dict.get('text_suicide_risk', 0),
        )

        # ── 1. 遍历规则库，收集激活规则 ──
        activations: List[RuleActivation] = []
        for rule in self.rule_base.rules:
            satisfied, met_list = rule.evaluate(feat_dict)
            if satisfied:
                details: List[str] = []
                for (feat, op, thr), met in zip(rule.conditions, met_list):
                    actual = feat_dict.get(feat, 0)
                    sign = ' ✓' if met else ''
                    details.append(f'  · {feat} {op} {thr}? 实际={actual:.1f}{sign}')
                activations.append(RuleActivation(
                    rule_id=rule.id,
                    explain=rule.explain,
                    priority=rule.priority,
                    met_conditions=met_list,
                    condition_details=details,
                ))

        log.info('规则评估完成：激活 %d/%d 条', len(activations), len(self.rule_base.rules))

        # ── 2. 分维度计算风险分 ──
        dim_scores = {
            'depression': self._calc_dim_score(activations, 'depression', feat_dict),
            'anxiety':    self._calc_dim_score(activations, 'anxiety', feat_dict),
            'suicide':    self._calc_dim_score(activations, 'suicide', feat_dict),
        }

        # ── 3. 综合分 + 等级 + 建议 ──
        max_score = max(dim_scores.values())
        risk_level, recommendation = self._level_and_recommend(max_score)

        # ── 4. LLM 个性化建议（失败降级，不阻塞主流程） ──
        llm_suggestion = ''
        if generate_llm_suggestion:
            try:
                from backend.core.llm_client import generate_suggestion
                suicide_flag = feat_dict.get('text_suicide_risk', 0) > 0
                llm_suggestion = generate_suggestion(
                    level=risk_level,
                    score=max_score,
                    depression=dim_scores['depression'],
                    anxiety=dim_scores['anxiety'],
                    suicide_flag=suicide_flag,
                    activated_rules=[a.__dict__ for a in activations],
                )
            except Exception as e:
                log.warning('LLM 建议生成失败，降级: %s', e)

        # ── 5. 构建推理链路 ──
        chain = self._build_explanation_chain(
            activations, feat_dict,
            dim_scores['depression'], dim_scores['anxiety'], dim_scores['suicide'],
        )

        # ── 6. RAG 知识库检索（按 risk_level + 特征维度匹配） ──
        # 维度标签：CRISIS 优先拉 crisis_resources
        base_level = risk_level.upper() if risk_level else 'LOW'
        effective_level = base_level if base_level not in ('LOW', 'MEDIUM', 'HIGH', 'URGENT') else base_level
        if crisis_level == 'CRISIS':
            effective_level = 'URGENT'
        dimensions = []
        if open_text and ('学习' in open_text or '考试' in open_text or '论文' in open_text):
            dimensions.append('academic')
        if dim_scores['depression'] > 50:
            dimensions.append('cognitive')
        knowledge_suggestions = retrieve_knowledge(effective_level, dimensions)

        elapsed_ms = (time.time() - t0) * 1000
        log.info('评估完成：level=%s crisis=%s score=%.1f elapsed=%.0fms llm=%s kb=%d条',
                 risk_level, crisis_level, max_score, elapsed_ms,
                 bool(llm_suggestion), len(knowledge_suggestions))

        return RiskAssessment(
            overall_risk_level=risk_level,
            overall_risk_score=round(max_score, 2),
            depression_score=round(dim_scores['depression'], 2),
            anxiety_score=round(dim_scores['anxiety'], 2),
            suicide_risk_score=round(dim_scores['suicide'], 2),
            activated_rules=activations,
            features_used=feat_dict,
            explanation_chain=chain,
            recommendation=recommendation,
            llm_suggestion=llm_suggestion,
            crisis_level=crisis_level,
            crisis_hits=crisis_hits,
            knowledge_suggestions=knowledge_suggestions,
            elapsed_ms=elapsed_ms,
        )

    def _calc_dim_score(self, activations: List[RuleActivation],
                        dim: str, feat: Dict[str, Any]) -> float:
        """为某个维度计算 0-100 的风险分。

        基础分来自对应量表得分归一化，激活规则按优先级加权提升。
        """
        base_map = {
            'depression': ('phq9_score', 27),
            'anxiety':    ('gad7_score', 21),
            'suicide':    ('text_suicide_risk', 10),
        }
        feat_key, max_val = base_map[dim]
        raw = feat.get(feat_key, 0)
        score = min(100, raw / max_val * 100)

        for act in activations:
            score += act.priority * 2

        return min(100, score)

    def _level_and_recommend(self, score: float) -> Tuple[str, str]:
        """综合分 → 风险等级 + 简短建议。"""
        if score >= 76:
            return 'urgent', '综合评分极高，建议立即联系专业心理干预。'
        elif score >= 56:
            return 'high', '综合评分较高，建议尽快联系专业心理咨询师。'
        elif score >= 36:
            return 'medium', '存在一定心理压力，建议关注情绪变化并预约校内咨询。'
        else:
            return 'low', '各项指标正常，建议保持良好的学习生活习惯。'

    def _build_explanation_chain(self, activations, feat, dep, anx, sui) -> List[str]:
        """构建人类可读的推理链路（时间序列，每步有说明）。"""
        chain: List[str] = []
        chain.append(f'开始神经符号推理，输入特征数：{len(feat)}')
        chain.append(f'规则库激活规则数：{len(activations)}（总计 {len(self.rule_base.rules)} 条规则）')

        for act in sorted(activations, key=lambda a: a.priority, reverse=True):
            chain.append(f'  ✓ [规则 {act.rule_id}] {act.explain}')
            if act.condition_details:
                chain.extend(act.condition_details)

        chain.append('--- 分维度风险分 ---')
        chain.append(f'  抑郁  {dep:.1f}/100  （PHQ-9={feat.get("phq9_score", "?")}）')
        chain.append(f'  焦虑  {anx:.1f}/100  （GAD-7={feat.get("gad7_score", "?")}）')
        chain.append(f'  自杀风险  {sui:.1f}/100  （文本关键词={feat.get("text_suicide_risk", 0)}）')
        chain.append('综合最高风险 → 结论给出 100% 可复核的结论。')

        return chain


# ──────────────────────────────────────────────
# 单例获取
# ──────────────────────────────────────────────

_engine_instance: Optional[NeuroSymbolicEngine] = None


def get_engine() -> NeuroSymbolicEngine:
    """获取全局单例引擎（进程内复用，避免重复加载规则）。"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = NeuroSymbolicEngine()
    return _engine_instance


# ──────────────────────────────────────────────
# 危机分级（UMoodBuddy 三层架构简化版）
# ──────────────────────────────────────────────

def classify_crisis(text: str, suicide_feature: float = 0.0) -> Tuple[str, List[str]]:
    """四级危机分级：CRISIS > HIGH > MEDIUM > LOW。

    先扫描开放文本中的所有关键词，再结合 features 里的
    text_suicide_risk 计数综合判定。

    Returns
    -------
    (危机等级, 命中的关键词列表)  —— 包含真实文本词 + 特征层兜底标记
    """
    from config.settings import CRISIS_KEYWORDS

    all_hits: List[str] = []
    worst_level = 'LOW'

    # 1. 扫描文本关键词（从最紧急到一般困扰，累计所有命中词）
    for level_key in ['LEVEL_1_IMMEDIATE', 'LEVEL_2_PLANNING',
                      'LEVEL_3_RISK', 'LEVEL_4_DISTRESS']:
        keywords = CRISIS_KEYWORDS.get(level_key, [])
        found = [k for k in keywords if k in text]
        if found:
            all_hits.extend(found)
            if worst_level == 'LOW':
                if level_key == 'LEVEL_1_IMMEDIATE':
                    worst_level = 'CRISIS'
                elif level_key == 'LEVEL_2_PLANNING':
                    worst_level = 'HIGH'
                elif level_key == 'LEVEL_3_RISK':
                    worst_level = 'MEDIUM'
                else:
                    worst_level = 'LOW'

    # 2. 特征层兜底：text_suicide_risk >= 3 直接 CRISIS
    if suicide_feature >= 3:
        all_hits.append('(特征层) 自杀关键词命中 ≥ 3')
        worst_level = 'CRISIS'

    return worst_level, sorted(set(all_hits))


def retrieve_knowledge(level: str, dimensions: List[str]) -> List[str]:
    """按 risk_level + 维度标签从知识库检索匹配的干预建议。

    纯 dict 检索（等价于轻量 RAG，无向量依赖）。

    Parameters
    ----------
    level : str
        'LOW' / 'MEDIUM' / 'HIGH' / 'URGENT'
    dimensions : List[str]
        可选维度：'academic', 'cognitive', 'tools', 'crisis_resources'

    Returns
    -------
    List[str]  最多 5 条建议（去重）
    """
    from config.settings import MENTAL_HEALTH_KB

    kb = MENTAL_HEALTH_KB.get(level, {})
    picked: List[str] = []

    # 1. 优先匹配传入的维度
    for dim in dimensions:
        for item in kb.get(dim, []):
            if item not in picked:
                picked.append(item)
                if len(picked) >= 5:
                    break
        if len(picked) >= 5:
            break

    # 2. 兜底：general / crisis_resources / cognitive 依次补充
    for fallback_key in ('general', 'crisis_resources', 'tools', 'cognitive'):
        for item in kb.get(fallback_key, []):
            if item not in picked:
                picked.append(item)
                if len(picked) >= 5:
                    break
        if len(picked) >= 5:
            break

    # 3. 如果该 level 完全没有 → 拿 LOW 的 general 做最后的兜底
    if not picked:
        picked = list(MENTAL_HEALTH_KB.get('LOW', {}).get('general', []))[:3]

    return picked[:5]
