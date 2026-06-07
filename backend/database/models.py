from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from backend.database.connection import Base
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ── Table 1: runs ─────────────────────────────────────────────────────────────
# One row per analysis run (one click of Run Intelligence)

class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    status: Mapped[str] = mapped_column(
        String(20), default="queued"
        # Values: queued | scraping | analyzing | comparing | completed | failed
    )
    competitor_names: Mapped[list] = mapped_column(JSON, nullable=False)
    total_pages_fetched: Mapped[int] = mapped_column(Integer, default=0)
    run_duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # One run has many competitor analyses
    analyses: Mapped[list["CompetitorAnalysisRecord"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    # One run has one comparison result
    comparison: Mapped["ComparisonRecord"] = relationship(
        back_populates="run", cascade="all, delete-orphan", uselist=False
    )


# ── Table 2: competitor_analyses ─────────────────────────────────────────────
# One row per competitor per run

class CompetitorAnalysisRecord(Base):
    __tablename__ = "competitor_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False
    )
    competitor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    domain: Mapped[str] = mapped_column(String(200), nullable=False)

    # Structured fields — stored as columns for fast querying
    messaging_tone: Mapped[str] = mapped_column(String(50), nullable=True)
    momentum_score: Mapped[int] = mapped_column(Integer, nullable=True)
    analysis_success: Mapped[bool] = mapped_column(Boolean, default=True)

    # Full analysis stored as JSON — flexible, no schema changes needed
    # for new fields
    full_analysis: Mapped[dict] = mapped_column(JSON, nullable=True)

    pages_analyzed: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    run: Mapped["Run"] = relationship(back_populates="analyses")


# ── Table 3: comparison_results ──────────────────────────────────────────────
# One row per run — the cross-competitor comparison

class ComparisonRecord(Base):
    __tablename__ = "comparison_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )

    market_leader: Mapped[str] = mapped_column(Text, nullable=True)
    fastest_mover: Mapped[str] = mapped_column(Text, nullable=True)
    executive_briefing: Mapped[str] = mapped_column(Text, nullable=True)

    # Full comparison stored as JSON
    full_comparison: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    run: Mapped["Run"] = relationship(back_populates="comparison")


# ── Table 4: page_snapshots ───────────────────────────────────────────────────
# Raw scraped content — used later for drift detection diff

class PageSnapshot(Base):
    __tablename__ = "page_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False
    )
    competitor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    page_url: Mapped[str] = mapped_column(String(500), nullable=False)
    page_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Raw text content — used for diffing in Phase 3
    content_text: Mapped[str] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    fetch_success: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ── Table 5: alert_history ──────────────────────────────────────────────

class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    reasons: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ─────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


# ─────────────────────────────────────────────────────────────
# Watchlists
# ─────────────────────────────────────────────────────────────

class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    competitors = relationship(
        "WatchlistCompetitor",
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )

    monitoring_runs = relationship(
        "MonitoringRun",
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )


# ─────────────────────────────────────────────────────────────
# Watchlist Competitors
# ─────────────────────────────────────────────────────────────

class WatchlistCompetitor(Base):
    __tablename__ = "watchlist_competitors"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    watchlist_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    domain: Mapped[str] = mapped_column(
        String(200),
        nullable=True,
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    watchlist = relationship(
        "Watchlist",
        back_populates="competitors",
    )

    __table_args__ = (
        UniqueConstraint(
            "watchlist_id",
            "company_name",
            name="uq_watchlist_company",
        ),
    )


# ─────────────────────────────────────────────────────────────
# Notification Channels
# ─────────────────────────────────────────────────────────────

class NotificationChannel(Base):
    __tablename__ = "notification_channels"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

# ─────────────────────────────────────────────────────────────
# Notification Events
# ─────────────────────────────────────────────────────────────

class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    channel_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    delivery_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
    )

    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

# ─────────────────────────────────────────────────────────────
# Monitoring Runs
# ─────────────────────────────────────────────────────────────

class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    watchlist_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    trigger_type: Mapped[str] = mapped_column(
        String(50),
        default="SCHEDULED",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="QUEUED",
    )

    competitors_checked: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    alerts_generated: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    alerts_suppressed: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    notifications_sent: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    celery_task_id: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    error_detail: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    watchlist = relationship(
        "Watchlist",
        back_populates="monitoring_runs",
    )


# ─────────────────────────────────────────────────────────────
# Alert Suppression
# ─────────────────────────────────────────────────────────────

class AlertSuppression(Base):
    __tablename__ = "alert_suppression"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    suppressed_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    alert_id: Mapped[str] = mapped_column(
        String(36),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_suppression_company_type_until",
            "company_name",
            "alert_type",
            "suppressed_until",
        ),
    )