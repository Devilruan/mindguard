# -*- coding: utf-8 -*-
"""
config.logging_config
统一日志配置：输出到控制台 + 滚动文件。
启动时调用 setup_logging()，之后各处直接用 logging.getLogger(__name__)。
"""
from __future__ import annotations
import logging
import logging.handlers
import sys
from pathlib import Path

_logged = False


def setup_logging(level: int = logging.INFO) -> None:
    """初始化全局日志（仅执行一次）"""
    global _logged
    if _logged:
        return
    _logged = True

    # 根 logger
    root = logging.getLogger()
    root.setLevel(level)

    # 已有 handler 清理
    for h in root.handlers[:]:
        root.removeHandler(h)

    fmt = logging.Formatter(
        '%(asctime)s.%(msecs)03d %(levelname)-5s '
        '%(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # ── 控制台（stdout） ──
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    stream.setLevel(level)
    root.addHandler(stream)

    # ── 滚动文件（项目根目录 logs/mmhs.log，单文件上限 2 MB × 3 份） ──
    try:
        log_dir = Path(__file__).resolve().parent.parent / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'mmhs.log',
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8',
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(level)
        root.addHandler(file_handler)
    except Exception:
        # 文件写权限缺失时降级为仅控制台
        root.warning('无法写入日志文件，仅输出到控制台')

    # 压下第三方库的噪音
    for name in ['uvicorn', 'sqlalchemy.engine', 'passlib']:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """便捷获取命名 logger"""
    return logging.getLogger(name)
