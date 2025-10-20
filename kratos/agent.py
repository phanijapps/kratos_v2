from deepagents import create_deep_agent, SubAgent
from langchain.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


from typing import List
from dotenv import load_dotenv

from kratos.llm_factory import ModelProvider, LLMFactory
from kratos.search_tools import search_news, search_web

import os
import asyncio


from kratos.tools import ALPHA_VANTAGE_SUBAGENTS


def get_financial_tools() -> list[BaseTool]:
    """
    Gets financial tools from local yfinance-based fin_tools module
    """
    from kratos.fin_tools import TOOLS
    return TOOLS


async def get_alphavantage_tools() -> list[BaseTool]:
    """
    Connects to Alpha Vantage MCP server (kept for fallback)
    """
    load_dotenv()

    api_key = os.getenv("ALPHA_VANTAGE_KEY")
    if not api_key:
        raise Exception("No Alpha Vantage Key found")

    client = MultiServerMCPClient({
        "alphavantage": {
            "transport": "streamable_http",
            "url": f"https://mcp.alphavantage.co/mcp?apikey={api_key}"
        }
    })

    return await client.get_tools()

ADDITIONAL_INSTRUCTIONS = """
\nFor Tools that return large, result sets, offload them to memories so that they can be referred. When offloading,
Process the results using subtask and summarize the understanding and also save it to filesystem to save context.
"""

def build_subagents() -> List[SubAgent]:
    subagents = []
    tools = get_financial_tools()
    print("Inside build subagents - using local yfinance tools")
    for sub_agent in ALPHA_VANTAGE_SUBAGENTS:
        sub_agent_tool_names = [tool["tool"] for tool in sub_agent["tools"]]
        subagents.append(
            SubAgent(
                name=sub_agent["category"],
                description=sub_agent["description"],
                system_prompt=sub_agent["system_prompt"] + ADDITIONAL_INSTRUCTIONS,
                tools=[tool for tool in tools if tool.name in sub_agent_tool_names]
            )
        )
    return subagents

STOCK_PICKER_INSTRUCTIONS="""
You are a Stock Picker AI, an expert system for identifying and recommending stocks based on technical analysis, fundamentals, and recent finance news. Use your subagents collaboratively to deliver balanced, data-driven insights for short-term trades (1-7 days) or long-term investments (1+ months).

Core Process:
1. Parse user query: Identify symbol (e.g., AAPL), horizon (short/long/both), and any specifics (e.g., sector, risk tolerance).
2. Delegate tasks:
   - Always start with Data Fetcher for fresh prices, historical data, and validation.
   - Call Search Agent for latest finance news/sentiment on the symbol.
   - Route to Short-Term TA for quick momentum/volatility.
   - Route to Long-Term TA for trends/projections.
   - End with Risk & Signal Generator to synthesize signals, risks (e.g., VaR, stop-loss), and scenarios.
3. Iterate if needed: If confidence <70% or data gaps, refine by calling subagents again.
4. Incorporate news: Weigh sentiment from Search Agent in signals (e.g., positive news boosts buy confidence).
5. Not limited to the above instructions, you get creative and find ways for your customer to make insane amount of money in the market.

Output Format (Markdown Report):
- **Executive Summary**: Overall recommendation (buy/hold/sell) with confidence score.
- **News Highlights**: Key recent finance news from Search Agent (bullet points, with sources).
- **Short-Term View**: Indicators, signal, rationale (table if data-heavy).
- **Long-Term View**: Trends, projection, rationale.
- **Risks & Signals**: Aggregated signal, risk level, stop-loss/target, scenarios (bull/bear/base).
- **Chart Suggestions**: Describe 1-2 charts (e.g., "RSI over 1h with MACD").
- **Prediction**: Predict what calls can be traded for short term and how to make money,
- **Next Steps**: Actionable advice (e.g., "Monitor $150 support level").


Be objective, cite data/news sources inline. Prioritize risk management. Disclaimer: This is not financial advice; always DYOR and consult professionals.
"""

def build_search_subagent() -> SubAgent:
    return SubAgent(
        name="Search Internet",
        description="Used to Search internet for stocks, commodities, currencies related information",
        system_prompt="You are finance information search agent, your job is to search internet and get answers needed for the main agent to complete its task.",
        tools=[search_news,search_web]
    )

def get_fin_graph():
    """
    Factory function that builds and returns the financial deep agent graph.
    """
    model = LLMFactory.get_llm_model(model_provider=ModelProvider.OPENROUTER)
    subagents = build_subagents()
    subagents.append(build_search_subagent())
    return create_deep_agent(
        system_prompt=STOCK_PICKER_INSTRUCTIONS,
        model=model, 
        subagents=subagents, 
        use_longterm_memory=True
    )

graph = get_fin_graph()
