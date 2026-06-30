"""
SOP Metric Registry tests — validate that SOP metrics referenced in coaching
issues are consistent with the known metric registry from tenant config.

Ground truth: tenant_onboarding_audit_otto_ai_storage.json → sop_metrics
"""
import pytest
import requests

from tests.api.test_data.f438b048_data import ALL_CALLS
from tests.api.test_data.sop_metrics import (
    SOP_METRIC_REGISTRY,
    TOTAL_METRICS,
    METRIC_IDS,
    CATEGORIES,
    TOTAL_WEIGHT,
    CONFIGURED_METRICS,
)


@pytest.mark.usefixtures("api_available")
class TestSOPMetricRegistry:
    """Validate SOP metric references in coaching data."""

    ENDPOINT = "/api/v1/call-processing/summary"

    @pytest.fixture
    def coaching_data(self, api_base_url, api_headers):
        """Extract all SOP metric references from test calls."""
        metrics_found = []
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{self.ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code != 200:
                continue
            data = r.json()
            sop = data.get("compliance", {}).get("sop_compliance", {})
            for issue in sop.get("coaching_issues", []):
                m = issue.get("related_sop_metric")
                sev = issue.get("severity")
                if m:
                    metrics_found.append({"metric": m, "severity": sev, "call": call_id[:8]})
            for strength in sop.get("coaching_strengths", []):
                m = strength.get("related_sop_metric")
                if m:
                    metrics_found.append({"metric": m, "severity": None, "call": call_id[:8]})
        return metrics_found

    def test_metrics_in_test_calls_belong_to_registry(self, coaching_data):
        """All SOP metrics referenced by test calls must be in the known registry."""
        for ref in coaching_data:
            m = ref["metric"]
            assert m in SOP_METRIC_REGISTRY, \
                f"Unknown SOP metric '{m}' referenced in call {ref['call']}"

    def test_no_undefined_metric_references(self, api_base_url, api_headers):
        """Scan for any metric NOT in the registry."""
        unknown = set()
        for call_info in ALL_CALLS:
            call_id = call_info["call_id"]
            r = requests.get(f"{api_base_url}{self.ENDPOINT}/{call_id}", headers=api_headers, timeout=30)
            if r.status_code != 200:
                continue
            sop = r.json().get("compliance", {}).get("sop_compliance", {})
            for issue in sop.get("coaching_issues", []):
                m = issue.get("related_sop_metric")
                if m and m not in SOP_METRIC_REGISTRY:
                    unknown.add(m)
            for strength in sop.get("coaching_strengths", []):
                m = strength.get("related_sop_metric")
                if m and m not in SOP_METRIC_REGISTRY:
                    unknown.add(m)
        assert not unknown, \
            f"Found {len(unknown)} SOP metric(s) not in registry: {unknown}"

    def test_metric_severity_is_valid(self, coaching_data):
        """SOP metric references must have valid severity or be strengths."""
        for ref in coaching_data:
            sev = ref["severity"]
            if sev is not None:
                assert sev in ("high", "medium", "low"), \
                    f"Metric '{ref['metric']}' in call {ref['call']} has invalid severity '{sev}'"

    def test_registry_has_configured_metrics(self):
        """Registry must contain the configured 20 CSR SOP metrics (+ observed)."""
        assert len(CONFIGURED_METRICS) == 20, \
            f"Expected 20 CSR metrics from config, got {len(CONFIGURED_METRICS)}"
        assert TOTAL_METRICS >= 20, \
            f"Expected at least 20 metrics, got {TOTAL_METRICS}"
        print(f"\n  SOP metrics: {len(CONFIGURED_METRICS)} configured, {TOTAL_METRICS} total across {len(CATEGORIES)} categories")

    def test_all_categories_represented(self):
        """Registry should have metrics across multiple categories."""
        expected_categories = {"discovery", "booking", "administrative", "closing", "opening", "objection_handling"}
        missing = expected_categories - CATEGORIES
        assert not missing, f"Missing expected categories: {missing}"

    def test_total_weight_approx_one(self):
        """Configured metric weights should sum to approximately 1.0."""
        configured_weight = sum(SOP_METRIC_REGISTRY[m]["weight"] for m in CONFIGURED_METRICS)
        assert 0.99 <= configured_weight <= 1.01, \
            f"Configured weight {configured_weight:.4f} outside expected range [0.99, 1.01]"

    def test_all_metrics_have_required_fields(self):
        """Every metric in the registry must have name, section, weight, category."""
        for mid, info in SOP_METRIC_REGISTRY.items():
            assert "name" in info, f"Metric '{mid}' missing 'name'"
            assert "section" in info, f"Metric '{mid}' missing 'section'"
            assert "weight" in info, f"Metric '{mid}' missing 'weight'"
            assert "category" in info, f"Metric '{mid}' missing 'category'"
            assert isinstance(info["weight"], (int, float)), \
                f"Metric '{mid}' weight must be numeric, got {type(info['weight'])}"
            assert info["category"] in CATEGORIES, \
                f"Metric '{mid}' has invalid category '{info['category']}'"

    def test_registry_size_is_valid(self):
        """Registry should have a reasonable number of metrics."""
        assert 20 <= TOTAL_METRICS <= 50, \
            f"Unusual registry size: {TOTAL_METRICS} metrics (expected 20-30)"

