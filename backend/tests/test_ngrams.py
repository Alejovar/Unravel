from app.similarity.ngrams import phrase_overlap


def test_phrase_overlap_identical_text_is_high():
    text = "the authorities set up a wide security perimeter earlier today"
    assert phrase_overlap(text, text, n=5) == 1.0


def test_phrase_overlap_unrelated_text_is_zero():
    a = "the authorities set up a wide security perimeter"
    b = "the local team won the football match last night by two goals"
    assert phrase_overlap(a, b, n=5) == 0.0
