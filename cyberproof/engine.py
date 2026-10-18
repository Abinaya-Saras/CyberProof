"""
engine.py
---------
The deterministic verdict engine for CyberProof.

This module contains a single public function, verify(), which takes a Claim
and a list of Evidence items and returns a Verdict.

Design rules
------------
1. No AI, no network calls, no randomness — output depends only on inputs.
2. Checks run in a fixed order.  The first failure stops evaluation and
   returns the appropriate CAN'T VERIFY or CONTRADICTED verdict.
3. Any unexpected exception is caught and returned as CAN'T VERIFY with a
   safe error message.  An exception must NEVER produce a CONFIRMED verdict.
4. An empty evidence list is treated the same as no evidence (NO_EVIDENCE).

Check order
-----------
  1. Existence check   — is there any evidence at all?
  2. Date check        — is every evidence item dated on/before signing date?
  3. Strength check    — does evidence prove the specific subtype claimed?
  4. Coverage check    — does evidence cover the full claim scope?
  → All passed         → CONFIRMED

Rationale for strength-before-coverage:
  Evidence that proves the wrong control type (e.g. 'registered' when
  'enforced' is required) is fundamentally insufficient regardless of how
  many entities it covers.  Reporting the strength failure first gives the
  most actionable signal — especially for the primary Acme Textiles demo,
  where registration evidence can never substitute for enforcement evidence.
"""

from cyberproof.models import Claim, Evidence, Verdict
from cyberproof import reason_codes as rc


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_result(name: str, passed: bool, detail: str) -> dict:
    """Return a single check-step dict for inclusion in Verdict.checks."""
    return {"name": name, "passed": passed, "detail": detail}


def _cant_verify(reason_code: str, checks: list[dict]) -> Verdict:
    """Convenience constructor for a CAN'T VERIFY verdict."""
    return Verdict(
        result="CAN'T VERIFY",
        reason_code=reason_code,
        reason_text=rc.REASON_MESSAGES[reason_code],
        checks=checks,
    )


def _contradicted(reason_code: str, checks: list[dict]) -> Verdict:
    """Convenience constructor for a CONTRADICTED verdict."""
    return Verdict(
        result="CONTRADICTED",
        reason_code=reason_code,
        reason_text=rc.REASON_MESSAGES[reason_code],
        checks=checks,
    )


def _confirmed(checks: list[dict]) -> Verdict:
    """Convenience constructor for a CONFIRMED verdict."""
    return Verdict(
        result="CONFIRMED",
        reason_code=rc.ALL_CHECKS_PASSED,
        reason_text=rc.REASON_MESSAGES[rc.ALL_CHECKS_PASSED],
        checks=checks,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def verify(claim: Claim, evidence_list: list[Evidence]) -> Verdict:
    """
    Verify whether the supplied evidence supports the claim.

    Parameters
    ----------
    claim         : The security-control claim to verify.
    evidence_list : Zero or more Evidence items submitted for that claim.

    Returns
    -------
    Verdict with result, reason_code, reason_text, and per-check breakdown.
    """
    checks: list[dict] = []

    try:
        # ------------------------------------------------------------------ #
        # Check 1 — Existence                                                 #
        # ------------------------------------------------------------------ #
        if not evidence_list:
            checks.append(_check_result(
                name="Evidence exists",
                passed=False,
                detail="No evidence was submitted.",
            ))
            return _cant_verify(rc.NO_EVIDENCE, checks)

        checks.append(_check_result(
            name="Evidence exists",
            passed=True,
            detail=f"{len(evidence_list)} evidence item(s) submitted.",
        ))

        # ------------------------------------------------------------------ #
        # Check 2 — Signing date                                              #
        # Each evidence item must be dated on or before policy_signing_date.  #
        # ------------------------------------------------------------------ #
        outdated = [
            e for e in evidence_list
            if e.evidence_date > claim.policy_signing_date
        ]

        if outdated:
            offender = outdated[0]
            checks.append(_check_result(
                name="Evidence date",
                passed=False,
                detail=(
                    f"'{offender.description}' is dated {offender.evidence_date} "
                    f"— after the policy signing date of {claim.policy_signing_date}."
                ),
            ))
            return _cant_verify(rc.EVIDENCE_OUTDATED, checks)

        checks.append(_check_result(
            name="Evidence date",
            passed=True,
            detail=(
                f"All evidence is dated on or before the policy signing date "
                f"({claim.policy_signing_date})."
            ),
        ))

        # ------------------------------------------------------------------ #
        # Check 3 — Strength                                                  #
        # At least one evidence item must prove the subtype that is claimed.  #
        # "contradicts" is a special subtype meaning active failure.          #
        # Runs before coverage: evidence proving the wrong control type is     #
        # fundamentally insufficient, regardless of how many entities it       #
        # covers.                                                              #
        # ------------------------------------------------------------------ #

        # First look for an active contradiction across all evidence items.
        contradicting = [
            e for e in evidence_list if e.proves_subtype == "contradicts"
        ]
        if contradicting:
            offender = contradicting[0]
            checks.append(_check_result(
                name="Evidence strength",
                passed=False,
                detail=(
                    f"'{offender.description}' actively contradicts the claim: "
                    f"it shows the control is absent or disabled."
                ),
            ))
            return _contradicted(rc.ACTIVE_CONTRADICTION, checks)

        # Now check whether any evidence proves the claimed subtype.
        strong_evidence = [
            e for e in evidence_list
            if e.proves_subtype == claim.control_subtype
        ]

        if not strong_evidence:
            # Report what the best evidence actually proves for clarity.
            best_proves = evidence_list[0].proves_subtype
            checks.append(_check_result(
                name="Evidence strength",
                passed=False,
                detail=(
                    f"Evidence proves '{best_proves}' but the claim requires "
                    f"'{claim.control_subtype}'. "
                    f"A stronger level of proof is needed."
                ),
            ))
            # Secondary note: also report coverage gap if one exists.
            # This is informational only — it does not change the verdict.
            # The strength failure is always the primary reason.
            best_coverage = max(e.entities_covered for e in evidence_list)
            if claim.scope_size > 0 and best_coverage < claim.scope_size:
                checks.append(_check_result(
                    name="Coverage (secondary gap)",
                    passed=False,
                    detail=(
                        f"Additionally, evidence only covers {best_coverage} of "
                        f"{claim.scope_size} required entities ({claim.scope}). "
                        f"Even if stronger evidence were provided, full scope "
                        f"coverage would also be needed."
                    ),
                ))
            return _cant_verify(rc.STRENGTH_INSUFFICIENT, checks)

        checks.append(_check_result(
            name="Evidence strength",
            passed=True,
            detail=(
                f"Evidence proves '{claim.control_subtype}' as claimed."
            ),
        ))

        # ------------------------------------------------------------------ #
        # Check 4 — Coverage                                                  #
        # Use the evidence item with the highest entity count.                #
        # scope_size == 0 means the claim has no explicit scope limit;        #
        # any coverage (even zero entities) is treated as full coverage.      #
        # Only reached when the evidence type is already confirmed correct.   #
        # ------------------------------------------------------------------ #
        best_coverage = max(e.entities_covered for e in evidence_list)

        if claim.scope_size > 0 and best_coverage < claim.scope_size:
            checks.append(_check_result(
                name="Coverage",
                passed=False,
                detail=(
                    f"Best evidence covers {best_coverage} of "
                    f"{claim.scope_size} required entities "
                    f"({claim.scope})."
                ),
            ))
            return _cant_verify(rc.COVERAGE_INCOMPLETE, checks)

        checks.append(_check_result(
            name="Coverage",
            passed=True,
            detail=(
                f"Evidence covers {best_coverage} entities — "
                f"meets the required {claim.scope_size} ({claim.scope})."
            ),
        ))

        # ------------------------------------------------------------------ #
        # All checks passed → CONFIRMED                                       #
        # ------------------------------------------------------------------ #
        return _confirmed(checks)

    except Exception as exc:  # noqa: BLE001
        # Safety net: any unexpected error must never produce CONFIRMED.
        checks.append(_check_result(
            name="Internal error",
            passed=False,
            detail=f"An unexpected error occurred: {exc}",
        ))
        return _cant_verify(rc.NO_EVIDENCE, checks)
