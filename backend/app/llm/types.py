from dataclasses import dataclass, field


@dataclass
class ExtractedClaim:
    text: str
    subject: str = ""
    value: str = ""


@dataclass
class ClaimComparisonResult:
    relation: str  # SUPPORTS | CONTRADICTS | RELATED | INSUFFICIENT
    explanation: str
    confidence: float = 0.5


@dataclass
class NarrativeChange:
    changed: bool
    explanation: str


@dataclass
class EvidenceItem:
    """One evidence entry handed to the LLM for the final summary. The
    model NEVER receives arbitrary results from the internet: only what the
    LLM-free engine already processed and verified (VeriGraph.md section
    32)."""

    source: str
    published_at: str | None
    headline: str
    role: str = ""  # e.g. "origin", "confirms", "corrects", "contradicts"
    claims: list[str] = field(default_factory=list)
