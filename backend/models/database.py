# -*- coding: utf-8 -*-
"""
backend.models.database
SQLAlchemy ORM 模型 + 数据库初始化。

数据库路径由 config.settings.DB_PATH 决定，支持通过 .env 覆盖。
"""
from __future__ import annotations
import logging
import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text, Index, event,
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

from config.settings import (
    SQLALCHEMY_DATABASE_URL, DB_PATH,
    DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD,
)

log = logging.getLogger(__name__)

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in SQLALCHEMY_DATABASE_URL else {},
)

# SQLite 外键约束默认关闭，需要显式开启
@event.listens_for(engine, 'connect')
def _enable_sqlite_fk(dbapi_connection, connection_record):
    if 'sqlite' in SQLALCHEMY_DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ──────────────────────────────────────────────
# ORM 模型
# ──────────────────────────────────────────────

class User(Base):
    """匿名筛查用户（学生）。"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    anon_id = Column(String(64), unique=True, index=True)
    student_id_hash = Column(String(128), nullable=True)
    grade = Column(String(20), nullable=True)
    major = Column(String(60), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship('ScreeningSession', back_populates='user')


class AdminUser(Base):
    """管理员（心理老师/辅导员）。"""
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True)
    password_hash = Column(String(256))
    role = Column(String(20))            # 'admin' / 'counselor'
    name = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)

    def verify_password(self, plain: str) -> bool:
        """校验明文密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, plain)


class ScreeningSession(Base):
    """一次完整的筛查会话。"""
    __tablename__ = 'screening_sessions'
    __table_args__ = (
        Index('ix_session_risk_time', 'overall_risk_level', 'created_at'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 原始作答
    duration_sec = Column(Float, nullable=True)
    phq9_answers = Column(Text, nullable=True)
    gad7_answers = Column(Text, nullable=True)
    open_text = Column(Text, nullable=True)
    audio_path = Column(String(512), nullable=True)

    # 计算得分
    phq9_score = Column(Float, default=0)
    gad7_score = Column(Float, default=0)
    overall_risk_level = Column(String(20), default='low', index=True)
    overall_risk_score = Column(Float, default=0)
    depression_score = Column(Float, default=0)
    anxiety_score = Column(Float, default=0)
    suicide_risk_score = Column(Float, default=0)

    # 神经符号引擎输出
    activated_rules = Column(Text, nullable=True)
    explanation_chain = Column(Text, nullable=True)
    features_json = Column(Text, nullable=True)

    # 干预关联
    alert_sent = Column(Boolean, default=False)
    intervention_id = Column(Integer, ForeignKey('interventions.id'), nullable=True)

    user = relationship('User', foreign_keys=[user_id])
    intervention = relationship('Intervention', foreign_keys=[intervention_id],
                                 back_populates='sessions')


class Intervention(Base):
    """干预记录/工单。"""
    __tablename__ = 'interventions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('screening_sessions.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    status = Column(String(20), default='pending')   # pending / processing / closed
    handler_id = Column(Integer, ForeignKey('admins.id'), nullable=True)
    notes = Column(Text, nullable=True)
    outcome = Column(String(60), nullable=True)
    risk_level = Column(String(20), nullable=True)
    assigned_to = Column(String(80), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = relationship('ScreeningSession', foreign_keys=[
        ScreeningSession.intervention_id], back_populates='intervention')


class RuleVersion(Base):
    """规则版本管理（每次规则变更自动记录）。"""
    __tablename__ = 'rule_versions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(32))
    rules_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(64), nullable=True)


# ──────────────────────────────────────────────
# 心情打卡 / 快速日记
# ──────────────────────────────────────────────

class MoodJournal(Base):
    """心情快速打卡 + 简短日记。"""
    __tablename__ = 'mood_journals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    anon_id = Column(String(64), index=True)
    mood_score = Column(Float)
    emotion = Column(String(20))
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class EmergencyContact(Base):
    """安全代理 / 紧急联系人（可选绑定）。"""
    __tablename__ = 'emergency_contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    anon_id = Column(String(64), unique=True, index=True)
    contact_name = Column(String(60))
    contact_phone = Column(String(20))
    relation = Column(String(30), nullable=True)
    notify_threshold = Column(String(20), default='urgent')
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────────
# 数据库操作
# ──────────────────────────────────────────────

def get_db():
    """FastAPI Depends 注入：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """建表（首次运行调用）+ 初始化默认管理员。"""
    log.info('初始化数据库: %s', DB_PATH)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(AdminUser).count() == 0:
            from werkzeug.security import generate_password_hash
            admin = AdminUser(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=generate_password_hash(DEFAULT_ADMIN_PASSWORD),
                role='admin',
                name='系统管理员',
            )
            db.add(admin)
            db.commit()
            log.info('已创建默认管理员: %s', DEFAULT_ADMIN_USERNAME)
        else:
            log.debug('管理员已存在，跳过初始化')
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
