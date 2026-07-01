# Otto Apex Power Roofing — API Test Suite

## Overview
Pytest-based test suite for the Otto Intelligence API, testing against the
**Apex Power Roofing** tenant (company f438b048). All test logic follows the
**Updated_Otto_API_Documentation.md** as the ground-truth specification —
the API doc is the QA process document.

## Setup

```bash
pip install -r requirements.txt

# copy .env.example to .env and fill in your API key
cp .env.example .env
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test module
pytest tests/api/test_ground_truth/test_cross_field_consistency.py -v

# Run schema contract tests only
pytest -m contract -v

# Run ground-truth invariant tests
pytest -m ground_truth -v

# Generate HTML report
pytest --html=report.html --self-contained-html

# Run and show print() output
pytest -v -s
```

## Test Structure

```
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Dependencies
├── .env                          # API keys (not committed)
├── docs/
│   ├── Otto_Intelligence_Architecture_Changes_v2.pdf
│   └── Updated_Otto_API_Documentation.md
└── tests/
    └── api/
        ├── conftest.py           # API fixtures (base_url, headers, api_available)
        ├── test_data/
        │   ├── __init__.py
        │   ├── f438b048_data.py  # Test calls + ground truth expectations
        │   ├── sop_metrics.py    # SOP metric registry
        │   └── schemas.py        # JSON Schema definitions from API doc
        └── test_ground_truth/
            ├── __init__.py
            ├── test_schema_contracts.py         # Validate response shape vs API doc
            ├── test_cross_field_consistency.py  # Cross-field business rules
            ├── test_coaching_invariants.py      # 3-question coaching framework
            ├── test_objection_invariants.py      # Objection detection rules
            ├── test_qualification_invariants.py # Qualification rules
            ├── test_sop_metric_registry.py      # SOP metric consistency
            └── test_regression_comparison.py    # Snapshot-based regression
    └── reports/
        └── generate_report.py              # 9-tab Excel report generator

```

## Report Generation

Generate the 9-tab Excel compliance report (CSR, Sales, Summary, Objections,
Compliance, Qualification, Cross-field, Coaching, Metadata):

```bash
python tests/api/reports/generate_report.py
```

## Test Principles

1. **API doc is the ground truth** — all pass/fail is determined by what the
   specification says should happen, not what the API returns
2. **Empty results can be violations** — e.g., empty `pending_actions` when
   action items contain commitments is a pipeline failure
3. **Every test has a PDF/doc section reference** — tests cite their rule source
