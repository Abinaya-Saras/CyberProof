# CyberProof — Cyber Insurance Evidence Verifier

**CyberForge 2026 | AI & Cybersecurity Track**

## Overview
CyberProof is a prototype that checks whether evidence supports cybersecurity claims made during cyber-insurance underwriting. It evaluates evidence completeness, signing dates, coverage, and control strength.

## How It Works
The deterministic Python engine assigns one of three verdicts:

- ✅ **CONFIRMED** — Evidence satisfies the implemented rules.
- ⚠️ **CAN'T VERIFY** — Evidence is missing, incomplete, outdated, or insufficient.
- ❌ **CONTRADICTED** — Evidence explicitly conflicts with the claim.

## Key Features
- Scope and coverage verification
- Evidence-strength assessment
- Policy signing-date validation
- Reason-based verification results
- Interactive Streamlit dashboard
- Six fictional demonstration scenarios

## Tech Stack
Python · Streamlit · Pydantic · JSON · pytest

## Run Locally
```bash
git clone https://github.com/Abinaya-Saras/CyberProof.git
cd CyberProof
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Limitations
The current prototype uses deterministic rules and predefined synthetic scenarios. AI-based document extraction and production integrations are future work. It is not validated for real-world underwriting decisions.

## References
1. [Mapping the coverage of security controls in cyber insurance proposal forms (2017)](https://doi.org/10.1186/s13174-017-0059-y)
2. [Cyber insurance: State of the art, trends and future directions (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9841933/)
3. [Evidence of Assurance — Carnegie Mellon SEI (2013)](https://www.sei.cmu.edu/library/evidence-of-assurance-laying-the-foundation-for-a-credible-security-case/)

## Disclaimer
All companies, claims, and evidence are fictional. CyberProof is a hackathon prototype for demonstration and educational purposes only.