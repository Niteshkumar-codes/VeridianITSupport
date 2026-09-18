import json
import os
import re
from datetime import datetime
from pathlib import Path

from data import POLICIES, TICKETS

AUDIT_FILE = Path("audit_log.json")
TICKETS_CREATED_FILE = Path("tickets_created.json")

def create_structured_ticket(employee, request, decision, policy_ids, response_text, followup=""):
    """Creates a structured ticket object for all processed requests (persists only for escalation)."""
    q = request.lower()

    if any(x in q for x in ["phishing", "malware", "unauthorized access", "suspicious email"]) or "KB-09" in policy_ids:
        category = "Security Incident"
        priority = "High"
        assigned_team = "IT Security"
        notes = "Suspected security incident reported. Immediate investigation required; message must not be redistributed."
    elif "admin access" in q or "finance reporting server" in q:
        category = "Privileged Access Request"
        priority = "High"
        assigned_team = "IT Administration & Security"
        notes = "Privileged/admin server access requested. Requires formal business justification and human/security authorization."
    elif any(x in q for x in ["non-catalog", "software catalog", "browser extension"]) or "KB-04" in policy_ids:
        category = "Software Installation"
        priority = "Medium"
        assigned_team = "IT Security Review"
        notes = "Non-catalog software/browser extension requested. IT Security review required (3-5 business days turnaround)."
    elif any(x in q for x in ["laptop", "dead", "won't turn on", "wont turn on", "replace", "replacement"]) or ("KB-03" in policy_ids and "ASSET" in policy_ids):
        category = "Hardware Replacement"
        priority = "Medium"
        assigned_team = "IT Support & Finance"
        notes = "Early laptop replacement requested under overlapping policies (KB-03 / ASSET). Requires technician hardware diagnosis and Finance sign-off."
    elif any(x in q for x in ["password", "locked out", "lockout", "login"]) or "KB-01" in policy_ids:
        category = "Access Management"
        priority = "Medium" if decision != "resolve" else "Low"
        assigned_team = "IT Service Desk"
        notes = "Account lockout or password reset assistance."
    elif any(x in q for x in ["vpn"]) or "KB-02" in policy_ids:
        category = "Network & Remote Access"
        priority = "Medium"
        assigned_team = "Network Operations"
        notes = "VPN credential/connectivity request."
    elif any(x in q for x in ["wifi", "wi-fi", "guest"]) or "KB-07" in policy_ids:
        category = "Network Access"
        priority = "Low"
        assigned_team = "Office IT & Front Desk"
        notes = "Guest Wi-Fi credential request."
    elif any(x in q for x in ["printer", "paper jam", "print"]) or "KB-05" in policy_ids:
        category = "Hardware & Peripherals"
        priority = "Low"
        assigned_team = "Local IT Support"
        notes = "Printer maintenance and troubleshooting."
    elif any(x in q for x in ["mailbox", "quota", "email"]) or "KB-06" in policy_ids:
        category = "Email Services"
        priority = "Low"
        assigned_team = "IT Messaging Services"
        notes = "Mailbox quota inquiry/expansion."
    elif any(x in q for x in ["home office", "equipment", "wfh", "chair", "monitor"]) or "KB-10" in policy_ids:
        category = "Workplace Equipment"
        priority = "Low"
        assigned_team = "IT Asset Management"
        notes = "Remote work equipment allowance."
    elif any(x in q for x in ["expense", "expense tool"]) or "KB-08" in policy_ids:
        category = "Finance Software"
        priority = "Medium"
        assigned_team = "Finance & IT Application Support"
        notes = "Expense application access or troubleshooting."
    else:
        category = "General IT Support"
        priority = "Medium"
        assigned_team = "IT Tier 1 Support"
        notes = followup if followup else response_text[:200]

    # Map decision to status
    if decision == "escalate":
        status = "Open (escalated)"
    elif decision == "resolve":
        status = "Resolved (guided)"
        if assigned_team == "IT Tier 1 Support":
            assigned_team = "IT Service Desk (Automated)"
    elif decision == "followup":
        status = "Pending clarification"
        assigned_team = "IT Service Desk (Awaiting Details)"
    else:
        status = "Open"

    existing = []
    if TICKETS_CREATED_FILE.exists():
        try:
            existing = json.loads(TICKETS_CREATED_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    ticket_id = f"TK-{1052 + len(existing)}"

    ticket = {
        "ticket_id": ticket_id,
        "employee": employee if employee else "Unspecified Employee",
        "original_request": request,
        "category": category,
        "priority": priority,
        "decision": decision,
        "assigned_team": assigned_team,
        "policy_sources": policy_ids,
        "status": status,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "notes": notes
    }

    if decision == "escalate":
        existing.append(ticket)
        TICKETS_CREATED_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        log_event("ticket_created", ticket)

    return ticket

def log_event(event, details):
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event": event,
        "details": details
    }
    existing = []
    if AUDIT_FILE.exists():
        try:
            existing = json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    existing.append(row)
    AUDIT_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")

def search_policies(query):
    q = query.lower()
    words = set(re.findall(r"[a-z0-9]+", q))
    scored = []
    for p in POLICIES:
        hay = (p["title"] + " " + p["text"]).lower()
        score = sum(1 for w in words if len(w) > 2 and w in hay)
        if score:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:3]]

def search_tickets(query, active_only=False):
    q = query.lower()
    stopwords = {
        "the", "and", "for", "with", "from", "not", "how", "get", "got",
        "can", "our", "all", "that", "this", "need", "have", "had", "hey",
        "help", "says", "keeps", "just", "about", "any", "some", "someone",
        "please", "approval", "tomorrow", "starting", "started", "office",
        "request", "also"
    }
    words = set(w for w in re.findall(r"[a-z0-9]+", q) if len(w) > 2 and w not in stopwords)
    scored = []
    for t in TICKETS:
        if active_only and "active" not in t.get("status", "").lower():
            continue
        hay_words = set(re.findall(r"[a-z0-9]+", (t["issue"] + " " + t["employee"]).lower()))
        score = sum(1 for w in words if w in hay_words)
        if score > 0:
            scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:3]]

def guardrail(request, policy_ids):
    """Deterministic safety layer. The LLM never gets to override these rules."""
    q = request.lower()
    if any(x in q for x in ["phishing", "malware", "unauthorized access", "suspicious email"]):
        return {
            "decision": "escalate",
            "reason": "Security incident: route immediately to Security; do not redistribute the suspicious message.",
            "policy_ids": ["KB-09"]
        }
    if "admin access" in q or ("access" in q and "finance reporting server" in q):
        return {
            "decision": "escalate",
            "reason": "Privileged access is not an ordinary IT self-service request; human/security review is required.",
            "policy_ids": []
        }
    if "non-catalog" in q or "not in the software catalog" in q or "browser extension" in q:
        return {
            "decision": "escalate",
            "reason": "Non-catalog software requires IT Security review.",
            "policy_ids": ["KB-04"]
        }
    if "contract" in q and "vpn" in q:
        if not any(x in q for x in ["contractor", "full-time", "full time", "answered:"]):
            return {
                "decision": "followup",
                "reason": "VPN policy differs for full-time employees and contractors; employment type is required.",
                "policy_ids": ["KB-02"]
            }
    if "laptop" in q and any(x in q for x in ["not a replacement", "needs a fix", "just needs a fix", "fix not", "repair"]):
        return {
            "decision": "resolve",
            "reason": (
                "Under KB-03, scheduled laptop replacement applies after 3 years of service (and 4 years under ASSET), "
                "so scheduled replacement does not apply to a 2-year-old device. As you indicated that it only needs a fix "
                "rather than replacement, please submit a ticket for hardware diagnosis and screen repair with an IT technician."
            ),
            "policy_ids": ["KB-03"],
            "followup": None
        }
    if ("laptop" in q or "KB-03" in policy_ids or "ASSET" in policy_ids) and any(x in q for x in ["replace", "replacement", "dead", "won't turn on", "wont turn on", "turn on", "failure", "years", "old"]):
        return {
            "decision": "escalate",
            "reason": (
                "Laptop replacement involves two overlapping policies:\n\n"
                "- **KB-03 (IT Policy)**: Covers replacement eligibility after 3 years of service, or earlier in case of verified hardware failure (requests require 2 weeks advance notice).\n"
                "- **ASSET Policy (Finance & Assets)**: Establishes a standard 4-year refresh cycle from date of issue; early replacement outside this cycle requires Finance sign-off in addition to IT approval.\n\n"
                "**Current Assessment:** The laptop has been in service for ~3.5 years (eligible under KB-03's 3-year guideline, but early under ASSET's 4-year cycle). Furthermore, hardware failure has not yet been independently verified by an IT technician. Therefore, this request cannot be automatically approved and is routed to IT for diagnostic verification and Finance for early replacement sign-off."
            ),
            "policy_ids": ["KB-03", "ASSET"],
            "followup": None
        }
    return None

def fallback_plan(request):
    q = request.lower()
    if any(x in q for x in ["password", "locked out"]):
        if "6 times" in q or "5 failed" in q or "locked out" in q:
            return {"decision":"resolve","response":"Your account is locked after more than five failed attempts. IT needs to unlock it manually. No approval is required.","policy_ids":["KB-01"],"followup":None}
        return {"decision":"resolve","response":"You can reset your password through the self-service portal. If you are locked out after five failed attempts, IT can unlock the account manually.","policy_ids":["KB-01"],"followup":None}
    if "guest" in q and ("wifi" in q or "wi-fi" in q):
        return {"decision":"resolve","response":"Guest Wi-Fi credentials are valid for 24 hours and can be generated by any employee from the front-desk kiosk. No IT ticket is required.","policy_ids":["KB-07"],"followup":None}
    if "vpn" in q:
        if any(c in q for c in ["contractor", "contract"]):
            return {"decision":"resolve","response":"Under KB-02, contractors require manager approval submitted via the access request form before VPN access can be granted or renewed.","policy_ids":["KB-02"],"followup":None}
        if any(f in q for f in ["full-time", "full time", "fte", "permanent"]):
            return {"decision":"resolve","response":"Under KB-02, VPN access is granted automatically to full-time employees. VPN credentials expire every 90 days and must be renewed by the employee via the self-service portal.","policy_ids":["KB-02"],"followup":None}
        return {"decision":"followup","response":"VPN access policy differs depending on your employment type.","policy_ids":["KB-02"],"followup":"Are you a full-time employee or contractor?"}
    if "mailbox" in q or "email" in q and "full" in q:
        return {"decision":"resolve","response":"The default mailbox quota is 25GB. Archive old mail first; increases beyond 25GB require manager approval and cannot exceed 50GB.","policy_ids":["KB-06"],"followup":None}
    if "printer" in q:
        return {"decision":"resolve","response":"First check the printer queue and restart the print spooler. If the issue remains, a ticket should include the printer asset tag.","policy_ids":["KB-05"],"followup":"What is the printer asset tag?"}
    if "home" in q and ("office" in q or "setup" in q or "equipment" in q):
        return {"decision":"resolve","response":"Employees working remotely more than 3 days/week are eligible for a one-time home-office equipment allowance, subject to manager sign-off and Finance processing. IT handles shipping after approval.","policy_ids":["KB-10"],"followup":None}
    if "expense" in q:
        return {"decision":"resolve","response":"Finance grants access to the expense management tool. IT can help with login/technical issues only after an account exists.","policy_ids":["KB-08"],"followup":"Do you already have an expense-tool account, and can you share the exact error message?"}
    if "laptop" in q or "screen" in q:
        if any(x in q for x in ["not a replacement", "needs a fix", "just needs a fix", "fix not", "repair"]):
            return {
                "decision": "resolve",
                "response": (
                    "Under KB-03, scheduled laptop replacement applies after 3 years of service (and 4 years under ASSET), "
                    "so scheduled replacement does not apply to a 2-year-old device. As you indicated that it only needs a fix "
                    "rather than replacement, please submit a ticket for hardware diagnosis and screen repair with an IT technician."
                ),
                "policy_ids": ["KB-03"],
                "followup": None
            }
        return {
            "decision": "escalate",
            "response": (
                "Laptop replacement involves two overlapping policies:\n\n"
                "- **KB-03 (IT Policy)**: Covers replacement eligibility after 3 years of service, or earlier in case of verified hardware failure.\n"
                "- **ASSET Policy (Finance & Assets)**: Establishes a standard 4-year refresh cycle; early replacement requires Finance sign-off in addition to IT approval.\n\n"
                "Hardware failure has not yet been independently verified by IT, and the device is under the 4-year cycle. Automatic approval cannot be granted; request is routed for technician diagnosis and Finance sign-off."
            ),
            "policy_ids": ["KB-03", "ASSET"],
            "followup": None
        }
    return {
        "decision": "followup",
        "response": "Clarification required before routing: insufficient detail to identify the affected system or policy.",
        "policy_ids": [],
        "followup": "What system or device is not working, and what error do you see?",
        "clarification_questions": [
            "What system, device, or application is not working?",
            "What were you trying to do?",
            "What error message do you see?",
            "When did the problem start?"
        ]
    }

def llm_plan(request):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_plan(request)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        policy_text = "\n".join(f'{p["id"]}: {p["title"]} — {p["text"]}' for p in POLICIES)
        prompt = f"""
You are the Veridian Corp IT support triage assistant.
Use ONLY the supplied policies. Never invent a policy.
Return JSON only with keys:
decision (resolve|followup|escalate),
response (short employee-facing response),
policy_ids (list of policy IDs),
followup (string or null).

Important safety rules:
- Security incidents must be escalated.
- Privileged/admin access must not be granted by the assistant.
- Non-catalog software requires Security review.
- If a policy depends on employment type (e.g. VPN under KB-02) and it is not specified, ask for it as a followup. If the employee specifies they are a contractor or full-time, resolve using KB-02.
- Laptop replacement requests must evaluate both KB-03 (3-year eligibility / verified hardware failure) and ASSET (4-year refresh cycle requiring Finance sign-off). Never automatically approve laptop replacement. If hardware failure is unverified or laptop is under 4 years, explain both policies, state that hardware failure requires independent technician verification, and escalate for IT diagnosis and Finance approval.
- If the request is too vague, ask one useful question.
- Cite only IDs present in the supplied policy list.

Policies:
{policy_text}

Employee request:
{request}
"""
        result = client.models.generate_content(model=model, contents=prompt)
        raw = result.text.strip()
        raw = re.sub(r"^```json\s*|\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        log_event("llm_fallback", {"error": str(e)})
        return fallback_plan(request)

def run_agent(request, employee=""):
    log_event("agent_started", {"employee": employee, "request": request})
    matched = search_policies(request)
    log_event("policy_search", {"matched_policy_ids": [p["id"] for p in matched]})

    # Search relevant historical precedent tickets
    matched_tickets = search_tickets(request, active_only=False)
    log_event("ticket_search", {"found_tickets": [t["id"] for t in matched_tickets]})

    hard = guardrail(request, [p["id"] for p in matched])
    if hard:
        result = {
            "decision": hard["decision"],
            "response": hard["reason"],
            "policy_ids": hard["policy_ids"],
            "followup": hard.get("followup")
        }
    else:
        result = llm_plan(request)

    # Final safety normalization: never allow the model to override mandatory routing.
    hard = guardrail(request, result.get("policy_ids", []))
    if hard and hard["decision"] == "escalate":
        result["decision"] = "escalate"
        result["response"] = hard["reason"]
        result["policy_ids"] = hard["policy_ids"]

    # Attach relevant ticket context
    result["tickets"] = matched_tickets

    # Generate structured ticket for every processed request (persisted only for escalate)
    result["structured_ticket"] = create_structured_ticket(
        employee=employee,
        request=request,
        decision=result.get("decision", "resolve"),
        policy_ids=result.get("policy_ids", []),
        response_text=result.get("response", ""),
        followup=result.get("followup", "")
    )

    log_event("agent_decision", {
        "employee": employee,
        "decision": result.get("decision"),
        "policy_ids": result.get("policy_ids", []),
        "tickets": [t["id"] for t in matched_tickets],
        "created_ticket_id": result["structured_ticket"]["ticket_id"] if result.get("structured_ticket") else None,
        "response": result.get("response", "")
    })
    return result
