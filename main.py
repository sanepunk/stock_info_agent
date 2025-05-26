import asyncio  # For async execution
import json       # For JSON serialization/deserialization
import re         # For regex-based parsing
from utils import identify_ticker, get_price, get_price_change, get_news, analyze  # Core subagent functions

from google.adk.agents import LlmAgent   # ADK agent class
from google.adk.runners import Runner     # To run agents
from google.adk.sessions import InMemorySessionService  # In-memory session store
from google.genai import types            # Message types for GenAI
from pydantic import BaseModel, Field     # For input/output schemas
import os                                 # Environment access

# os.environ["GOOGLE_API_KEY"] = "Alsapkpoj"  # Uncomment to set GenAI API key

# --- 1. Define Constants for App & Sessions ---
APP_NAME = "agent_comparison_app"                    # Logical application name
USER_ID = "test_user_456"                            # Unique end-user identifier
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"     # Session ID for tool-based agent
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz" # Session ID for schema-based agent
MODEL_NAME = "gemini-2.0-flash"                     # LLM model name

# --- 2. Input/Output Schemas using Pydantic ---
class StockQueryInput(BaseModel):
    """
    Schema for free-form stock queries.
    - query: e.g. "Why did Tesla drop today?"
    """
    query: str = Field(description="Free-form question about a stock.")

class StockInfoOutput(BaseModel):
    """
    Structured JSON schema for stock info:
    - ticker: symbol
    - current_price: last price
    - change_pct: % change over timeframe
    - timeframe: human-readable label
    - top_headline: top news title
    - analysis: summary analysis
    """
    ticker: str = Field(description="Stock ticker symbol.")
    current_price: float = Field(description="Current stock price.")
    change_pct: float = Field(description="Percentage change over timeframe.")
    timeframe: str = Field(description="Timeframe used for change.")
    top_headline: str = Field(description="Most relevant news headline.")
    analysis: str = Field(description="Summary of why the stock moved.")

# --- 3. Helper Function: Determine Timeframe ---
def extract_days_from_query(q: str):
    """
    Inspect query keywords to choose lookback period:
      - "7 days" or "last week" → 7 days
      - "today", "yesterday" etc. → 1 day
      - default → 1 day
    Returns tuple (days, label).
    """
    ql = q.lower()
    if "7 days" in ql or "last week" in ql:
        return 7, "7 days"
    if "today" in ql or "last day" in ql or "yesterday" in ql:
        return 1, "1 day"
    return 1, "1 day"

# --- 4. Tool Definition: Aggregate Stock Data ---
def get_stock_info(query: str) -> dict:
    """
    Tool that:
      1. Identifies ticker from natural query
      2. Determines timeframe
      3. Fetches price, price change, news, analysis
      4. Returns consolidated result as dict
    """
    print(f"\n-- Tool Call: get_stock_info(query='{query}') --")
    # Identify the stock ticker
    ticker = identify_ticker(query)
    # Parse timeframe from query
    days, label = extract_days_from_query(query)
    # Fetch price and change
    price = get_price(ticker)
    change = get_price_change(ticker, days=days)
    # Fetch recent news
    articles = get_news(ticker, limit=3)
    # Summarize analysis (supports dict or raw string)
    analysis_text = analyze(ticker, days=days)
    if isinstance(analysis_text, dict):
        summary = analysis_text.get("summary") or analysis_text.get("analysis") or ""
    else:
        summary = analysis_text
    # Choose top headline
    headline = articles[0]["title"] if articles else "No recent headlines"
    # Build result
    result = {
        "ticker": ticker,
        "current_price": price,
        "change_pct": round(change, 2),
        "timeframe": label,
        "top_headline": headline,
        "analysis": summary
    }
    print(f"-- Tool Result: {result} --")
    return result

# --- 5. Agent Configurations ---
# 5a. Tool-based agent: calls get_stock_info
stock_agent_with_tool = LlmAgent(
    model=MODEL_NAME,
    name="stock_agent_tool",
    description="Answer free-form stock queries by invoking get_stock_info.",
    instruction="""
You are an agent that receives JSON {"query":"..."}.\
Invoke get_stock_info tool and reply with its JSON output.
""",
    tools=[get_stock_info],            # Plug in our tool
    input_schema=StockQueryInput,     # Expect structured input
    output_key="stock_tool_result",  # Where to store output
    disallow_transfer_to_parent=True,  # No agent transfers
    disallow_transfer_to_peers=True,
)

# 5b. Schema-based agent: pure LLM, no tools
stock_info_agent_schema = LlmAgent(
    model=MODEL_NAME,
    name="stock_info_agent_schema",
    description="Generate structured stock info JSON without external calls.",
    instruction=f"""
You are an agent that receives JSON {{"query":"..."}}.\
Respond ONLY with JSON matching this schema:\
{json.dumps(StockInfoOutput.model_json_schema(), indent=2)}
""",
    input_schema=StockQueryInput,     # Same input wrapper
    output_schema=StockInfoOutput,    # Enforce JSON output format
    output_key="stock_info_result",
    disallow_transfer_to_parent=True,  # No transfers
    disallow_transfer_to_peers=True,
)

# --- 6. Session Service & Runners ---
session_service = InMemorySessionService()  # In-memory session storage
stock_runner = Runner(agent=stock_agent_with_tool, app_name=APP_NAME, session_service=session_service)
structured_runner = Runner(agent=stock_info_agent_schema, app_name=APP_NAME, session_service=session_service)

# --- 7. Interaction Logic ---
async def call_agent(runner, agent, session_id, query):
    """
    Sends a query to the given agent, streams the final response,
    and then prints stored session output.
    """
    print(f"\n>>> Calling {agent.name} | Query: {query}")
    # Wrap raw query into required JSON input
    content = types.Content(role='user', parts=[types.Part(text=json.dumps({"query": query}))])
    # Run agent asynchronously
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"<<< Response: {event.content.parts[0].text}")
    # Retrieve session data
    sess = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    stored = sess.state.get(agent.output_key)
    print(f"--- Stored [{agent.output_key}]:")
    try:
        print(json.dumps(json.loads(stored), indent=2))
    except:
        print(stored)
    print("-" * 40)

# --- 8. Main Entrypoint ---
async def main():
    """
    Runs through example queries demonstrating both agents.
    """
    examples = [
        "Why did Tesla stock drop today?",
        "What's happening with Palantir stock recently?",
        "How has Nvidia stock changed in the last 7 days?"
    ]
    for q in examples:
        # Ensure sessions exist before calling
        await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_TOOL_AGENT)
        await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_SCHEMA_AGENT)
        print("\n=== TOOL-BASED AGENT ===")
        await call_agent(stock_runner, stock_agent_with_tool, SESSION_ID_TOOL_AGENT, q)
        print("\n=== SCHEMA-ONLY AGENT ===")
        await call_agent(structured_runner, stock_info_agent_schema, SESSION_ID_SCHEMA_AGENT, q)

if __name__ == "__main__":
    # Launch the async main function
    asyncio.run(main())
