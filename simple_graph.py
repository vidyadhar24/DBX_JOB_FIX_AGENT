import os
from dotenv import load_dotenv

# ==========================================
# 0. LOAD SECRETS AND SET RULES FIRST!
# ==========================================
load_dotenv()
# We force these strictly to "1" right here before Hugging Face wakes up
os.environ["HF_HUB_OFFLINE"] = "1" 
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1" # This also stops it from sending usage pings

# ==========================================
# NOW IMPORT EVERYTHING ELSE
# ==========================================
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ==========================================
# 1. THE STATE (Updated Clipboard)
# ==========================================
class AgentState(TypedDict):
    error_log: str
    retrieved_context: str  # <-- NEW: Space for our database notes
    diagnosis: str
    suggested_fix: str

# ==========================================
# 2. THE NODES (The Workers)
# ==========================================

# NEW WORKER: The Librarian
def retrieve_context(state: AgentState):
    print("--- Node 1: Searching Local Knowledge Base... ---")
    
    # 1. Load the same embedding model we used to build the DB
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # 2. Connect to our local Chroma folder
    vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # 3. Search for the top 3 closest mathematical matches (instead of k=1)
    results = vector_store.similarity_search(state['error_log'], k=3)
    
    # If we found matches, join all 3 of their texts together. Otherwise, fallback string.
    if results:
        context = "\n\n---\n\n".join([doc.page_content for doc in results])
    else:
        context = "No matching known errors found in the database."
    
    return {"retrieved_context": context}


# UPDATED WORKER: The Diagnoser
def diagnose_error(state: AgentState):
    print("--- Node 2: Diagnosing Error (with open book)... ---")
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("MODEL_NAME")
    )
    
    # NEW: We now feed the AI both the raw error AND our private database notes
    prompt = f"""You are a Databricks expert. 
    Briefly diagnose this PySpark error and explain why it happened.
    
    USER ERROR:
    {state['error_log']}
    
    KNOWN SOLUTIONS (From our internal database):
    {state['retrieved_context']}
    
    Use the known solutions to heavily guide your diagnosis if they are relevant."""
    
    response = llm.invoke(prompt)
    return {"diagnosis": response.content}


# WORKER 3: The Coder (Unchanged, but benefits from the smarter diagnosis)
def suggest_fix(state: AgentState):
    print("--- Node 3: Generating Code Fix... ---")
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("MODEL_NAME")
    )
    
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

# Add all three workers to the factory floor
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("diagnose", diagnose_error)
workflow.add_node("suggest_fix", suggest_fix)

# Define the new sequence: START -> Librarian -> Diagnoser -> Coder -> END
workflow.add_edge(START, "retrieve_context")
workflow.add_edge("retrieve_context", "diagnose")
workflow.add_edge("diagnose", "suggest_fix")
workflow.add_edge("suggest_fix", END)

app = workflow.compile()

# ==========================================
# RUNNING THE APP
# ==========================================
if __name__ == "__main__":
    from fixtures import SPARK_ERRORS
    
    print("Starting Phase 3 Agentic Workflow (RAG Enabled)...\n")
    
    # We will test against our schema mismatch dummy data
    test_log = SPARK_ERRORS["schema_mismatch"]
    
    # Pass the initial clipboard into the graph
    result = app.invoke({"error_log": test_log})
    
    print("\n--- 1. Retrieved Context (From ChromaDB) ---")
    print(result["retrieved_context"])
    
    print("\n--- 2. Final Diagnosis ---")
    print(result["diagnosis"])
    
    print("\n--- 3. Suggested PySpark Fix ---")
    print(result["suggested_fix"])