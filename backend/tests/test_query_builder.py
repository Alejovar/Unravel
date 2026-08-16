from app.discovery.query_builder import build_queries, normalize_title


def test_normalize_title_strips_stopwords():
    normalized = normalize_title("Explosion at the plant forces the evacuation of the area")
    assert "explosion" in normalized
    assert " the " not in f" {normalized} "
    assert " for " not in f" {normalized} "


def test_build_queries_returns_title_and_phrases():
    title = "Explosion at plant forces evacuation of the area"
    text = (
        "The authorities set up a security perimeter after the explosion. "
        "Civil Protection reported that 500 people were evacuated from the affected area."
    )
    queries = build_queries(title, text, max_queries=4)
    assert queries[0] == title
    assert len(queries) <= 4
    assert len(queries) == len(set(q.lower() for q in queries))
