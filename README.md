# 🧠 Kratos v2 – LangGraph DeepAgents for Financial Analysis

Kratos v2 packages a LangGraph DeepAgents deployment that specializes in multi-agent financial research. The project combines a configurable LLM factory, a rich suite of financial tooling built on `yfinance`, persistent file management via a FileVault middleware, and explainable code-execution subagents that can extend analyses on demand.


## Prerequisites
- Python 3.11+
- A virtual environment manager (venv, `uv`, or Conda)
- Network access for LLM APIs, Yahoo Finance, and DuckDuckGo Search
- API keys for the model providers you intend to use (see below)

## Installation
```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the repository root and define the credentials you need. The default graph loads `ModelProvider.DEEPSEEK`, so a DeepSeek key is required out of the box.

```
# LLM providers (set the ones you use)
DEEPSEEK_API_KEY=sk-your-key
OPENROUTER_API_KEY=...
OPENAI_API_KEY=...
OLLAMA_API_KEY=...          # only for Ollama Cloud

# Optional observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=kratos-v2
```

Switch providers by editing `LLMFactory.get_llm_model` arguments in `kratos/kai_raja.py` (or by injecting a different provider before instantiating the graph).


## Highlights
- Multi-tier DeepAgents graph (`kratos/kai_raja.py`) with a default DeepSeek model and optional OpenRouter, OpenAI, or Ollama backends.
- Financial subagents with role-specific prompts and tool bundles covering market data, options, fundamentals, macro, crypto, and technical indicators (`kratos/subagents`).
- FileVault-powered filesystem middleware that persists artifacts per session and enables grep/glob/todo workflows (`kratos/core/middleware/vault_middleware.py`).
- Tooling layer that mirrors Alpha Vantage endpoints while sourcing live data through `yfinance`, plus DDGS-powered web/news search and a Python code-execution REPL agent (`kratos/tools`).
- Extensible configuration via `langgraph.json`, enabling local LangGraph CLI development loops.

## Repository Layout
- `kratos/kai_raja.py` – graph factory that stitches the master agent, middleware, tools, and subagents.
- `kratos/core/graph.py` – utilities for constructing DeepAgents graphs with shared middleware.
- `kratos/subagents` – prompt definitions, output-format helpers, and subagent assembly logic.
- `kratos/tools` – financial data handlers, search helpers, and session-aware REPL utilities.
- `kratos/core/middleware` – FileVault middleware providing persistent storage and filesystem tools.
- `tests/` – unit and integration coverage for tools, subagents, and middleware behaviors.## Highlights
- Multi-tier DeepAgents graph (`kratos/kai_raja.py`) with a default DeepSeek model and optional OpenRouter, OpenAI, or Ollama backends.
- Financial subagents with role-specific prompts and tool bundles covering market data, options, fundamentals, macro, crypto, and technical indicators (`kratos/subagents`).
- FileVault-powered filesystem middleware that persists artifacts per session and enables grep/glob/todo workflows (`kratos/core/middleware/vault_middleware.py`).
- Tooling layer that mirrors Alpha Vantage endpoints while sourcing live data through `yfinance`, plus DDGS-powered web/news search and a Python code-execution REPL agent (`kratos/tools`).
- Extensible configuration via `langgraph.json`, enabling local LangGraph CLI development loops.

## Repository Layout
- `kratos/kai_raja.py` – graph factory that stitches the master agent, middleware, tools, and subagents.
- `kratos/core/graph.py` – utilities for constructing DeepAgents graphs with shared middleware.
- `kratos/subagents` – prompt definitions, output-format helpers, and subagent assembly logic.
- `kratos/tools` – financial data handlers, search helpers, and session-aware REPL utilities.
- `kratos/core/middleware` – FileVault middleware providing persistent storage and filesystem tools.
- `tests/` – unit and integration coverage for tools, subagents, and middleware behaviors.

### FileVault Storage
The FileVault middleware stores session artifacts under `.vault/`. The directory is created automatically; you can delete it between runs if you want a clean state. Large tool responses are offloaded there so downstream agents can read them via filesystem tools.

## Running the Agent

### LangGraph CLI (recommended)
```bash
langgraph dev --graph agent_new --import langgraph.json
```
This launches the LangGraph developer UI wired to the `kai` graph defined in `langgraph.json`. You can swap or extend graphs by updating that file.

### Programmatic Usage
```python
import asyncio
from kratos.kai_raja import kai

async def main():
    result = await kai.ainvoke({"input": "Summarize NFLX performance over the last quarter"})
    print(result)

asyncio.run(main())
```

### Customizing Subagents
- Modify `kratos/subagents/agents.py` to add or remove categories.
- Update prompt text and output-format instructions in `kratos/subagents/system_prompts.py`.
- Register new `yfinance`-backed handlers under `kratos/tools/fin_tools/` and ensure they are exported via `kratos/tools/__init__.py`.

## Testing
```bash
pytest
```
Tests cover financial tool handlers, middleware, and integration behaviors for the DeepAgents stack. Add new cases under `tests/` when extending prompts, tools, or middleware.

## Troubleshooting
- **Missing API keys** – ensure the expected environment variables are present; DeepSeek is required unless you change the default provider.
- **Large payload warnings** – responses are intentionally offloaded to `.vault`. Use the filesystem tools (`ls`, `read_file`, `glob_search`, `grep_search`) to retrieve them.
- **LLM mismatches** – check the `LLMFactory` implementation if the selected provider does not support the requested model or parameters.
- **Import errors** – rerun `pip install -r requirements.txt` inside your activated environment.

## Next Steps
- Extend subagent prompts or tools for new research workflows.
- Integrate additional LLM providers in `LLMFactory`.
- Wire LangSmith or custom telemetry for production observability.
