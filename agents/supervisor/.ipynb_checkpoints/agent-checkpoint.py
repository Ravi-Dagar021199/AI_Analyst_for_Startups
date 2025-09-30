from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent
from google.adk.models.gemini import Gemini
from google.genai import types

# --- 1. Define Placeholder Sub-Agents (The Flow Supervisor's Team) ---
# These are simple BaseAgent instances. Their actual complex logic will be built later.

class DataIngestionAgent(BaseAgent):
    """
    Responsible for reading user files, performing OCR/Transcription, 
    and storing the raw, unified text in the shared state (DB).
    Triggered by: FlowSupervisor
    """
    name: str = "DataIngestionAgent"
    description: str = "Handles multi-file upload and content normalization (OCR/Transcription)."

class ExternalDataAgent(BaseAgent):
    """
    Dedicated to fetching supplementary, real-time data from external sources 
    (e.g., company news, market data) to augment the user's files.
    Triggered by: FlowSupervisor
    """
    name: str = "ExternalDataAgent"
    description: str = "Retrieves and saves relevant external data via API calls."

class DataCurationAgent(BaseAgent):
    """
    Manages the Human-in-the-Loop step. Presents combined data to the user for 
    editing and waits for the final 'Approve & Finalize' signal.
    Triggered by: FlowSupervisor
    """
    name: str = "DataCurationAgent"
    description: str = "Manages user review and final data preparation before analysis."

class AIAnalysisAgent(BaseAgent):
    """
    The final agent. Responsible for performing the complex multimodal analysis 
    using Gemini Pro and generating the structured Investment Memo.
    Triggered by: FlowSupervisor
    """
    name: str = "AIAnalysisAgent"
    description: str = "Generates the final, structured report."


# --- 2. Define the Flow Supervisor (Orchestrator) ---

# The SequentialAgent executes the workers in a strict, defined order.
FLOW_SEQUENCE = SequentialAgent(
    name="FlowSequencePipeline",
    description="Executes the sequential pipeline of Data Ingestion, External Enrichment, Curation, and final Analysis.",
    sub_agents=[
        DataIngestionAgent(),        # Step 1: Process User Files
        ExternalDataAgent(),         # Step 2: Fetch External Data
        DataCurationAgent(),         # Step 3: Human Review/Curation
        AIAnalysisAgent()            # Step 4: Final AI Analysis
    ]
)


# --- 3. Define the Root Orchestrator (Entry Point) ---

# This LlmAgent receives the user's click and delegates the full flow to the SequentialAgent.
GEMINI_MODEL = "gemini-2.5-pro" 

RootOrchestrator = LlmAgent(
    name="RootOrchestrator",
    model=GEMINI_MODEL,
    instruction=f"""You are the central coordinator for the 'AI Startup Analyst Platform'.
    Your primary function is to immediately initiate the sequential workflow defined in the 'FlowSequencePipeline' sub-agent whenever a user submits data.
    
    Delegate the entire task to the 'FlowSequencePipeline' to ensure data is correctly prepared, enriched, and curated before final analysis.
    """,
    sub_agents=[FLOW_SEQUENCE] 
)

# Export the Root Orchestrator as the main agent accessible by the API
root_agent = RootOrchestrator
