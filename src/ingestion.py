import time
import re
from collections import deque
import os
from ragPipeline import setup_knowledge_base, retrieve_relevant_docs
from llmService import generate_rca

LOG_FILE = "../logs/dummy_app.log"
CONTEXT_WINDOW_SIZE = 20 # How many lines of history to keep

def tail_and_analyze(file_path):
    # Wait for the log file to be created by the dummy app
    while not os.path.exists(file_path):
        print(f"Waiting for {file_path} to be created...")
        time.sleep(1)

    # Initialize a fast, fixed-size rolling window for context
    log_history = deque(maxlen=CONTEXT_WINDOW_SIZE)
    
    # Regex to detect lines containing ERROR, CRITICAL, or FATAL
    error_pattern = re.compile(r"(ERROR|CRITICAL|FATAL|Traceback)")

    print(f"Listening to {file_path} for errors...")

    with open(file_path, "r") as file:
        # Move to the end of the file to only read new logs
        file.seek(0, 2) 
        print(f"Listening to {file_path} for errors...")
    
    # Initialize the DB
    doc_collection = setup_knowledge_base()

    with open(file_path, "r") as file:

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
                trigger_incident(log_history, doc_collection)

# Pass the collection into the function
def trigger_incident(log_history, doc_collection): 
    print("\n" + "="*50)
    print("🚨 INCIDENT DETECTED! Capturing Context...")
    print("="*50)
    
    context_chunk = "\n".join(log_history)
    print(context_chunk)
    print("="*50)
    
    print("\n🧠 Routing context to LLM via Cloud API...")
    
    rca_report = generate_rca(context_chunk, doc_collection)
    
    print("\n" + "█"*50)
    print("📋 ROOT CAUSE ANALYSIS REPORT")
    print("█"*50)
    print(rca_report)
    print("█"*50 + "\n")
 
    time.sleep(2) 

if __name__ == "__main__":
    tail_and_analyze(LOG_FILE)