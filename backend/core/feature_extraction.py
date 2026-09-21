# -*- coding: utf-8 -*-
"""
backend.core.feature_extraction
多模态特征提取：量表评分 + 文本情绪 + 语音韵律 + 作答行为

降级策略：
  BERT 未加载 → 关键词规则匹配
  librosa 未加载 → 语音模块跳过
"""
from __future__ import annotations
import logging
from typing import List, Optional, Dict, Any

from backend.core.neuro_symbolic.engine import RiskFeature
from config.settings import (
    SUICIDE_KEYWORDS, ANXIETY_KEYWORDS, DEPRESSION_KEYWORDS,
    NEGATIVE_EMOTION_WORDS, FEATURE_NAMES,
)

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 可选依赖（未安装不影响核心流程）
# ──────────────────────────────────────────────

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

try:
    import torch
    from transformers import BertTokenizer, BertModel
    HAS_BERT = True
except ImportError:
    HAS_BERT = False


# ──────────────────────────────────────────────
# PHQ-9 / GAD-7 量表评分
# ──────────────────────────────────────────────

def calc_phq9_score(answers: List[int]) -> float:
    """PHQ-9 抑郁筛查得分（0-27）"""
    if not answers:
        return 0.0
    return float(sum(int(a) for a in answers[:9]))


def calc_gad7_score(answers: List[int]) -> float:
    """GAD-7 焦虑筛查得分（0-21）"""
    if not answers:
        return 0.0
    return float(sum(int(a) for a in answers[:7]))


# ──────────────────────────────────────────────
# 文本情绪特征提取
# ──────────────────────────────────────────────

def extract_text_features(text: str) -> Dict[str, Any]:
    """
    从开放文本提取情绪特征。

    优先使用 BERT 语义分析（text_negativity 0-1），
    降级为关键词词典匹配（各类消极词计数）。
    """
    result = {
        'text_negativity': 0.0,
        'text_anxiety_keywords': 0,
        'text_depression_keywords': 0,
        'text_suicide_risk': 0,
    }

    if not text or not text.strip():
        return result

    text_lower = text.lower()

    # 关键词计数（始终执行，作为降级+补充信号）
    for kw in SUICIDE_KEYWORDS:
        result['text_suicide_risk'] += text_lower.count(kw)
    for kw in ANXIETY_KEYWORDS:
        result['text_anxiety_keywords'] += text_lower.count(kw)
    for kw in DEPRESSION_KEYWORDS:
        result['text_depression_keywords'] += text_lower.count(kw)

    # BERT 语义分析（如果可用）
    if HAS_BERT:
        try:
            result['text_negativity'] = _bert_negativity(text)
        except Exception:
            result['text_negativity'] = _keyword_negativity(text_lower)
    else:
        # 降级：基于关键词密度估计消极度
        result['text_negativity'] = _keyword_negativity(text_lower)

    return result


def _keyword_negativity(text_lower: str) -> float:
    """基于关键词密度估计文本消极度（0-1）"""
    if not text_lower:
        return 0.0

    total_neg = sum(text_lower.count(kw) for kw in NEGATIVE_EMOTION_WORDS)

    # 粗略估计文本长度（中文字符数）
    # 中文一字一 token，英文按词数
    chinese_chars = sum(1 for c in text_lower if '\u4e00' <= c <= '\u9fff')
    total_chars = max(len(text_lower), chinese_chars)
    density = total_neg / max(total_chars, 1)

    # 映射到 0-1（密度 > 0.1 算较高消极度）
    return min(1.0, density * 50.0)


def _bert_negativity(text: str) -> float:
    """BERT 嵌入余弦相似度估计消极度（简化实现）"""
    # 真实场景这里应该用预训练的 BERT 模型提取 CLS 向量，
    # 然后与"消极情绪"原型向量做余弦相似度。
    # 由于环境限制，这里用关键词法作为占位实现。
    return _keyword_negativity(text.lower())


# ──────────────────────────────────────────────
# 语音韵律特征提取（可选）
# ──────────────────────────────────────────────

def extract_speech_features(audio_path: Optional[str]) -> Dict[str, float]:
    """从语音文件提取韵律特征（基频标准差、语速、jitter）"""
    result = {
        'speech_pitch_std': 0.0,
        'speech_speaking_rate': 0.0,
        'speech_jitter': 0.0,
    }

    if not audio_path or not HAS_LIBROSA:
        return result

    try:
        y, sr = librosa.load(audio_path, sr=22050)
        # 基频跟踪
        f0, voiced_flag, _ = librosa.pyin(y, fmin=80, fmax=400, sr=sr)
        voiced_f0 = f0[voiced_flag]
        if len(voiced_f0) > 0:
            result['speech_pitch_std'] = float(voiced_f0.std())
        # 语速估算（每秒语音段数）
        speech_segments = len(voiced_flag) / max(len(y) / sr, 0.1)
        result['speech_speaking_rate'] = float(speech_segments)
        # Jitter（简化：相邻基频变化率）
        if len(voiced_f0) > 1:
            diffs = abs(voiced_f0[1:] - voiced_f0[:-1])
            result['speech_jitter'] = float(diffs.mean() / max(voiced_f0.mean(), 1))
    except Exception:
        pass

    return result


# ──────────────────────────────────────────────
# 组装 RiskFeature
# ──────────────────────────────────────────────

def build_feature_vector(
    phq9_answers: List[int],
    gad7_answers: List[int],
    open_text: Optional[str] = None,
    audio_path: Optional[str] = None,
    response_duration_sec: Optional[float] = None,
) -> RiskFeature:
    """
    将各模态输入组装成 10 维 RiskFeature 特征向量。

    参数
    ----
    phq9_answers : PHQ-9 九题答案（0-3 分整数列表）
    gad7_answers : GAD-7 七题答案
    open_text    : 开放文本（可选）
    audio_path   : 语音文件路径（可选）
    response_duration_sec : 作答总时长

    返回
    ----
    RiskFeature dataclass（可直接传给 NeuroSymbolicEngine.assess()）
    """
    text_feats = extract_text_features(open_text or '')
    speech_feats = extract_speech_features(audio_path)

    return RiskFeature(
        phq9_score=calc_phq9_score(phq9_answers),
        gad7_score=calc_gad7_score(gad7_answers),
        text_negativity=text_feats['text_negativity'],
        text_anxiety_keywords=text_feats['text_anxiety_keywords'],
        text_depression_keywords=text_feats['text_depression_keywords'],
        text_suicide_risk=text_feats['text_suicide_risk'],
        speech_pitch_std=speech_feats['speech_pitch_std'],
        speech_speaking_rate=speech_feats['speech_speaking_rate'],
        speech_jitter=speech_feats['speech_jitter'],
        response_duration_sec=float(response_duration_sec or 0),
    )
