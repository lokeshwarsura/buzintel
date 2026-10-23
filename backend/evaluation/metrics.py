"""Evaluation calculations that do not need a model provider."""


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    selected = retrieved[:k]
    return sum(item in relevant for item in selected) / len(selected) if selected else 0.0


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 1.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def citation_validity(citation_ids: list[str], evidence_ids: set[str]) -> float:
    if not citation_ids:
        return 0.0
    return sum(item in evidence_ids for item in citation_ids) / len(citation_ids)
