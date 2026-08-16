from app.similarity.ngrams import phrase_overlap


def test_phrase_overlap_identical_text_is_high():
    text = "las autoridades establecieron un perímetro de seguridad amplio hoy"
    assert phrase_overlap(text, text, n=5) == 1.0


def test_phrase_overlap_unrelated_text_is_zero():
    a = "las autoridades establecieron un perímetro de seguridad"
    b = "el equipo local gano el partido de futbol ayer por la noche"
    assert phrase_overlap(a, b, n=5) == 0.0
