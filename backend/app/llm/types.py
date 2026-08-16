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
    """Una entrada de evidencia que se le pasa al LLM para el resumen final.
    El modelo NUNCA recibe resultados arbitrarios de Internet: solo lo que
    el motor sin LLM ya procesó y verificó (VeriGraph.md sección 32)."""

    source: str
    published_at: str | None
    headline: str
    role: str = ""  # p.ej. "origen", "confirma", "corrige", "contradice"
    claims: list[str] = field(default_factory=list)
