# 🚀 V2.0 Technical Roadmap & Backlog

This document outlines the planned features, architectural upgrades, and UI/UX improvements to elevate this MVP into a flawless, enterprise-grade 10/10 application. 

## 🛠️ Phase 1: Frontend & UX Polish (Immediate Fixes)

These are the user-experience improvements and edge-case handlers to make the Streamlit app more robust.

* **Set Dark Theme as Default:** * *Instruction:* Update the `st.session_state` initialization block at the top of `app.py`. Change `if "theme" not in st.session_state: st.session_state.theme = "Light"` to default to `"Dark"`.
* **Implement Pre-API Input Validation (Regex):**
    * *Instruction:* Prevent unnecessary and costly API calls by validating the user's input before invoking LangGraph. Import the `re` module in `app.py`. Write a regex pattern (e.g., `^\d{15}$`) to ensure the input strictly consists of integers and matches the exact character length of a standard Databricks Run ID. If validation fails, use `st.warning` to halt execution.
* **Smart Error Routing & Banners:**
    * *Instruction:* Currently, API failures (like a 404 or 400 error) are buried in the "Raw Logs" tab while the Diagnosis tab renders empty. Update the Streamlit display logic to check the `state["error_log"]` value *before* rendering the three tabs. If the log starts with "API Request Failed", bypass the tab rendering entirely and display a bold `st.error` banner explaining the specific API issue to the user.
* **Cosmetic UI Overhaul:**
    * *Instruction:* As a final polish, refactor the Streamlit layout. Explore `st.columns` for better screen real estate usage, add custom CSS animations, and refine the color palette integration to make the dashboard look like a modern SaaS product.

---

## 🏗️ Phase 2: Enterprise Architecture (The "10/10" Upgrades)

These upgrades will transition the application from a robust MVP to a highly scalable, FAANG-level production system.

* **Observability and Telemetry:** * *Instruction:* Integrate tools like LangSmith or Datadog to monitor LLM token usage, cost, and execution steps in real-time. This will provide a dashboard to track exactly where the LangGraph assembly line is spending time and if the LLM is hallucinating.
* **Dynamic Knowledge Ingestion:** * *Instruction:* Replace the static `build_kb.py` script with an automated data pipeline. Write a CRON job or Databricks Workflow that periodically scrapes resolved Jira tickets, Slack channels, or Databricks historical logs to automatically update ChromaDB without human intervention.
* **Automated Testing (CI/CD):** * *Instruction:* Production systems require safety nets. Add unit tests using frameworks like `pytest` to validate the LangGraph node. Set up automated GitHub Actions to run these tests every time a new commit is pushed before it deploys to the cloud.
* **Decoupled Architecture:** * *Instruction:* To scale for thousands of users, decouple the frontend from the backend. Expose the LangGraph agent as a secure FastAPI backend. Build a completely separate, high-performance frontend in React or Next.js that communicates with the FastAPI layer via HTTP requests.