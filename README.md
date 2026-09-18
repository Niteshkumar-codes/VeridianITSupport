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

## Inputs, Sources & Assumptions

### Inputs
- **Employee request ID**: Unique identifier for the incoming request (`REQ-01` through `REQ-15`).
- **Employee name/email**: Identity and corporate email address of the requesting employee.
- **Original IT support request**: Natural-language text submitted by the employee describing their technical inquiry or problem.
- **Optional follow-up information supplied by the employee**: Additional clarifying details provided by the employee in response to diagnostic questions (e.g., employment contract status, symptoms).
- **Historical ticket records used only for precedent/reference context**: Past support tickets (`TK-1042` through `TK-1051`) referenced to check for previous resolutions or similar inquiries.

### Sources
- **KB-01 through KB-10 from the Assignment 2 data pack**:
  - `KB-01`: Password Reset
  - `KB-02`: VPN Access
  - `KB-03`: Laptop Replacement
  - `KB-04`: Software Installation Requests
  - `KB-05`: Printer Troubleshooting
  - `KB-06`: Email Mailbox Quota
  - `KB-07`: Guest Wi-Fi Access
  - `KB-08`: Expense Software Access
  - `KB-09`: Security Incident Reporting
  - `KB-10`: Work-From-Home Equipment
- **Asset Management Policy**: Corporate policy extract from Finance & Assets establishing a standard 4-year hardware refresh cycle and requiring Finance sign-off for early replacement.
- **Employee requests REQ-01 through REQ-15**: 15 benchmark workplace requests from the assignment pack used for testing and validation.
- **Historical ticket records TK-1042 through TK-1051**: 10 historical support records from the corporate ticket archive.

### Assumptions & Guardrails
1. **Supplied Data as Single Source of Truth**: The agent uses only the supplied Veridian assignment data as its policy/source-of-truth material.
2. **Mandatory Policy Grounding**: When a decision is grounded in a policy, the relevant policy ID is shown as a source.
3. **Reference-Only Precedents**: Historical tickets are reference precedents only; they are not treated as the current employee's ticket.
4. **Closed Historical Records**: Closed historical tickets remain available for history/reference but are not treated as actionable work.
5. **No Guessing on Incomplete Requests**: If required information is missing or the request is too vague, the agent asks a follow-up question rather than guessing.
6. **Safety-First Escalation**: Security-sensitive, risky, or unclear requests are escalated instead of being automatically approved.
7. **Prototype Scope**: The prototype is not connected to a live enterprise ticketing system.
8. **No Fabricated SLAs**: Do not invent SLA values because the assignment data pack does not provide SLA information.
9. **Hardware Lifecycle Reconciliation**: For laptop lifecycle decisions, the Asset Management Policy is considered alongside KB-03 where relevant.
10. **Structured Ticket Creation**: The agent creates a structured ticket record for the interaction; escalation tickets are persisted in the prototype's ticket file (`tickets_created.json`).

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

## AI Tools Used & How

### 1. Google Antigravity
**Purpose:**
- Used as the primary development environment/agent-assisted coding workspace.
- Used to implement and refine the Streamlit application.
- Used to organize the project files and development workflow.
- Used to run and validate the application and tests.
- Used to help inspect implementation issues and iterate on the prototype.

### 2. ChatGPT
**Purpose:**
- Used as a development assistant for planning the solution architecture and workflow.
- Used to help translate the assignment requirements into implementation tasks.
- Used to review logic, identify edge cases, and suggest improvements.
- Used to help prepare documentation, testing scenarios, and presentation/demo material.

### 3. Human Review & Validation
The final implementation was reviewed and validated against the authoritative Assignment 2 data pack:
- The agent is grounded in the supplied `KB-01` to `KB-10` policies and Asset Management Policy.
- The `REQ-01` to `REQ-15` employee requests were used as the benchmark test set.
- Historical tickets `TK-1042` through `TK-1051` were used for precedent/reference context.
- The implementation was tested with the 15 benchmark requests.
- Current validation result is **15/15 policy tests passing**.
- Precedent validation includes `REQ-03` → `TK-1049` and `REQ-10` → `TK-1050`.
- Streamlit UI validation was also performed.

### 4. AI Disclosure
AI tools were used during development of this prototype. Google Antigravity and ChatGPT assisted with implementation planning, coding iteration, debugging/review, testing preparation, and documentation. The final project was reviewed and validated against the assignment's authoritative data pack and requirements.
