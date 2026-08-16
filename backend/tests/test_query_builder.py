from app.discovery.query_builder import build_queries, normalize_title


def test_normalize_title_strips_stopwords():
    normalized = normalize_title("Explosión en la planta obliga a evacuar la zona")
    assert "explosión" in normalized
    assert " la " not in f" {normalized} "
    assert " en " not in f" {normalized} "


def test_build_queries_returns_title_and_phrases():
    title = "Explosión en planta obliga a evacuar zona"
    text = (
        "Las autoridades establecieron un perímetro de seguridad tras la explosión. "
        "Protección Civil informó que 500 personas fueron evacuadas de la zona afectada."
    )
    queries = build_queries(title, text, max_queries=4)
    assert queries[0] == title
    assert len(queries) <= 4
    assert len(queries) == len(set(q.lower() for q in queries))
