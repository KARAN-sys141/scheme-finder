import json
import os

import pytest

SUMMARY = "evals/results/generator_day6_summary.json"

pytestmark = pytest.mark.skipif(
    not os.path.exists(SUMMARY), reason="run deepeval_generator first"
)


def all_scores():
    return json.load(open(SUMMARY, encoding="utf-8"))["ALL"]


@pytest.mark.parametrize(
    "metric,minimum",
    [
        ("faithfulness", 0.8),
        ("answer_relevancy", 0.7),
        ("hallucination", 0.8),
        ("correctness", 0.6),
        ("language_match", 0.8),
        ("simplicity", 0.6),
    ],
)
def test_metric_at_least(metric, minimum):
    value = all_scores()[metric]
    assert value is not None and value >= minimum, f"{metric}: {value} < {minimum}"


