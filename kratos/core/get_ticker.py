from langchain.agents import create_agent
from pydantic import BaseModel
from langchain.agents.middleware import TodoListMiddleware
from langchain.agents.middleware.summarization import SummarizationMiddleware
from kratos.llm_factory import LLMFactory, ModelProvider
from kratos.tools.search_tools import search_web
from langchain.agents.structured_output import ToolStrategy


model = LLMFactory.get_llm_model(model_provider=ModelProvider.DEEPSEEK) 


SYSTEM_PROMPT = """
You are a fast financial ticker lookup agent. Your ONLY job is to return a Yahoo Finance-compatible ticker symbol for the company or instrument in the user query.

- If you know the ticker instantly from knowledge, return it immediately.
- If unsure or not 100% certain, use the `search_web` tool ONCE with query: 'SITE:finance.yahoo.com "COMPANY_NAME" ticker' (replace COMPANY_NAME with exact user term).
- Parse the first relevant result for the ticker in the format XXXXX.X (e.g., AAPL, BRK-B, TSLA).
- Respond EXCLUSIVELY in this JSON format and NOTHING else:

```json
{
  "ticker": "TICKER_SYMBOL",
  "found": true
}
```

- If not found after search or parsing fails:

```json
{
  "found": false,
  "reason": "not found"
}
```

Rules:
- Never add explanations, greetings, or extra text.
- Be case-insensitive but return ticker in uppercase.
- Support stocks, ETFs, indices, crypto if on Yahoo Finance.
- Timeouts or errors → return `found: false`.
- Maximum 1 tool call per query.
"""


class Ticker(BaseModel):
    ticker: str
    found: bool = True
    reason: str | None = None


ticker_agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[search_web],
    response_format=ToolStrategy(Ticker),
)

def get_ticker(query: str) -> Ticker:
    """Get the ticker symbol for a given company or financial instrument."""
    print("Invoking get ticker")
    result = ticker_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    # What if ticker is not found?
    return result['structured_response']


if __name__ == "__main__":
    query = "adfasdfdasfasdfdsf"
    result = ticker_agent.invoke({
    "messages": [{"role": "user", "content": query}]
    })
    print(f"Ticker Symbol: {result['structured_response']}")