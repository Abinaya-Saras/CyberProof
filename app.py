"""
app.py
------
CyberProof — Streamlit UI

Loads synthetic scenarios from data/scenarios.json, lets the user pick one,
and displays the claim, evidence, and verdict side-by-side.

Run with:
    streamlit run app.py
"""

import json
from pathlib import Path

import streamlit as st

from cyberproof.models import Scenario
from cyberproof.engine import verify

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="CyberProof — Attestation Verifier",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — presentation only
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
/* ------------------------------------------------------------------------
   CyberProof visual system
   Warm, restrained, student-engineering project aesthetic.
   ------------------------------------------------------------------------ */

:root {
    --page: #F5F3EE;
    --surface: #FFFFFF;
    --text: #292B27;
    --muted: #686B63;
    --success: #34483B;
    --failure: #B85C45;
    --border: #E4E0D7;
    --soft: #EFECE5;
    --success-soft: #EEF2EF;
    --failure-soft: #F8EFEC;
}

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: var(--page);
    color: var(--text);
}

html,
body,
button,
input,
textarea,
select,
[class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Keep the content compact and deliberately aligned. */
.block-container {
    max-width: 1180px;
    padding-top: 2.6rem;
    padding-bottom: 2.5rem;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: #F8F6F1 !important;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div {
    background: #F8F6F1 !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
    color: var(--text);
}

.sidebar-brand {
    margin: 0.35rem 0 0.15rem 0;
    font-size: 1.15rem;
    line-height: 1.2;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.015em;
}

.sidebar-subtitle {
    color: var(--muted);
    font-size: 0.8rem;
    line-height: 1.55;
    margin-bottom: 0.35rem;
}

.sidebar-meta {
    color: var(--muted);
    font-size: 0.79rem;
    line-height: 1.7;
}

.sidebar-meta b {
    color: var(--text);
    font-weight: 600;
}

section[data-testid="stSidebar"] hr {
    border-color: var(--border);
    margin: 1rem 0;
}

section[data-testid="stSidebar"] .stSelectbox label {
    color: var(--muted) !important;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.075em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* Streamlit/BaseWeb select — force a readable light field. */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    box-shadow: none !important;
    min-height: 42px;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
    border-color: #C8C3B8 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: var(--text) !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] svg {
    color: var(--muted) !important;
    fill: var(--muted) !important;
}

/* Dropdown menu is rendered outside the sidebar DOM. */
[data-baseweb="popover"] [role="listbox"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    box-shadow: 0 8px 24px rgba(41, 43, 39, 0.08) !important;
}

[data-baseweb="popover"] [role="option"] {
    color: var(--text) !important;
    background: var(--surface) !important;
}

[data-baseweb="popover"] [role="option"]:hover {
    background: var(--page) !important;
}

/* ---------- Primary action ---------- */
.stButton > button[kind="primary"] {
    min-height: 42px;
    background: var(--success) !important;
    border: 1px solid var(--success) !important;
    border-radius: 7px !important;
    color: #FFFFFF !important;
    box-shadow: none !important;
    font-weight: 600 !important;
    transition: background 120ms ease, border-color 120ms ease;
}

.stButton > button[kind="primary"] * {
    color: #FFFFFF !important;
}

.stButton > button[kind="primary"]:hover {
    background: #2C3D32 !important;
    border-color: #2C3D32 !important;
}

.stButton > button[kind="primary"]:focus {
    box-shadow: 0 0 0 2px rgba(52, 72, 59, 0.16) !important;
}

/* ---------- Page heading ---------- */
.project-kicker {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.085em;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}

.project-title {
    color: var(--text);
    font-size: clamp(1.65rem, 2.4vw, 2.05rem);
    line-height: 1.15;
    font-weight: 700;
    letter-spacing: -0.025em;
    margin: 0;
}

.project-description {
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.6;
    max-width: 900px;
    margin: 0.65rem 0 1.65rem 0;
}

/* ---------- Section labels ---------- */
.section-header {
    color: var(--muted);
    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.085em;
    text-transform: uppercase;
    margin: 0 0 0.55rem 0;
}

/* ---------- Claim / evidence cards ---------- */
.info-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.62rem;
    box-shadow: none;
}

.info-card .label {
    color: var(--muted);
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 0.22rem;
}

.info-card .value {
    color: var(--text);
    font-size: 0.96rem;
    line-height: 1.4;
    font-weight: 600;
    overflow-wrap: anywhere;
}

/* ---------- Evidence expander ---------- */
div[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden;
    box-shadow: none !important;
}

div[data-testid="stExpander"] details,
div[data-testid="stExpander"] summary {
    background: var(--surface) !important;
}

div[data-testid="stExpander"] summary {
    min-height: 46px;
    color: var(--text) !important;
    border-bottom: 1px solid transparent;
}

div[data-testid="stExpander"] details[open] summary {
    border-bottom-color: var(--border);
}

div[data-testid="stExpander"] summary:hover {
    background: #FAF9F6 !important;
}

div[data-testid="stExpander"] summary * {
    color: var(--text) !important;
}

div[data-testid="stExpander"] svg {
    color: var(--muted) !important;
    fill: var(--muted) !important;
}

/* Reduce duplicated card chrome inside evidence expanders. */
div[data-testid="stExpander"] .info-card {
    background: #FCFBF8;
}

/* ---------- Divider ---------- */
[data-testid="stAppViewContainer"] hr {
    border-color: var(--border);
}

/* ---------- Streamlit informational notice ---------- */
div[data-testid="stAlert"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

div[data-testid="stAlert"] * {
    color: var(--text) !important;
}

/* ---------- Verdict ---------- */
.verdict-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 9px;
    overflow: hidden;
}

.verdict-accent {
    height: 4px;
    width: 100%;
}

.verdict-confirmed .verdict-accent {
    background: var(--success);
}

.verdict-cant-verify .verdict-accent,
.verdict-contradicted .verdict-accent {
    background: var(--failure);
}

.verdict-content {
    padding: 1.15rem 1.25rem 1.2rem 1.25rem;
}

.verdict-eyebrow {
    color: var(--muted);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.085em;
    text-transform: uppercase;
    margin-bottom: 0.28rem;
}

.verdict-label {
    color: var(--text);
    font-size: 1.45rem;
    line-height: 1.2;
    font-weight: 700;
    letter-spacing: -0.018em;
    margin-bottom: 0.9rem;
}

.reason-block {
    background: #FAF9F6;
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 0.85rem 0.95rem;
}

.reason-label {
    color: var(--muted);
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.075em;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}

.reason-code {
    color: var(--text);
    font-size: 0.95rem;
    line-height: 1.35;
    font-weight: 700;
}

.reason-detail {
    color: var(--muted);
    font-size: 0.84rem;
    line-height: 1.5;
    margin-top: 0.35rem;
}

.secondary-issue {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-top: 0.7rem;
    padding-top: 0.7rem;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.45;
}

.secondary-issue strong {
    color: var(--failure);
    font-weight: 700;
}

/* ---------- Check breakdown ---------- */
.check-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}

.check-row {
    display: grid;
    grid-template-columns: 22px minmax(0, 1fr);
    gap: 0.65rem;
    align-items: start;
    padding: 0.78rem 0.95rem;
    border-bottom: 1px solid var(--border);
}

.check-row:last-child {
    border-bottom: 0;
}

.check-mark {
    width: 20px;
    height: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-size: 0.72rem;
    font-weight: 800;
    line-height: 1;
}

.check-mark.pass {
    background: var(--success-soft);
    color: var(--success);
}

.check-mark.fail {
    background: var(--failure-soft);
    color: var(--failure);
}

.check-mark.skip {
    background: var(--soft);
    color: var(--muted);
}

.check-name {
    color: var(--text);
    font-size: 0.87rem;
    font-weight: 650;
    line-height: 1.35;
}

.check-detail {
    color: var(--muted);
    font-size: 0.8rem;
    line-height: 1.45;
    margin-top: 0.13rem;
}

/* ---------- Small notes ---------- */
.disclaimer {
    color: var(--muted);
    font-size: 0.75rem;
    line-height: 1.45;
    margin-top: 1rem;
    padding-top: 0.85rem;
    border-top: 1px solid var(--border);
}

.footer-note {
    color: var(--muted);
    font-size: 0.76rem;
    line-height: 1.55;
    margin-top: 2rem;
    padding-top: 0.9rem;
    border-top: 1px solid var(--border);
}

.footer-note strong {
    color: var(--text);
    font-weight: 600;
}

/* ---------- Responsive ---------- */
@media (max-width: 900px) {
    .block-container {
        padding-top: 1.6rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load scenarios
# ---------------------------------------------------------------------------

@st.cache_data
def load_scenarios() -> list[Scenario]:
    """Load and validate all scenarios from data/scenarios.json."""
    data_path = Path(__file__).parent / "data" / "scenarios.json"
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    return [Scenario.model_validate(item) for item in raw]


scenarios = load_scenarios()
scenario_map = {s.title: s for s in scenarios}

# ---------------------------------------------------------------------------
# Session state — track which scenario was last verified
# ---------------------------------------------------------------------------

# "last_verified" stores the scenario id that was most recently run.
# It starts as None so the verdict panel is hidden on first load.
# When the user clicks "Run Verification" the id is stored and the panel
# renders. Changing the dropdown means a different scenario id is active,
# so the new scenario still requires its own verification click.
if "last_verified" not in st.session_state:
    st.session_state["last_verified"] = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'>CyberProof</div>"
        "<div class='sidebar-subtitle'>"
        "Scope-aware attestation verification<br>for cyber insurance evidence"
        "</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    selected_title = st.selectbox(
        "Select a scenario",
        options=list(scenario_map.keys()),
        help="Each scenario represents one company's claim and submitted evidence.",
    )
    scenario: Scenario = scenario_map[selected_title]

    st.divider()

    st.markdown(
        f"<div class='sidebar-meta'>"
        f"<b>Company</b><br>{scenario.claim.company_name}<br><br>"
        f"<b>Policy signed</b><br>{scenario.claim.policy_signing_date}<br><br>"
        f"<b>Evidence items</b><br>{len(scenario.evidence)}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    run = st.button("Run Verification", use_container_width=True, type="primary")
    if run:
        # Store the id of the scenario that was just verified so the
        # verdict section knows it should render.
        st.session_state["last_verified"] = scenario.id

    st.markdown(
        "<div class='disclaimer'>Demonstration using synthetic data.</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main area — header
# ---------------------------------------------------------------------------

st.markdown(
    f"<div class='project-kicker'>Cyber insurance evidence review</div>"
    f"<h1 class='project-title'>CyberProof — Attestation Verifier</h1>"
    f"<p class='project-description'>{scenario.description}</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Claim + Evidence columns
# ---------------------------------------------------------------------------

col_claim, col_evidence = st.columns(2, gap="large")

with col_claim:
    st.markdown("<div class='section-header'>Claim</div>", unsafe_allow_html=True)
    c = scenario.claim

    def info_card(label: str, value: str) -> None:
        st.markdown(
            f"<div class='info-card'>"
            f"<div class='label'>{label}</div>"
            f"<div class='value'>{value}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    info_card("Company", c.company_name)
    info_card("Control type", c.control_type)
    info_card("Claimed level", c.control_subtype.upper())
    info_card("Scope", c.scope)
    info_card("Scope size", f"{c.scope_size} entities required")
    info_card("Policy signing date", str(c.policy_signing_date))

with col_evidence:
    st.markdown(
        "<div class='section-header'>Evidence submitted</div>",
        unsafe_allow_html=True,
    )

    if not scenario.evidence:
        st.warning("No evidence was submitted for this claim.")
    else:
        for i, ev in enumerate(scenario.evidence, start=1):
            with st.expander(f"Evidence {i}: {ev.description}", expanded=True):
                info_card("Evidence type", ev.evidence_type)
                info_card("Entities covered", str(ev.entities_covered))
                info_card("Evidence date", str(ev.evidence_date))
                info_card("What it proves", ev.proves_subtype.upper())

# ---------------------------------------------------------------------------
# Verdict section
# ---------------------------------------------------------------------------

st.divider()
st.markdown(
    "<div class='section-header'>Verification result</div>",
    unsafe_allow_html=True,
)

# Only render the verdict after the button has been clicked for THIS scenario.
if st.session_state["last_verified"] != scenario.id:
    st.info(
        "Select a scenario in the sidebar and click **Run Verification** "
        "to review the submitted evidence."
    )
else:
    verdict = verify(scenario.claim, scenario.evidence)

    VERDICT_CSS = {
        "CONFIRMED": "verdict-confirmed",
        "CONTRADICTED": "verdict-contradicted",
        "CAN'T VERIFY": "verdict-cant-verify",
    }
    css_class = VERDICT_CSS.get(verdict.result, "verdict-cant-verify")

    # Presentation-only breakdown for the common insufficient-strength result.
    # The engine verdict itself is unchanged.
    if verdict.reason_code == "STRENGTH_INSUFFICIENT":
        strongest_coverage = max(
            (ev.entities_covered for ev in scenario.evidence),
            default=0,
        )
        coverage_gap = max(c.scope_size - strongest_coverage, 0)

        reason_html = (
            "<div class='reason-block'>"
            "<div class='reason-label'>Primary reason</div>"
            f"<div class='reason-code'>{verdict.reason_code}</div>"
            "<div class='reason-detail'>"
            "The submitted evidence does not demonstrate the same control "
            "strength as the claim being verified."
            "</div>"
            "<div class='secondary-issue'>"
            "<span>Secondary issue</span>"
            f"<strong>{strongest_coverage} of {c.scope_size} covered</strong>"
            f"<span>— {coverage_gap} entities are outside the submitted coverage.</span>"
            "</div>"
            "</div>"
        )
    else:
        reason_html = (
            "<div class='reason-block'>"
            "<div class='reason-label'>Reason</div>"
            f"<div class='reason-code'>{verdict.reason_code}</div>"
            f"<div class='reason-detail'>{verdict.reason_text}</div>"
            "</div>"
        )

    st.markdown(
        f"<div class='verdict-panel {css_class}'>"
        "<div class='verdict-accent'></div>"
        "<div class='verdict-content'>"
        "<div class='verdict-eyebrow'>Decision</div>"
        f"<div class='verdict-label'>{verdict.result}</div>"
        f"{reason_html}"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Check-step breakdown
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header'>Check breakdown</div>",
        unsafe_allow_html=True,
    )

    rows_html = ""
    for check in verdict.checks:
        if check["passed"] is True:
            mark, mark_class = "✓", "pass"
        elif check["passed"] is False:
            mark, mark_class = "×", "fail"
        else:
            mark, mark_class = "–", "skip"

        rows_html += (
            "<div class='check-row'>"
            f"<div class='check-mark {mark_class}'>{mark}</div>"
            "<div>"
            f"<div class='check-name'>{check['name']}</div>"
            f"<div class='check-detail'>{check['detail']}</div>"
            "</div>"
            "</div>"
        )

    st.markdown(
        f"<div class='check-panel'>{rows_html}</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    "<div class='footer-note'>"
    "<strong>CyberProof</strong> · Cyber insurance evidence review<br>"
    #"Demonstration using synthetic data."
    "</div>",
    unsafe_allow_html=True,
)
