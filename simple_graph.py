import os
import requests  # <-- NEW: For our API Fetcher
from dotenv import load_dotenv

# ==========================================
# 0. LOAD SECRETS AND SET RULES FIRST!
# ==========================================
load_dotenv()
os.environ["HF_HUB_OFFLINE"] = "1" 
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1" 

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ==========================================
# 1. THE STATE (Updated Clipboard)
# ==========================================
class AgentState(TypedDict):
    run_id: str        # <-- NEW: We start with the Run ID
    error_log: str     # <-- NEW: The API fetcher will fill this in
    retrieved_context: str
    diagnosis: str
    suggested_fix: str

# ==========================================
# 2. THE NODES (The Workers)
# ==========================================

# NEW WORKER 0: The API Fetcher
# NEW WORKER 0: The Smarter API Fetcher
def fetch_run_logs(state: AgentState):
    print(f"--- Node 0: Fetching real logs for Run ID {state['run_id']}... ---")
    
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    
    # STEP 1: Get the parent job run details to find the failed task
    get_run_url = f"{host}/api/2.1/jobs/runs/get?run_id={state['run_id']}"
    run_response = requests.get(get_run_url, headers=headers)
    
    if run_response.status_code != 200:
        return {"error_log": f"API Request Failed: {run_response.status_code} - {run_response.text}"}
        
    run_data = run_response.json()
    tasks = run_data.get("tasks", [])
    
    # Loop through the tasks to find the one that failed
    target_run_id = state['run_id'] # Default to the parent ID just in case
    for task in tasks:
        if task.get("state", {}).get("result_state") == "FAILED":
            target_run_id = task.get("run_id")
            print(f"Found failed child task! Using Task Run ID: {target_run_id}")
            break
            
    # STEP 2: Fetch the actual output of the failed task
    output_url = f"{host}/api/2.1/jobs/runs/get-output?run_id={target_run_id}"
    out_response = requests.get(output_url, headers=headers)
    
    if out_response.status_code == 200:
        out_data = out_response.json()
        error_log = out_data.get("error", out_data.get("error_trace", "No explicit error trace found."))
    else:
        error_log = f"API Request Failed: {out_response.status_code} - {out_response.text}"
        
    return {"error_log": str(error_log)}


# WORKER 1: The Librarian
def retrieve_context(state: AgentState):
    print("--- Node 1: Searching Local Knowledge Base... ---")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    results = vector_store.similarity_search(state['error_log'], k=3)
    
    if results:
        context = "\n\n---\n\n".join([doc.page_content for doc in results])
    else:
        context = "No matching known errors found in the database."
        
    return {"retrieved_context": context}


# WORKER 2: The Diagnoser
def diagnose_error(state: AgentState):
    print("--- Node 2: Diagnosing Error (with open book)... ---")
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name=os.getenv("MODEL_NAME"))
    
    prompt = f"""You are a Databricks expert. 
    Briefly diagnose this PySpark error and explain why it happened.
    
    USER ERROR:
    {state['error_log']}
    
    KNOWN SOLUTIONS (From our internal database):
    {state['retrieved_context']}
    
    Use the known solutions to heavily guide your diagnosis if they are relevant."""
    
    response = llm.invoke(prompt)
    return {"diagnosis": response.content}


# WORKER 3: The Coder
def suggest_fix(state: AgentState):
    print("--- Node 3: Generating Code Fix... ---")
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name=os.getenv("MODEL_NAME"))
    
    prompt = f"""You are a Databricks expert. 
    Here is a PySpark error: {state['error_log']}
    Here is the diagnosis: {state['diagnosis']}
    
    Provide a concrete PySpark code fix for this issue. Format your answer as a clear code snippet. Do not include a lengthy explanation, just the code and a brief comment."""
    
    response = llm.invoke(prompt)
    return {"suggested_fix": response.content}

# NEW DECISION MAKER: The Traffic Cop
def route_after_fetch(state: AgentState) -> str:
    # Check if the API fetcher threw an error
    if state["error_log"].startswith("API Request Failed"):
        print("--- ROUTING: API Failed. Bypassing LLM nodes. ---")
        return "end_early"
    
    # Otherwise, continue down the assembly line
    print("--- ROUTING: Log successfully fetched. Proceeding to process further. ---")
    return "continue_to_rag"


# ==========================================
# 3. THE GRAPH (Updated Conveyor Belt)
# ==========================================
workflow = StateGraph(AgentState)

# Add all four workers to the factory floor
workflow.add_node("fetch_run_logs", fetch_run_logs)
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("diagnose", diagnose_error)
workflow.add_node("suggest_fix", suggest_fix)

# Define the new sequence: START -> Fetcher -> Librarian -> Diagnoser -> Coder -> END
workflow.add_edge(START, "fetch_run_logs")

workflow.add_conditional_edges(
    "fetch_run_logs",   # The node we are coming from
    route_after_fetch,  # The traffic cop function we just built
    {
        "continue_to_rag": "retrieve_context", # If successful, go to Node 1
        "end_early": END                       # If failed, skip to END
    }
)

workflow.add_edge("retrieve_context", "diagnose")
workflow.add_edge("diagnose", "suggest_fix")
workflow.add_edge("suggest_fix", END)

app = workflow.compile()

# ==========================================
# RUNNING THE APP
# ==========================================
if __name__ == "__main__":
    print("Starting Phase 4 Agentic Workflow (Live API Enabled)...\n")
    
    # We pass the real Run ID into the graph
    result = app.invoke({"run_id": "986066794406930"})
    
    print("\n=== RAW ERROR LOG (Fetched from Databricks API) ===")
    print(result["error_log"])
    
    print("\n=== FINAL DIAGNOSIS ===")
    print(result["diagnosis"])
    
    print("\n=== SUGGESTED PYSPARK FIX ===")
    print(result["suggested_fix"])