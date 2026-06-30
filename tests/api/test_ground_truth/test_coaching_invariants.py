"""
Coaching invariants — validate the 3-question coaching framework.

Rules enforced:
  1. Every coaching issue must answer: WHAT HAPPENED, WHY IT MATTERS, WHAT TO DO
  2. Severity must be high/medium/low
  3. High-severity issues must have transcript_evidence and example_language
  4. Coaching strengths must have behavior + why_effective
  5. related_sop_metric should link to known SOP metrics when populated

Ground truth: CSR_SOP.pdf Section 12 (What Good Looks Like)
"""
import pytest
import requests

from tests.api.test_data.f438b048_data import ALL_CALLS
from tests.api.test_data.sop_metrics import SOP_METRIC_REGISTRY

ENDPOINT = "/api/v1/call-processing/summary"


@pytest.mark.usefixtures("api_available")
class TestCoachingInvariants:
    """Validate coaching data against the 3-question framework."""

    @pytest.fixture
    def coaching_data(self, api_base_url, api_headers):
        """Extract all coaching issues/strengths from test calls."""
        data = {"issues": [], "strengths": []}
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code != 200:
                continue
            resp = r.json()
            sop = resp.get("compliance", {}).get("sop_compliance", {})
            for issue in sop.get("coaching_issues", []):
                data["issues"].append({"call": call_id[:8], **issue})
            for strength in sop.get("coaching_strengths", []):
                data["strengths"].append({"call": call_id[:8], **strength})
        return data

    def test_all_issues_have_three_questions(self, coaching_data):
        """Every coaching issue must answer What/Why/How."""
        for issue in coaching_data["issues"]:
            assert "issue" in issue and issue["issue"], \
                f"{issue['call']}: coaching issue missing 'issue' (WHAT HAPPENED?)"
            assert "why_it_matters" in issue and issue["why_it_matters"], \
                f"{issue['call']}: coaching issue missing 'why_it_matters' (WHY DOES IT MATTER?)"
            assert "how_to_fix" in issue and issue["how_to_fix"], \
                f"{issue['call']}: coaching issue missing 'how_to_fix' (WHAT TO DO DIFFERENTLY?)"

    def test_all_issues_have_valid_severity(self, coaching_data):
        """Severity must be high, medium, or low."""
        for issue in coaching_data["issues"]:
            assert issue.get("severity") in ("high", "medium", "low"), \
                f"{issue['call']}: invalid severity '{issue.get('severity')}'"

    def test_high_severity_has_transcript_evidence(self, coaching_data):
        """High-severity issues should have transcript_evidence."""
        for issue in coaching_data["issues"]:
            if issue.get("severity") == "high":
                assert issue.get("transcript_evidence"), \
                    f"{issue['call']}: high-severity issue missing transcript_evidence"

    def test_high_severity_has_example_language(self, coaching_data):
        """High-severity issues should have example_language."""
        for issue in coaching_data["issues"]:
            if issue.get("severity") == "high":
                el = issue.get("example_language")
                assert el and len(el) > 20, \
                    f"{issue['call']}: high-severity issue missing/lacking example_language"

    def test_all_strengths_have_behavior_and_why(self, coaching_data):
        """Strengths must have behavior + why_effective."""
        for strength in coaching_data["strengths"]:
            assert "behavior" in strength and strength["behavior"], \
                f"{strength['call']}: coaching strength missing 'behavior'"
            assert "why_effective" in strength and strength["why_effective"], \
                f"{strength['call']}: coaching strength missing 'why_effective'"

    def test_known_sop_metrics(self, coaching_data):
        """If related_sop_metric is set, it must be in the registry (or close match)."""
        for issue in coaching_data["issues"]:
            metric = issue.get("related_sop_metric")
            if metric and metric not in SOP_METRIC_REGISTRY:
                # Check for close matches (case-insensitive)
                close = [k for k in SOP_METRIC_REGISTRY if k.lower() == metric.lower()]
                assert close, \
                    f"{issue['call']}: unknown SOP metric '{metric}' in coaching issue"

    def test_issues_have_sop_linkage(self, coaching_data):
        """At least some coaching issues should have related_sop_metric."""
        linked = [i for i in coaching_data["issues"] if i.get("related_sop_metric")]
        if len(coaching_data["issues"]) > 0:
            assert len(linked) > 0, \
                "No coaching issues have related_sop_metric — expected at least some linkage"

    def test_issue_text_not_truncated(self, coaching_data):
        """Issue text should be substantial (not just a label)."""
        for issue in coaching_data["issues"]:
            assert len(issue.get("issue", "")) > 40, \
                f"{issue['call']}: issue text too short: '{issue.get('issue', '')[:50]}'"
            assert len(issue.get("why_it_matters", "")) > 40, \
                f"{issue['call']}: why_it_matters too short"
            assert len(issue.get("how_to_fix", "")) > 40, \
                f"{issue['call']}: how_to_fix too short"
