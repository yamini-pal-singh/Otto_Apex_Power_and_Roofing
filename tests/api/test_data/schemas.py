"""
JSON Schema definitions derived from API response structure.
Validates response shape matches expected contract.

Ground truth: CSR_SOP.pdf, SALES_REP_SOP.pdf, Reference.docx.pdf
"""
from jsonschema import validate, ValidationError

# ── Top-level Summary Response Schema ──
SUMMARY_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["call_id", "company_id", "status", "summary", "compliance", "objections", "qualification"],
    "properties": {
        "call_id": {"type": "string"},
        "company_id": {"type": "string"},
        "status": {"type": "string", "enum": ["completed", "processing", "queued", "failed"]},
        "processed_at": {"type": ["string", "null"]},
        "summary": {
            "type": "object",
            "required": ["summary", "key_points", "action_items", "next_steps", "pending_actions",
                         "sentiment_score", "confidence_score"],
            "properties": {
                "summary": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "action_items": {"type": "array", "items": {"type": "string"}},
                "next_steps": {"type": "array", "items": {"type": "string"}},
                "pending_actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["type", "action_item", "owner", "raw_text", "confidence", "category"],
                        "properties": {
                            "type": {"type": "string"},
                            "action_item": {"type": "string"},
                            "owner": {"type": "string"},
                            "due_at": {"type": ["string", "null"]},
                            "raw_text": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "contact_method": {"type": ["string", "null"]},
                            "category": {"type": "string"},
                        },
                    },
                },
                "sentiment_score": {"type": "number", "minimum": 0, "maximum": 1},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
            },
        },
        "compliance": {
            "type": "object",
            "required": ["sop_compliance"],
            "properties": {
                "target_role": {"type": "string"},
                "evaluation_mode": {"type": "string"},
                "sop_compliance": {
                    "type": "object",
                    "required": ["score", "stages", "coaching_issues", "coaching_strengths"],
                    "properties": {
                        "score": {"type": "number", "minimum": 0, "maximum": 1},
                        "compliance_rate": {"type": "number", "minimum": 0, "maximum": 1},
                        "stages": {
                            "type": "object",
                            "properties": {
                                "total": {"type": "integer", "minimum": 0},
                                "followed": {"type": "array", "items": {"type": "string"}},
                                "missed": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "positive_behaviors": {"type": "array", "items": {"type": "string"}},
                        "coaching_issues": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["issue", "why_it_matters", "how_to_fix", "severity"],
                                "properties": {
                                    "issue": {"type": "string"},
                                    "why_it_matters": {"type": "string"},
                                    "how_to_fix": {"type": "string"},
                                    "example_language": {"type": ["string", "null"]},
                                    "transcript_evidence": {"type": ["string", "null"]},
                                    "related_sop_metric": {"type": ["string", "null"]},
                                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                                },
                            },
                        },
                        "coaching_strengths": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["behavior", "why_effective"],
                                "properties": {
                                    "behavior": {"type": "string"},
                                    "why_effective": {"type": "string"},
                                    "transcript_evidence": {"type": ["string", "null"]},
                                    "related_sop_metric": {"type": ["string", "null"]},
                                },
                            },
                        },
                        "confidence": {"type": ["number", "null"]},
                    },
                },
            },
        },
        "objections": {
            "type": "object",
            "required": ["total_count", "objections"],
            "properties": {
                "total_count": {"type": "integer", "minimum": 0},
                "objections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category_id": {"type": "integer"},
                            "category_text": {"type": "string"},
                            "sub_objection": {"type": ["string", "null"]},
                            "objection_text": {"type": "string"},
                            "overcome": {"type": "boolean"},
                            "speaker_id": {"type": "string"},
                            "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                            "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                            "response_suggestions": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        },
        "qualification": {
            "type": "object",
            "required": ["bant_scores", "overall_score", "qualification_status", "booking_status",
                         "call_outcome_category"],
            "properties": {
                "bant_scores": {
                    "type": "object",
                    "properties": {
                        "need": {"type": "number", "minimum": 0, "maximum": 1},
                        "budget": {"type": "number", "minimum": 0, "maximum": 1},
                        "timeline": {"type": "number", "minimum": 0, "maximum": 1},
                        "authority": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                },
                "overall_score": {"type": "number", "minimum": 0, "maximum": 1},
                "qualification_status": {"type": "string"},
                "booking_status": {"type": "string"},
                "call_outcome_category": {"type": "string"},
                "appointment_confirmed": {"type": "boolean"},
                "appointment_date": {"type": ["string", "null"]},
                "appointment_type": {"type": ["string", "null"]},
                "scope_classification": {"type": "string"},
                "customer_name": {"type": ["string", "null"]},
                "customer_name_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "follow_up_required": {"type": "boolean"},
                "follow_up_reason": {"type": ["string", "null"]},
                "detected_call_type": {"type": "string"},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
            },
        },
        "lead_score": {"type": ["object", "null"]},
        "created_at": {"type": ["string", "null"]},
    },
}


def validate_summary_response(data):
    """Validate response data against the summary schema.
    Returns (is_valid, errors) tuple.
    """
    try:
        validate(instance=data, schema=SUMMARY_RESPONSE_SCHEMA)
        return True, []
    except ValidationError as e:
        return False, [e.message]


# ── Call List Response Schema ──
CALL_LIST_SCHEMA = {
    "type": "object",
    "required": ["company_id", "total", "calls"],
    "properties": {
        "company_id": {"type": "string"},
        "total": {"type": "integer", "minimum": 0},
        "limit": {"type": "integer"},
        "offset": {"type": "integer"},
        "calls": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["call_id", "company_id", "status"],
                "properties": {
                    "call_id": {"type": "string"},
                    "company_id": {"type": "string"},
                    "status": {"type": "string"},
                    "rep_role": {"type": ["string", "null"]},
                    "duration": {"type": ["number", "null"]},
                    "call_date": {"type": ["string", "null"]},
                },
            },
        },
    },
}
