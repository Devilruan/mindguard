# -*- coding: utf-8 -*-
"""
config.admin_auth
管理员 Session 存储 + 鉴权依赖（独立模块，避免 main.py ↔ backend/api/* 的循环导入）

所有 admin 级别的 API 路由都通过 `Depends(require_admin_auth)` 保护。
"""
from __future__ import annotations
import time
import secrets
import logging

from starlette.requests import Request
from fastapi import HTTPException, Depends

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 进程内 Session 存储（单进程部署够用；PyInstaller 打包版）
# ──────────────────────────────────────────────
_admin_sessions: dict[str, dict] = {}

# Session 有效期 24 小时
_SESSION_MAX_AGE = 86400


def create_admin_session(username: str) -> str:
    """生成新 session token 并存入内存"""
    token = secrets.token_urlsafe(32)
    _admin_sessions[token] = {
        'username': username,
        'created_at': time.time(),
    }
    log.info('创建管理员 session: user=%s', username)
    return token


def check_admin_session(request: Request) -> bool:
    """检查请求是否带有有效 admin session cookie"""
    token = request.cookies.get('admin_session')
    if not token:
        return False
    session = _admin_sessions.get(token)
    if not session:
        return False
    # 检查过期
    if time.time() - session['created_at'] > _SESSION_MAX_AGE:
        _admin_sessions.pop(token, None)
        return False
    return True


def delete_admin_session(request: Request) -> None:
    """登出时删除 session"""
    token = request.cookies.get('admin_session')
    if token and token in _admin_sessions:
        del _admin_sessions[token]


def require_admin_auth(request: Request) -> bool:
    """FastAPI 依赖：用于保护 admin 路由，未登录抛 401"""
    if not check_admin_session(request):
        raise HTTPException(
            status_code=401,
            detail='请先登录管理员账号',
        )
    return True
