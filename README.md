# ⚡ Databricks Job Failure Diagnostic Agent

An Agentic AI application designed to act as a senior data engineer. This tool automatically fetches failed Databricks Job logs via the Databricks REST API, diagnoses the root cause using a Retrieval-Augmented Generation (RAG) architecture, and provides a formatted PySpark code fix.

## 🚀 Section 1: About the Project

### **Core Features**
* **Agentic Orchestration:** Utilizes **LangGraph** to build a multi-node reasoning assembly line, passing state context between diagnostic and coding nodes.
* **Live API Integration:** Connects directly to the **Databricks Jobs API** to pull real-time execution traces and error logs from failed Spark jobs.
* **Private RAG Knowledge Base:** Uses **ChromaDB** and local **Hugging Face** embeddings (`all-MiniLM-L6-v2`) to search a private database of known PySpark errors and their verified solutions.
* **Advanced LLM Reasoning:** Powered by **Groq** (Llama-3.3-70b-versatile) for lightning-fast log analysis, context evaluation, and code generation.
* **Interactive Frontend:** Wrapped in a custom-themed **Streamlit** web application with dark/light mode toggles and state-aware memory.

### **Technical Architecture**
1. **API Fetcher Node:** Retrieves raw error traces using a provided Databricks Run ID.
2. **Librarian Node:** Converts the error to mathematical embeddings locally and retrieves the top 3 closest known solutions from ChromaDB.
3. **Diagnoser & Coder Nodes:** Context-chains the raw log and the retrieved solutions to the LLM to generate a plain-English diagnosis and a PySpark code fix.

---

## 🛠️ Section 2: Local Setup & Execution Guide

Follow these instructions to run the application locally on your machine.

### **Prerequisites**
* Python installed on your system
* **uv** installed (the lightning-fast Python project manager). 
* A free **Groq** API Key.
* A **Databricks** Workspace URL and Personal Access Token (PAT).

### **Step 1: Clone the Repository**
Open your terminal and clone this repository to your local machine:

```bash
git clone [https://github.com/YOUR_USERNAME/dbx_job_fix_agent.git](https://github.com/YOUR_USERNAME/dbx_job_fix_agent.git)
cd dbx_job_fix_agent
```

### **Step 2: Set Up Environment Variables**
This project requires secure credentials to function. Create a hidden `.env` file in the root directory:

```bash
touch .env
```

Open the `.env` file in your code editor and add the following keys. **Do not use quotes around the variable names, but do use double quotes around the values.**

```env
GROQ_API_KEY="gsk_your_groq_api_key_here"
MODEL_NAME="llama-3.3-70b-versatile"
DATABRICKS_HOST="[https://dbc-your-workspace.cloud.databricks.com](https://dbc-your-workspace.cloud.databricks.com)"
DATABRICKS_TOKEN="dapi_your_databricks_personal_access_token_here"
HF_HUB_OFFLINE="0"
HF_HUB_DISABLE_TELEMETRY="1"
```

### **Step 3: Build the Local Knowledge Base (First Time Only)**
Before running the app for the first time, you need to generate the local ChromaDB vector database so the RAG pipeline has past solutions to search.

```bash
uv run build_kb.py
```

*(You should see a `chroma_db` folder appear in your project directory after this runs).*

### **Step 4: Launch the Application**
Start the Streamlit web server using `uv`:

```bash
uv run streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`. 

### **Usage**
1. Trigger a failed job in your Databricks workspace.
2. Copy the `Run ID` from the Databricks URL (e.g., `986066794406930`).
3. Paste the Run ID into the Streamlit application and click **Diagnose Run**.