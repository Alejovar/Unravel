"""Turns the database rows of an analysis into the graph + timeline JSON
consumed by the frontend (Cytoscape.js)."""

from __future__ import annotations

from app.models.models import Analysis
from app.schemas.graph import GraphEdge, GraphNode, GraphResponse, GraphSummaryCard


def build_graph_response(analysis: Analysis) -> GraphResponse:
    articles = analysis.articles
    relations = analysis.relations
    summary = analysis.summary

    sources_with_outgoing = {r.source_article_id for r in relations}

    nodes: list[GraphNode] = []
    for article in articles:
        node_type = "origin" if article.is_origin else article.status.value
        is_latest = article.id not in sources_with_outgoing and not article.is_origin
        nodes.append(
            GraphNode(
                id=article.id,
                type=node_type,
                label=article.domain or article.title[:30],
                source=article.source_handle,
                platform=article.source_platform,
                url=article.url,
                domain=article.domain,
                published_at=article.published_at,
                headline=article.title,
                summary=article.summary,
                status=article.status.value,
                reads=article.reads,
                shares=article.shares,
                is_origin=article.is_origin,
                is_latest=is_latest,
            )
        )

    edges: list[GraphEdge] = [
        GraphEdge(
            id=rel.id,
            source=rel.source_article_id,
            target=rel.target_article_id,
            relation=rel.relation.value,
            kind=rel.kind.value,
            confidence=rel.confidence,
            explanation=rel.explanation,
        )
        for rel in relations
    ]

    summary_cards: list[GraphSummaryCard] = []
    if summary:
        origin_article = next((a for a in articles if a.is_origin), None)
        origin_desc = ""
        if origin_article:
            pub = origin_article.published_at
            # Many sources only provide the date; the parser fills the
            # missing time with midnight UTC, which is not a real time.
            has_time = pub and not (pub.hour == 0 and pub.minute == 0 and pub.second == 0)
            when = pub.strftime("%H:%M") if has_time else ""
            origin_desc = (
                f"{origin_article.source_handle or origin_article.domain} · {when} · "
                f"{origin_article.status.value.capitalize()}"
            )
        summary_cards = [
            GraphSummaryCard(
                key="origin",
                icon="origin",
                label="ORIGIN",
                title=summary.origin_label or "—",
                description=origin_desc,
            ),
            GraphSummaryCard(
                key="story_drift",
                icon="drift",
                label="STORY DRIFT",
                title=(
                    f"{summary.divergence_count} major divergence"
                    + ("s" if summary.divergence_count != 1 else "")
                    if summary.divergence_count
                    else "No major divergence"
                ),
                description=summary.story_drift_label or "",
            ),
            GraphSummaryCard(
                key="latest_state",
                icon="latest",
                label="LATEST STATE",
                title=summary.latest_state_label or "—",
                description="Most recent state of the coverage found.",
            ),
        ]

    return GraphResponse(
        nodes=nodes,
        edges=edges,
        summary_text=summary.summary_text if summary else None,
        summary_cards=summary_cards,
        divergence_count=summary.divergence_count if summary else 0,
        sources_count=summary.sources_count if summary else len(articles),
        edges_count=summary.edges_count if summary else len(relations),
    )
