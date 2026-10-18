"""
models.py
---------
Pydantic data models for CyberProof.

These models define exactly what a Claim, an Evidence item, and a Verdict
look like.  Pydantic validates that every field has the right type when an
object is created, so bugs caused by missing or wrongly-typed data are caught
early — before the verdict engine ever runs.

Data flow:
  scenarios.json  →  Claim + list[Evidence]  →  engine.verify()  →  Verdict
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Claim
# ---------------------------------------------------------------------------

class Claim(BaseModel):
    """
    A single security-control claim made by a company on its insurance
    application.

    Attributes
    ----------
    company_name      : The fictional company making the claim.
    control_type      : The broad control category (e.g. "MFA", "Backup").
    control_subtype   : The *specific* level of control claimed.
                        Examples: "enforced", "registered", "enabled",
                        "tested", "encrypted".
    scope             : A human-readable description of what the claim covers.
                        Example: "all privileged accounts"
    scope_size        : The number of distinct entities (users, servers, …)
                        that must be covered.  Evidence must cover ALL of them.
    policy_signing_date : The date the insurance policy was signed.
                        Evidence dated after this date is not admissible.
    """

    company_name: str
    control_type: str
    control_subtype: str
    scope: str
    scope_size: int = Field(ge=0)        # must be 0 or greater
    policy_signing_date: date


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

class Evidence(BaseModel):
    """
    A single piece of evidence submitted to support a claim.

    Attributes
    ----------
    description     : Human-readable label shown in the UI.
    evidence_type   : Machine-readable category of the document.
                      Examples: "mfa_registration_report",
                      "mfa_enforcement_log", "backup_test_report",
                      "endpoint_protection_disabled_log"
    entities_covered : How many entities (users, servers, …) this evidence
                       covers.  Compared against Claim.scope_size.
    evidence_date   : The date the evidence was produced or last updated.
                      Must be on or before Claim.policy_signing_date.
    proves_subtype  : What control level this evidence actually proves.
                      Examples: "registered", "enforced", "tested",
                      "contradicts"  ← special value meaning active failure.
    """

    description: str
    evidence_type: str
    entities_covered: int = Field(ge=0)
    evidence_date: date
    proves_subtype: str


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

class Verdict(BaseModel):
    """
    The output produced by engine.verify() for one Claim + Evidence pair.

    Attributes
    ----------
    result       : One of three possible outcomes.
    reason_code  : Machine-readable constant from reason_codes.py.
    reason_text  : Plain-English explanation shown in the UI.
    checks       : Step-by-step breakdown of each check performed.
                   Each entry is a dict with keys:
                     "name"   – check label
                     "passed" – True / False / None (not reached)
                     "detail" – one-line explanation
    """

    result: Literal["CONFIRMED", "CONTRADICTED", "CAN'T VERIFY"]
    reason_code: str
    reason_text: str
    checks: list[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Scenario  (top-level container used by scenarios.json loader)
# ---------------------------------------------------------------------------

class Scenario(BaseModel):
    """
    A complete test scenario: one claim paired with its evidence list.
    This is the unit loaded from scenarios.json and shown in the UI dropdown.

    Attributes
    ----------
    id          : Short identifier used internally (e.g. "acme_mfa").
    title       : Display name shown in the Streamlit dropdown.
    description : One-sentence summary of what makes this scenario interesting.
    claim       : The Claim being verified.
    evidence    : List of Evidence items submitted for that claim.
                  May be empty (tests the NO_EVIDENCE path).
    """

    id: str
    title: str
    description: str
    claim: Claim
    evidence: list[Evidence] = Field(default_factory=list)
