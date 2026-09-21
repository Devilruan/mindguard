# 神经符号心理健康风险智能筛查系统

> **版本**：v1.1.0  
> **技术栈**：Python 3.11 + FastAPI + SQLAlchemy + Vue 3  
> **核心创新**：神经符号双引擎（BERT 语义 + 心理学规则 + RIPPER 规则学习）→ 100% 可解释的心理健康风险筛查

## 快速启动（唯一推荐）

```bash
# Windows：双击即可，无需 pip install（自动挂载内置依赖）
双击 start.bat

# 或手动
python main.py
```

访问：
- 首页：http://localhost:8000/
- 筛查：http://localhost:8000/screening
- 管理后台：http://localhost:8000/admin（admin / admin123）
- API 文档：http://localhost:8000/docs

> 说明：`start_dev.bat` 仅为旧版开发入口；系统 Python 已安装全部依赖时也可用。
> 本项目依赖存放在 `mmhs.exe_extracted/PYZ.pyz_extracted`，由 `config/bootstrap_runtime.py` 自动挂载，
> 因此**无需运行 pip install**。

## 项目结构

```
源码_restored/
├── main.py                           # FastAPI 应用入口
├── requirements.txt
├── start_dev.bat
├── config/
│   ├── __init__.py
│   └── settings.py                   # 6 条默认规则 + 关键词词典 + 路径
├── backend/
│   ├── api/
│   │   ├── screening_api.py          # 筛查提交 + 知情同意 + 题目
│   │   ├── admin_api.py              # 管理后台 8 个端点
│   │   ├── analytics_api.py          # 智能分析 7 个端点
│   │   └── rules_api.py              # 规则 CRUD + RIPPER 学习
│   ├── core/
│   │   ├── feature_extraction.py     # 多模态特征提取（BERT + 关键词）
│   │   └── neuro_symbolic/
│   │       └── engine.py             # ⭐ 神经符号引擎核心
│   └── models/
│       └── database.py               # SQLAlchemy 5 张表 ORM
└── frontend/
    ├── templates/                    # 6 个 Vue 3 单页
    └── static/css/app.css            # 全站设计系统
```

## 核心流程

```
用户 → 筛查向导 → PHQ-9 + GAD-7 + 开放文本
         ↓
    feature_extraction.py（10 维特征向量）
         ↓
    engine.py（规则评估 + RIPPER 学习）
         ↓
    RiskAssessment（分数 + 触发规则 + 推理链）
         ↓
    SQLite 存储 + 高危自动创建干预工单
```

## 数据库

首次运行自动建表 + 默认 admin：`admin / admin123`

| 表 | 说明 |
|----|------|
| users | 匿名用户（学号哈希预留） |
| admins | 管理员（scrypt 加密） |
| screening_sessions | 筛查会话（核心表，含推理链） |
| interventions | 干预工单（pending→processing→closed） |
| rule_versions | 规则版本管理 |

## 默认心理学规则

| ID | 条件 | 结论 |
|----|------|------|
| R001 | PHQ-9 ≥ 20 | 抑郁高风险 |
| R002 | GAD-7 ≥ 15 | 焦虑高风险 |
| R003 | 消极词 ≥ 3 | 风险提升 |
| R004 | 语音基频标准差 ≥ 30 | 情绪激动风险 |
| R005 | 作答时长 < 60s | 可能随意作答 |
| R006 | 自杀关键词 ≥ 1 | 自杀风险预警 |

## API 列表

| 路由 | 说明 |
|------|------|
| POST /api/screening/submit | 提交筛查 |
| GET /api/admin/stats/overview | 仪表盘统计 |
| GET /api/admin/sessions | 会话列表 |
| GET /api/admin/sessions/{id} | 会话详情（含推理链） |
| POST /api/admin/alerts/send | 批量推送预警 |
| POST /api/rules/learn | RIPPER 自动学习 |
| GET /api/analytics/trend-forecast | 14 天趋势 + 7 天预测 |
| ... | 共 27 个端点 |

## 降级策略

- **BERT 未安装** → 关键词密度法估计文本消极度
- **librosa 未安装** → 跳过语音韵律特征
- **wittgenstein 未安装** → RIPPER 降级为启发式规则

## PyInstaller 打包

```bash
pip install pyinstaller
pyinstaller --onefile --name mmhs ^
  --add-data "frontend;templates" ^
  --add-data "frontend;static" ^
  main.py
```
