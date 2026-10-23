from backend.evaluation.metrics import citation_validity, precision_at_k, recall_at_k


def test_retrieval_metrics() -> None:
    assert precision_at_k(["a", "x"], {"a", "b"}, 2) == 0.5
    assert recall_at_k(["a", "x"], {"a", "b"}, 2) == 0.5


def test_citation_validity() -> None:
    assert citation_validity(["a", "x"], {"a"}) == 0.5
