"""
Test data for company f438b048-9cec-47f5-a8a8-9609f48b81e6 (Apex Power Roofing).
Two completed calls with contrasting profiles for ground-truth validation.

Company: Apex Power & Roofing (f438b048-9cec-47f5-a8a8-9609f48b81e6)
Base URL: https://ottoai.shunyalabs.ai

Ground truth sources:
  - CSR_SOP.pdf (CSR Standard Operating Procedure)
  - SALES_REP_SOP.pdf (Sales Rep Field SOP)
  - Reference.docx.pdf (Company & Product Reference)
  - tenant_onboarding_audit_otto_ai_storage.json (tenant config)
"""

COMPANY_ID = "f438b048-9cec-47f5-a8a8-9609f48b81e6"
COMPANY_TOTAL_CALLS = 616  # verified 2026-06-30

# ---------------------------------------------------------------------------
# Call 1 — Cancellation / objection scenario (sales_rep, James Bond)
# ---------------------------------------------------------------------------
CALL_JAMES_BOND_ID = "4bf68a1b-3815-4fa8-b896-4aee02614bfb"
CALL_JAMES_BOND_META = {
    "agent_name": "James Bond",
    "role": "sales_rep",
    "interaction_type": "meeting",
    "call_type": "sales_call",
    "is_appointment": True,
    "date": "2026-06-24T10:00:00Z",
}

# Ground truth expectations for Call 1
CALL_JAMES_BOND_GT = {
    "has_objection": True,
    "expected_objection_count": 1,
    "expected_category_id": 12,
    "expected_category_text": "Prior Negative Experience",
    "expected_severity": "high",
    "min_confidence": 0.9,
    "expected_overcome": False,
    "expected_sentiment_low": 0.0,
    "expected_sentiment_high": 0.4,
    "expected_compliance_score_low": 0.0,
    "expected_compliance_score_high": 0.4,
    "expected_qual_status": "cold",
    "expected_booking_status": "not_booked",
    "expected_outcome": "unqualified",
    "expected_call_type": "fresh_sales",
    "expected_scope": "IN_SCOPE",
    "expected_customer": "Jake",
    "coaching_issues_count": 1,
    "coaching_strengths_count": 1,
    "has_lead_score": False,
    # PDF §4.2: No actionable commitments (process descriptions only → excluded)
    "has_pending_actions": False,
}

# ---------------------------------------------------------------------------
# Call 2 — Service call / follow-up (customer_rep, Iseah Alegria)
# ---------------------------------------------------------------------------
CALL_ISEAH_ID = "bb219502-3022-413b-8035-66ce7a08575c"
CALL_ISEAH_META = {
    "agent_name": "Iseah Alegria",
    "role": "customer_rep",
    "interaction_type": "phone_call",
    "call_type": "csr_call",
    "is_appointment": False,
    "date": "2026-06-23T18:07:23Z",
    "phone": "+16027365482",
    "direction": "Outbound",
}

# Ground truth expectations for Call 2
CALL_ISEAH_GT = {
    "has_objection": False,
    "expected_objection_count": 0,
    "expected_sentiment_low": 0.6,
    "expected_sentiment_high": 1.0,
    "expected_compliance_score_low": 0.0,
    "expected_compliance_score_high": 0.0,
    "expected_qual_status": "hot",
    "expected_booking_status": "not_booked",
    "expected_outcome": "qualified_but_unbooked",
    "expected_call_type": "service_call",
    "expected_scope": "IN_SCOPE",
    "expected_customer": "Brad",
    "coaching_issues_count": 2,
    "coaching_strengths_count": 1,
    "has_lead_score": False,
    # PDF §4.2: action item "send quote" is rep_commitment → should be pending_action
    "has_pending_actions": True,
    "follow_up_required": True,
    "follow_up_reason_contains": "quote",
}

# ---------------------------------------------------------------------------
# All calls for iteration
# ---------------------------------------------------------------------------
ALL_CALLS = [
    {"call_id": CALL_JAMES_BOND_ID, "meta": CALL_JAMES_BOND_META, "gt": CALL_JAMES_BOND_GT},
    {"call_id": CALL_ISEAH_ID, "meta": CALL_ISEAH_META, "gt": CALL_ISEAH_GT},
]
