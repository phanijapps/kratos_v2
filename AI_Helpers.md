I used the below prompt to extract all tools to build my subagents. I ran this perplixity and edited the instructions of each subagent

```markdown
In Alplha Vantage there are number of tools available.. I want you to group tools in a json format
[
{
"category": "core_stock_apis",
"instructions": "Simple subagent instrucations"
[
{
"tool": "TIME_SERIES_INTRADAY",
"Description": "Current and 20+ years of historical intraday OHLCV data"
}
]
}
]
Above is example of one tool in one category. I want a json with array of tools for each category
core_stock_apis
options_data_apis
alpha_intelligence
fundamental_data
forex
cryptocurrencies
commodities
economic_indicators
technical_indicators
https://mcp.alphavantage.co/
```