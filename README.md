# Veridian IT Service Desk Agent

An internal IT support and triage prototype developed for the **AIONOS Agentic AI Factory (Assessment 2)**. 

The application provides deterministic, policy-grounded IT service desk triage, automated policy citation, interactive single-turn clarification, structured human escalation, and comprehensive audit logging.

---

## 1. What the Agent Does

1. **Natural Language Triage**: Understands employee IT requests in normal workplace language.
2. **Policy Search & Grounding**: Retrieves relevant policies from the official Veridian Knowledge Base (`KB-01` to `KB-10`, `ASSET`) without hallucinating rules.
3. **Historical Context Retrieval**: Correlates requests against 10 historical IT support tickets (`TK-1042` to `TK-1051`).
4. **Three-Way Decision Routing**:
   - **`RESOLVE`**: For safe, policy-backed self-service inquiries (e.g., password lockouts, guest Wi-Fi).
   - **`FOLLOW-UP`**: Prompts the employee for missing required details (e.g., full-time vs. contractor for VPN renewal).
   - **`ESCALATE`**: Enforces human review for security incidents (phishing), privileged server access, non-catalog software, or early hardware replacements.
5. **Structured Escalation Tickets**: Automatically generates a structured ticket object (ID, priority, status, assigned team, policy citations, routing notes) saved locally to `tickets_created.json`.
6. **Auditability**: Records all searches, decisions, and ticket creations with timestamps to `audit_log.json`.

---

## 2. Architecture

The system uses a **deterministic-first, LLM-enhanced hybrid architecture**:
- **Triage & Decision Engine (`agent.py`)**: Evaluates policy keywords and deterministic safety guardrails.
- **Service Desk UI (`app.py`)**: An interactive Streamlit dashboard featuring Service Desk triage, employee request loader, policy explorer, and audit trail viewer.
- **Supplied Data Store (`data.py`)**: Contains the 11 verified corporate policies, 15 benchmark requests, and 10 historical tickets.
- **Persistence**: Flat-file local JSON logging (`tickets_created.json` and `audit_log.json`).

For full architecture diagrams, data flows, and component interactions, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 3. Setup and Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.14 on Windows)
- Windows PowerShell

### Installation Steps

1. **Create and activate virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **(Optional) Configure Gemini API:**
   Copy `.env.example` to `.env` if you wish to enable the optional Gemini LLM path:
   ```powershell
   copy .env.example .env
   ```
   Add your API key inside `.env`:
   ```text
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 4. Running the Application

To start the Streamlit service desk dashboard, run:

```powershell
.\.venv\Scripts\streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## 5. Runtime Modes: Policy-Grounded Engine vs. Gemini

* **Policy-Grounded Engine (Default / Recommended for Assessment Demo)**:
  - Requires **zero external API keys or network calls**.
  - Operates using deterministic keyword and guardrail logic.
  - Fully passes 100% of benchmark test cases reproducibly.
  - Indicated in the header by the `● System Status: Active • Policy-Grounded Engine` status badge.
* **Gemini LLM Mode (Optional Enhancement)**:
  - Activated automatically when `GEMINI_API_KEY` is present in `.env`.
  - Uses `gemini-2.5-flash` for natural language summarization.
  - **Deterministic Guardrail Normalization**: All model outputs are strictly verified against hard guardrails post-generation; if a model attempts to self-approve a risky action, the guardrail forces human escalation.

---

## 6. Test Coverage (15/15 Passing)

The prototype includes 15 benchmark test cases covering all 11 supplied policies, edge cases, and safety guardrails:

| Request ID | Employee | Topic | Expected Decision | Policy |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Aditi Sharma | Dead laptop (3.5 yrs) | `escalate` | `KB-03`, `ASSET` |
| **REQ-02** | Vikram Chawla | Guest Wi-Fi access | `resolve` | `KB-07` |
| **REQ-03** | Karan Mehta | Account locked (6 attempts) | `resolve` | `KB-01` |
| **REQ-04** | Ritu Bhatia | Non-catalog software | `escalate` | `KB-04` |
| **REQ-05** | Sanjay Oberoi | Expired VPN credentials | `followup` | `KB-02` |
| **REQ-06** | Meera Iyer | Printer phantom jam | `resolve` | `KB-05` |
| **REQ-07** | Farhan Ali | Home office allowance | `resolve` | `KB-10` |
| **REQ-08** | Ananya Reddy | Suspicious phishing email | `escalate` | `KB-09` |
| **REQ-09** | Rohit Desai | Full mailbox (25GB) | `resolve` | `KB-06` |
| **REQ-10** | Kavya Pillai | Finance server admin access | `escalate` | Guardrail |
| **REQ-11** | Nikhil Bansal | Contractor VPN renewal | `followup` | `KB-02` |
| **REQ-12** | Sneha Kulkarni | Expense tool login | `resolve` | `KB-08` |
| **REQ-13** | Aman Gupta | Flickering screen (repair) | `resolve` | `KB-03` |
| **REQ-14** | Tanya Chopra | Browser extension install | `escalate` | `KB-04` |
| **REQ-15** | Rahul Menon | Vague / unspecified issue | `followup` | Guardrail |

For comprehensive test details and expected behaviors, see [TEST_CASES.md](TEST_CASES.md).

---

## 7. Limitations

- **Synthetic Assignment Scope**: Grounded strictly in the 11 supplied Veridian policies and 15 benchmark requests.
- **Local JSON Storage**: Runtime state and audit logs use flat local files (`tickets_created.json`, `audit_log.json`) rather than an external database.
- **Single-Turn Clarification**: Follow-up questioning supports single-turn Q&A disambiguation.
- **No Live ITSM Integration**: Does not connect directly to ServiceNow, Jira, Active Directory, or live email servers.

---

## 8. AI Tools Disclosure

In accordance with academic and assessment integrity guidelines:
- Large Language Models (including Google Antigravity / Gemini) were utilized as assistive coding and pair-programming agents to aid in drafting code, writing automated tests, refining UI styling, and compiling documentation.
- All final architecture decisions, guardrail boundaries, and test validation were verified directly against the Veridian Corp assignment requirements.
