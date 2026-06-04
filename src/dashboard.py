import streamlit as st
import requests
import os

st.set_page_config(page_title="System Monitor", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/analyze")
LOG_FILE = "logs/dummy.log"

st.markdown("### System Monitor & Diagnostics")

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("**Log stream**")
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()
            log_display = "".join(logs[-25:])
    except FileNotFoundError:
        log_display = "Waiting for logs to be generated..."

    st.code(log_display, language="bash")

with col2:
    st.markdown("**Manual execution**")
    st.caption("Paste an error log snippet to trigger the RAG pipeline.")

    error_input = st.text_area("Error context", height=150, label_visibility="collapsed")

    if st.button("Run analysis"):
        if error_input:
            with st.spinner("Querying vector DB and LLM..."):
                payload = {
                    "error_line": error_input.split("\n")[-1],
                    "context": error_input,
                }
                try:
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        st.markdown("**RCA report**")
                        st.markdown(response.json()["rca_report"])
                    else:
                        st.error(f"API error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
        else:
            st.warning("Provide error log context before running analysis.")

