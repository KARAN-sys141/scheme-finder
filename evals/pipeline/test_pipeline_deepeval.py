import json
import os

import pytest

SUMMARY = "evals/results/pipeline_deepeval_day8_summary.json"

pytestmark = pytest.mark.skipif(not os.path.exists(SUMMARY), reason="run deepeval_pipeline first")


@pytest.mark.parametrize(
    "metric,minimum",
    [("faithfulness", 0.8), ("answer_relevancy", 0.7), ("correctness", 0.6), ("task_completion", 0.7)],
)
def test_pipeline_metric_at_least(metric, minimum):
    value = json.load(open(SUMMARY, encoding="utf-8"))["ALL"][metric]
    assert value is not None and value >= minimum, f"{metric}: {value} < {minimum}"