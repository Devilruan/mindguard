# -*- coding: utf-8 -*-
"""
config.settings
全局配置常量：路径、数据库、默认规则、关键词词典、LLM 接口

敏感配置通过项目根目录的 .env 文件注入（不提交到版本库）。
"""
from __future__ import annotations
import os
import logging
from pathlib import Path


# ──────────────────────────────────────────────
# .env 加载（纯 Python 实现，避免引入 dotenv 依赖）
# ──────────────────────────────────────────────

def _load_dotenv() -> None:
    """从项目根目录 .env 读取 KEY=VALUE 环境变量（不覆盖已有）"""
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if not env_path.exists():
        return
    with open(env_path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, val = line.partition('=')
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


_load_dotenv()


# ──────────────────────────────────────────────
# 应用基本信息
# ──────────────────────────────────────────────

APP_NAME = '神经符号心理健康风险智能筛查系统'
APP_VERSION = '1.1.0'
APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
APP_PORT = int(os.environ.get('APP_PORT', '8000'))


# ──────────────────────────────────────────────
# 路径（兼容 PyInstaller 打包模式）
# ──────────────────────────────────────────────

def _base_dir() -> Path:
    """返回项目根目录（打包时自动切换到 _MEIPASS）"""
    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


ROOT: Path = _base_dir()
TEMPLATES_DIR: Path = ROOT / 'frontend' / 'templates'
STATIC_DIR: Path = ROOT / 'frontend' / 'static'
DATA_DIR: Path = ROOT / 'data'
RULES_DIR: Path = DATA_DIR


def _resolve_db_path() -> Path:
    """数据库路径：.env > 打包 exe 旁 mmhs.db > 根目录 mmhs.db"""
    env_path = os.environ.get('DB_PATH')
    if env_path:
        p = Path(env_path)
        return p if p.is_absolute() else ROOT / env_path

    import sys
    if getattr(sys, 'frozen', False):
        # 打包版：优先使用 exe 旁的 mmhs.db（可见、可持久化、可携带示例数据）
        exe_side = Path(sys.executable).resolve().parent / 'mmhs.db'
        if exe_side.exists():
            return exe_side
    # 开发模式：源码根目录旁
    dev = ROOT / 'mmhs.db'
    dev.parent.mkdir(parents=True, exist_ok=True)
    return dev


DB_PATH: Path = _resolve_db_path()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


# ──────────────────────────────────────────────
# 管理员默认密码（首次启动时初始化，建议通过 .env 覆盖）
# ──────────────────────────────────────────────

DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')


# ──────────────────────────────────────────────
# LLM 个性化建议（DeepSeek API，兼容 OpenAI 格式）
# ──────────────────────────────────────────────

LLM_ENABLED = bool(os.environ.get('LLM_API_KEY'))
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com/v1')
LLM_MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')


# ──────────────────────────────────────────────
# 10 维特征名（与 RiskFeature dataclass 字段对应）
# ──────────────────────────────────────────────

FEATURE_NAMES = [
    'phq9_score',
    'gad7_score',
    'text_negativity',
    'text_anxiety_keywords',
    'text_depression_keywords',
    'text_suicide_risk',
    'speech_pitch_std',
    'speech_speaking_rate',
    'speech_jitter',
    'response_duration_sec',
]


# ──────────────────────────────────────────────
# 6 条默认心理学规则（R001-R006）
# 依据：PHQ-9 / GAD-7 临床阈值 + 多模态信号补充
# ──────────────────────────────────────────────

DEFAULT_RULES = [
    {
        'id': 'R001',
        'priority': 10,
        'conditions': [('phq9_score', '>=', 20)],
        'consequence': '抑郁高风险',
        'explain': 'PHQ-9 总分 ≥ 20，达到重度抑郁阈值',
    },
    {
        'id': 'R002',
        'priority': 10,
        'conditions': [('gad7_score', '>=', 15)],
        'consequence': '焦虑高风险',
        'explain': 'GAD-7 总分 ≥ 15，达到重度焦虑阈值',
    },
    {
        'id': 'R003',
        'priority': 5,
        'conditions': [('text_depression_keywords', '>=', 3)],
        'consequence': '风险提升',
        'explain': '开放式文本出现 ≥ 3 个消极/抑郁相关词',
    },
    {
        'id': 'R004',
        'priority': 5,
        'conditions': [('speech_pitch_std', '>=', 30.0)],
        'consequence': '情绪激动风险',
        'explain': '语音基频标准差 ≥ 30，提示情绪激动',
    },
    {
        'id': 'R005',
        'priority': 3,
        'conditions': [('response_duration_sec', '<', 60)],
        'consequence': '可能随意作答',
        'explain': '21 题总作答时长 < 60 秒，可能未认真作答',
    },
    {
        'id': 'R006',
        'priority': 3,
        'conditions': [('text_suicide_risk', '>=', 1)],
        'consequence': '自杀风险预警',
        'explain': '文本出现自杀相关表达',
    },
]


# ──────────────────────────────────────────────
# 关键词词典（用于降级模式：BERT 未加载时的规则匹配）
# ──────────────────────────────────────────────

SUICIDE_KEYWORDS = [
    '自杀', '自伤', '想死', '不想活', '结束生命',
    '割腕', '跳楼', '活着没', '活不下去', '一了百了',
    '告别', '遗书', '最后一次',
]

ANXIETY_KEYWORDS = [
    '焦虑', '紧张', '害怕', '担心', '惶恐', '不安',
    '心慌', '冒汗', '发抖', '坐立不安', '静不下',
    '崩溃', '撑不住', '快疯了',
]

DEPRESSION_KEYWORDS = [
    '抑郁', '低落', '绝望', '无助', '没希望',
    '心累', '不想动', '没兴趣', '什么都不想',
    '麻木', '空', '累', '失眠', '吃不下',
    '自我否定', '没用', '很差', '失败',
]

NEGATIVE_EMOTION_WORDS = SUICIDE_KEYWORDS + ANXIETY_KEYWORDS + DEPRESSION_KEYWORDS


# ──────────────────────────────────────────────
# 知情同意文案（前端弹窗用）
# ──────────────────────────────────────────────

CONSENT_TEXT = """
欢迎使用神经符号心理健康风险智能筛查系统。

【目的】本系统通过 PHQ-9 抑郁筛查量表、GAD-7 焦虑筛查量表和简短的开放文本，
为您提供一次快速的心理健康风险评估。

【隐私保护】
· 本系统不收集真实身份信息，您可使用匿名代号
· 文本内容仅提取情绪特征，不保留原文
· 筛查结果仅用于风险提示，不构成医学诊断

【免责声明】
· 本系统输出的风险分数和建议仅供参考，不能替代专业医生的诊断
· 如果评估结果显示"高风险"或"极高风险"，强烈建议您立即联系专业心理咨询
· 全国心理援助热线：12356（24小时） / 010-82951332（危机干预）

点击"同意"即表示您已阅读并理解以上内容。
"""


# ──────────────────────────────────────────────
# PHQ-9 / GAD-7 题目
# ──────────────────────────────────────────────

PHQ9_QUESTIONS = [
    '做事提不起劲或没有兴趣',
    '感到心情低落、沮丧或绝望',
    '入睡困难、睡不安稳或睡眠过多',
    '感觉疲倦或没有活力',
    '食欲不振或吃太多',
    '觉得自己很糟或让家人失望',
    '注意力难以集中（如看报纸、看电视）',
    '动作或说话迟缓/烦躁不安',
    '有不如死掉或用某种方式伤害自己的念头',
]

GAD7_QUESTIONS = [
    '感到紧张、焦虑或烦躁',
    '不能停止或控制担忧',
    '对各种事情过度担忧',
    '难以放松下来',
    '坐立不安、静不下',
    '容易烦恼或易怒',
    '害怕有可怕的事情发生',
]

QUESTION_OPTIONS = [
    {'value': 0, 'label': '完全没有'},
    {'value': 1, 'label': '几天'},
    {'value': 2, 'label': '一半以上天数'},
    {'value': 3, 'label': '几乎每天'},
]


# ──────────────────────────────────────────────
# 危机分级词库（四级，用于文本关键词匹配分层干预）
# 按紧急程度从高到低，命中即停
# ──────────────────────────────────────────────
CRISIS_KEYWORDS: dict[str, list[str]] = {
    'LEVEL_1_IMMEDIATE': [
        '自杀', '去死', '不想活了', '结束生命', '结束一切',
        '跳楼', '割腕', '上吊', '服毒', '自焚', '绝食',
        '不想活', '活不下去', '死了算了',
    ],
    'LEVEL_2_PLANNING': [
        '不想上学', '不想见人', '活着没意思', '没希望',
        '有个想法', '想好了', '准备好了', '撑不住了',
    ],
    'LEVEL_3_RISK': [
        '很累', '压力大', '扛不住', '抑郁', '焦虑', '崩溃',
        '放弃', '熬不下去', '身心俱疲',
    ],
    'LEVEL_4_DISTRESS': [
        '烦恼', '心情不好', '不开心', '难过', '迷茫',
        '烦', '累', '闷', '纠结',
    ],
}

CRISIS_LEVEL_META: dict[str, tuple[str, str]] = {
    'CRISIS': ('IMMEDIATE', '#AC4E42'),   # (中文标签, 强调色)
    'HIGH':   ('HIGH_RISK',  '#D97706'),
    'MEDIUM': ('MEDIUM_RISK','#F59E0B'),
    'LOW':    ('LOW_RISK',   '#1C7A6E'),
}


# ──────────────────────────────────────────────
# RAG 心理干预知识库（结构化，用于按特征维度检索匹配建议）
# 参考：《大学生心理健康教育》第 3 版 / Kroenke 2001 / Spitzer 2006
# ──────────────────────────────────────────────
MENTAL_HEALTH_KB: dict[str, dict[str, list[str]]] = {
    'LOW': {
        'general': [
            '保持规律作息，每天保证 7-8 小时睡眠',
            '适度运动（每天 30 分钟快走）能有效降低焦虑激素',
            '找 1-2 个信任的朋友聊聊近况，社交联结是天然的情绪缓冲',
        ],
        'academic': [
            '学业压力大时试试番茄工作法（25 分钟专注 + 5 分钟休息）',
            '和导师聊聊科研方向，很多焦虑来自"不确定"而非"做不好"',
        ],
    },
    'MEDIUM': {
        'general': [
            '建议去校心理中心做一次免费的一对一咨询（通常 48 小时内可预约）',
            '尝试写情绪日记：每天记下 3 件小事 + 1 件让你纠结的事，写出来会轻很多',
            '限制咖啡因摄入，下午 6 点后不碰手机 1 小时，观察睡眠质量变化',
        ],
        'tools': [
            '正念类 APP「Headspace」「潮汐」：每天 10 分钟呼吸练习',
            '自助阅读《伯恩斯新情绪疗法》（认知行为疗法经典自助手册）',
        ],
    },
    'HIGH': {
        'general': [
            '强烈建议尽快预约专业心理咨询（可通过学校/医院心理科，费用通常较低）',
            '不要独自承受，告诉一个你信任的人你的真实感受——"我最近状态不太好"这句话本身就是求助',
            '如果出现自伤或伤害他人的念头，请立即联系心理危机热线（见下方资源）',
        ],
        'cognitive': [
            '尝试识别认知扭曲：你是否在"过度概括"（"所有人都讨厌我"）或"灾难化"（"这次挂科我就完了"）？',
            '五感接地法：慢慢说出你此刻 看到的 5 件事、摸到的 4 件事、听到的 3 种声音、闻到的 2 种气味、尝到的 1 种味道',
        ],
    },
    'URGENT': {
        'crisis_resources': [
            '全国心理援助热线：400-161-9995（24 小时，免费）',
            '北京心理危机研究与干预中心：010-8295-1332',
            '上海心理援助热线：021-12320-5',
            '立即前往就近医院急诊室，不要独处',
        ],
    },
}


# ──────────────────────────────────────────────
# 量表信效度元数据（用于报告底部展示学科依据）
# ──────────────────────────────────────────────
SCALE_METADATA: dict[str, dict[str, object]] = {
    'PHQ9': {
        'name': 'PHQ-9 抑郁症状自评量表',
        'developer': 'Kroenke K, Spitzer RL, Williams JBW',
        'year': 2001,
        'source': 'Annals of Internal Medicine, 134(9): 817-829',
        'items': 9,
        'score_range': [0, 27],
        'interpretation': {
            '0-4':   '无或极轻抑郁',
            '5-9':   '轻度抑郁',
            '10-14': '中度抑郁',
            '15-19': '中重度抑郁',
            '20-27': '重度抑郁',
        },
        'cronbach_alpha': 0.89,
        'sensitivity': 0.88,
        'specificity': 0.82,
        'validated_population': '全球多中心（含中国人群），样本量 > 30,000',
    },
    'GAD7': {
        'name': 'GAD-7 广泛性焦虑自评量表',
        'developer': 'Spitzer RL, Kroenke K, Williams JBW, Lowe B',
        'year': 2006,
        'source': 'Archives of Internal Medicine, 166(10): 1092-1097',
        'items': 7,
        'score_range': [0, 21],
        'interpretation': {
            '0-4':   '无或极轻焦虑',
            '5-9':   '轻度焦虑',
            '10-14': '中度焦虑',
            '15-21': '重度焦虑',
        },
        'cronbach_alpha': 0.92,
        'sensitivity': 0.89,
        'specificity': 0.82,
        'validated_population': '全球多中心（含中国人群），样本量 > 15,000',
    },
}
