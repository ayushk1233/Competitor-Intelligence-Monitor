from datetime import datetime
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON
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