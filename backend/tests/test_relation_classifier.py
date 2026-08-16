from app.pipeline.relation_classifier import ClassificationInput, classify_relation, status_for_target


def test_high_phrase_overlap_is_republication():
    data = ClassificationInput(
        link_evidence=False,
        phrase_overlap=0.9,
        temporal_gap_hours=1.0,
        claim_relation=None,
        narrative_changed=False,
    )
    assert classify_relation(data) == "republication"


def test_contradicts_is_correction():
    data = ClassificationInput(
        link_evidence=False,
        phrase_overlap=0.2,
        temporal_gap_hours=2.0,
        claim_relation="CONTRADICTS",
        narrative_changed=False,
    )
    assert classify_relation(data) == "correction"


def test_supports_is_confirmation():
    data = ClassificationInput(
        link_evidence=True,
        phrase_overlap=0.1,
        temporal_gap_hours=0.2,
        claim_relation="SUPPORTS",
        narrative_changed=False,
    )
    assert classify_relation(data) == "confirmation"


def test_quick_reaction_without_claims():
    data = ClassificationInput(
        link_evidence=False,
        phrase_overlap=0.1,
        temporal_gap_hours=0.1,
        claim_relation=None,
        narrative_changed=False,
    )
    assert classify_relation(data) == "reaction"


def test_status_for_target_correction_locks_corrected():
    assert status_for_target("correction", "unverified") == "corrected"
    assert status_for_target("confirmation", "corrected") == "corrected"
