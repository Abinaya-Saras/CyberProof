# CyberProof — Scope-Aware Attestation Verifier for Cyber Insurance

> **CyberForge 2026 Hackathon — AI & Cybersecurity track**
> All data is entirely fictional. No real companies or security controls are represented.

---

## What it does

CyberProof checks whether submitted evidence genuinely supports a cyber-insurance security claim.  
It runs three deterministic checks on every claim:

| Check | Question |
|---|---|
| **Evidence exists** | Was any evidence submitted at all? |
| **Signing date** | Is all evidence dated on or before the policy signing date? |
| **Coverage** | Does evidence cover all entities in the claim scope? |
| **Strength** | Does evidence prove the *specific control level* claimed? |

Each claim receives one of three verdicts:

- ✅ **CONFIRMED** — all checks pass.
- ⚠️ **CAN'T VERIFY** — evidence is missing, outdated, incomplete, or too weak.
- ❌ **CONTRADICTED** — evidence actively disproves the claim.

**Key property:** deterministic Python decides the verdict. AI is not involved.  
No unexpected error can produce a false CONFIRMED result.

---

## Setup

```bash
# Clone or navigate to the project
cd cyb3rknight5

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Run the tests

```bash
pytest tests/ -v
```

All 8 tests must pass before running the demo.

---

## Run the app

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.  
Use the sidebar dropdown to switch between the six pre-built scenarios.

---

## Project structure

```
cyb3rknight5/
├── data/
│   └── scenarios.json          # Synthetic claim + evidence scenarios
├── cyberproof/
│   ├── __init__.py
│   ├── models.py               # Pydantic data models
│   ├── engine.py               # Deterministic verdict engine
│   └── reason_codes.py         # Reason code constants and messages
├── tests/
│   └── test_engine.py          # Pytest unit tests
├── app.py                      # Streamlit UI
├── requirements.txt
└── README.md
```

---

## Scenarios included

| # | Company | Verdict | Reason |
|---|---|---|---|
| 1 | Acme Textiles | CAN'T VERIFY | MFA registration ≠ enforcement |
| 2 | Bravo Corp | CAN'T VERIFY | No evidence submitted |
| 3 | Charlie Inc | CAN'T VERIFY | Backup coverage: 8 of 12 servers |
| 4 | Delta Ltd | CONFIRMED | Full MFA enforcement with valid date |
| 5 | Echo Co | CONTRADICTED | AV explicitly disabled |
| 6 | Foxtrot LLC | CAN'T VERIFY | Evidence dated after policy signing |

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| streamlit | ≥1.35.0 | Web UI |
| pydantic | ≥2.7.0 | Data validation |
| pytest | ≥8.0.0 | Testing |

No OpenAI or LLM API key required.

---

## Disclaimer

This tool is a hackathon prototype built for demonstration purposes only.  
It makes no claim of real-world accuracy, legal validity, or production readiness.  
All companies, scenarios, and data are entirely fictional.
