# Common API Reference

## Error Handling

All functions return structured error responses:

```json
{
  "tool": "FUNCTION_NAME",
  "symbol": "AAPL",
  "error": "error_type",
  "message": "Human readable error message",
  "suggestion": "Suggested action to resolve"
}
```

Common error types:
- `data_unavailable`: No data for symbol/period
- `insufficient_data`: Not enough data for calculation
- `rate_limit`: API rate limit exceeded
- `invalid_symbol`: Symbol not found

## Chart Integration

Charts are returned as figure objects:
- **Plotly**: `plotly.graph_objects.Figure` (default)
- **Matplotlib**: `matplotlib.figure.Figure`

Access charts from response:
```python
result = fl.get_historical_data("AAPL", include_chart=True)
if "chart" in result:
    chart = result["chart"]
    chart.show()  # For Plotly
    # chart.savefig("chart.png")  # For Matplotlib
```

## Sample Output Snapshot

All example payloads across the docs were captured on 2025-11-08 and saved (trimmed) to `fin_lib/docs/api/sample_outputs.json`. Each API page references that file when showing abbreviated JSON responses.

## Performance Notes

- **Caching**: All data is cached with TTL (60-1800 seconds)
- **Rate Limits**: Respects yfinance rate limits
- **Memory**: Large datasets automatically serialized
- **Concurrency**: Thread-safe caching implementation

## Dependencies

- `yfinance`: Market data
- `pandas-ta`: Technical indicators
- `plotly`: Interactive charts
- `matplotlib`: Static charts
- `pandas`, `numpy`: Data processing
