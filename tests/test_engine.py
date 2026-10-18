"""
test_engine.py
--------------
Unit tests for the CyberProof verdict engine (cyberproof/engine.py).

Each test is self-contained: it builds a minimal Claim and Evidence list
inline and asserts the expected verdict result and reason code.

Run with:
    pytest tests/ -v

All 8 tests must pass (0 failures) before the Streamlit UI is considered
ready to demo.
"""

import pytest
from datetime import date

from cyberproof.models import Claim, Evidence
from cyberproof.engine import verify
from cyberproof import reason_codes as rc


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

SIGNING_DATE = date(2026, 9, 1)

def _mfa_claim(subtype: str = "enforced", scope_size: int = 20) -> Claim:
    """Return a generic MFA claim."""
    return Claim(
        company_name="Test Corp",
        control_type="MFA",
        control_subtype=subtype,
        scope="all privileged accounts",
        scope_size=scope_size,
        policy_signing_date=SIGNING_DATE,
    )

def _mfa_evidence(
    proves_subtype: str = "enforced",
    entities_covered: int = 20,
    days_before_signing: int = 10,
) -> Evidence:
    """Return a generic MFA evidence item."""
    evidence_date = date(
        SIGNING_DATE.year,
        SIGNING_DATE.month,
        SIGNING_DATE.day,
    )
    # Subtract days manually to stay stdlib-only
    from datetime import timedelta
    evidence_date = SIGNING_DATE - timedelta(days=days_before_signing)
    return Evidence(
        description="Test Evidence",
        evidence_type="mfa_test",
        entities_covered=entities_covered,
        evidence_date=evidence_date,
        proves_subtype=proves_subtype,
    )


# ---------------------------------------------------------------------------
# Test 1 — No evidence submitted (empty list passed explicitly)
# ---------------------------------------------------------------------------

def test_no_evidence():
    """Empty evidence list → CAN'T VERIFY / NO_EVIDENCE."""
    verdict = verify(_mfa_claim(), evidence_list=[])
    assert verdict.result == "CAN'T VERIFY"
    assert verdict.reason_code == rc.NO_EVIDENCE


# ---------------------------------------------------------------------------
# Test 2 — Evidence dated after policy signing date
# ---------------------------------------------------------------------------

def test_outdated_evidence():
    """Evidence date > signing date → CAN'T VERIFY / EVIDENCE_OUTDATED."""
    from datetime import timedelta
    late_evidence = Evidence(
        description="Late Report",
        evidence_type="mfa_enforcement_log",
        entities_covered=20,
        evidence_date=SIGNING_DATE + timedelta(days=14),  # 2 weeks AFTER signing
        proves_subtype="enforced",
    )
    verdict = verify(_mfa_claim(), evidence_list=[late_evidence])
    assert verdict.result == "CAN'T VERIFY"
    assert verdict.reason_code == rc.EVIDENCE_OUTDATED


# ---------------------------------------------------------------------------
# Test 3 — Evidence covers fewer entities than scope requires
# ---------------------------------------------------------------------------

def test_incomplete_coverage():
    """entities_covered < scope_size → CAN'T VERIFY / COVERAGE_INCOMPLETE."""
    evidence = _mfa_evidence(entities_covered=17)   # claim requires 20
    verdict = verify(_mfa_claim(scope_size=20), evidence_list=[evidence])
    assert verdict.result == "CAN'T VERIFY"
    assert verdict.reason_code == rc.COVERAGE_INCOMPLETE


# ---------------------------------------------------------------------------
# Test 4 — Evidence proves a weaker subtype than claimed (the Acme scenario)
# ---------------------------------------------------------------------------

def test_insufficient_strength():
    """
    Claim: MFA enforced.
    Evidence: MFA registered (proves_subtype='registered').
    Expected: CAN'T VERIFY / STRENGTH_INSUFFICIENT.
    This is the primary Acme Textiles demo scenario.
    """
    claim    = _mfa_claim(subtype="enforced", scope_size=20)
    evidence = _mfa_evidence(proves_subtype="registered", entities_covered=20)
    verdict  = verify(claim, evidence_list=[evidence])
    assert verdict.result == "CAN'T VERIFY"
    assert verdict.reason_code == rc.STRENGTH_INSUFFICIENT


# ---------------------------------------------------------------------------
# Test 5 — Evidence actively contradicts the claim
# ---------------------------------------------------------------------------

def test_active_contradiction():
    """proves_subtype='contradicts' → CONTRADICTED / ACTIVE_CONTRADICTION."""
    evidence = _mfa_evidence(proves_subtype="contradicts", entities_covered=20)
    verdict  = verify(_mfa_claim(), evidence_list=[evidence])
    assert verdict.result == "CONTRADICTED"
    assert verdict.reason_code == rc.ACTIVE_CONTRADICTION


# ---------------------------------------------------------------------------
# Test 6 — Full happy path: all checks pass
# ---------------------------------------------------------------------------

def test_confirmed():
    """All checks pass → CONFIRMED / ALL_CHECKS_PASSED."""
    claim    = _mfa_claim(subtype="enforced", scope_size=15)
    evidence = _mfa_evidence(proves_subtype="enforced", entities_covered=15)
    verdict  = verify(claim, evidence_list=[evidence])
    assert verdict.result == "CONFIRMED"
    assert verdict.reason_code == rc.ALL_CHECKS_PASSED


# ---------------------------------------------------------------------------
# Test 7 — Edge: scope_size == 0 means no specific count is required
# ---------------------------------------------------------------------------

def test_zero_scope_size():
    """scope_size=0 should not trigger COVERAGE_INCOMPLETE."""
    claim    = _mfa_claim(subtype="enforced", scope_size=0)
    evidence = _mfa_evidence(proves_subtype="enforced", entities_covered=0)
    verdict  = verify(claim, evidence_list=[evidence])
    # Coverage check is skipped for zero-scope claims; engine should confirm.
    assert verdict.result == "CONFIRMED"
    assert verdict.reason_code == rc.ALL_CHECKS_PASSED


# ---------------------------------------------------------------------------
# Test 8 — Verdict.checks breakdown is populated correctly
# ---------------------------------------------------------------------------

def test_checks_populated():
    """
    Every returned Verdict must contain a non-empty checks list.
    Spot-check the happy path: four checks, all passed=True.
    """
    claim    = _mfa_claim(subtype="enforced", scope_size=10)
    evidence = _mfa_evidence(proves_subtype="enforced", entities_covered=10)
    verdict  = verify(claim, evidence_list=[evidence])

    assert len(verdict.checks) == 4, (
        f"Expected 4 check steps, got {len(verdict.checks)}: {verdict.checks}"
    )
    for check in verdict.checks:
        assert check["passed"] is True, (
            f"Expected all checks to pass, but '{check['name']}' failed: "
            f"{check['detail']}"
        )
