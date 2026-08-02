import os
import streamlit as st
from simple_graph import app as graph_app

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM THEME (CSS)
# ==========================================
st.set_page_config(
    page_title="Databricks Job Error Agent",
    page_icon="⚡",
    layout="wide"
)

# Inject custom CSS using your brand palette
st.markdown("""
<style>
    /* Main app background and font settings */
    .stApp {
        background-color: #f4f7f6;
        color: #023047;
    }
    
    /* Header Container */
    .main-header {
        background-color: #023047;
        color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border-left: 8px solid #fb8500;
        margin-bottom: 25px;
    }
    
    .main-header h1 {
        color: #8ecae6 !important;
        margin: 0;
        font-size: 2.2rem;
    }
    
    .main-header p {
        color: #ffffff;
        margin-top: 8px;
        font-size: 1.05rem;
    }

    /* Custom Input Box styling */
    div.stTextInput > div > div > input {
        border: 2px solid #219ebc !important;
        border-radius: 8px !important;
        color: #023047 !important;
    }

    /* Primary Action Button (#fb8500) */
    div.stButton > button {
        background-color: #fb8500 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-size: 1rem !important;
        transition: background-color 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #ffb703 !important;
        color: #023047 !important;
    }

    /* Result Card Containers */
    .result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #219ebc;
        box-shadow: 0px 4px 10px rgba(2, 48, 71, 0.05);
        margin-bottom: 20px;
    }

    .result-card-header {
        color: #219ebc;
        font-weight: bold;
        font-size: 1.15rem;
        border-bottom: 2px solid #8ecae6;
        padding-bottom: 6px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. UI HEADER
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>⚡ Databricks Job Failure Diagnostic Agent</h1>
    <p>Automated root-cause diagnosis and code fix generator for Databricks workflows.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. USER INPUT SECTION
# ==========================================
col1, col2 = st.columns([3, 1])

with col1:
    run_id_input = st.text_input(
        "Enter Databricks Job Run ID:",
        placeholder="e.g., 986066794406930",
        help="Copy the run ID from the end of the Databricks workflow URL."
    )

with col2:
    st.write(" ") # Alignment spacer
    st.write(" ")
    analyze_button = st.button("🔍 Diagnose Run")

# ==========================================
# 4. EXECUTION & RESULTS DISPLAY
# ==========================================
if analyze_button:
    if not run_id_input.strip():
        st.warning("⚠️ Please enter a valid Databricks Run ID before proceeding.")
    else:
        with st.spinner("🤖 Agent analyzing run logs and consulting knowledge base..."):
            try:
                # Invoke the LangGraph pipeline
                response = graph_app.invoke({"run_id": run_id_input.strip()})
                
                st.success("Analysis Complete!")
                
                # Tabbed view for clear information hierarchy
                tab1, tab2, tab3 = st.tabs(["💡 Diagnosis & Fix", "📖 Retrieved Context", "📄 Raw Logs"])
                
                with tab1:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="result-card-header">Root Cause Diagnosis</div>', unsafe_allow_html=True)
                    st.write(response.get("diagnosis", "No diagnosis generated."))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="result-card-header">Recommended PySpark Fix</div>', unsafe_allow_html=True)
                    st.code(response.get("suggested_fix", "# No code fix available"), language="python")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with tab2:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="result-card-header">Matched Solution from Internal Knowledge Base</div>', unsafe_allow_html=True)
                    st.write(response.get("retrieved_context", "No context retrieved."))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with tab3:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="result-card-header">Raw Databricks Execution Trace</div>', unsafe_allow_html=True)
                    st.code(response.get("error_log", "No log available"), language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"An error occurred while running the agent: {str(e)}")