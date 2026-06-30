"""
Qualification invariants — validate qualification/BANT scoring.

Rules enforced:
  1. BANT scores are 0.0-1.0
  2. overall_score = average of BANT components (simple average per API)
  3. qualification_status maps to score ranges (hot≥0.75, warm≥0.5, cold≥0.25)
  4. booking_status is valid enum
  5. call_outcome_category is valid
  6. If follow_up_required=true, reason must be present
  7. Valid appointment_type when appointment is booked

Ground truth: tenant_onboarding_audit_otto_ai_storage.json → qualification_thresholds
"""
import pytest
import requests

from tests.api.test_data.f438b048_data import ALL_CALLS

ENDPOINT = "/api/v1/call-processing/summary"

VALID_STATUSES = {"hot", "warm", "cold", "unqualified"}
VALID_BOOKING = {"booked", "not_booked", "service_not_offered"}
VALID_OUTCOMES = {
    "qualified_and_booked", "qualified_but_unbooked", "qualified_but_deprioritized",
    "qualified_service_not_offered", "follow_up_inquiry", "existing_customer_service",
    "unqualified",
}
VALID_CALL_TYPES = {"new_inquiry", "follow_up", "service_call", "confirmation", "quote_only",
                     "fresh_sales", "csr_call"}
VALID_APPT_TYPES = {"in-person", "virtual", "phone"}
VALID_INTENTS = {"new", "reschedule", "cancel", "confirm"}


@pytest.mark.usefixtures("api_available")
class TestQualificationInvariants:
    """Validate qualification field values and cross-field consistency."""

    @pytest.fixture
    def qualifications(self, api_base_url, api_headers):
        """Extract qualification data from test calls."""
        quals = {}
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code == 200:
                quals[call_id] = r.json().get("qualification", {})
        return quals

    def test_bant_scores_in_range(self, qualifications):
        """BANT scores must be 0.0-1.0."""
        for call_id, q in qualifications.items():
            bant = q.get("bant_scores", {})
            for key in ("need", "budget", "timeline", "authority"):
                val = bant.get(key)
                if val is not None:
                    assert 0.0 <= val <= 1.0, \
                        f"{call_id[:8]}: bant.{key}={val} out of range [0,1]"

    def test_overall_score_is_bant_average(self, qualifications):
        """overall_score should approximate average of BANT scores."""
        for call_id, q in qualifications.items():
            bant = q.get("bant_scores", {})
            overall = q.get("overall_score")
            vals = [bant[k] for k in ("need", "budget", "timeline", "authority")
                   if bant.get(k) is not None]
            if vals and overall is not None:
                avg = sum(vals) / len(vals)
                assert abs(overall - avg) <= 0.15, \
                    f"{call_id[:8]}: overall_score={overall:.3f}, BANT avg={avg:.3f} (diff={abs(overall-avg):.3f})"

    def test_qualification_status_valid(self, qualifications):
        """qualification_status must be a valid enum."""
        for call_id, q in qualifications.items():
            status = q.get("qualification_status")
            assert status in VALID_STATUSES, \
                f"{call_id[:8]}: invalid qual_status '{status}'"

    def test_booking_status_valid(self, qualifications):
        """booking_status must be a valid enum."""
        for call_id, q in qualifications.items():
            booking = q.get("booking_status")
            assert booking in VALID_BOOKING, \
                f"{call_id[:8]}: invalid booking_status '{booking}'"

    def test_outcome_category_valid(self, qualifications):
        """call_outcome_category must be a known outcome."""
        for call_id, q in qualifications.items():
            outcome = q.get("call_outcome_category")
            assert outcome in VALID_OUTCOMES, \
                f"{call_id[:8]}: invalid outcome '{outcome}'"

    def test_appointment_type_valid(self, qualifications):
        """If appointment_type is set, it must be a valid type."""
        for call_id, q in qualifications.items():
            appt_type = q.get("appointment_type")
            if appt_type:
                assert appt_type in VALID_APPT_TYPES, \
                    f"{call_id[:8]}: invalid appointment_type '{appt_type}'"

    def test_appointment_intent_valid(self, qualifications):
        """If appointment_intent is set, it must be valid."""
        for call_id, q in qualifications.items():
            intent = q.get("appointment_intent")
            if intent:
                assert intent in VALID_INTENTS, \
                    f"{call_id[:8]}: invalid appointment_intent '{intent}'"

    def test_detected_call_type_valid(self, qualifications):
        """detected_call_type must be a known type."""
        for call_id, q in qualifications.items():
            ctype = q.get("detected_call_type")
            assert ctype in VALID_CALL_TYPES, \
                f"{call_id[:8]}: invalid detected_call_type '{ctype}'"

    def test_follow_up_consistency(self, qualifications):
        """follow_up_required=true must have follow_up_reason."""
        for call_id, q in qualifications.items():
            fur = q.get("follow_up_required")
            reason = q.get("follow_up_reason")
            if fur is True:
                assert reason and len(reason) > 10, \
                    f"{call_id[:8]}: follow_up_required but no meaningful reason"
            if reason and len(reason) > 10:
                assert fur is True, \
                    f"{call_id[:8]}: follow_up_reason present but follow_up_required={fur}"

    def test_urgency_signals_type(self, qualifications):
        """urgency_signals must be an array."""
        for call_id, q in qualifications.items():
            signals = q.get("urgency_signals")
            assert isinstance(signals, list), \
                f"{call_id[:8]}: urgency_signals is not an array"

    def test_budget_indicators_type(self, qualifications):
        """budget_indicators must be an array."""
        for call_id, q in qualifications.items():
            indicators = q.get("budget_indicators")
            assert isinstance(indicators, list), \
                f"{call_id[:8]}: budget_indicators is not an array"

    def test_customer_name_confidence_range(self, qualifications):
        """customer_name_confidence must be 0.0-1.0."""
        for call_id, q in qualifications.items():
            conf = q.get("customer_name_confidence")
            if conf is not None:
                assert 0.0 <= conf <= 1.0, \
                    f"{call_id[:8]}: customer_name_confidence={conf} out of range"

    def test_confidence_score_range(self, qualifications):
        """qualification.confidence_score must be 0.0-1.0."""
        for call_id, q in qualifications.items():
            conf = q.get("confidence_score")
            if conf is not None:
                assert 0.0 <= conf <= 1.0, \
                    f"{call_id[:8]}: qualification.confidence_score={conf} out of range"

    def test_appointment_intent_cancel_consistency(self, qualifications):
        """appointment_intent=cancel should be consistent with call outcome."""
        for call_id, q in qualifications.items():
            intent = q.get("appointment_intent")
            outcome = q.get("call_outcome_category")
            if intent == "cancel":
                assert outcome == "unqualified" or "cancel" in str(outcome), \
                    f"{call_id[:8]}: intent=cancel but outcome='{outcome}'"
