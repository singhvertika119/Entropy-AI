import time
import re
import os
import requests
from collections import deque

# Configuration
LOG_FILE = "../logs/dummy_app.log"
CONTEXT_WINDOW_SIZE = 20
API_URL = "http://localhost:8000/api/v1/analyze"

def tail_and_analyze(file_path):
    """Continuously tails the log file, maintaining a rolling window of context."""
    # Wait for the log file to be created by the dummy app
    while not os.path.exists(file_path):
        print(f"⏳ Waiting for {file_path} to be created...")
        time.sleep(1)

    # Initialize a fast, fixed-size rolling window for context
    log_history = deque(maxlen=CONTEXT_WINDOW_SIZE)
    
    # Regex to detect lines containing error keywords
    error_pattern = re.compile(r"(ERROR|CRITICAL|FATAL|Traceback)")

    print(f"🎧 Listening to {file_path} for errors...")

    with open(file_path, "r") as file:
        # Move to the end of the file to only read new logs
        file.seek(0, 2) 

        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1) # Briefly sleep if no new lines (prevents CPU spiking)
                continue
            
            # Clean the line and add it to our rolling history
            clean_line = line.strip()
            log_history.append(clean_line)

            # Check if the line contains an error
            if error_pattern.search(clean_line):
                trigger_incident(log_history)

def trigger_incident(history):
    """Fires when an error is detected, packaging the context and sending it to the API."""
    print("\n" + "="*50)
    print("🚨 INCIDENT DETECTED! Sending to API Server...")
    print("="*50)
    
    # Join the deque into a single string of context
    context_chunk = "\n".join(history)
    
    # The actual error is usually the last line in our rolling window
    exact_error_line = history[-1] 
    
    # Package the data into a JSON payload
    payload = {
        "error_line": exact_error_line,
        "context": context_chunk
    }
    
    try:
        # Send a POST request to our FastAPI server
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n" + "█"*50)
            print("📋 ROOT CAUSE ANALYSIS RECEIVED FROM API")
            print("█"*50)
            print(data["rca_report"])
            print("█"*50 + "\n")
        else:
            print(f"⚠️ API Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API Server. Is main.py running on port 8000?")
        
    # Pause slightly to avoid spamming if multiple errors hit at once
    time.sleep(2) 

if __name__ == "__main__":
    tail_and_analyze(LOG_FILE)