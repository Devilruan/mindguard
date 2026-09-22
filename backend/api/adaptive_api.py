# -*- coding: utf-8 -*-
"""
backend.api.adaptive_api
═══════════════════════
自适应心理测评引擎 (CAT - Computerized Adaptive Testing)

核心思想：
  不用固定的 PHQ-9/GAD-7 量表，而是从 50+ 题的多维心理题库中，
  根据用户已答题目，用「贝叶斯概率更新 + 信息增益」动态选择下一题，
  让测评在更少题目下达到更高精度。

算法流程：
  1. 初始化：8 个心理维度的先验分布（均匀分布）
  2. 用户答题 → 贝叶斯更新对应维度的后验概率
  3. 计算每道未答题目对当前不确定性的「信息增益」
  4. 选信息增益最大的题 → 重复 2-3
  5. 当总不确定性低于阈值 或 答够 20 题 → 结束

题库维度（8 维，覆盖大学生常见心理困扰）：
  - depression   抑郁情绪
  - anxiety      焦虑情绪
  - sleep        睡眠质量
  - social       社交恐惧
  - perfection   完美主义
  - burnout      学业倦怠
  - loneliness   孤独感
  - emotion_reg  情绪调节困难
"""
from __future__ import annotations
import json
import math
import random
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

log = logging.getLogger(__name__)
router = APIRouter()


# ════════════════════════════════════════════════════════════
# Part 1: 多维心理题库（52 题）
# 每题绑定 1-2 个心理维度，带「区分度 a」和「难度 b」参数
# 参照：项目反应理论 (IRT) 双参数逻辑斯蒂模型
# ════════════════════════════════════════════════════════════

ITEM_BANK = [
    # ── 抑郁情绪 (depression) ──
    {'id': 'd1', 'dim': 'depression', 'text': '做事时提不起劲或没有兴趣', 'a': 1.2, 'b': 0.5},
    {'id': 'd2', 'dim': 'depression', 'text': '感到心情低落、沮丧或绝望', 'a': 1.4, 'b': 0.8},
    {'id': 'd3', 'dim': 'depression', 'text': '觉得自己很糟或让家人失望', 'a': 1.1, 'b': 1.2},
    {'id': 'd4', 'dim': 'depression', 'text': '对未来感到没有希望', 'a': 1.3, 'b': 1.0},
    {'id': 'd5', 'dim': 'depression', 'text': '什么都不想做，只想一个人待着', 'a': 1.0, 'b': 0.6},
    {'id': 'd6', 'dim': 'depression', 'text': '觉得活着没什么意思', 'a': 1.5, 'b': 1.8},
    {'id': 'd7', 'dim': 'depression', 'text': '无法集中注意力做任何事', 'a': 0.9, 'b': 0.4},

    # ── 焦虑情绪 (anxiety) ──
    {'id': 'a1', 'dim': 'anxiety', 'text': '感到紧张、焦虑或烦躁', 'a': 1.3, 'b': 0.5},
    {'id': 'a2', 'dim': 'anxiety', 'text': '不能停止或控制担忧', 'a': 1.2, 'b': 0.7},
    {'id': 'a3', 'dim': 'anxiety', 'text': '对各种事情过度担忧', 'a': 1.0, 'b': 0.9},
    {'id': 'a4', 'dim': 'anxiety', 'text': '难以放松下来', 'a': 1.1, 'b': 0.6},
    {'id': 'a5', 'dim': 'anxiety', 'text': '容易烦恼或易怒', 'a': 0.9, 'b': 0.3},
    {'id': 'a6', 'dim': 'anxiety', 'text': '害怕有可怕的事情发生', 'a': 1.4, 'b': 1.1},
    {'id': 'a7', 'dim': 'anxiety', 'text': '出现心慌、出汗、发抖等身体反应', 'a': 1.2, 'b': 1.3},

    # ── 睡眠质量 (sleep) ──
    {'id': 's1', 'dim': 'sleep', 'text': '入睡困难（躺下后很久才能睡着）', 'a': 1.1, 'b': 0.4},
    {'id': 's2', 'dim': 'sleep', 'text': '夜间容易醒来', 'a': 0.9, 'b': 0.3},
    {'id': 's3', 'dim': 'sleep', 'text': '比平时早醒很多，再也睡不着', 'a': 1.2, 'b': 0.8},
    {'id': 's4', 'dim': 'sleep', 'text': '睡眠过多（每天超过 10 小时）', 'a': 0.8, 'b': 0.6},
    {'id': 's5', 'dim': 'sleep', 'text': '睡了一晚还是觉得没休息好', 'a': 1.0, 'b': 0.5},
    {'id': 's6', 'dim': 'sleep', 'text': '白天经常打瞌睡', 'a': 0.9, 'b': 0.7},

    # ── 社交恐惧 (social) ──
    {'id': 'o1', 'dim': 'social', 'text': '在人群中感到不自在', 'a': 1.1, 'b': 0.5},
    {'id': 'o2', 'dim': 'social', 'text': '害怕别人注意到自己', 'a': 1.3, 'b': 0.9},
    {'id': 'o3', 'dim': 'social', 'text': '不敢在课堂上发言或做汇报', 'a': 1.2, 'b': 1.0},
    {'id': 'o4', 'dim': 'social', 'text': '回避社交场合，尽量一个人待着', 'a': 1.0, 'b': 0.7},
    {'id': 'o5', 'dim': 'social', 'text': '在陌生人面前容易紧张', 'a': 1.0, 'b': 0.4},
    {'id': 'o6', 'dim': 'social', 'text': '担心自己说的话会被别人笑话', 'a': 1.2, 'b': 0.8},

    # ── 完美主义 (perfection) ──
    {'id': 'p1', 'dim': 'perfection', 'text': '对自己要求很高，容不得一点错误', 'a': 1.1, 'b': 0.6},
    {'id': 'p2', 'dim': 'perfection', 'text': '做事必须做到"最好"才肯罢休', 'a': 1.2, 'b': 0.8},
    {'id': 'p3', 'dim': 'perfection', 'text': '经常因为小事反复纠结', 'a': 0.9, 'b': 0.5},
    {'id': 'p4', 'dim': 'perfection', 'text': '达不到自己的标准就会很沮丧', 'a': 1.0, 'b': 0.9},
    {'id': 'p5', 'dim': 'perfection', 'text': '害怕失败，所以不敢尝试新事物', 'a': 1.3, 'b': 1.1},

    # ── 学业倦怠 (burnout) ──
    {'id': 'b1', 'dim': 'burnout', 'text': '对学习感到厌倦', 'a': 1.2, 'b': 0.5},
    {'id': 'b2', 'dim': 'burnout', 'text': '学习时容易分心，效率很低', 'a': 1.0, 'b': 0.4},
    {'id': 'b3', 'dim': 'burnout', 'text': '觉得学习毫无意义', 'a': 1.3, 'b': 1.0},
    {'id': 'b4', 'dim': 'burnout', 'text': '经常拖到最后一刻才开始做事', 'a': 0.9, 'b': 0.6},
    {'id': 'b5', 'dim': 'burnout', 'text': '课业压力大到快要承受不住', 'a': 1.4, 'b': 1.3},
    {'id': 'b6', 'dim': 'burnout', 'text': '经常熬夜赶作业/复习', 'a': 0.8, 'b': 0.3},

    # ── 孤独感 (loneliness) ──
    {'id': 'l1', 'dim': 'loneliness', 'text': '经常感到孤独', 'a': 1.2, 'b': 0.7},
    {'id': 'l2', 'dim': 'loneliness', 'text': '觉得没有人真正理解自己', 'a': 1.3, 'b': 0.9},
    {'id': 'l3', 'dim': 'loneliness', 'text': '有心里话找不到人说', 'a': 1.1, 'b': 0.6},
    {'id': 'l4', 'dim': 'loneliness', 'text': '即使在人群中也感觉很孤单', 'a': 1.2, 'b': 1.1},
    {'id': 'l5', 'dim': 'loneliness', 'text': '很少有机会和朋友好好聊聊', 'a': 0.9, 'b': 0.5},

    # ── 情绪调节困难 (emotion_reg) ──
    {'id': 'e1', 'dim': 'emotion_reg', 'text': '情绪来得很快，自己控制不住', 'a': 1.1, 'b': 0.5},
    {'id': 'e2', 'dim': 'emotion_reg', 'text': '心情不好时很难自己调节过来', 'a': 1.2, 'b': 0.7},
    {'id': 'e3', 'dim': 'emotion_reg', 'text': '容易被小事激怒或难过', 'a': 1.0, 'b': 0.4},
    {'id': 'e4', 'dim': 'emotion_reg', 'text': '知道自己该"想开点"但就是做不到', 'a': 1.1, 'b': 0.8},
    {'id': 'e5', 'dim': 'emotion_reg', 'text': '情绪低落时会持续很久', 'a': 1.0, 'b': 0.6},
]

# 8 维度元数据（用于前端雷达图 + 解释文案）
DIMENSION_META = {
    'depression':   {'name': '抑郁情绪',     'icon': '😔', 'color': '#6366F1', 'desc': '持续的悲伤、空虚或绝望感',
                     'high': '建议关注：你近期情绪低落较为明显，可能需要更多自我关怀或专业支持。',
                     'low': '情绪状态良好，能正常应对日常起伏。'},
    'anxiety':      {'name': '焦虑情绪',     'icon': '😰', 'color': '#F59E0B', 'desc': '过度担忧、紧张或烦躁不安',
                     'high': '建议关注：焦虑水平偏高，试试呼吸练习或规律运动来缓解。',
                     'low': '心态较为平和，能较好应对压力。'},
    'sleep':        {'name': '睡眠质量',     'icon': '😴', 'color': '#8B5CF6', 'desc': '入睡、维持或恢复性睡眠的困难',
                     'high': '建议关注：睡眠可能在影响你的情绪，试试固定作息时间。',
                     'low': '睡眠质量不错，身体恢复良好。'},
    'social':       {'name': '社交适应',     'icon': '🙋', 'color': '#EC4899', 'desc': '在社交场合中的不安与回避',
                     'high': '建议关注：社交让你感到压力，从微笑打招呼开始可能会有帮助。',
                     'low': '在社交中比较自在，能建立良好的人际关系。'},
    'perfection':   {'name': '完美主义',     'icon': '🎯', 'color': '#EF4444', 'desc': '对自己过高且僵化的标准',
                     'high': '建议关注：完美主义可能在消耗你，试试"足够好"思维。',
                     'low': '对自己要求合理，能接受不完美。'},
    'burnout':      {'name': '学业倦怠',     'icon': '📚', 'color': '#06B6D4', 'desc': '对学习的疲惫、厌倦与无力感',
                     'high': '建议关注：你可能太累了，允许自己休息几天，不是偷懒。',
                     'low': '学习状态良好，有动力也有节奏。'},
    'loneliness':   {'name': '孤独感',       'icon': '🌙', 'color': '#14B8A6', 'desc': '缺乏有意义的人际联结',
                     'high': '建议关注：孤独是信号，试着主动联系一个朋友，哪怕只说一句"最近好吗"。',
                     'low': '有良好的社交支持网络，不感到孤单。'},
    'emotion_reg':  {'name': '情绪调节',     'icon': '🌊', 'color': '#6366F1', 'desc': '管理和调节自身情绪的困难',
                     'high': '建议关注：情绪调节有些费力，CBT 思维记录可能帮得上你。',
                     'low': '能较好地觉察和管理自己的情绪。'},
}

# 选项（4 级李克特量表）
OPTIONS = [
    {'value': 0, 'label': '完全没有'},
    {'value': 1, 'label': '几天'},
    {'value': 2, 'label': '一半以上天数'},
    {'value': 3, 'label': '几乎每天'},
]

# 自适应测试参数
MAX_QUESTIONS = 20          # 最多答题数
MIN_QUESTIONS = 8           # 最少答题数
UNCERTAINTY_THRESHOLD = 0.15 # 不确定性阈值（低于此值停止）


# ════════════════════════════════════════════════════════════
# Part 2: 贝叶斯自适应引擎
# ════════════════════════════════════════════════════════════

class BayesianCATEngine:
    """
    贝叶斯自适应测评引擎。
    对每个维度维护一个 0-1 的"风险程度"连续变量，
    用 Beta 分布近似后验，用 IRT 模型计算题目反应概率。
    """

    def __init__(self):
        # 每个维度的 Beta 分布参数 (alpha, beta)，初始均匀 Beta(1,1)
        self.dim_params: Dict[str, List[float]] = {
            dim: [1.0, 1.0] for dim in DIMENSION_META
        }
        self.answered_ids: List[str] = []
        self.responses: List[Dict] = []
        self.total_entropy_reduction = 0.0

    def _prob_correct(self, item: Dict, theta: float) -> float:
        """
        IRT 双参数模型：P(答题=3 | theta) = sigmoid(a * (theta - b))
        theta: 0~1 的风险程度
        """
        a, b = item['a'], item['b']
        # 映射 theta 到 -3~3 的 IRT 尺度
        theta_scaled = theta * 6.0 - 3.0
        b_scaled = b * 6.0 - 3.0
        z = a * (theta_scaled - b_scaled)
        return 1.0 / (1.0 + math.exp(-z))

    def _expected_entropy(self, dim: str, alpha: float, beta: float) -> float:
        """Beta 分布的近似微分熵"""
        # 用正态近似：Entropy ≈ 0.5 * ln(2πe * Var)
        mean = alpha / (alpha + beta)
        var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        if var < 1e-10:
            return 0.0
        return 0.5 * math.log(2 * math.pi * math.e * var)

    def _mean(self, dim: str) -> float:
        """获取某维度当前后验均值（即风险程度估计 0-1）"""
        a, b = self.dim_params[dim]
        return a / (a + b)

    def _variance(self, dim: str) -> float:
        """获取某维度当前后验方差（即不确定性）"""
        a, b = self.dim_params[dim]
        return (a * b) / ((a + b) ** 2 * (a + b + 1))

    def total_uncertainty(self) -> float:
        """所有维度的方差之和"""
        return sum(self._variance(d) for d in DIMENSION_META)

    def update(self, item_id: str, response: int):
        """
        用户答完一题后，贝叶斯更新对应维度的后验分布。
        
        response: 0/1/2/3 对应"完全没有"到"几乎每天"
        映射到二值似然：>1 = "有症状" (success), <=1 = "无症状" (failure)
        """
        item = next(it for it in ITEM_BANK if it['id'] == item_id)
        dim = item['dim']
        
        # 记录
        self.answered_ids.append(item_id)
        self.responses.append({'item_id': item_id, 'response': response, 'dim': dim})

        alpha, beta = self.dim_params[dim]
        old_entropy = self._expected_entropy(dim, alpha, beta)

        # 贝叶斯更新：Beta 共轭于二项似然
        # 高风险回答 (response >= 2) → 增加 alpha（更确定有症状）
        # 低风险回答 (response <= 1) → 增加 beta（更确定无症状）
        if response >= 2:
            alpha += 1.0
        else:
            beta += 1.0

        self.dim_params[dim] = [alpha, beta]
        new_entropy = self._expected_entropy(dim, alpha, beta)
        self.total_entropy_reduction += (old_entropy - new_entropy)

    def select_next(self) -> Optional[Dict]:
        """
        选择下一题：计算所有未答题的「期望信息增益」，选最大的。
        信息增益 = 当前熵 - 期望后验熵
        """
        remaining = [it for it in ITEM_BANK if it['id'] not in self.answered_ids]
        if not remaining:
            return None

        current_total_entropy = sum(
            self._expected_entropy(d, *self.dim_params[d])
            for d in DIMENSION_META
        )

        best_item = None
        best_gain = -1.0

        for item in remaining:
            dim = item['dim']
            alpha, beta = self.dim_params[dim]
            mean_theta = self._mean(dim)

            # 计算两种可能回答下的期望熵
            p_high = self._prob_correct(item, mean_theta)  # 答高风险的概率
            p_high = max(0.05, min(0.95, p_high))
            p_low = 1.0 - p_high

            # 假设答高风险后的后验
            e_high = self._expected_entropy(dim, alpha + 1.0, beta)
            # 假设答低风险后的后验
            e_low = self._expected_entropy(dim, alpha, beta + 1.0)

            expected_entropy = p_high * e_high + p_low * e_low
            gain = (current_total_entropy - expected_entropy)
            # 轻微随机化，避免完全确定性选题
            gain += random.uniform(0, 0.01)

            if gain > best_gain:
                best_gain = gain
                best_item = item

        return best_item


# ════════════════════════════════════════════════════════════
# Part 3: Pydantic 模型
# ════════════════════════════════════════════════════════════

class AdaptiveAnswer(BaseModel):
    session_id: str
    item_id: str
    response: int  # 0-3


class AdaptiveStart(BaseModel):
    anon_id: Optional[str] = None


# ════════════════════════════════════════════════════════════
# Part 4: API 路由
# ════════════════════════════════════════════════════════════

# 内存中的会话存储（生产环境应换成 Redis/Session）
_sessions: Dict[str, BayesianCATEngine] = {}


@router.get('/info')
def get_adaptive_info():
    """返回题库元数据 + 维度说明（前端初始化用）"""
    return {
        'total_items': len(ITEM_BANK),
        'dimensions': DIMENSION_META,
        'options': OPTIONS,
        'max_questions': MAX_QUESTIONS,
        'min_questions': MIN_QUESTIONS,
    }


@router.post('/start')
def adaptive_start(payload: AdaptiveStart = None):
    """
    开始一次自适应测评。
    返回 session_id + 第一道题。
    """
    engine = BayesianCATEngine()
    session_id = datetime.utcnow().strftime('%Y%m%d%H%M%S') + str(random.randint(100, 999))
    _sessions[session_id] = engine

    first_item = engine.select_next()

    log.info('自适应测评开始 session=%s', session_id)

    return {
        'session_id': session_id,
        'first_question': {
            'item_id': first_item['id'],
            'text': first_item['text'],
            'dimension': first_item['dim'],
            'dim_name': DIMENSION_META[first_item['dim']]['name'],
            'question_num': 1,
            'options': OPTIONS,
        },
        'total_questions': MAX_QUESTIONS,
    }


@router.post('/answer')
def adaptive_answer(payload: AdaptiveAnswer):
    """
    提交一道题的答案，返回下一题或最终结果。
    """
    engine = _sessions.get(payload.session_id)
    if not engine:
        raise HTTPException(404, 'Session 不存在或已过期')

    if payload.item_id in engine.answered_ids:
        raise HTTPException(400, '此题已答')

    engine.update(payload.item_id, payload.response)
    q_num = len(engine.answered_ids)

    # 判断是否结束
    uncertainty = engine.total_uncertainty()
    should_stop = (
        q_num >= MAX_QUESTIONS
        or (q_num >= MIN_QUESTIONS and uncertainty < UNCERTAINTY_THRESHOLD)
    )

    if should_stop:
        # 计算最终结果
        result = _compute_result(engine)
        # 清理会话
        del _sessions[payload.session_id]
        return {
            'finished': True,
            'total_answered': q_num,
            'result': result,
        }

    # 返回下一题
    next_item = engine.select_next()
    return {
        'finished': False,
        'question_num': q_num + 1,
        'next_question': {
            'item_id': next_item['id'],
            'text': next_item['text'],
            'dimension': next_item['dim'],
            'dim_name': DIMENSION_META[next_item['dim']]['name'],
            'question_num': q_num + 1,
            'options': OPTIONS,
        },
        'progress': {
            'answered': q_num,
            'max': MAX_QUESTIONS,
            'uncertainty': round(uncertainty, 4),
            'remaining_uncertainty_pct': round(min(100, uncertainty * 100), 1),
        },
    }


def _compute_result(engine: BayesianCATEngine) -> Dict[str, Any]:
    """
    计算 8 维心理画像 + 综合风险等级 + 干预建议
    """
    dims = {}
    for dim_key, meta in DIMENSION_META.items():
        mean = engine._mean(dim_key)
        var = engine._variance(dim_key)
        # 转为 0-100 分数
        score = round(mean * 100, 1)
        # 风险等级
        if score < 25:
            level, level_color = 'low', '#1C7A6E'
        elif score < 50:
            level, level_color = 'medium', '#E6A817'
        elif score < 75:
            level, level_color = 'high', '#C97B3A'
        else:
            level, level_color = 'urgent', '#AC4E42'

        dims[dim_key] = {
            'name': meta['name'],
            'icon': meta['icon'],
            'color': meta['color'],
            'desc': meta['desc'],
            'score': score,
            'level': level,
            'level_color': level_color,
            'confidence': round((1 - var * 4) * 100, 1),  # 置信度
            'suggestion': meta['high'] if score >= 50 else meta['low'],
        }

    # 综合风险：加权平均（抑郁/焦虑权重更高）
    weights = {
        'depression': 0.25, 'anxiety': 0.20,
        'sleep': 0.10, 'social': 0.10,
        'perfection': 0.08, 'burnout': 0.12,
        'loneliness': 0.08, 'emotion_reg': 0.07,
    }
    overall = sum(dims[k]['score'] * weights[k] for k in weights)
    overall = round(overall, 1)

    if overall < 25:
        risk_level, level_cn = 'low', '🟢 低风险'
    elif overall < 50:
        risk_level, level_cn = 'medium', '🟡 中风险'
    elif overall < 70:
        risk_level, level_cn = 'high', '🟠 高风险'
    else:
        risk_level, level_cn = 'urgent', '🔴 极高风险'

    # 雷达图数据（ECharts 格式）
    radar_indicator = [
        {'name': DIMENSION_META[k]['name'], 'max': 100}
        for k in DIMENSION_META
    ]
    radar_value = [dims[k]['score'] for k in DIMENSION_META]

    # 触发的规则（神经符号风格）
    activated_rules = []
    for dim_key, d in dims.items():
        if d['score'] >= 70:
            activated_rules.append({
                'rule_id': f'CAT-HIGH-{dim_key.upper()}',
                'explain': f'{DIMENSION_META[dim_key]["name"]} 得分 {d["score"]}，达到高风险阈值 (≥70)',
                'priority': 10,
            })
        elif d['score'] >= 50:
            activated_rules.append({
                'rule_id': f'CAT-MED-{dim_key.upper()}',
                'explain': f'{DIMENSION_META[dim_key]["name"]} 得分 {d["score"]}，中度关注 (≥50)',
                'priority': 5,
            })

    return {
        'overall_score': overall,
        'risk_level': risk_level,
        'risk_level_cn': level_cn,
        'dimensions': dims,
        'radar': {
            'indicator': radar_indicator,
            'value': radar_value,
        },
        'activated_rules': activated_rules,
        'answered_count': len(engine.answered_ids),
        'total_entropy_reduction': round(engine.total_entropy_reduction, 3),
        'ai_summary': _generate_summary(dims, overall),
    }


def _generate_summary(dims: Dict, overall: float) -> str:
    """生成一段人话总结"""
    high_dims = [d['name'] for d in dims.values() if d['score'] >= 50]

    if overall >= 70:
        opening = '综合评估显示，你的心理状态目前处于较高风险区间。'
    elif overall >= 50:
        opening = '综合来看，你有几个方面需要给予一些关注。'
    elif overall >= 25:
        opening = '整体心理状态稳定良好，但以下几个方面值得留意。'
    else:
        opening = '你的心理状态非常健康，继续保持这种自我觉察。'

    if high_dims:
        detail = f'其中 {"、".join(high_dims)} 方面得分相对较高。'
    else:
        detail = '各方面得分都在理想区间内。'

    closing = '记住：这个测评只是一次快速的自我扫描，不能替代专业诊断。如果感到困扰，寻求帮助永远是明智的选择。'

    return opening + detail + closing

