import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from data import POLICIES, REQUESTS, TICKETS
from agent import (
    run_agent,
    search_policies,
    search_tickets,
    log_event,
    AUDIT_FILE,
    TICKETS_CREATED_FILE
)

load_dotenv()

st.set_page_config(
    page_title="Veridian IT Service Desk",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Subtle custom CSS for balanced padding, readable typography, and clean status pills
st.markdown("""
<style>
    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #E0E0E0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 2.75rem;
        font-weight: 500;
        font-size: 0.95rem;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.825rem;
        font-weight: 600;
        background-color: #E6F4EA;
        color: #137333;
        border: 1px solid #CEEAD6;
    }
</style>
""", unsafe_allow_html=True)

# Top header row with prominent title, official subtitle, and clean status indicator
header_left, header_right = st.columns([3, 1], vertical_alignment="center")
with header_left:
    st.title("Veridian IT Service Desk")
    st.caption("Internal support prototype • policy-grounded triage • human escalation")
with header_right:
    st.markdown(
        '<div style="text-align: right;"><span class="status-badge">● System Status: Active • Policy-Grounded Engine</span></div>',
        unsafe_allow_html=True
    )

# Compact, professional sidebar
with st.sidebar:
    st.subheader("Prototype status")
    st.markdown("**Engine Status:** `● Active • Policy-Grounded Engine`")
    st.markdown("**Policy Source:** Veridian assignment pack")
    st.markdown(f"**Policies Loaded:** `{len(POLICIES)} policies`")
    st.markdown(f"**Historical Tickets:** `{len(TICKETS)} records`")
    st.divider()
    st.markdown("**Safety Principles:**")
    st.write("• Strictly grounded in verified company policies.")
    st.write("• No policy invention or unverified self-service.")
    st.write("• Risky, admin, or early-replacement requests route to human teams.")

if "employee" not in st.session_state:
    st.session_state["employee"] = "Demo Employee"
if "request_text" not in st.session_state:
    st.session_state["request_text"] = ""

tab1, tab2, tab3, tab4 = st.tabs(["💬 Service Desk", "📋 Employee Requests", "📚 Policies", "🧾 Audit Trail"])

with tab1:
    with st.container(border=True):
        st.subheader("Ask IT")
        st.caption("Quick example scenarios:")
        presets = {
            "Locked account": "I'm locked out of my account, I tried my password 6 times.",
            "Guest Wi-Fi": "Can I get Wi-Fi access for a guest visiting our office tomorrow?",
            "Phishing": "I think I got a phishing email asking for my login.",
            "Non-catalog software": "Need approval to install a data-analysis tool that's not in the software catalog.",
            "VPN": "My VPN stopped working this morning, says credentials expired.",
            "Vague request": "Hey can you help, it's not working."
        }
        cols = st.columns(6)
        for col, (label, value) in zip(cols, presets.items()):
            if col.button(label, use_container_width=True):
                st.session_state["request_text"] = value
                st.session_state.pop("last_result", None)
                st.session_state.pop("original_request", None)
                st.session_state.pop("followup_answer", None)

        st.text_input("Employee name", key="employee")
        st.text_area(
            "Employee message",
            key="request_text",
            height=100,
            placeholder="Describe the issue in normal language..."
        )

        if st.button("Run support agent", type="primary", use_container_width=True):
            req_val = st.session_state.get("request_text", "")
            emp_val = st.session_state.get("employee", "")
            if not req_val.strip():
                st.warning("Enter an employee request first.")
            else:
                st.session_state["original_request"] = req_val
                st.session_state.pop("followup_answer", None)
                result = run_agent(req_val, emp_val)
                st.session_state["last_result"] = result
                st.session_state["last_request"] = req_val

    result = st.session_state.get("last_result")
    if result:
        st.divider()
        decision = result.get("decision", "followup")
        labels = {
            "resolve": "Resolved / guided",
            "followup": "Clarification Required Before Routing",
            "escalate": "Human escalation"
        }

        # 1. Decision shown first with distinct styling
        st.subheader(labels.get(decision, decision.title()))
        if decision == "resolve":
            st.success("Decision: RESOLVE — Policy-supported resolution")
        elif decision == "followup":
            st.info("Decision: NEED_INFO — Clarification required before routing")
        elif decision == "escalate":
            st.warning("Decision: ESCALATE — Requires human review / approval (no automatic action)")

        # Follow-up interaction right below decision
        if decision == "followup" and result.get("followup"):
            with st.container(border=True):
                st.info(f"**Follow-up Question:** {result['followup']}")
                questions = result.get("clarification_questions")
                if questions:
                    st.markdown("**Diagnostic Checklist:**")
                    for q_item in questions:
                        st.markdown(f"- {q_item}")
                elif not result.get("policy_ids"):
                    st.markdown("""**Diagnostic Checklist:**
- What system, device, or application is not working?
- What were you trying to do?
- What error message do you see?
- When did the problem start?
""")
                followup_input = st.text_input("Employee answer", key="followup_answer_input", placeholder="Type your answer here...")
                if st.button("Submit answer", type="primary"):
                    if not followup_input.strip():
                        st.warning("Please provide an answer first.")
                    else:
                        orig = st.session_state.get("original_request", st.session_state.get("request_text", ""))
                        emp_name = st.session_state.get("employee", "")
                        combined = f"{orig} (Employee answered: {followup_input.strip()})"
                        log_event("followup_answered", {
                            "employee": emp_name,
                            "original_request": orig,
                            "followup_question": result["followup"],
                            "answer": followup_input.strip()
                        })
                        new_result = run_agent(combined, emp_name)
                        st.session_state["last_result"] = new_result
                        st.session_state["followup_answer"] = followup_input.strip()
                        st.rerun()

        if st.session_state.get("followup_answer"):
            st.markdown(f"**Original Request:** *{st.session_state.get('original_request', '')}*")
            st.markdown(f"**Employee Answer:** *{st.session_state.get('followup_answer', '')}*")

        # 2. Response
        with st.container(border=True):
            st.markdown("### Guidance & Response")
            st.write(result.get("response", ""))

        # 3. Sources used
        policy_ids = result.get("policy_ids", [])
        if policy_ids:
            st.markdown("**Sources used**")
            for pid in policy_ids:
                p = next((x for x in POLICIES if x["id"] == pid), None)
                if p:
                    with st.expander(f'{p["id"]} — {p["title"]}'):
                        st.write(p["text"])

        # 4. Historical Precedents (clearly separated and labelled)
        st.markdown("### 📜 Historical Precedents (Reference Context)")
        st.caption("Past IT tickets from corporate history for similarity context. (Note: Precedent tickets represent past reference cases from other employees, not current tickets.)")
        tickets = result.get("tickets", [])
        if tickets:
            for t in tickets:
                st.markdown(f"- **{t['id']}** — {t['employee']} — {t['issue']} — *Status: {t['status']}*")
        else:
            st.write("No relevant historical precedent ticket found.")

        # 5. Generated Structured Ticket (displayed after every processed request)
        ticket = result.get("structured_ticket")
        if ticket:
            with st.container(border=True):
                st.markdown("### 🎫 Generated Structured Ticket")
                if decision == "escalate":
                    st.caption("Status: Persisted locally to tickets_created.json for human team action.")
                elif decision == "resolve":
                    st.caption("Status: Standard resolution record (session execution).")
                else:
                    st.caption("Status: Clarification ticket record (pending user input).")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Ticket ID", ticket["ticket_id"])
                m2.metric("Priority", ticket["priority"])
                m3.metric("Status", ticket["status"])
                m4.metric("Assigned Team", ticket["assigned_team"])

                c_left, c_right = st.columns(2)
                with c_left:
                    st.markdown(f"**Category:** {ticket['category']}")
                    st.markdown(f"**Employee:** {ticket['employee']}")
                    st.markdown(f"**Created At:** `{ticket['created_at']}`")
                with c_right:
                    p_sources = ', '.join(ticket['policy_sources']) if ticket['policy_sources'] else 'N/A (General IT Guardrail)'
                    st.markdown(f"**Policy Sources:** `{p_sources}`")
                    st.markdown(f"**Routing Notes:** {ticket['notes']}")

                with st.expander("View Full Ticket JSON"):
                    st.json(ticket)

with tab2:
    with st.container(border=True):
        st.subheader("Load Employee Request")
        st.caption("Select any of the 15 benchmark requests to test the service desk triage:")

        def load_selected_request():
            idx = st.session_state.get("selected_req_idx", 0)
            chosen = REQUESTS[idx]
            st.session_state["employee"] = chosen["employee"]
            st.session_state["request_text"] = chosen["request"]
            st.session_state["loaded_req_id"] = chosen["id"]
            st.session_state.pop("last_result", None)
            st.session_state.pop("original_request", None)
            st.session_state.pop("followup_answer", None)

        col_sel, col_btn = st.columns([4, 1], vertical_alignment="bottom")
        with col_sel:
            st.selectbox(
                "Select Request ID to test:",
                range(len(REQUESTS)),
                key="selected_req_idx",
                format_func=lambda i: f"{REQUESTS[i]['id']}: {REQUESTS[i]['employee']} — \"{REQUESTS[i]['request']}\""
            )
        with col_btn:
            st.button("Load into Service Desk", type="primary", use_container_width=True, on_click=load_selected_request)

        if "loaded_req_id" in st.session_state:
            st.success(f"✅ Loaded {st.session_state['loaded_req_id']} into Service Desk! Switch to the '💬 Service Desk' tab to run it.")

    st.subheader("Provided employee requests")
    st.caption("Full list of test employee requests (REQ-01 to REQ-15):")
    st.dataframe(pd.DataFrame(REQUESTS), width="stretch", hide_index=True)

    st.divider()
    st.subheader("Related Existing Tickets")
    st.caption("Historical corporate ticket repository for similarity context (TK-1042 to TK-1051):")
    st.dataframe(pd.DataFrame(TICKETS), width="stretch", hide_index=True)

    st.divider()
    st.subheader("Newly Created Escalation Tickets")
    st.caption("Escalation tickets created and persisted during runtime:")
    if TICKETS_CREATED_FILE.exists():
        try:
            created_data = json.loads(TICKETS_CREATED_FILE.read_text(encoding="utf-8"))
            if created_data:
                st.dataframe(pd.DataFrame(created_data), width="stretch", hide_index=True)
            else:
                st.info("No escalation tickets created yet in this session.")
        except Exception:
            st.info("No escalation tickets created yet in this session.")
    else:
        st.info("No escalation tickets created yet in this session.")

with tab3:
    st.subheader("Knowledge Base / Policies")
    st.caption("Official Veridian corporate policies used for deterministic and AI-guided triage:")
    for p in POLICIES:
        with st.expander(f'{p["id"]} — {p["title"]}'):
            st.markdown("**Policy Content:**")
            st.write(p["text"])

    st.divider()
    st.subheader("Search the policy base")
    q = st.text_input("Policy search", placeholder="Search by topic or keyword (e.g., password, VPN, screen, remote)...")
    if q:
        results = search_policies(q)
        if results:
            for p in results:
                with st.container(border=True):
                    st.write(f'**{p["id"]} — {p["title"]}**')
                    st.write(p["text"])
        else:
            st.info("No matching policy found. The agent should not invent one.")

with tab4:
    st.subheader("Audit trail")
    st.caption("Immutable system log of all agent executions, policy evaluations, and routing decisions:")
    if AUDIT_FILE.exists():
        try:
            events = json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
            if events:
                flattened = []
                for item in events[::-1]:
                    details = item.get("details", {})
                    pol_ids = details.get("policy_ids", [])
                    flattened.append({
                        "Timestamp": item.get("timestamp", "-"),
                        "Event": item.get("event", "-"),
                        "Employee": details.get("employee", "-"),
                        "Decision": details.get("decision", "-"),
                        "Policy IDs": ", ".join(pol_ids) if isinstance(pol_ids, list) else str(pol_ids or "-"),
                        "Created Ticket": details.get("created_ticket_id") or "-",
                        "Details / Response": details.get("response") or details.get("request") or details.get("answer") or str(details)
                    })
                st.dataframe(pd.DataFrame(flattened), width="stretch", hide_index=True)
                with st.expander("View Raw Audit JSON"):
                    st.json(events[::-1])
            else:
                st.info("Audit log is currently empty.")
        except Exception:
            st.info("Audit log is empty or could not be read.")
    else:
        st.info("No actions recorded yet.")
