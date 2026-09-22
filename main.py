# -*- coding: utf-8 -*-
"""
main.py — FastAPI 应用入口

启动服务、初始化日志和数据库、注册路由、挂载静态资源。
"""
from __future__ import annotations
import sys
import threading
import time
import webbrowser
import logging
import secrets
import json
from contextlib import asynccontextmanager
from pathlib import Path

from pydantic import BaseModel

# 先挂载 PyInstaller 提取的第三方库（避免 pip install）
import config.bootstrap_runtime  # noqa: F401

from fastapi import FastAPI, Request, HTTPException, Depends, status
try:
    from fastapi.middleware.cors import CORSMiddleware
    _HAS_CORS = True
except ImportError:
    _HAS_CORS = False
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.settings import (
    APP_NAME, APP_VERSION, APP_HOST, APP_PORT,
    ROOT, TEMPLATES_DIR, STATIC_DIR,
)
from config.logging_config import setup_logging
from backend.models.database import init_db

# 路由模块
from backend.api import screening_api, admin_api, rules_api, analytics_api, export_api, features_api, adaptive_api

log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Admin Session 管理（委托给 config.admin_auth 独立模块）
# ──────────────────────────────────────────────
import config.admin_auth as _auth


# ──────────────────────────────────────────────
# FastAPI 应用实例（lifespan 事件处理器，避免 DeprecationWarning）
# ──────────────────────────────────────────────

@asynccontextmanager
async def _lifespan(app):
    # startup
    setup_logging()
    init_db()

    log.info('=' * 50)
    log.info('  %s v%s', APP_NAME, APP_VERSION)
    log.info('  监听地址 http://%s:%d', APP_HOST, APP_PORT)
    log.info('  管理员后台 http://localhost:%d/admin', APP_PORT)
    log.info('  API 文档  http://localhost:%d/docs', APP_PORT)
    log.info('=' * 50)

    # 打包后的 exe 自动打开浏览器
    if hasattr(sys, '_MEIPASS') or getattr(sys, 'frozen', False):
        def _open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f'http://localhost:{APP_PORT}')
            except Exception:
                pass
        threading.Thread(target=_open_browser, daemon=True).start()

    yield
    # shutdown（暂无清理）


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description='神经符号双引擎驱动的心理健康风险智能筛查系统',
    lifespan=_lifespan,
)

# CORS（可选：如果 fastapi 版本支持）
if _HAS_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


# ──────────────────────────────────────────────
# 全局异常处理器（404 / 500）
# ──────────────────────────────────────────────

@app.exception_handler(404)
async def custom_404(request, exc):
    """404 返回友好的 HTML 页面"""
    return HTMLResponse(_read_html('404.html'), status_code=404)


@app.exception_handler(500)
async def custom_500(request, exc):
    log.exception('500 error on %s', request.url.path)
    return HTMLResponse(
        '<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>服务器错误</title>'
        '<style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f7f9fa;}'
        '.box{text-align:center;padding:40px;background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.08);max-width:480px;}'
        'h1{color:#AC4E42;margin:0;font-size:64px;} h2{color:#203248;margin:8px 0 16px;} '
        'p{color:#666;margin:0 0 20px;} a{color:#1C7A6E;text-decoration:none;}</style></head>'
        '<body><div class="box"><h1>500</h1><h2>服务器开小差了</h2>'
        '<p>系统遇到了一个内部错误，开发团队已经收到通知。</p>'
        '<a href="/">← 返回首页</a></div></body></html>',
        status_code=500,
    )


# ──────────────────────────────────────────────
# 挂载静态资源
# ──────────────────────────────────────────────

app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')


# ──────────────────────────────────────────────
# 请求日志 + 安全响应头中间件
# ──────────────────────────────────────────────

@app.middleware('http')
async def _request_logging(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    elapsed_ms = (time.time() - t0) * 1000
    log.info('%s %s → %d (%.0fms)', request.method, request.url.path,
             response.status_code, elapsed_ms)

    # 安全响应头
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'"

    return response


# ──────────────────────────────────────────────
# 工具函数：读 HTML 模板
# ──────────────────────────────────────────────

def _read_html(name: str) -> str:
    """直接读 HTML 文件返回，绕开 Jinja2 避免 Vue 模板语法冲突。"""
    return (TEMPLATES_DIR / name).read_text(encoding='utf-8')


# ──────────────────────────────────────────────
# 前端页面路由（纯 HTML 直出）
# ──────────────────────────────────────────────

@app.get('/', response_class=HTMLResponse)
def index():
    return _read_html('index.html')


@app.get('/screening', response_class=HTMLResponse)
def screening():
    return _read_html('screening.html')


@app.get('/admin', response_class=HTMLResponse)
def admin_page(request: Request):
    """Admin 页面：未登录显示登录页"""
    if not _auth.check_admin_session(request):
        return _read_html('admin_login.html')
    return _read_html('admin.html')


@app.get('/report/{session_id}', response_class=HTMLResponse)
def report(session_id: int):
    return _read_html('report.html')


@app.get('/my-records', response_class=HTMLResponse)
def my_records():
    return _read_html('records.html')

@app.get('/breathing', response_class=HTMLResponse)
def breathing():
    return _read_html('breathing.html')

@app.get('/mood-journal', response_class=HTMLResponse)
def mood_journal_page():
    return _read_html('mood_journal.html')

@app.get('/healing', response_class=HTMLResponse)
def healing_page():
    return _read_html('healing.html')

@app.get('/cbt', response_class=HTMLResponse)
def cbt_page():
    return _read_html('cbt.html')


@app.get('/assessment', response_class=HTMLResponse)
def assessment_page():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url='/adaptive')

@app.get('/adaptive', response_class=HTMLResponse)
def adaptive_page():
    return _read_html('adaptive.html')


@app.get('/radar-report', response_class=HTMLResponse)
def radar_report_page():
    return _read_html('radar_report.html')


@app.get('/resources', response_class=HTMLResponse)
def resources():
    return _read_html('resources.html')


# ──────────────────────────────────────────────
# favicon + robots.txt
# ──────────────────────────────────────────────

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<text y=".9em" font-size="90">🧠</text></svg>'
    )
    return Response(content=svg, media_type='image/svg+xml')


@app.get('/robots.txt', include_in_schema=False)
async def robots():
    content = (
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /api/admin/\n'
        'Disallow: /admin\n'
        'Disallow: /api/rules/\n'
    )
    return Response(content=content, media_type='text/plain')


# ──────────────────────────────────────────────
# Admin 登录 / 登出 / 状态 API
# ──────────────────────────────────────────────

# Admin 登录请求体（Pydantic 模型，避免手动解析 request.body 的 coroutine 问题）
class _AdminLoginBody(BaseModel):
    username: str
    password: str

@app.post('/api/admin/login')
def admin_login(payload: _AdminLoginBody):
    username = payload.username.strip()
    password = payload.password

    from backend.models.database import SessionLocal, AdminUser
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == username).first()
        if admin and admin.verify_password(password):
            token = _auth.create_admin_session(admin.username)
            resp = JSONResponse({'ok': True})
            resp.set_cookie('admin_session', token, httponly=True, samesite='lax', max_age=86400)
            return resp
    finally:
        db.close()

    raise HTTPException(status_code=401, detail='用户名或密码错误')


@app.post('/api/admin/logout')
def admin_logout(request: Request):
    _auth.delete_admin_session(request)
    return {'ok': True}


@app.get('/api/admin/status')
def admin_status(request: Request):
    return {'authenticated': _auth.check_admin_session(request)}


# ──────────────────────────────────────────────
# 健康检查
# ──────────────────────────────────────────────

@app.get('/api/health')
def health():
    return {'status': 'ok', 'app': APP_NAME, 'version': APP_VERSION}


# ──────────────────────────────────────────────
# API 路由注册
# ──────────────────────────────────────────────

app.include_router(screening_api.router, prefix='/api/screening', tags=['筛查'])
app.include_router(admin_api.router,    prefix='/api/admin',      tags=['管理'])
app.include_router(rules_api.router,    prefix='/api/rules',      tags=['规则管理'])
app.include_router(analytics_api.router,prefix='/api/analytics',  tags=['智能分析'])
app.include_router(features_api.router, prefix='/api/features',  tags=['新功能'])
app.include_router(adaptive_api.router, prefix='/api/adaptive', tags=['自适应测评'])


# ──────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=APP_HOST, port=APP_PORT, reload=False)
