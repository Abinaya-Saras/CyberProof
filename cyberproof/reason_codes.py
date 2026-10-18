"""
reason_codes.py
---------------
All verdict reason codes used by the CyberProof engine.

A reason code is a short machine-readable string that identifies exactly why
a particular verdict was reached.  The REASON_MESSAGES dict maps each code to
a plain-English explanation that is shown in the Streamlit UI.

Adding a new reason code:
  1. Add a constant below.
  2. Add a matching entry in REASON_MESSAGES.
  3. Use the constant in engine.py — never hard-code the string elsewhere.
"""

# ---------------------------------------------------------------------------
# Reason code constants
# ---------------------------------------------------------------------------

# Verdict: CAN'T VERIFY
NO_EVIDENCE = "NO_EVIDENCE"
EVIDENCE_OUTDATED = "EVIDENCE_OUTDATED"
COVERAGE_INCOMPLETE = "COVERAGE_INCOMPLETE"
STRENGTH_INSUFFICIENT = "STRENGTH_INSUFFICIENT"

# Verdict: CONTRADICTED
ACTIVE_CONTRADICTION = "ACTIVE_CONTRADICTION"

# Verdict: CONFIRMED
ALL_CHECKS_PASSED = "ALL_CHECKS_PASSED"

# ---------------------------------------------------------------------------
# Human-readable messages shown in the UI
# ---------------------------------------------------------------------------

REASON_MESSAGES: dict[str, str] = {
    NO_EVIDENCE: (
        "No evidence was submitted for this claim. "
        "At least one piece of dated evidence is required to verify the control."
    ),
    EVIDENCE_OUTDATED: (
        "One or more evidence items are dated after the policy signing date. "
        "Evidence must have been available on or before the policy was signed."
    ),
    COVERAGE_INCOMPLETE: (
        "The submitted evidence does not cover all entities included in the claim. "
        "Every person, system, or account referenced in the claim scope must be "
        "represented in the evidence."
    ),
    STRENGTH_INSUFFICIENT: (
        "The evidence proves a weaker control than what is claimed. "
        "For example, showing that users registered for MFA does not prove that "
        "MFA is actively enforced — users could still log in without it."
    ),
    ACTIVE_CONTRADICTION: (
        "The evidence actively contradicts the claim. "
        "A reliable source shows that the claimed control is absent, disabled, "
        "or failed during the policy period."
    ),
    ALL_CHECKS_PASSED: (
        "All three checks passed: the evidence covers the full claim scope, "
        "proves the specific control claimed, and was available before the "
        "policy signing date."
    ),
}

# ---------------------------------------------------------------------------
# Helper: verdict associated with each reason code
# ---------------------------------------------------------------------------

REASON_TO_VERDICT: dict[str, str] = {
    NO_EVIDENCE:            "CAN'T VERIFY",
    EVIDENCE_OUTDATED:      "CAN'T VERIFY",
    COVERAGE_INCOMPLETE:    "CAN'T VERIFY",
    STRENGTH_INSUFFICIENT:  "CAN'T VERIFY",
    ACTIVE_CONTRADICTION:   "CONTRADICTED",
    ALL_CHECKS_PASSED:      "CONFIRMED",
}
