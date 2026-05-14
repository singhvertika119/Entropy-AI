import streamlit as st
import requests
import os

# Configure the page
st.set_page_config(page_title="Entropy AI", page_icon="📡", layout="wide")

# API Configuration (Works locally or in Docker)
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/analyze")
LOG_FILE = "logs/dummy.log"

st.title("📡 Entropy AI")
st.markdown("Real-time log ingestion and AI-powered Root Cause Analysis.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🖥️ Live Server Logs")
    # Read the shared log file
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()
            # Show only the last 20 lines for a clean UI
            log_display = "".join(logs[-20:])
    except FileNotFoundError:
        log_display = "Waiting for logs to be generated..."
        
    st.code(log_display, language="log")

with col2:
    st.subheader("🧠 Manual AI Analysis")
    st.markdown("Paste an error log snippet below to manually trigger the RAG pipeline.")
    
    error_input = st.text_area("Error Line Context:", height=150)
    
    if st.button("Generate Root Cause Analysis", type="primary"):
        if error_input:
            with st.spinner("Querying Vector DB & Cloud LLM..."):
                payload = {
                    "error_line": error_input.split('\n')[-1], # Grab the last line as the trigger
                    "context": error_input
                }
                try:
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        st.success("Analysis Complete!")
                        st.markdown("### 📋 RCA Report")
                        st.info(response.json()["rca_report"])
                    else:
                        st.error(f"API Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
        else:
            st.warning("Please paste an error log first.")