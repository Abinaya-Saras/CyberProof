# CyberProof — Scope-Aware Attestation Verifier for Cyber Insurance

**CyberForge 2026 Hackathon | AI & Cybersecurity Track**

## What it does

Cyber-insurance underwriting often relies on organizations reporting their security controls. However, submitted evidence may not prove that a control is enforced, covers every relevant system, or was in place by the policy signing date.

**CyberProof checks whether submitted evidence supports the specific cybersecurity claim being made.**

It performs four deterministic checks:

| Check | Question |
|---|---|
| **Evidence existence** | Was any evidence submitted? |
| **Signing date** | Is the evidence dated on or before the policy signing date? |
| **Coverage** | Does the evidence cover all entities in the claim scope? |
| **Evidence strength** | Does the evidence prove the specific control level claimed? |

### Verification verdicts

- ✅ **CONFIRMED** — Evidence satisfies the implemented verification rules.
- ⚠️ **CAN'T VERIFY** — Evidence is missing, incomplete, outdated, or insufficient.
- ❌ **CONTRADICTED** — Evidence explicitly conflicts with the claim.

**Key property:** Python rules determine the verdict; AI is not involved in the current verification engine. Missing or insufficient evidence must not produce a CONFIRMED verdict under the implemented rules.

## Scenarios included

| # | Company | Verdict | Reason |
|---|---|---|---|
| 1 | Acme Textiles | CAN'T VERIFY | MFA registration does not prove enforcement |
| 2 | Bravo Corp | CAN'T VERIFY | No evidence submitted |
| 3 | Charlie Inc | CAN'T VERIFY | Backup coverage: 8 of 12 servers |
| 4 | Delta Ltd | CONFIRMED | Evidence supports full MFA enforcement with a valid date |
| 5 | Echo Co | CONTRADICTED | Antivirus explicitly disabled |
| 6 | Foxtrot LLC | CAN'T VERIFY | Evidence dated after policy signing |

All scenarios use fictional companies and synthetic evidence.

## Technology stack

| Technology | Purpose |
|---|---|
| Python | Verification engine |
| Streamlit | Interactive dashboard |
| Pydantic | Data validation |
| JSON | Demonstration scenarios |
| pytest | Automated testing |

No LLM API key is required.

## Project structure

```text
CyberProof/
├── data/
│   └── scenarios.json
├── cyberproof/
│   ├── __init__.py
│   ├── models.py
│   ├── engine.py
│   └── reason_codes.py
├── tests/
│   └── test_engine.py
├── app.py
├── requirements.txt
└── README.md
```

## Setup and usage

```bash
git clone https://github.com/Abinaya-Saras/CyberProof.git
cd CyberProof

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

Run the tests:

```bash
pytest tests/ -v
```

Launch the application:

```bash
streamlit run app.py
```

Open `http://localhost:8501` and select a scenario from the sidebar.

## Limitations and future scope

The current prototype uses deterministic verification rules and predefined synthetic scenarios. Automated AI-based document extraction and integrations with real-world evidence sources are potential future enhancements. Further testing and validation are required before production deployment.

## References

1. Woods, D. W., Agrafiotis, I., Nurse, J. R. C., & Creese, S. (2017). [Mapping the coverage of security controls in cyber insurance proposal forms](https://doi.org/10.1186/s13174-017-0059-y). *Journal of Internet Services and Applications*.

2. [Cyber insurance: State of the art, trends and future directions](https://pmc.ncbi.nlm.nih.gov/articles/PMC9841933/) (2023).

3. Weinstock, C., & Lipson, H. F. (2013). [Evidence of Assurance: Laying the Foundation for a Credible Security Case](https://www.sei.cmu.edu/library/evidence-of-assurance-laying-the-foundation-for-a-credible-security-case/). Carnegie Mellon Software Engineering Institute.

These references inform CyberProof's approach to cyber-insurance evidence verification and security assurance.

## Disclaimer

CyberProof addresses the real-world challenge of verifying cybersecurity claims during cyber-insurance underwriting. This prototype demonstrates an evidence-based verification approach using synthetic data. All demonstration companies and evidence are fictional. Further validation and integration with real-world evidence sources are required before production deployment.