"""
Regression comparison test — compares current API responses against the
stored baseline snapshot. Detects drift in key metrics over time.

Baseline is stored at: tests/api/test_data/baseline.json
"""
import json
import os
import pytest
import requests
from tests.api.test_data.f438b048_data import ALL_CALLS

BASELINE_PATH = os.path.join(os.path.dirname(__file__), "..", "test_data", "baseline.json")


@pytest.mark.usefixtures("api_available")
class TestRegressionComparison:
    """Compare current data against baseline snapshot."""

    ENDPOINT = "/api/v1/call-processing/summary"

    @pytest.fixture(scope="class")
    def baseline(self):
        if not os.path.exists(BASELINE_PATH):
            pytest.skip("No baseline file found — run with --update-baseline to create")
        with open(BASELINE_PATH) as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def current_run(self, api_base_url, api_headers):
        """Fetch fresh data for all test calls."""
        run = {"metrics": {}}
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{self.ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code != 200:
                continue
            data = r.json()
            run["metrics"][call_id[:8]] = {
                "sentiment": data.get("summary", {}).get("sentiment_score"),
                "summary_confidence": data.get("summary", {}).get("confidence_score"),
                "compliance_score": data.get("compliance", {}).get("sop_compliance", {}).get("score"),
                "objection_count": data.get("objections", {}).get("total_count", 0),
                "coaching_issues": len(data.get("compliance", {}).get("sop_compliance", {}).get("coaching_issues", [])),
                "qual_status": data.get("qualification", {}).get("qualification_status"),
                "outcome": data.get("qualification", {}).get("call_outcome_category"),
                "scope": data.get("qualification", {}).get("scope_classification"),
            }
        return run

    def test_baseline_has_runs(self, baseline):
        """Baseline must have at least one run."""
        assert len(baseline.get("runs", [])) > 0, "Baseline is empty"

    def test_sentiment_drift(self, baseline, current_run):
        """Sentiment scores should not drift beyond 0.3 from baseline."""
        latest = baseline["runs"][-1]
        for cid_key, bm in latest.get("metrics", {}).items():
            current = current_run["metrics"].get(cid_key)
            if not current or not bm:
                continue
            b_sent = bm.get("sentiment")
            c_sent = current.get("sentiment")
            if b_sent is not None and c_sent is not None:
                drift = abs(c_sent - b_sent)
                assert drift <= 0.3, \
                    f"{cid_key}: sentiment drifted {b_sent} -> {c_sent} (delta={drift:.2f})"
                if drift > 0.1:
                    print(f"  {cid_key}: sentiment drift: {b_sent} -> {c_sent} (delta={drift:.2f})")

    def test_compliance_score_stability(self, baseline, current_run):
        """Compliance scores should not change significantly."""
        latest = baseline["runs"][-1]
        for cid_key, bm in latest.get("metrics", {}).items():
            current = current_run["metrics"].get(cid_key)
            if not current or not bm:
                continue
            b_comp = bm.get("compliance_score")
            c_comp = current.get("compliance_score")
            if b_comp is not None and c_comp is not None and b_comp != 0:
                drift = abs(c_comp - b_comp)
                assert drift <= 0.2, \
                    f"{cid_key}: compliance score drifted {b_comp} -> {c_comp}"

    def test_objection_count_stable(self, baseline, current_run):
        """Objection counts should be identical (deterministic AI)."""
        latest = baseline["runs"][-1]
        for cid_key, bm in latest.get("metrics", {}).items():
            current = current_run["metrics"].get(cid_key)
            if not current or not bm:
                continue
            b_obj = bm.get("objection_count", 0)
            c_obj = current.get("objection_count", 0)
            assert b_obj == c_obj, \
                f"{cid_key}: objection count changed {b_obj} -> {c_obj}"

    def test_qualification_status_stable(self, baseline, current_run):
        """Qualification status should be stable."""
        latest = baseline["runs"][-1]
        for cid_key, bm in latest.get("metrics", {}).items():
            current = current_run["metrics"].get(cid_key)
            if not current or not bm:
                continue
            b_status = bm.get("qual_status")
            c_status = current.get("qual_status")
            assert b_status == c_status, \
                f"{cid_key}: qualification status changed '{b_status}' -> '{c_status}'"
