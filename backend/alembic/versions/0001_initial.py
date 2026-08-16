"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# create_type=False: the types are created explicitly, once, at the start
# of upgrade() (see below). Without this, SQLAlchemy automatically emits
# CREATE TYPE again for every table that uses the enum as a column type,
# which blows up with "type already exists".
# NOTE: create_type is only honoured by postgresql.ENUM, not by the generic
# sa.Enum.
analysis_status = PGEnum(
    "queued", "scraping", "discovering", "comparing", "analyzing", "done", "failed",
    name="analysis_status",
    create_type=False,
)
article_status = PGEnum(
    "unverified", "confirmed", "developing", "corrected", name="article_status", create_type=False
)
relation_type = PGEnum(
    "confirmation", "developing", "correction", "reaction", "update",
    "republication", "cites", "links_to", "same_story", name="relation_type",
    create_type=False,
)
relation_kind = PGEnum("observed", "inferred", name="relation_kind", create_type=False)
claim_relation = PGEnum(
    "SUPPORTS", "CONTRADICTS", "RELATED", "INSUFFICIENT", name="claim_relation", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    analysis_status.create(bind, checkfirst=True)
    article_status.create(bind, checkfirst=True)
    relation_type.create(bind, checkfirst=True)
    relation_kind.create(bind, checkfirst=True)
    claim_relation.create(bind, checkfirst=True)

    op.create_table(
        "analyses",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("query_input", sa.Text(), nullable=False),
        sa.Column("status", analysis_status, nullable=False, server_default="queued"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("origin_article_id", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "articles",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.String(32),
            sa.ForeignKey("analyses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("title", sa.Text(), nullable=False, server_default=""),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("text", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("source_handle", sa.String(255), nullable=True),
        sa.Column("source_platform", sa.String(255), nullable=True),
        sa.Column("reads", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("is_origin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", article_status, nullable=False, server_default="unverified"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("entities", sa.JSON(), nullable=True),
        sa.Column("links", sa.JSON(), nullable=True),
        sa.Column("raw_metadata", sa.JSON(), nullable=True),
        sa.Column("discovered_via", sa.String(32), nullable=False, server_default="seed"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_articles_analysis_id", "articles", ["analysis_id"])
    op.create_index("ix_articles_content_hash", "articles", ["content_hash"])

    op.create_foreign_key(
        "fk_analyses_origin_article",
        "analyses",
        "articles",
        ["origin_article_id"],
        ["id"],
        use_alter=True,
    )

    op.create_table(
        "claims",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "article_id",
            sa.String(32),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_claims_article_id", "claims", ["article_id"])

    op.create_table(
        "article_relations",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.String(32),
            sa.ForeignKey("analyses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_article_id",
            sa.String(32),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_article_id",
            sa.String(32),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("relation", relation_type, nullable=False),
        sa.Column("kind", relation_kind, nullable=False, server_default="inferred"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_breakdown", sa.JSON(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_article_relations_analysis_id", "article_relations", ["analysis_id"])

    op.create_table(
        "claim_comparisons",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.String(32),
            sa.ForeignKey("analyses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "claim_a_id", sa.String(32), sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "claim_b_id", sa.String(32), sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("relation", claim_relation, nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_claim_comparisons_analysis_id", "claim_comparisons", ["analysis_id"])

    op.create_table(
        "analysis_summaries",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.String(32),
            sa.ForeignKey("analyses.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("summary_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("origin_label", sa.Text(), nullable=True),
        sa.Column("story_drift_label", sa.Text(), nullable=True),
        sa.Column("latest_state_label", sa.Text(), nullable=True),
        sa.Column("divergence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sources_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("edges_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("analysis_summaries")
    op.drop_table("claim_comparisons")
    op.drop_table("article_relations")
    op.drop_table("claims")
    op.drop_constraint("fk_analyses_origin_article", "analyses", type_="foreignkey")
    op.drop_table("articles")
    op.drop_table("analyses")

    bind = op.get_bind()
    claim_relation.drop(bind, checkfirst=True)
    relation_kind.drop(bind, checkfirst=True)
    relation_type.drop(bind, checkfirst=True)
    article_status.drop(bind, checkfirst=True)
    analysis_status.drop(bind, checkfirst=True)
