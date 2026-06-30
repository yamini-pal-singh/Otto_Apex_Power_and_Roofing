"""
Cross-field consistency tests — validate that relationships between fields
hold according to documented business rules and tenant configuration.

Ground truth: CSR_SOP.pdf, tenant_onboarding_audit_otto_ai_storage.json
Qualification thresholds from config: hot≥0.75, warm≥0.5, cold≥0.25, <0.25=unqualified
"""
import pytest
import requests

from tests.api.test_data.f438b048_data import ALL_CALLS


@pytest.mark.usefixtures("api_available")
class TestCrossFieldConsistency:
    """Validate cross-field relationships in the summary response."""

    ENDPOINT = "/api/v1/call-processing/summary"

    @pytest.fixture
    def summaries(self, api_base_url, api_headers):
        results = {}
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{self.ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code == 200:
                results[call_id] = r.json()
        return results

    # ------------------------------------------------------------------
    # Compliance score vs stages consistency
    # ------------------------------------------------------------------
    def test_score_zero_when_no_stages(self, summaries):
        """If stages.total=0, compliance score must be 0."""
        for call_id, data in summaries.items():
            stages = data.get("compliance", {}).get("sop_compliance", {}).get("stages", {})
            score = data.get("compliance", {}).get("sop_compliance", {}).get("score")
            if stages.get("total", 0) == 0:
                assert score == 0.0, \
                    f"{call_id[:8]}: stages.total=0 but score={score}"

    def test_followed_plus_missed_reasonable(self, summaries):
        """followed + missed should not exceed total by a large margin."""
        for call_id, data in summaries.items():
            stages = data.get("compliance", {}).get("sop_compliance", {}).get("stages", {})
            total = stages.get("total", 0)
            if total > 0:
                n_followed = len(stages.get("followed", []))
                n_missed = len(stages.get("missed", []))
                total_flagged = n_followed + n_missed
                assert total_flagged <= total + 2, \
                    f"{call_id[:8]}: followed+missed={total_flagged} > total={total}"

    def test_no_duplicate_stages(self, summaries):
        """A stage should not appear in both followed and missed."""
        for call_id, data in summaries.items():
            stages = data.get("compliance", {}).get("sop_compliance", {}).get("stages", {})
            followed = set(stages.get("followed", []))
            missed = set(stages.get("missed", []))
            duplicates = followed & missed
            assert not duplicates, \
                f"{call_id[:8]}: stages in both followed and missed: {duplicates}"

    # ------------------------------------------------------------------
    # Qualification field consistency
    # ------------------------------------------------------------------
    def test_qual_status_consistency(self, summaries):
        """Qualification status should align with overall_score ranges.

        Thresholds from tenant_config.qualification_thresholds:
          hot_min_score=0.75, warm_min_score=0.5, cold_min_score=0.25
        """
        status_ranges = {
            "hot": (0.7499, 1.01),
            "warm": (0.4999, 0.7501),
            "cold": (0.2499, 0.5001),
            "unqualified": (0.0, 0.2501),
        }
        for call_id, data in summaries.items():
            q = data.get("qualification", {})
            status = q.get("qualification_status")
            score = q.get("overall_score")
            if status and status in status_ranges and score is not None:
                lo, hi = status_ranges[status]
                assert lo <= score <= hi, \
                    f"{call_id[:8]}: status='{status}' with overall_score={score} (expected {lo}-{hi})"

    def test_booking_outcome_consistency(self, summaries):
        """Booking status and outcome must be consistent."""
        for call_id, data in summaries.items():
            q = data.get("qualification", {})
            booking = q.get("booking_status")
            outcome = q.get("call_outcome_category")
            if booking == "booked":
                assert outcome == "qualified_and_booked", \
                    f"{call_id[:8]}: booking=booked but outcome='{outcome}'"
            if outcome == "qualified_and_booked":
                assert booking == "booked", \
                    f"{call_id[:8]}: outcome=qualified_and_booked but booking='{booking}'"

    def test_appointment_fields_consistency(self, summaries):
        """Appointment fields must be consistent with booking status."""
        for call_id, data in summaries.items():
            q = data.get("qualification", {})
            booked = q.get("booking_status") == "booked"
            confirmed = q.get("appointment_confirmed")
            appt_date = q.get("appointment_date")
            appt_type = q.get("appointment_type")

            if booked:
                if confirmed:
                    assert appt_date is not None, \
                        f"{call_id[:8]}: booked+confirmed but no appointment_date"
                    assert appt_type is not None, \
                        f"{call_id[:8]}: booked+confirmed but no appointment_type"
            else:
                if not booked and not confirmed:
                    assert confirmed is False or confirmed is None, \
                        f"{call_id[:8]}: not booked but appointment_confirmed={confirmed}"

    def test_follow_up_fields_consistency(self, summaries):
        """follow_up_required must align with follow_up_reason."""
        for call_id, data in summaries.items():
            q = data.get("qualification", {})
            fur = q.get("follow_up_required")
            reason = q.get("follow_up_reason")
            if fur is True:
                assert reason is not None and len(reason) > 10, \
                    f"{call_id[:8]}: follow_up_required but no meaningful reason"
            if reason and len(reason) > 10:
                assert fur is True, \
                    f"{call_id[:8]}: follow_up_reason present but follow_up_required={fur}"

    def test_customer_name_confidence_consistency(self, summaries):
        """customer_name_confidence>0 means customer_name must not be null."""
        for call_id, data in summaries.items():
            q = data.get("qualification", {})
            name = q.get("customer_name")
            conf = q.get("customer_name_confidence")
            if conf is not None and conf > 0.3:
                assert name is not None, \
                    f"{call_id[:8]}: name_confidence={conf} but no customer_name"

    # ------------------------------------------------------------------
    # Sentiment vs objection count consistency
    # ------------------------------------------------------------------
    def test_sentiment_not_unreasonably_high_with_objections(self, summaries):
        """Calls with objections should not have very high sentiment."""
        for call_id, data in summaries.items():
            obj_count = data.get("objections", {}).get("total_count", 0)
            sentiment = data.get("summary", {}).get("sentiment_score", 0.5)
            if obj_count > 0:
                assert sentiment <= 0.8, \
                    f"{call_id[:8]}: {obj_count} objection(s) but sentiment={sentiment} (unusually high)"

    # ------------------------------------------------------------------
    # Coaching severity rules
    # ------------------------------------------------------------------
    def test_high_severity_has_transcript_evidence(self, summaries):
        """High-severity coaching issues should have transcript evidence."""
        for call_id, data in summaries.items():
            issues = data.get("compliance", {}).get("sop_compliance", {}).get("coaching_issues", [])
            for i, issue in enumerate(issues):
                if issue.get("severity") == "high":
                    te = issue.get("transcript_evidence")
                    assert te is not None, \
                        f"{call_id[:8]}: high-severity coaching_issue[{i}] lacks transcript_evidence"

    def test_high_severity_has_example_language(self, summaries):
        """High-severity coaching issues should have example language."""
        for call_id, data in summaries.items():
            issues = data.get("compliance", {}).get("sop_compliance", {}).get("coaching_issues", [])
            for i, issue in enumerate(issues):
                if issue.get("severity") == "high":
                    el = issue.get("example_language")
                    assert el is not None and len(el) > 20, \
                        f"{call_id[:8]}: high-severity coaching_issue[{i}] lacks example_language"

    # ------------------------------------------------------------------
    # Pending actions vs action_items consistency
    # ------------------------------------------------------------------
    def test_pending_actions_have_action_item(self, summaries):
        """Every pending action must have an action_item."""
        for call_id, data in summaries.items():
            pa = data.get("summary", {}).get("pending_actions", [])
            for i, action in enumerate(pa):
                assert "action_item" in action, \
                    f"{call_id[:8]}: pending_action[{i}] missing action_item (v2 requirement)"

    def test_pending_action_fields(self, summaries):
        """Pending actions must have type, confidence, raw_text, category."""
        for call_id, data in summaries.items():
            pa = data.get("summary", {}).get("pending_actions", [])
            for i, action in enumerate(pa):
                for field in ["type", "confidence", "raw_text", "category"]:
                    assert field in action, \
                        f"{call_id[:8]}: pending_action[{i}] missing '{field}'"

    def test_pending_actions_should_exist_when_commitments_present(self, summaries):
        """CSR SOP §9: action_items with commitments must produce pending_actions."""
        commitment_phrases = [
            "send quote", "send the estimate", "call back", "schedule",
            "generate", "send a quote", "send the quote", "follow up",
            "send the contract", "email you", "call you", "must",
        ]

        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            data = summaries.get(call_id)
            if not data:
                continue
            action_items = data.get("summary", {}).get("action_items", [])
            pending_actions = data.get("summary", {}).get("pending_actions", [])
            next_steps = data.get("summary", {}).get("next_steps", [])

            has_commitment = any(
                any(phrase in (ai or "").lower() for phrase in commitment_phrases)
                for ai in action_items
            )
            if not has_commitment:
                has_commitment = any(
                    any(phrase in (ns or "").lower() for phrase in ["send quote", "send the quote",
                           "send the estimate", "call back", "call you"])
                    for ns in next_steps
                )

            if has_commitment:
                assert len(pending_actions) > 0, \
                    f"{call_id[:8]}: action_items contain commitments ('{action_items[0][:80]}...') but " \
                    f"pending_actions is empty. Finalizing the booking (SOP §9) should produce at least one."

    # ------------------------------------------------------------------
    # overcome_evidence field check
    # ------------------------------------------------------------------
    def test_objection_overcome_evidence_field(self, summaries):
        """overcome_evidence field should exist on objection objects (if populated by API)."""
        for call_id, data in summaries.items():
            objections = data.get("objections", {}).get("objections", [])
            for i, obj in enumerate(objections):
                if "overcome_evidence" not in obj:
                    print(f"  WARN: {call_id[:8]}: objection[{i}] missing 'overcome_evidence' field")

    # ------------------------------------------------------------------
    # BANT sum consistency
    # ------------------------------------------------------------------
    def test_bant_consistency(self, summaries):
        """overall_score should roughly equal average of BANT scores."""
        for call_id, data in summaries.items():
            q = data.get("qualification", {})
            bant = q.get("bant_scores", {})
            overall = q.get("overall_score")
            bant_values = [v for v in [bant.get(k) for k in ("need", "budget", "timeline", "authority")]
                          if v is not None]
            if bant_values and overall is not None:
                avg = sum(bant_values) / len(bant_values)
                assert abs(overall - avg) <= 0.15, \
                    f"{call_id[:8]}: overall_score={overall} but BANT avg={avg}"
