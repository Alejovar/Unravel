from datetime import datetime

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    type: str  # origin | confirmed | developing | corrected
    label: str
    source: str | None = None
    platform: str | None = None
    url: str
    domain: str
    published_at: datetime | None = None
    headline: str
    summary: str | None = None
    status: str  # unverified | confirmed | developing | corrected
    reads: int | None = None
    shares: int | None = None
    is_origin: bool = False
    is_latest: bool = False


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    kind: str  # observed | inferred
    confidence: float
    explanation: str | None = None


class GraphSummaryCard(BaseModel):
    key: str  # origin | story_drift | latest_state
    icon: str
    label: str
    title: str
    description: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    summary_text: str | None = None
    summary_cards: list[GraphSummaryCard] = []
    divergence_count: int = 0
    sources_count: int = 0
    edges_count: int = 0
