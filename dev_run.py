# -*- coding: utf-8 -*-
"""
dev_run.py — 开发模式启动

首次使用需要先装依赖（在 cmd 里跑一次即可）：
  pip install fastapi sqlalchemy pydantic passlib[bcrypt] uvicorn jinja2 werkzeug
  # 清华镜像加速版：
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi sqlalchemy pydantic passlib[bcrypt] uvicorn jinja2 werkzeug

以后每次开发直接：
  python dev_run.py
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 先挂载 PyInstaller 提取的第三方库（PYZ.pyz_extracted），无需 pip install
try:
    import config.bootstrap_runtime  # noqa: F401
except Exception as e:  # 没有 bundled 依赖时，退回系统 Python pip 装的包
    print(f'[INFO] 未使用 bundle 依赖 ({(e)})，尝试系统 Python')

# 基础依赖检查
REQUIRED = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'jinja2', 'werkzeug']
missing = []
for pkg in REQUIRED:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print('=' * 50)
    print('  ERROR: missing dependencies')
    print('=' * 50)
    print('  Need to install:')
    print(f'    pip install {" ".join(missing)}')
    print('  Or all at once:')
    print('    pip install fastapi sqlalchemy pydantic passlib[bcrypt]')
    print('                  uvicorn jinja2 werkzeug')
    print('=' * 50)
    sys.exit(1)

from main import app

if __name__ == '__main__':
    import uvicorn
    print()
    print('=' * 50)
    print('  SOURCE CODE DEV SERVER')
    print('  http://localhost:8000')
    print('  docs: http://localhost:8000/docs')
    print('  admin: http://localhost:8000/admin')
    print('  (admin / admin123)')
    print('=' * 50)
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=False)
