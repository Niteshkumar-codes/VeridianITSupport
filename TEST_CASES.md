# Veridian IT Service Desk Agent — Test Cases (REQ-01 to REQ-15)

This document contains 15 manual test cases based **strictly** on the supplied Veridian Corp employee requests and policies from `data.py`. No policies or external facts are invented.

---

## Test Cases Summary Table

| Test ID | Request ID | Employee | Expected Intent | Policy Source(s) | Expected Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | REQ-01 | Aditi Sharma | Laptop replacement for dead device (3.5 yrs) | `KB-03`, `ASSET` | `escalate` |
| **TC-02** | REQ-02 | Vikram Chawla | Guest Wi-Fi access | `KB-07` | `resolve` |
| **TC-03** | REQ-03 | Karan Mehta | Account lockout after 6 failed attempts | `KB-01` | `resolve` |
| **TC-04** | REQ-04 | Ritu Bhatia | Non-catalog software installation | `KB-04` | `escalate` |
| **TC-05** | REQ-05 | Sanjay Oberoi | Expired VPN credentials | `KB-02` | `followup` |
| **TC-06** | REQ-06 | Meera Iyer | Printer phantom paper jam | `KB-05` | `resolve` |
| **TC-07** | REQ-07 | Farhan Ali | Home office equipment allowance | `KB-10` | `resolve` |
| **TC-08** | REQ-08 | Ananya Reddy | Phishing email reporting | `KB-09` | `escalate` |
| **TC-09** | REQ-09 | Rohit Desai | Mailbox quota limit reached (25GB) | `KB-06` | `resolve` |
| **TC-10** | REQ-10 | Kavya Pillai | Privileged admin access to Finance server | Guardrail / `KB-08` | `escalate` |
| **TC-11** | REQ-11 | Nikhil Bansal | Contractor VPN access transition | `KB-02` | `followup` |
| **TC-12** | REQ-12 | Sneha Kulkarni | Expense tool login credentials failure | `KB-08` | `resolve` |
| **TC-13** | REQ-13 | Aman Gupta | Laptop screen flickering (2 yrs, repair) | `KB-03` | `resolve` |
| **TC-14** | REQ-14 | Tanya Chopra | Browser extension installation | `KB-04` | `escalate` |
| **TC-15** | REQ-15 | Rahul Menon | Vague / underspecified issue | None | `followup` |

---

## Detailed Test Cases

### TC-01: Laptop Replacement Overlap (3.5 Years Old, Completely Dead)
* **Test ID:** TC-01
* **Request ID:** REQ-01
* **Employee:** Aditi Sharma
* **Input / Request:** "My laptop won't turn on at all, it's completely dead, had it about 3.5 years now."
* **Expected Intent:** Hardware replacement request due to complete failure after 3.5 years of service.
* **Expected Policy Source(s):** `KB-03` (Laptop Replacement) and `ASSET` (Asset Management Policy Extract)
* **Expected Decision:** `escalate` (Human escalation)
* **Expected Escalation or Follow-up:** Route to IT Support for hardware diagnostics and to Finance for early replacement approval.
* **Expected Key Behaviour:**
  1. Retrieve and evaluate **both** `KB-03` and `ASSET`.
  2. Explain that under `KB-03`, laptops are eligible after 3 years or earlier for verified hardware failure.
  3. Explain that under `ASSET`, standard refresh cycle is 4 years and early replacement requires Finance sign-off.
  4. Do **not** automatically approve replacement.
  5. Note that hardware failure has **not yet been independently verified** by an IT technician.

---

### TC-02: Guest Wi-Fi Access
* **Test ID:** TC-02
* **Request ID:** REQ-02
* **Employee:** Vikram Chawla
* **Input / Request:** "Can I get Wi-Fi access for a guest visiting our office tomorrow?"
* **Expected Intent:** Inquiring about guest Wi-Fi access credentials.
* **Expected Policy Source(s):** `KB-07` (Guest Wi-Fi Access)
* **Expected Decision:** `resolve` (Resolved / guided)
* **Expected Escalation or Follow-up:** None.
* **Expected Key Behaviour:**
  1. State that guest Wi-Fi credentials are valid for 24 hours.
  2. Explain that credentials can be generated self-service by any employee from the front-desk kiosk.
  3. Explicitly state that **no IT ticket is required**.

---

### TC-03: Account Lockout (>5 Failed Password Attempts)
* **Test ID:** TC-03
* **Request ID:** REQ-03
* **Employee:** Karan Mehta
* **Input / Request:** "I'm locked out of my account, I tried my password 6 times."
* **Expected Intent:** Unlocking account after exceeding failed login attempt threshold.
* **Expected Policy Source(s):** `KB-01` (Password Reset)
* **Expected Decision:** `resolve` (Resolved / guided)
* **Expected Escalation or Follow-up:** None (IT manual unlock instructions).
* **Expected Key Behaviour:**
  1. Recognize that 6 attempts exceeds the 5-attempt limit under `KB-01`.
  2. Explain that self-service reset is for normal resets, but once locked out after 5 failed attempts, IT must unlock the account manually.
  3. Note that **no approval is required** for account unlocking.

---

### TC-04: Non-Catalog Software Request
* **Test ID:** TC-04
* **Request ID:** REQ-04
* **Employee:** Ritu Bhatia
* **Input / Request:** "Need approval to install a data-analysis tool that's not in the software catalog."
* **Expected Intent:** Requesting installation of third-party software not present in the approved catalog.
* **Expected Policy Source(s):** `KB-04` (Software Installation Requests)
* **Expected Decision:** `escalate` (Human escalation)
* **Expected Escalation or Follow-up:** Route request to IT Security review (3–5 business days turnaround).
* **Expected Key Behaviour:**
  1. Contrast catalog software (self-installable) with non-catalog software.
  2. Enforce deterministic escalation: non-catalog software **cannot be auto-approved**.
  3. Inform the employee that IT Security review takes 3–5 business days.

---

### TC-05: Expired VPN Credentials (Follow-up Flow)
* **Test ID:** TC-05
* **Request ID:** REQ-05
* **Employee:** Sanjay Oberoi
* **Input / Request:** "My VPN stopped working this morning, says credentials expired."
* **Expected Intent:** Inability to connect to VPN due to expired credentials.
* **Expected Policy Source(s):** `KB-02` (VPN Access)
* **Expected Decision:** `followup` (Needs one detail)
* **Expected Escalation or Follow-up:**
  * Initial follow-up: "Are you a full-time employee or contractor?"
  * If answered "Contractor" -> resolve citing manager approval via access request form.
  * If answered "Full-time" -> resolve citing automatic access and 90-day renewal cycle.
* **Expected Key Behaviour:**
  1. Explain that VPN credentials expire every 90 days.
  2. Distinguish rules for full-time employees (automatic) vs contractors (requires manager approval).
  3. Ask exactly one focused clarifying question regarding employment type.

---

### TC-06: Printer Paper Jam Troubleshooting
* **Test ID:** TC-06
* **Request ID:** REQ-06
* **Employee:** Meera Iyer
* **Input / Request:** "Printer on the 3rd floor keeps showing 'paper jam' even though there's no jam."
* **Expected Intent:** Printer hardware error that persists despite no visible obstruction.
* **Expected Policy Source(s):** `KB-05` (Printer Troubleshooting)
* **Expected Decision:** `resolve` (Resolved / guided)
* **Expected Escalation or Follow-up:** Follow-up prompt for printer asset tag if escalation ticket is needed.
* **Expected Key Behaviour:**
  1. Provide first-line troubleshooting: check printer queue and restart print spooler.
  2. State that if issue persists after spooler restart, a ticket must be logged including the **printer's asset tag**.

---

### TC-07: Work-From-Home Equipment Allowance
* **Test ID:** TC-07
* **Request ID:** REQ-07
* **Employee:** Farhan Ali
* **Input / Request:** "I've started working from home 4 days a week, how do I get a home office setup?"
* **Expected Intent:** Inquiring about home office equipment allowance eligibility and process.
* **Expected Policy Source(s):** `KB-10` (Work-From-Home Equipment)
* **Expected Decision:** `resolve` (Resolved / guided)
* **Expected Escalation or Follow-up:** None (procedural guidance).
* **Expected Key Behaviour:**
  1. Confirm eligibility: working remotely >3 days/week qualifies for a one-time allowance (chair, monitor).
  2. Explain workflow: requires **manager sign-off** and **Finance processing**.
  3. Clarify IT scope: IT only handles equipment shipping once approval is completed.

---

### TC-08: Security Incident — Suspected Phishing
* **Test ID:** TC-08
* **Request ID:** REQ-08
* **Employee:** Ananya Reddy
* **Input / Request:** "I think I got a phishing email asking for my login — a few teammates got the same email."
* **Expected Intent:** Reporting a suspected phishing email targeting corporate credentials.
* **Expected Policy Source(s):** `KB-09` (Security Incident Reporting)
* **Expected Decision:** `escalate` (Human escalation)
* **Expected Escalation or Follow-up:** Immediate escalation to Security team (security@veridian-corp.example).
* **Expected Key Behaviour:**
  1. Deterministic guardrail intercept: never allow LLM to handle security incidents as routine requests.
  2. Instruct employee to report immediately to `security@veridian-corp.example`.
  3. Explicitly caution the employee **not to forward or redistribute** the email to teammates.

---

### TC-09: Mailbox Storage Quota Exceeded
* **Test ID:** TC-09
* **Request ID:** REQ-09
* **Employee:** Rohit Desai
* **Input / Request:** "My mailbox is full and I can't send emails."
* **Expected Intent:** Mailbox full; unable to send or receive messages.
* **Expected Policy Source(s):** `KB-06` (Email Mailbox Quota)
* **Expected Decision:** `resolve` (Resolved / guided)
* **Expected Escalation or Follow-up:** None (procedural guidance).
* **Expected Key Behaviour:**
  1. Inform employee that default mailbox quota is 25GB.
  2. Advise archiving old emails first.
  3. Clarify that quota increases beyond 25GB require manager approval and are strictly capped at 50GB.

---

### TC-10: Privileged Admin Access Request
* **Test ID:** TC-10
* **Request ID:** REQ-10
* **Employee:** Kavya Pillai
* **Input / Request:** "Can someone give me admin access to the Finance reporting server? Need it urgently for month-end."
* **Expected Intent:** Urgent privileged administrator access to financial reporting infrastructure.
* **Expected Policy Source(s):** Guardrail (Privileged Access Rule) / `KB-08` context
* **Expected Decision:** `escalate` (Human escalation)
* **Expected Escalation or Follow-up:** Escalate to Security and Server Administration for human review and business justification.
* **Expected Key Behaviour:**
  1. Deterministic guardrail blocks automated granting of admin or privileged access.
  2. State that privileged access cannot be granted via self-service IT support.
  3. Route to human administrator / Security with formal business justification required.

---

### TC-11: Contractor VPN Access at End of Contract
* **Test ID:** TC-11
* **Request ID:** REQ-11
* **Employee:** Nikhil Bansal
* **Input / Request:** "My contract is ending next month, they'll need VPN access."
* **Expected Intent:** VPN access request for contractor status.
* **Expected Policy Source(s):** `KB-02` (VPN Access)
* **Expected Decision:** `followup` (Needs one detail)
* **Expected Escalation or Follow-up:** Prompt for confirmation of employment/contractor details and direct to manager access request form.
* **Expected Key Behaviour:**
  1. Identify that VPN access for contractors is not automatic.
  2. Emphasize that contractors require manager approval submitted via the access request form.
  3. Note that VPN credentials expire every 90 days and must be renewed.

---

### TC-12: Expense Software Authentication Failure
* **Test ID:** TC-12
* **Request ID:** REQ-12
* **Employee:** Sneha Kulkarni
* **Input / Request:** "I can't log into the expense tool, keeps saying invalid credentials."
* **Expected Intent:** Login failure on expense management software.
* **Expected Policy Source(s):** `KB-08` (Expense Software Access)
* **Expected Decision:** `resolve` (Resolved / guided)
* **Expected Escalation or Follow-up:** Optional follow-up checking if an account has already been created by Finance.
* **Expected Key Behaviour:**
  1. Clarify policy boundary: access to the expense tool is granted by **Finance, not IT**.
  2. Explain that IT can only assist with login/technical troubleshooting after an account already exists.
  3. Guide user to contact Finance if no account has been provisioned yet.

---

### TC-13: Laptop Hardware Repair vs. Replacement (2 Years Old)
* **Test ID:** TC-13
* **Request ID:** REQ-13
* **Employee:** Aman Gupta
* **Input / Request:** "Laptop screen is flickering on and off, had it 2 years, maybe just needs a fix not a replacement."
* **Expected Intent:** Display hardware issue requiring diagnostic and repair, explicitly noting that replacement may not be required.
* **Expected Policy Source(s):** `KB-03` (Laptop Replacement)
* **Expected Decision:** `resolve` (Resolved / guided)
* **Expected Escalation or Follow-up:** Direct to IT technician for physical hardware diagnostic/screen repair.
* **Expected Key Behaviour:**
  1. **Distinguish repair from replacement**: Acknowledge the employee's note that it only needs a fix.
  2. Device is 2 years old (under the 3-year threshold of `KB-03` and 4-year cycle of `ASSET`), so scheduled replacement does not apply.
  3. Guide employee to submit device for physical hardware inspection/repair rather than initiating a replacement ticket.

---

### TC-14: Browser Extension Installation Request
* **Test ID:** TC-14
* **Request ID:** REQ-14
* **Employee:** Tanya Chopra
* **Input / Request:** "Requesting approval to install a browser extension for productivity tracking."
* **Expected Intent:** Approval request to install a browser add-on.
* **Expected Policy Source(s):** `KB-04` (Software Installation Requests)
* **Expected Decision:** `escalate` (Human escalation)
* **Expected Escalation or Follow-up:** Route to IT Security for review (3–5 business days).
* **Expected Key Behaviour:**
  1. Browser extensions are treated as unapproved/non-catalog software under `KB-04`.
  2. Disallow automated approval or self-installation.
  3. Route to IT Security review, noting the 3–5 business day turnaround.

---

### TC-15: Vague Request ("It's not working")
* **Test ID:** TC-15
* **Request ID:** REQ-15
* **Employee:** Rahul Menon
* **Input / Request:** "Hey can you help, it's not working."
* **Expected Intent:** Undefined IT support issue with zero specifics.
* **Expected Policy Source(s):** None (no policy can be safely matched)
* **Expected Decision:** `followup` (Needs one detail)
* **Expected Escalation or Follow-up:** Follow-up question: "What system or device is not working, and what error do you see?"
* **Expected Key Behaviour:**
  1. **Do not hallucinate or guess** a policy.
  2. Ask exactly **one** focused clarifying question to identify the affected system and error symptoms.
  3. Defer policy matching until necessary details are provided.
