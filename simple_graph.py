import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

load_dotenv()

# ==========================================
# 1. THE STATE (Updated Clipboard)
# ==========================================
class AgentState(TypedDict):
    error_log: str
    diagnosis: str
    suggested_fix: str  # <-- NEW: We made room for the code fix!

# ==========================================
# 2. THE NODES (The Workers)
# ==========================================
def diagnose_error(state: AgentState):
    print("--- Node 1: Diagnosing Error... ---")
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("MODEL_NAME")
    )
    prompt = f"You are a Databricks expert. Briefly diagnose this PySpark error and explain why it happened:\n\n{state['error_log']}"
    
    response = llm.invoke(prompt)
    return {"diagnosis": response.content}


# NEW: The Code Fix Node
def suggest_fix(state: AgentState):
    print("--- Node 2: Generating Code Fix... ---")
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("MODEL_NAME")
    )
    
    # We pass both the original error AND the diagnosis to ground the AI's fix
    prompt = f"""You are a Databricks expert. 
    Here is a PySpark error: {state['error_log']}
    Here is the diagnosis: {state['diagnosis']}
    
    Provide a concrete PySpark code fix for this issue. Format your answer as a clear code snippet. Do not include a lengthy explanation, just the code and a brief comment."""
    
    response = llm.invoke(prompt)
    return {"suggested_fix": response.content}

# ==========================================
# 3. THE GRAPH (Updated Conveyor Belt)
# ==========================================
workflow = StateGraph(AgentState)

# Add both workers to the factory floor
workflow.add_node("diagnose", diagnose_error)
workflow.add_node("suggest_fix", suggest_fix)

# Define the sequence: START -> Node 1 -> Node 2 -> END
workflow.add_edge(START, "diagnose")
workflow.add_edge("diagnose", "suggest_fix")  # <-- NEW: Passing the baton from Node 1 to Node 2
workflow.add_edge("suggest_fix", END)

app = workflow.compile()

# ==========================================
# RUNNING THE APP
# ==========================================
if __name__ == "__main__":
    from fixtures import SPARK_ERRORS
    
    print("Starting Phase 2 Agentic Workflow...\n")
    
    # Testing against our schema mismatch dummy data
    test_log = SPARK_ERRORS["schema_mismatch"]
    
    # Pass the initial clipboard into the graph
    result = app.invoke({"error_log": test_log})
    
    print("\n--- Final Diagnosis ---")
    print(result["diagnosis"])
    
    print("\n--- Suggested PySpark Fix ---")
    print(result["suggested_fix"])