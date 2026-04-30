import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables safely
load_dotenv()

# Initialize the fast cloud model via Groq API
# This avoids local compute bottlenecks and keeps deployment lightweight
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant", 
    temperature=0.1 # Low temperature ensures analytical, deterministic responses
)

def generate_rca(error_context, retrieved_docs):
    """Fuses logs and docs into a strict prompt for the LLM."""
    
    # The System Prompt 
    system_prompt = """You are an expert Senior DevOps Engineer analyzing system incidents.
    You have been provided with official documentation regarding the system.
    
    OFFICIAL DOCUMENTATION:
    {docs}
    
    Your task is to analyze the user's provided server logs, identify the error, and generate a Root Cause Analysis (RCA).
    If the official documentation addresses the error, you MUST base your solution on it.
    
    Format your response strictly as follows:
    
    **ROOT CAUSE:**
    (A concise 1-2 sentence explanation of why the system failed)
    
    **REMEDIATION PLAN:**
    (Step-by-step actionable fixes)
    """
    
    # Construct the final prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Here is the captured log context ending in the critical error:\n\n{logs}")
    ])
    
    # Create the processing chain
    chain = prompt | llm
    
    # Invoke the cloud API
    response = chain.invoke({
        "docs": retrieved_docs,
        "logs": error_context
    })
    
    return response.content