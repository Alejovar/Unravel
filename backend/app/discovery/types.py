from dataclasses import dataclass
from datetime import datetime


@dataclass
class CandidateSource:
    url: str
    title: str = ""
    published_at: datetime | None = None
    discovered_via: str = "search"  # gdelt | rss | search | link
