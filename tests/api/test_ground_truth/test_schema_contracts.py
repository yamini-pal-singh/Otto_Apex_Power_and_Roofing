"""
Schema contract tests — validate API response structure against
the JSON Schema definitions derived from API response shape.

Ground truth: CSR_SOP.pdf, SALES_REP_SOP.pdf, Reference.docx.pdf
"""
import pytest
import requests

from tests.api.test_data.schemas import validate_summary_response
from tests.api.test_data.f438b048_data import ALL_CALLS

ENDPOINT = "/api/v1/call-processing/summary"


@pytest.mark.usefixtures("api_available")
class TestSummarySchemaContracts:
    """Validate response shape matches the API documentation."""

    @pytest.fixture
    def responses(self, api_base_url, api_headers):
        results = {}
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code == 200:
                results[call_id] = r.json()
        return results

    def test_all_responses_valid(self, responses):
        """Every response must pass JSON Schema validation."""
        errors = []
        for call_id, data in responses.items():
            valid, errs = validate_summary_response(data)
            if not valid:
                errors.append(f"{call_id[:8]}: {errs}")
        assert not errors, "\n".join(errors[:5])

    def test_required_fields_present(self, responses):
        """All required top-level fields must be present."""
        for call_id, data in responses.items():
            for field in ["call_id", "company_id", "status", "summary", "compliance",
                          "objections", "qualification"]:
                assert field in data, \
                    f"{call_id[:8]}: missing required field '{field}'"

    def test_summary_has_all_sections(self, responses):
        """Summary section must have all documented fields."""
        for call_id, data in responses.items():
            s = data.get("summary", {})
            for field in ["summary", "key_points", "action_items", "next_steps",
                          "pending_actions", "sentiment_score", "confidence_score"]:
                assert field in s, \
                    f"{call_id[:8]}: summary missing '{field}'"

    def test_pending_actions_structure(self, responses):
        """Each pending action must conform to the documented schema."""
        for call_id, data in responses.items():
            pa_list = data.get("summary", {}).get("pending_actions", [])
            for i, pa in enumerate(pa_list):
                for field in ["type", "action_item", "owner", "raw_text",
                              "confidence", "category"]:
                    assert field in pa, \
                        f"{call_id[:8]}: pending_actions[{i}] missing '{field}'"
                # Confidence must be 0-1
                if "confidence" in pa:
                    assert 0 <= pa["confidence"] <= 1, \
                        f"{call_id[:8]}: pending_actions[{i}] confidence={pa['confidence']} out of range"

    def test_coaching_issues_structure(self, responses):
        """Each coaching issue must have the 3-question framework."""
        for call_id, data in responses.items():
            issues = data.get("compliance", {}).get("sop_compliance", {}).get("coaching_issues", [])
            for i, ci in enumerate(issues):
                for field in ["issue", "why_it_matters", "how_to_fix", "severity"]:
                    assert field in ci, \
                        f"{call_id[:8]}: coaching_issues[{i}] missing '{field}'"
                assert ci["severity"] in ("high", "medium", "low"), \
                    f"{call_id[:8]}: coaching_issues[{i}] invalid severity '{ci['severity']}'"

    def test_coaching_strengths_structure(self, responses):
        """Each coaching strength must have expected fields."""
        for call_id, data in responses.items():
            strengths = data.get("compliance", {}).get("sop_compliance", {}).get("coaching_strengths", [])
            for i, cs in enumerate(strengths):
                for field in ["behavior", "why_effective"]:
                    assert field in cs, \
                        f"{call_id[:8]}: coaching_strengths[{i}] missing '{field}'"

    def test_objections_structure(self, responses):
        """Each objection must have documented fields."""
        for call_id, data in responses.items():
            objections = data.get("objections", {}).get("objections", [])
            for i, obj in enumerate(objections):
                for field in ["category_id", "category_text", "objection_text",
                              "overcome", "confidence_score", "severity"]:
                    assert field in obj, \
                        f"{call_id[:8]}: objections[{i}] missing '{field}'"
                assert obj["severity"] in ("high", "medium", "low"), \
                    f"{call_id[:8]}: objections[{i}] invalid severity '{obj['severity']}'"

    def test_qualification_structure(self, responses):
        """Qualification section must have documented fields."""
        for call_id, data in responses.items():
            q = data.get("qualification", {})
            for field in ["bant_scores", "overall_score", "qualification_status",
                          "booking_status", "call_outcome_category"]:
                assert field in q, \
                    f"{call_id[:8]}: qualification missing '{field}'"

    def test_sentiment_in_range(self, responses):
        """sentiment_score must be 0.0-1.0."""
        for call_id, data in responses.items():
            s = data.get("summary", {})
            score = s.get("sentiment_score")
            if score is not None:
                assert 0.0 <= score <= 1.0, \
                    f"{call_id[:8]}: sentiment_score={score} out of range [0,1]"
