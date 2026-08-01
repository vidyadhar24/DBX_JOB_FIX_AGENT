import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

# 1. Load Secrets
load_dotenv()

# ==========================================
# CONCEPT 1: THE STATE (The Clipboard)
# ==========================================
# We define what variables our clipboard will hold.
class AgentState(TypedDict):
    error_log: str
    diagnosis: str

# ==========================================
# CONCEPT 2: THE NODE (The Worker)
# ==========================================
# This function reads the error_log from the state, asks Groq to fix it, 
# and returns the new diagnosis to update the state.
def diagnose_error(state: AgentState):
    print("--- Node: Diagnosing Error... ---")
    
    # Initialize our LLM just like we did in the test script
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("MODEL_NAME")
    )
    
    # Give the AI its persona and the specific error log
    prompt = f"You are a Databricks expert. Briefly diagnose this PySpark error and explain why it happened:\n\n{state['error_log']}"
    
    # Get the answer from Groq
    response = llm.invoke(prompt)
    
    # Return the new information to be added to our clipboard (State)
    return {"diagnosis": response.content}

# ==========================================
# CONCEPT 3: THE GRAPH (The Conveyor Belt)
# ==========================================
# Initialize the graph and give it our State blueprint
workflow = StateGraph(AgentState)

# Add our worker node to the factory floor
workflow.add_node("diagnose", diagnose_error)

# Define the sequence: START -> diagnose -> END
workflow.add_edge(START, "diagnose")
workflow.add_edge("diagnose", END)

# Compile it into a working application
app = workflow.compile()


# ==========================================
# RUNNING THE APP
# ==========================================
if __name__ == "__main__":
    from fixtures import SPARK_ERRORS
    
    print("Starting the Agentic Workflow against test fixtures...\n")
    
    # We will test the schema mismatch error as our baseline
    test_log = SPARK_ERRORS["schema_mismatch"]
    
    # Pass the chosen fixture into the graph
    result = app.invoke({"error_log": test_log})
    
    print("\n--- Final Diagnosis ---")
    print(result["diagnosis"])