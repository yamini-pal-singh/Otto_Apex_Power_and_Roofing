"""
SOP Metric Registry — derived from the tenant config in
tenant_onboarding_audit_otto_ai_storage.json (20 CSR SOP metrics)
plus additional metrics observed from the live coaching API.

Each entry records the metric_id with metadata from config or API observation.

Ground truth: tenant_onboarding_audit_otto_ai_storage.json → sop_metrics
             + live API coaching responses
"""
from collections import Counter

# Registry: metric_id -> {name, section, weight, category}
# 20 configured CSR metrics + additional API-observed metrics
SOP_METRIC_REGISTRY = {
    # ── Configured CSR SOP metrics (from tenant config, role=customer_rep) ──
    "call_qualification": {"name": "Call Qualification", "section": "CSR Mission", "weight": 0.0714, "category": "discovery"},
    "service_type_booking": {"name": "Accurate Service Type Booking", "section": "CSR Mission", "weight": 0.0714, "category": "booking"},
    "accurate_call_tagging": {"name": "Accurate Call Tagging", "section": "CSR Mission; Section 12", "weight": 0.0357, "category": "administrative"},
    "setting_customer_expectations": {"name": "Setting Customer Expectations", "section": "CSR Mission; Section 9", "weight": 0.0714, "category": "closing"},
    "standard_greeting_adherence": {"name": "Standard Greeting Adherence", "section": "Section 1: Greeting", "weight": 0.0357, "category": "opening"},
    "customer_identification": {"name": "Customer Identification & Profiling", "section": "Customer Identification", "weight": 0.0536, "category": "discovery"},
    "problem_investigation_and_safety": {"name": "Problem Investigation & Safety Check", "section": "Section 2: The Problem", "weight": 0.0536, "category": "discovery"},
    "decision_maker_identification": {"name": "Decision-Maker Identification", "section": "Section 2: The Decision-Maker", "weight": 0.0357, "category": "discovery"},
    "access_verification": {"name": "Access Verification", "section": "Section 2: Access", "weight": 0.0357, "category": "discovery"},
    "electrical_emergency_handling": {"name": "Electrical Emergency Handling", "section": "Section 10: Emergency Protocol", "weight": 0.0714, "category": "discovery"},
    "booking_hard_rules_compliance": {"name": "Booking Hard Rules Adherence", "section": "Section 6: Do Not Book", "weight": 0.0714, "category": "booking"},
    "opportunity_classification": {"name": "Opportunity Classification", "section": "Section 7: Opportunity Class.", "weight": 0.0357, "category": "administrative"},
    "job_summary_documentation": {"name": "Job Summary Documentation", "section": "Section 8; Section 12", "weight": 0.0357, "category": "administrative"},
    "job_level_classification": {"name": "Job Level Classification", "section": "Section 8: Levels", "weight": 0.0357, "category": "administrative"},
    "roofing_booking_tags": {"name": "Roofing Booking Tags (Roof Age)", "section": "Section 8: Roofing Tags", "weight": 0.0357, "category": "administrative"},
    "solar_status_verification": {"name": "Solar Status Verification", "section": "Solar: Yes | No", "weight": 0.0357, "category": "administrative"},
    "roofing_emergency_handling": {"name": "Roofing Emergency Handling", "section": "Section 10: Emergency Protocol", "weight": 0.0714, "category": "booking"},
    "after_hours_surcharge_communication": {"name": "After-Hours Surcharge Communication", "section": "Section 10: After-Hours", "weight": 0.0536, "category": "closing"},
    "common_scenario_script_adherence": {"name": "Common Scenario Script Adherence", "section": "Section 11: Common Scripts", "weight": 0.0536, "category": "objection_handling"},
    "club_member_acknowledgment": {"name": "Club Member Acknowledgment", "section": "Section 11: Common Scripts", "weight": 0.0357, "category": "discovery"},
    # ── Additional API-observed metrics (from live coaching responses) ──
    "quote_expectation_setting": {"name": "Quote Expectation Setting", "section": "API-observed", "weight": 0.0, "category": "closing"},
    "maintenance_upsell_resolution": {"name": "Maintenance Upsell/Resolution", "section": "API-observed", "weight": 0.0, "category": "closing"},
    "technical_explanation": {"name": "Technical Explanation & Reassurance", "section": "API-observed", "weight": 0.0, "category": "communication"},
}

TOTAL_METRICS = len(SOP_METRIC_REGISTRY)
METRIC_IDS = set(SOP_METRIC_REGISTRY.keys())
CATEGORIES = {m["category"] for m in SOP_METRIC_REGISTRY.values()}
TOTAL_WEIGHT = sum(m["weight"] for m in SOP_METRIC_REGISTRY.values())
CONFIGURED_METRICS = {k for k, v in SOP_METRIC_REGISTRY.items() if v["weight"] > 0}

