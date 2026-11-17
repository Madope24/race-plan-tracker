import os
from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./salum.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = 'postgresql+psycopg://' + DATABASE_URL[len('postgres://') :]
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = 'postgresql+psycopg://' + DATABASE_URL[len('postgresql://') :]

connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    pw_hash: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DayLog(Base):
    """One row per user per day: what was actually done (sessions, sets, readiness, food, feedback). Planned content is
    snapshotted inside `data.planned`, so a later plan change never rewrites history."""

    __tablename__ = 'day_logs'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), primary_key=True)
    data: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # when the phone changed it
    server_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)  # when the server stored it


class DayLogVersion(Base):
    """Append-only audit trail: the previous copy of a day log every time it is replaced."""

    __tablename__ = 'day_log_versions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    date: Mapped[str] = mapped_column(String(10), index=True)
    data: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    replaced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Result(Base):
    """Baselines (base:*), goal results (goal:*) and mini-goal results (mini:*)."""

    __tablename__ = 'results'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    server_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)


class Profile(Base):
    """Athlete settings that drive the plan engine: profile, races, fasting, Ramadan, bike start, baseline."""

    __tablename__ = 'profiles'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    config: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    server_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class PlanVersion(Base):
    """Every plan the athlete has had (config + version), so old plans can be inspected or restored."""

    __tablename__ = 'plan_versions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    version: Mapped[str] = mapped_column(String(32))
    config: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Activity(Base):
    """Recorded activities from a watch or an import (Garmin CSV now; Strava, Health Connect, Apple Health later via adapters)."""

    __tablename__ = 'activities'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), index=True)
    type: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(30))
    data: Mapped[str] = mapped_column(Text)
    server_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)


class SchemaVersion(Base):
    __tablename__ = 'schema_version'
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


# Ordered, idempotent migrations. Add new ones at the end; never edit an applied one.
def _m2_widen_result_key(conn):
    if conn.dialect.name == 'postgresql':
        conn.execute(text('ALTER TABLE results ALTER COLUMN key TYPE VARCHAR(120)'))


MIGRATIONS = [
    (1, 'initial tables: users, day_logs, results', None),
    (2, 'EnduraForge: profiles, plan_versions, activities, day_log_versions; longer result keys', _m2_widen_result_key),
]


def init_db() -> None:
    Base.metadata.create_all(engine)  # creates any missing tables
    with engine.begin() as conn:
        done = {r[0] for r in conn.execute(text('SELECT version FROM schema_version'))}
        for v, _desc, fn in MIGRATIONS:
            if v in done:
                continue
            if fn and inspect(conn).has_table('results'):
                fn(conn)
            conn.execute(text('INSERT INTO schema_version (version, applied_at) VALUES (:v, :t)'), {'v': v, 't': now()})
