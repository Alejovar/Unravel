from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import JSON as SAJSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.ids import new_id


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def pg_enum(enum_cls: type[enum.Enum], name: str) -> SAEnum:
    """SQLAlchemy manda por defecto el *nombre* del miembro del Enum de
    Python (p.ej. "QUEUED"), no su *valor* ("queued"). Nuestros tipos ENUM
    de Postgres (ver alembic/versions/0001_initial.py) usan los valores en
    minúscula, así que forzamos `values_callable` para que coincidan."""
    return SAEnum(enum_cls, name=name, values_callable=lambda obj: [e.value for e in obj])


class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    SCRAPING = "scraping"
    DISCOVERING = "discovering"
    COMPARING = "comparing"
    ANALYZING = "analyzing"
    DONE = "done"
    FAILED = "failed"


class ArticleStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    CONFIRMED = "confirmed"
    DEVELOPING = "developing"
    CORRECTED = "corrected"


class RelationType(str, enum.Enum):
    CONFIRMATION = "confirmation"
    DEVELOPING = "developing"
    CORRECTION = "correction"
    REACTION = "reaction"
    UPDATE = "update"
    REPUBLICATION = "republication"
    CITES = "cites"
    LINKS_TO = "links_to"
    SAME_STORY = "same_story"


class RelationKind(str, enum.Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"


class ClaimRelation(str, enum.Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    RELATED = "RELATED"
    INSUFFICIENT = "INSUFFICIENT"


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: new_id("ana"))
    query_input: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AnalysisStatus] = mapped_column(
        pg_enum(AnalysisStatus, "analysis_status"), default=AnalysisStatus.QUEUED
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin_article_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("articles.id", use_alter=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    articles: Mapped[list["Article"]] = relationship(
        "Article",
        back_populates="analysis",
        foreign_keys="Article.analysis_id",
        cascade="all, delete-orphan",
    )
    relations: Mapped[list["ArticleRelation"]] = relationship(
        "ArticleRelation", back_populates="analysis", cascade="all, delete-orphan"
    )
    comparisons: Mapped[list["ClaimComparison"]] = relationship(
        "ClaimComparison", back_populates="analysis", cascade="all, delete-orphan"
    )
    summary: Mapped["AnalysisSummary | None"] = relationship(
        "AnalysisSummary",
        back_populates="analysis",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: new_id("art"))
    analysis_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    source_handle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_platform: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reads: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_origin: Mapped[bool] = mapped_column(default=False)
    status: Mapped[ArticleStatus] = mapped_column(
        pg_enum(ArticleStatus, "article_status"), default=ArticleStatus.UNVERIFIED
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    entities: Mapped[list | None] = mapped_column(SAJSON, nullable=True)
    links: Mapped[list | None] = mapped_column(SAJSON, nullable=True)
    raw_metadata: Mapped[dict | None] = mapped_column(SAJSON, nullable=True)
    discovered_via: Mapped[str] = mapped_column(String(32), default="seed")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="articles", foreign_keys=[analysis_id]
    )
    claims: Mapped[list["Claim"]] = relationship(
        "Claim", back_populates="article", cascade="all, delete-orphan"
    )


class ArticleRelation(Base):
    __tablename__ = "article_relations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: new_id("rel"))
    analysis_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_article_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    target_article_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    relation: Mapped[RelationType] = mapped_column(pg_enum(RelationType, "relation_type"))
    kind: Mapped[RelationKind] = mapped_column(
        pg_enum(RelationKind, "relation_kind"), default=RelationKind.INFERRED
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    score_breakdown: Mapped[dict | None] = mapped_column(SAJSON, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="relations")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: new_id("clm"))
    article_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    article: Mapped["Article"] = relationship("Article", back_populates="claims")


class ClaimComparison(Base):
    __tablename__ = "claim_comparisons"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: new_id("cmp"))
    analysis_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    claim_a_id: Mapped[str] = mapped_column(String(32), ForeignKey("claims.id", ondelete="CASCADE"))
    claim_b_id: Mapped[str] = mapped_column(String(32), ForeignKey("claims.id", ondelete="CASCADE"))
    relation: Mapped[ClaimRelation] = mapped_column(pg_enum(ClaimRelation, "claim_relation"))
    explanation: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="comparisons")


class AnalysisSummary(Base):
    __tablename__ = "analysis_summaries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: new_id("sum"))
    analysis_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    summary_text: Mapped[str] = mapped_column(Text, default="")
    origin_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    story_drift_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    latest_state_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    divergence_count: Mapped[int] = mapped_column(Integer, default=0)
    sources_count: Mapped[int] = mapped_column(Integer, default=0)
    edges_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="summary")
