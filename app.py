import os
import streamlit as st
from simple_graph import app as graph_app

# ==========================================
# 1. PAGE CONFIGURATION & STATE
# ==========================================
st.set_page_config(
    page_title="Databricks Job Error Agent",
    page_icon="⚡",
    layout="wide"
)

# Initialize session state variables so it remembers your choices and data
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# ==========================================
# 2. THEME SWITCHER (Top Right)
# ==========================================
# We use columns to push the toggle switch to the far right
col_empty, col_toggle = st.columns([8, 2])
with col_toggle:
    st.write(" ") # Spacer
    is_dark = st.toggle("🌙 Dark Mode", value=(st.session_state.theme == "Dark"))
    
    # Update state and refresh if the toggle is clicked
    if is_dark and st.session_state.theme == "Light":
        st.session_state.theme = "Dark"
        st.rerun()
    elif not is_dark and st.session_state.theme == "Dark":
        st.session_state.theme = "Light"
        st.rerun()

# ==========================================
# 3. CUSTOM THEME (DYNAMIC CSS)
# ==========================================
# Your Palette: ["#8ecae6","#219ebc","#023047","#ffb703","#fb8500"]

if st.session_state.theme == "Light":
    custom_css = """
    <style>
        .stApp { background-color: #f4f7f6; color: #023047; }
        .main-header { background-color: #023047; color: #ffffff; padding: 24px; border-radius: 12px; border-left: 8px solid #fb8500; margin-bottom: 25px; }
        .main-header h1 { color: #8ecae6 !important; margin: 0; font-size: 2.2rem; }
        .main-header p { color: #ffffff; margin-top: 8px; font-size: 1.05rem; }
        
        /* Explicitly set input background and text color */
        div.stTextInput > div > div > input { background-color: #ffffff !important; color: #023047 !important; border: 2px solid #219ebc !important; border-radius: 8px !important; }
        div.stTextInput label { color: #023047 !important; font-weight: bold; }
        
        div.stButton > button { background-color: #fb8500 !important; color: #ffffff !important; font-weight: bold !important; border: none !important; border-radius: 8px !important; padding: 10px 24px !important; transition: 0.3s; }
        div.stButton > button:hover { background-color: #ffb703 !important; color: #023047 !important; }
        
        .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #219ebc; box-shadow: 0px 4px 10px rgba(2, 48, 71, 0.05); margin-bottom: 20px; color: #023047; }
        .result-card-header { color: #219ebc; font-weight: bold; font-size: 1.15rem; border-bottom: 2px solid #8ecae6; padding-bottom: 6px; margin-bottom: 12px; }
        
        /* THE REAL FIX: Targeting Streamlit's new div-based tab structure */
        div[data-testid="stTab"] p { 
            color: #023047 !important; 
        }
        
        div[data-testid="stTab"][aria-selected="true"] p { 
            color: #fb8500 !important; 
            font-weight: bold !important; 
        }
        
        div[data-testid="stTab"]:hover p { 
            color: #219ebc !important; 
        }
        }
    </style>
    """
else:
    custom_css = """
    <style>
        .stApp { background-color: #023047; color: #8ecae6; }
        .main-header { background-color: #219ebc; color: #ffffff; padding: 24px; border-radius: 12px; border-left: 8px solid #ffb703; margin-bottom: 25px; }
        .main-header h1 { color: #ffffff !important; margin: 0; font-size: 2.2rem; }
        .main-header p { color: #8ecae6; margin-top: 8px; font-size: 1.05rem; }
        
        /* FIX: Ensure dark mode inputs are visible */
        div.stTextInput > div > div > input { background-color: #023047 !important; color: #ffffff !important; border: 2px solid #8ecae6 !important; border-radius: 8px !important; }
        div.stTextInput label { color: #8ecae6 !important; font-weight: bold; }
        
        div.stButton > button { background-color: #fb8500 !important; color: #ffffff !important; font-weight: bold !important; border: none !important; border-radius: 8px !important; padding: 10px 24px !important; transition: 0.3s; }
        div.stButton > button:hover { background-color: #ffb703 !important; color: #023047 !important; }
        
        .result-card { background-color: #023047; padding: 20px; border-radius: 10px; border: 1px solid #8ecae6; margin-bottom: 20px; color: #ffffff; }
        .result-card-header { color: #ffb703; font-weight: bold; font-size: 1.15rem; border-bottom: 2px solid #219ebc; padding-bottom: 6px; margin-bottom: 12px; }
        
        /* Ensure tab text is visible in dark mode */
        .stTabs [data-baseweb="tab-list"] button { color: #8ecae6; }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { color: #ffb703; }
    </style>
    """

st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 4. UI HEADER
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>⚡ Databricks Job Failure Diagnostic Agent</h1>
    <p>Automated root-cause diagnosis and code fix generator for Databricks workflows.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. USER INPUT SECTION
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
# 6. EXECUTION & RESULTS DISPLAY
# ==========================================

# 1. Handle the Button Click (The Processing Phase)
if analyze_button:
    if not run_id_input.strip():
        st.warning("⚠️ Please enter a valid Databricks Run ID before proceeding.")
    else:
        with st.spinner("🤖 Agent analyzing run logs and consulting knowledge base..."):
            try:
                # Invoke the LangGraph pipeline
                response = graph_app.invoke({"run_id": run_id_input.strip()})
                
                # Save the response to Streamlit's memory so it survives reruns!
                st.session_state.analysis_result = response
                
            except Exception as e:
                st.error(f"An error occurred while running the agent: {str(e)}")

# 2. Render the Results (The Display Phase)
# We check the memory bank instead of the button state
if st.session_state.analysis_result:
    response = st.session_state.analysis_result
    
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