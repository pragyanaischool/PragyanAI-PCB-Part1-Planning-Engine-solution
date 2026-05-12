import streamlit as st
import json
import os
from dotenv import load_dotenv
from rich.console import Console

# --- Import Custom Logic ---
from orchestrator import PlanningOrchestrator
from core.schema import ARCH_SCHEMA

# Initialize environment and console
load_dotenv()
console = Console()

# --- Page Configuration ---
st.set_page_config(
    page_title="PragyanAI | The Brain",
    page_icon="🧠",
    layout="wide"
)

# --- Custom CSS for EDA Branding ---
st.markdown("""
    <style>
    .stTextArea textarea { font-family: 'Source Code Pro', monospace; }
    .status-box { padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: System Status ---
with st.sidebar:
    st.image("https://via.placeholder.com/150?text=PragyanAI", width=120)
    st.title("Planning Engine")
    st.markdown("---")
    st.info("LLM: **Llama-3-70b (Groq)**")
    st.info("State Machine: **LangGraph**")
    st.info("Embeddings: **HF all-mpnet-base-v2**")
    
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- Main Interface ---
st.title("🧠 Element 1: Planning & Strategy")
st.markdown("Transform natural language PRDs into validated **architecture_plan.json** files.")

col_in, col_out = st.columns([1, 1])

with col_in:
    st.subheader("📥 Input: Product Requirements (PRD)")
    user_prd = st.text_area(
        "Describe your hardware project in detail:",
        placeholder="e.g., A solar-powered IoT weather station with BME280 sensor, ESP32-S3, and an e-paper display. Must operate at 3.3V.",
        height=300
    )
    
    generate_btn = st.button("Synthesize Architecture 🚀", type="primary", use_container_width=True)

# --- Logic Execution ---
if generate_btn:
    if not user_prd:
        st.warning("Please enter your requirements first.")
    else:
        with st.spinner("Brain Agents are collaborating via Groq..."):
            try:
                # Initialize Orchestrator
                orchestrator = PlanningOrchestrator()
                
                # Execute LangGraph Workflow
                # We pass the PRD and the state machine handles extraction and architecture
                result = orchestrator.run_workflow(user_prd)
                
                st.session_state['final_plan'] = result.get('architecture_plan')
                st.session_state['validation_log'] = result.get('validation_score')
                
                st.success("Synthesis Complete!")
                
            except Exception as e:
                st.error(f"Engine Error: {str(e)}")

# --- Output Section ---
with col_out:
    st.subheader("📤 Output: Architecture Plan")
    
    if 'final_plan' in st.session_state:
        # Display the JSON output
        st.json(st.session_state['final_plan'])
        
        # Validation Badge
        if st.session_state['validation_log'] == 1.0:
            st.write("✅ **Schema Check: PASSED**")
        else:
            st.write("⚠️ **Schema Check: WARNING (Partial Data)**")
            
        # Action Buttons
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            st.download_button(
                label="📥 Download architecture_plan.json",
                data=json.dumps(st.session_state['final_plan'], indent=4),
                file_name="architecture_plan.json",
                mime="application/json",
                use_container_width=True
            )
        
        with c2:
            # Future Bridge to Element 2 (Implementation Core)
            if st.button("🚀 Send to Implementation Core", use_container_width=True):
                st.toast("Hand-off logic initiated...")
    else:
        st.info("Architecture data will appear here after synthesis.")

# --- Footer Logic Visualization ---
st.divider()
with st.expander("🔍 Trace: LangGraph State Transitions"):
    st.markdown("""
    1. **Requirement Extractor (Groq):** Parsed entities from PRD.
    2. **System Architect (Groq):** Mapped entities to Power Tree/MCU.
    3. **Design Critic (jsonschema):** Validated output against PragyanAI standards.
    """)
  
