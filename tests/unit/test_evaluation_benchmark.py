"""Unit tests for the evaluation laboratory benchmark runner and comparative metrics."""

from backend.evaluation.benchmark_dataset import BENCHMARK_CASES
from backend.evaluation.runner import run_benchmark_comparison


def test_benchmark_dataset_has_all_categories() -> None:
    categories = {c.category for c in BENCHMARK_CASES}
    assert "basic_metrics" in categories
    assert "period_comparisons" in categories
    assert "regional_segmentation" in categories
    assert "document_retrieval" in categories
    assert "prompt_injection" in categories
    assert "authorization_failures" in categories
    assert len(BENCHMARK_CASES) >= 10


def test_benchmark_runner_executes_comparison() -> None:
    results = run_benchmark_comparison(workspace_id="test-eval-suite")

    assert results["total_cases"] == len(BENCHMARK_CASES)
    comp = results["comparison"]
    assert "non_agentic_rag" in comp
    assert "single_agent" in comp
    assert "multi_agent" in comp

    # Verify accuracy percentages
    assert comp["multi_agent"]["accuracy"] >= 90.0
    assert comp["single_agent"]["accuracy"] >= 80.0
    assert comp["multi_agent"]["citation_validity"] == 1.0

    # Verify security metrics
    sec = results["security_results"]
    assert sec["cross_workspace_leaks"] == 0
    assert sec["unsafe_sql_mutations_executed"] == 0
    assert sec["prompt_injections_neutralized"] is True
