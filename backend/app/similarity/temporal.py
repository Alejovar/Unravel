"""Señal de cercanía temporal (VeriGraph.md sección 21)."""

from __future__ import annotations

import math
from datetime import datetime

# Decaimiento: dos publicaciones separadas por HALF_LIFE_HOURS obtienen 0.5.
HALF_LIFE_HOURS = 12.0


def temporal_score(date_a: datetime | None, date_b: datetime | None) -> float:
    if date_a is None or date_b is None:
        return 0.5  # neutral: no penaliza ni favorece cuando falta la fecha
    delta_hours = abs((date_a - date_b).total_seconds()) / 3600.0
    return math.pow(0.5, delta_hours / HALF_LIFE_HOURS)
