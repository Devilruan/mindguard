# -*- coding: utf-8 -*-
"""
backend.core.llm_client
LLM 个性化建议生成：规则推理后调用大模型生成温柔的安慰 + 建议话术。
走 DeepSeek API（OpenAI 兼容格式），失败时自动降级为固定建议模板。
"""
from __future__ import annotations
import json
import logging
import time
from typing import Optional, Dict, Any

from config.settings import LLM_ENABLED, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# 降级建议模板（LLM 不可用时兜底）
# ──────────────────────────────────────────────

_FALLBACK_BY_LEVEL = {
    'urgent': (
        '综合评分显示需要尽快获得专业帮助。\n'
        '建议你今天就拨打全国心理援助热线 12356（24 小时），或直接前往学校心理咨询室。\n'
        '也可以尝试 4-7-8 呼吸法：吸气 4 秒，屏息 7 秒，呼气 8 秒，连续 4 轮能帮你稳定情绪。'
    ),
    'high': (
        '你的心理压力评分较高，建议在本周内预约一次学校心理咨询。\n'
        '4-7-8 呼吸法或"着陆技术"（说出 5 个你看到的东西 → 3 种声音 → 1 种触摸）可以帮你在焦虑发作时快速稳定。'
    ),
    'medium': (
        '目前存在一定的情绪压力，但还在可控范围。\n'
        '可以尝试情绪日记：每天睡前 5 分钟，写下"发生了什么、我感受到什么、我做了什么应对"，帮助自己识别情绪模式。\n'
        '如果持续两周以上没有好转，建议预约一次心理咨询进一步评估。'
    ),
    'low': (
        '各项指标正常，目前心理状态良好。\n'
        '保持规律作息、适度运动和与朋友/家人的社会连接，是维护心理健康最有效的日常策略。'
    ),
}


def _fallback(level: str) -> str:
    """返回降级模板"""
    return _FALLBACK_BY_LEVEL.get(level, _FALLBACK_BY_LEVEL['low'])


# ──────────────────────────────────────────────
# LLM 调用（requests + DeepSeek 兼容 OpenAI 格式）
# ──────────────────────────────────────────────

_PROMPT_TEMPLATE = """你是一位温和、共情、专业的心理健康助手。

下面是一位匿名用户的心理筛查结果（仅用于风险提示，不构成诊断）：

风险等级：{level}（low / medium / high / urgent）
综合风险分：{score}（0-100，越高风险越大）
抑郁分：{depression:.1f} / 100
焦虑分：{anxiety:.1f} / 100
自杀风险标记：{suicide_flag}

激活规则：
{rules_text}

请用 150-200 字生成一段温柔、安慰、不诊断的建议，要求：
1. 语言温和，避免说教或命令语气
2. 不要使用医学术语，不要给出药物建议
3. 可以推荐 1-2 个简单的自我调节技巧（如 4-7-8 呼吸法、着陆技术、渐进式肌肉放松）
4. 如果风险等级较高（high/urgent），明确提示建议寻求专业帮助，并提到全国心理援助热线 12356
5. 不要提到 AI 或"系统"，用第一人称口吻"""


def generate_suggestion(
    level: str,
    score: float,
    depression: float,
    anxiety: float,
    suicide_flag: bool,
    activated_rules: list,
    timeout: float = 8.0,
) -> str:
    """
    根据规则推理结果生成个性化建议。

    优先调用 LLM（DeepSeek），不可用时降级为固定模板。
    返回一段 150-200 字的中文建议文本。
    """
    if not LLM_ENABLED or not LLM_API_KEY:
        log.debug('LLM 未启用，使用降级模板')
        return _fallback(level)

    try:
        import requests
    except ImportError:
        log.warning('requests 未安装，降级')
        return _fallback(level)

    rules_text = '\n'.join(
        f'  - {r.get("rule_id", "?")}: {r.get("explain", "")}'
        for r in (activated_rules or [])
    ) or '（无激活规则）'

    prompt = _PROMPT_TEMPLATE.format(
        level=level,
        score=score,
        depression=depression,
        anxiety=anxiety,
        suicide_flag='是' if suicide_flag else '否',
        rules_text=rules_text,
    )

    # 带一次重试的 LLM 调用
    last_err: Optional[Exception] = None
    for attempt in (1, 2):
        try:
            t0 = time.time()
            resp = requests.post(
                f'{LLM_BASE_URL.rstrip("/")}/chat/completions',
                headers={
                    'Authorization': f'Bearer {LLM_API_KEY}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': LLM_MODEL,
                    'messages': [
                        {'role': 'system', 'content': '你是一位温和、共情的心理健康助手。'},
                        {'role': 'user', 'content': prompt},
                    ],
                    'temperature': 0.6,
                    'max_tokens': 400,
                },
                timeout=timeout,
            )
            elapsed_ms = (time.time() - t0) * 1000

            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content'].strip()
                log.info('LLM 建议生成成功 (%.0fms, %d chars)', elapsed_ms, len(content))
                return content

            log.warning('LLM 返回 %d，尝试 %d', resp.status_code, attempt)
            last_err = RuntimeError(f'HTTP {resp.status_code}: {resp.text[:200]}')
        except Exception as e:
            last_err = e
            log.warning('LLM 调用失败 (attempt %d): %s', attempt, e)

    log.error('LLM 调用最终失败，降级：%s', last_err)
    return _fallback(level)
