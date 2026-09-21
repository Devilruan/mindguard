# -*- coding: utf-8 -*-
"""
config.bootstrap_runtime
自动发现并挂载 PyInstaller 打包产物中的第三方库和 C 扩展，
让源码开发版可以直接运行而不依赖 pip install。
"""
from __future__ import annotations
import os
import sys
from pathlib import Path


def _add_path(p: str, front: bool = False) -> None:
    if not p or p in sys.path:
        return
    if front:
        sys.path.insert(0, p)
    else:
        sys.path.append(p)


def _add_dll_dir(p: str) -> None:
    if not p or not os.path.isdir(p):
        return
    # 加进 PATH（兜底，所有子进程和 .dll 加载都能搜到）
    os.environ['PATH'] = p + os.pathsep + os.environ.get('PATH', '')
    # 加进 sys.path（Python import .pyd 时用）
    _add_path(p)
    # Windows 10+ 的 API
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(p)
        except (OSError, PermissionError):
            pass


def _walk_pyd_dirs(root: str) -> list:
    if not os.path.isdir(root):
        return []
    dirs = {root}  # 根目录里可能也有 .pyd
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.pyd'):
                dirs.add(dirpath)
                break
    return list(dirs)


def ensure_runtime() -> None:
    here = Path(__file__).resolve().parent.parent  # 源码根目录

    # ── 1. 项目根（源码目录必须在最前面，覆盖 PYZ 里的旧 backend/__init__.pyc） ──
    _add_path(str(here), front=True)

    # ── 2. PYZ.pyz_extracted（第三方库 .pyc，放后面） ──
    pyz_found = False
    for p in [
        here.parent / 'mmhs.exe_extracted' / 'PYZ.pyz_extracted',
    ]:
        if p.is_dir():
            for entry in os.listdir(p):
                full = p / entry
                if full.is_dir() and (full / '__init__.pyc').exists():
                    _add_path(str(p), front=False)
                    pyz_found = True
                    break
            if pyz_found:
                break

    # ── 3. _internal（含 python311.dll + libssl + C 扩展，放后面） ──
    for p in [
        here.parent / '_internal',
        here.parent.parent / '_internal',
        here.parent / '2026AIC·算法创新赛' / '代码包' / '直接运行' / '_internal',
    ]:
        if p.is_dir() and (p / 'python311.dll').is_file():
            _add_dll_dir(str(p))
            for sub in _walk_pyd_dirs(str(p)):
                if sub != str(p):
                    _add_dll_dir(sub)
            break


ensure_runtime()
