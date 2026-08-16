FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# spaCy models for entity extraction. English first, Spanish kept because
# the tool traces coverage published in either language.
# If the download fails (no network at build time) the system still works:
# app/similarity/entities.py falls back to a rule-based extractor.
RUN python -m spacy download en_core_web_sm || true
RUN python -m spacy download es_core_news_sm || true

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
