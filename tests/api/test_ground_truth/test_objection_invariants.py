"""
Objection invariants — validate objection detection against
tenant scoring_config and industry patterns.

Rules enforced:
  1. Categories match known 1-10 (or extended company-specific, e.g. 12)
  2. Each objection has category, text, overcome, confidence, severity
  3. Confidence score in 0-1 range
  4. response_suggestions present for true objections

Ground truth: tenant_onboarding_audit_otto_ai_storage.json → scoring_config
"""
import pytest
import requests

from tests.api.test_data.f438b048_data import ALL_CALLS

ENDPOINT = "/api/v1/call-processing/summary"

# Known objection categories from PDF §2.3 + company-specific extensions
KNOWN_CATEGORIES = {
    1: "Immediate Service Unavailability",
    2: "Phone Connection Issues",
    3: "Customer Needs Time to Decide",
    4: "Scheduling Conflicts",
    5: "Service Fee Concerns",
    6: "In-Person Estimates Only",
    7: "Inefficient Agent Communication",
    8: "Customer Data Privacy Concerns",
    9: "Other",
    10: "Service Not Catered",
    12: "Prior Negative Experience",  # company-specific extension
}


@pytest.mark.usefixtures("api_available")
class TestObjectionInvariants:
    """Validate objection data against the multi-agent debate spec."""

    @pytest.fixture
    def objection_data(self, api_base_url, api_headers):
        """Extract all objections from test calls."""
        data = []
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code != 200:
                continue
            resp = r.json()
            for obj in resp.get("objections", {}).get("objections", []):
                data.append({"call": call_id[:8], **obj})
        return data

    def test_total_count_matches(self, api_base_url, api_headers):
        """objections.total_count must match len(objections.objections)."""
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code != 200:
                continue
            resp = r.json()
            obj_section = resp.get("objections", {})
            assert obj_section.get("total_count", 0) == len(obj_section.get("objections", [])), \
                f"{call_id[:8]}: total_count={obj_section.get('total_count')} doesn't match objections count"

    def test_known_categories(self, objection_data):
        """Each objection must have a known category_id."""
        for obj in objection_data:
            cid = obj.get("category_id")
            assert cid in KNOWN_CATEGORIES, \
                f"{obj['call']}: unknown category_id={cid}"

    def test_category_text_matches(self, objection_data):
        """Category text should match the known mapping."""
        for obj in objection_data:
            cid = obj.get("category_id")
            text = obj.get("category_text")
            if cid in KNOWN_CATEGORIES:
                assert text == KNOWN_CATEGORIES[cid], \
                    f"{obj['call']}: category_id={cid} has text='{text}', expected '{KNOWN_CATEGORIES[cid]}'"

    def test_objection_has_required_fields(self, objection_data):
        """Each objection must have category, text, overcome, confidence, severity."""
        for obj in objection_data:
            assert "objection_text" in obj and obj["objection_text"], \
                f"{obj['call']}: objection missing objection_text"
            assert "overcome" in obj, \
                f"{obj['call']}: objection missing overcome status"
            assert isinstance(obj.get("overcome"), bool), \
                f"{obj['call']}: overcome must be boolean, got {type(obj.get('overcome'))}"
            assert "confidence_score" in obj, \
                f"{obj['call']}: objection missing confidence_score"
            assert 0 <= obj.get("confidence_score", -1) <= 1, \
                f"{obj['call']}: confidence_score={obj.get('confidence_score')} out of range"
            assert obj.get("severity") in ("high", "medium", "low"), \
                f"{obj['call']}: invalid severity '{obj.get('severity')}'"

    def test_response_suggestions_present(self, objection_data):
        """response_suggestions should be present."""
        for obj in objection_data:
            suggestions = obj.get("response_suggestions")
            assert suggestions is not None, \
                f"{obj['call']}: missing response_suggestions field"
            assert len(suggestions) > 0, \
                f"{obj['call']}: response_suggestions is empty — should have SOP-based recommendations"

    def test_high_severity_has_specific_text(self, objection_data):
        """High-severity objections should have specific objection text."""
        for obj in objection_data:
            if obj.get("severity") == "high":
                assert len(obj.get("objection_text", "")) > 20, \
                    f"{obj['call']}: high-severity objection text too short"

    def test_category_9_has_sub_objection(self, objection_data):
        """Category 9 'Other' should have sub_objection populated."""
        for obj in objection_data:
            if obj.get("category_id") == 9:
                assert obj.get("sub_objection"), \
                    f"{obj['call']}: category 9 'Other' missing sub_objection"
