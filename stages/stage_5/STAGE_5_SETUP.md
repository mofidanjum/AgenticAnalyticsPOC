# Stage 5: Add Charting Tool — Detailed Setup

Building on Stage 4, this stage adds visualization capability to the agent using matplotlib.

---

## What You'll Learn

- **Multi-tool agents**: Coordinating multiple tools (SQL + charting)
- **Declarative specs**: Constraining LLM output format for safety
- **Data visualization**: Matplotlib integration with agent loops
- **Tool composition**: Combining tools into workflows

---

## Prerequisites

✅ Stage 0-4 complete:
- Virtual environment at `.venv/` with all dependencies
- DuckDB database at `data/processed/superstore.duckdb`
- Metadata at `analytics/metadata/orders.yaml`
- Agent working with valid API key
- matplotlib already installed (included in base packages)

---

## Architecture: How Stage 5 Works

### Agent Loop (with Charting)

```
User Question
    │
    ├─→ Load metadata from orders.yaml
    │
    ├─→ Send to Claude API with TWO tools:
    │   1. run_sql (existing)
    │   2. render_chart (new)
    │
    ├─→ Claude analyzes question:
    │   • "How did sales change over time?" → needs SQL + chart
    │   • "What is total profit?" → just SQL, no chart
    │
    ├─→ Claude proposes SQL query
    │   └─→ Execute locally against DuckDB
    │   └─→ Results returned to Claude
    │
    ├─→ Claude decides if chart needed
    │   └─→ If yes: calls render_chart with spec
    │   └─→ If no: skips to answer
    │
    ├─→ render_chart tool:
    │   └─→ Takes DataFrame + spec
    │   └─→ Creates matplotlib chart
    │   └─→ Displays in window
    │   └─→ Saves PNG to analytics/output/
    │
    └─→ Claude generates natural language answer
```

### Tool Definitions

**Tool 1: run_sql** (from Stage 4)
```json
{
  "name": "run_sql",
  "description": "Execute a SQL query against the orders table",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "SQL query to execute (SELECT only)"
      }
    },
    "required": ["query"]
  }
}
```

**Tool 2: render_chart** (NEW)
```json
{
  "name": "render_chart",
  "description": "Create a visualization of query results",
  "input_schema": {
    "type": "object",
    "properties": {
      "type": {
        "type": "string",
        "enum": ["line", "bar", "grouped_bar", "histogram"],
        "description": "Chart type"
      },
      "x": {
        "type": "string",
        "description": "Column name for x-axis"
      },
      "y": {
        "type": "string",
        "description": "Column name for y-axis (numeric)"
      },
      "series": {
        "type": "string",
        "description": "Optional: column for grouping/coloring"
      },
      "title": {
        "type": "string",
        "description": "Chart title"
      }
    },
    "required": ["type", "x", "y", "title"]
  }
}
```

---

## Chart Types Guide

### 1. Line Chart (`type: "line"`)

**When to use**: Trends over time

**Example spec**:
```python
{
    "type": "line",
    "x": "Order Date",
    "y": "sales",
    "series": "region",  # Optional: color lines by region
    "title": "Sales Trend by Region Over Time"
}
```

**SQL Claude generates**:
```sql
SELECT "Order Date", region, SUM(sales) as sales
FROM orders
GROUP BY "Order Date", region
ORDER BY "Order Date"
```

**Output**: Multi-colored lines, one per region, showing sales trend

---

### 2. Bar Chart (`type: "bar"`)

**When to use**: Comparing categories

**Example spec**:
```python
{
    "type": "bar",
    "x": "category",
    "y": "total_profit",
    "title": "Total Profit by Category"
}
```

**SQL Claude generates**:
```sql
SELECT category, SUM(profit) as total_profit
FROM orders
GROUP BY category
```

**Output**: Vertical bars, one per category

---

### 3. Grouped Bar Chart (`type: "grouped_bar"`)

**When to use**: Comparing multiple categories together

**Example spec**:
```python
{
    "type": "grouped_bar",
    "x": "region",
    "y": "sales",
    "series": "category",  # Groups bars by category
    "title": "Sales by Region and Category"
}
```

**SQL Claude generates**:
```sql
SELECT region, category, SUM(sales) as sales
FROM orders
GROUP BY region, category
```

**Output**: Grouped bars (3 categories × 4 regions = 12 bars)

---

### 4. Histogram (`type: "histogram"`)

**When to use**: Showing distributions

**Example spec**:
```python
{
    "type": "histogram",
    "x": "profit",  # Not used for histograms
    "y": "profit",  # The column to show distribution of
    "title": "Distribution of Profit Values"
}
```

**SQL Claude generates**:
```sql
SELECT profit
FROM orders
WHERE profit IS NOT NULL
```

**Output**: Bins showing frequency of profit values

---

## Code Structure

### File: `analytics/agent_with_charts.py`

**Section 1: Imports & Setup** (lines 1-20)
```python
import duckdb
import yaml
from anthropic import Anthropic
import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = "data/processed/superstore.duckdb"
con = duckdb.connect(DB_PATH)
OUTPUT_DIR = Path("analytics/output")
OUTPUT_DIR.mkdir(exist_ok=True)
```

**Section 2: Load Metadata** (lines 22-50)
- Reads `orders.yaml`
- Formats columns info for system prompt
- Same as Stage 4

**Section 3: System Prompt** (lines 52-85)
- Includes metadata (from Stage 4)
- NEW: Chart selection guide
- NEW: Instructions on render_chart usage

**Section 4: Tool Definitions** (lines 87-145)
- Tool 1: run_sql (unchanged)
- Tool 2: render_chart (NEW)
  - Specifies chart types via enum
  - Requires x, y, title; series optional

**Section 5: run_sql Function** (lines 147-157)
- Unchanged from Stage 4
- Executes SQL, returns results as string

**Section 6: render_chart Function** (lines 159-228) — NEW
```python
def render_chart(chart_spec: dict, query_data: pd.DataFrame) -> str:
    """Create and save a chart from query results."""
    
    chart_type = chart_spec.get("type")
    x = chart_spec.get("x")
    y = chart_spec.get("y")
    series = chart_spec.get("series")
    title = chart_spec.get("title")
    
    plt.figure(figsize=(10, 6))
    
    if chart_type == "line":
        # Plot lines, one per series value
        if series:
            for s_val in query_data[series].unique():
                subset = query_data[query_data[series] == s_val]
                plt.plot(subset[x], subset[y], marker='o', label=s_val)
            plt.legend()
        else:
            plt.plot(query_data[x], query_data[y], marker='o')
    
    elif chart_type == "bar":
        # Create bar chart
        if series:
            # Pivot for grouped bars
            pivot = query_data.pivot_table(values=y, index=x, columns=series, aggfunc='sum')
            pivot.plot(kind='bar', ax=plt.gca())
        else:
            plt.bar(query_data[x], query_data[y])
    
    # ... etc for other chart types
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chart_{timestamp}.png"
    filepath = OUTPUT_DIR / filename
    
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.show()  # Display in window
    plt.close()
    
    return f"Chart saved: {filepath}"
```

**Key features**:
- Takes DataFrame (from SQL query) + spec
- Creates appropriate chart type
- Displays in matplotlib window
- Saves PNG with timestamp
- Returns filepath as string result

**Section 7: agent_loop Function** (lines 230-290) — ENHANCED
```python
def agent_loop(user_message: str):
    """Run agent with TWO tools: SQL + charting."""
    
    client = Anthropic()
    messages = [{"role": "user", "content": user_message}]
    
    latest_query_data = None  # Store data for charting
    
    while iteration < 5:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            tools=tools,  # Both run_sql AND render_chart
            messages=messages
        )
        
        if response.stop_reason == "tool_use":
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            
            # Process ALL tool uses (multiple SQL + charts possible)
            for tool_use in tool_uses:
                if tool_use.name == "run_sql":
                    # Execute SQL
                    latest_query_data = con.sql(query).fetchdf()
                    result = run_sql(query)
                
                elif tool_use.name == "render_chart":
                    # Create chart using latest query data
                    result = render_chart(chart_spec, latest_query_data)
```

**Key changes**:
- Store `latest_query_data` from SQL queries
- Loop through ALL tool_uses (can have multiple)
- Pass query DataFrame to render_chart
- Process results for each tool

**Section 8: main() Function** (lines 292-315)
- Interactive REPL
- Same as Stage 4
- Just different model name in docstring

---

## Running Stage 5

### Command

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
```

### Example Interactions

**Interaction 1: Simple Chart**
```
You: Show me sales by region

📊 User: Show me sales by region

🔍 SQL: SELECT region, SUM(sales) as total_sales FROM orders GROUP BY region

📊 Chart: Sales by Region
[matplotlib window opens showing bar chart]
Chart saved: analytics/output/chart_20260823_143022.png

💬 Answer: The chart shows sales by region. West leads with $725,457.82, 
followed by East ($678,781.24), Central ($501,239.89), and South ($391,721.91).

You: 
```

**Interaction 2: Trend with Series**
```
You: How did profit change by category over time?

📊 User: How did profit change by category over time?

🔍 SQL: SELECT "Order Date", category, SUM(profit) as profit
        FROM orders
        GROUP BY "Order Date", category
        ORDER BY "Order Date"

📊 Chart: Profit Trend by Category
[matplotlib window opens showing 3 colored lines]
Chart saved: analytics/output/chart_20260823_143023.png

💬 Answer: The chart shows profit trends for each category over the 2015-2016 period.
Technology shows the strongest growth trajectory...

You: 
```

**Interaction 3: Distribution**
```
You: Show me the profit distribution

📊 User: Show me the profit distribution

🔍 SQL: SELECT profit FROM orders WHERE profit IS NOT NULL

📊 Chart: Distribution of Profit Values
[matplotlib window opens showing histogram]
Chart saved: analytics/output/chart_20260823_143024.png

💬 Answer: The histogram shows the distribution of profit values across all line items.
Most profits cluster between $0-500, with a long tail of high-profit items...

You: exit
```

---

## Testing Stage 5

### Test 1: Simple Question (No Chart)

```powershell
& .venv\Scripts\python.exe analytics/agent_with_charts.py
# Type: What is total sales?
# Should see: Just SQL + answer, no chart
```

**Expected output**:
```
🔍 SQL: SELECT SUM(sales) as total_sales FROM orders

📈 Results:
   total_sales
0  2297200.86

💬 Answer: The total sales across all orders is $2,297,200.86.
```

### Test 2: Chart Question

```
# Type: How did sales change over time?
# Should see: SQL + chart window + answer
```

**Expected output**:
```
🔍 SQL: SELECT "Order Date", SUM(sales) as sales 
        FROM orders GROUP BY "Order Date" ORDER BY "Order Date"

📊 Chart: Sales Over Time
Chart saved: analytics/output/chart_20260823_143022.png

💬 Answer: The chart shows sales trends over the 2015-2016 period,
with seasonal peaks in Q4...
```

### Test 3: Grouped Data

```
# Type: Compare profit across regions and categories
# Should see: Grouped bar chart
```

### Test 4: Verify Saved Charts

```powershell
Get-ChildItem analytics/output/ -Filter "chart_*.png" | Sort-Object LastWriteTime -Descending
```

Should show PNG files created during agent runs.

---

## Validation: Using validate_agent.py with Charts

Stage 5 is compatible with `validate_agent.py` from Stage 4.5:

```powershell
& .venv\Scripts\python.exe validate_agent.py
# Type: top 3 categories by profit
# Should see: SQL comparison (chart not validated, only SQL)
```

**Note**: `validate_agent.py` validates SQL correctness, but not chart visual correctness. Charts are validated by:
1. Running the question
2. Visual inspection of chart window
3. Verifying data matches chart

---

## Common Issues & Fixes

### Issue: "Chart not displaying in terminal"

**Cause**: `plt.show()` requires a GUI. In headless environments, it does nothing.

**Solution**: Charts still save to `analytics/output/`. Open them with:
```powershell
Get-ChildItem analytics/output/ -Filter "chart_*.png" -Descending | Select-Object -First 1 | Invoke-Item
```

---

### Issue: "Column 'x' not found in results"

**Cause**: Claude used column name that doesn't match query results.

**Solution**: Metadata should specify exact column names. Update system prompt to include exact names in quotes:
```python
SYSTEM_PROMPT = """
...
5. Quote column names with spaces: "Order Date", "Product Name"
...
"""
```

---

### Issue: "Chart type not recognized"

**Cause**: Claude used chart type not in enum (e.g., "pie" instead of "bar").

**Solution**: System prompt includes chart selection guide. Ensure it covers common use cases:
```
Chart selection:
- Trend over time → type: "line"
- Comparing categories → type: "bar"
- Multiple series comparison → type: "grouped_bar"
- Distribution → type: "histogram"
```

---

### Issue: Chart displays but data looks wrong

**Solution**: Validate using `validate_agent.py`:
```powershell
& .venv\Scripts\python.exe validate_agent.py
# Ask same question
# Compare SQL results with chart
```

---

## Performance Tips

### 1. Limit Query Results for Display

Large DataFrames create busy charts. Claude should use LIMIT:

**Good**:
```sql
SELECT "Order Date", region, SUM(sales)
FROM orders
GROUP BY "Order Date", region
LIMIT 100  ← Limits data points
```

**Bad**:
```sql
SELECT *
FROM orders
-- No limit = 9,994 rows = cluttered chart
```

### 2. Aggregate Before Charting

Raw line items are too granular:

**Good**:
```sql
SELECT "Order Date", SUM(sales) as sales
FROM orders
GROUP BY "Order Date"  ← One point per day
```

**Bad**:
```sql
SELECT "Order Date", sales
FROM orders
-- Every line item = 9,994 points = slow
```

### 3. Use Timestamps for Output

Charts save with timestamps, so multiple runs don't overwrite:

```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"chart_{timestamp}.png"
# Result: chart_20260823_143022.png
```

---

## Next Steps

### Optional Enhancements

1. **Add chart interactivity**: Use Plotly instead of matplotlib
2. **Export data**: Save query results as CSV alongside chart
3. **Add filters**: Let agent filter by date range, region, etc.
4. **Caching**: Store chart specs to avoid recomputing
5. **Styling**: Custom color palettes, themes
6. **Multi-chart**: One question → multiple visualizations

### Moving to Production

- Deploy as web API (FastAPI + agent endpoints)
- Store charts in cloud storage (S3, GCS)
- Add authentication/authorization
- Log all questions, SQL, results for audit trail
- Set up monitoring for agent accuracy

---

## Summary

**Stage 5 adds**:
- ✅ `render_chart` tool for visualizations
- ✅ Multi-tool agent coordination
- ✅ Matplotlib integration
- ✅ Chart spec format (declarative)
- ✅ PNG export with timestamps

**You now have**:
- Text-to-SQL agent (Stage 4)
- Result validation (Stage 4.5)
- Charting agent (Stage 5)
- Complete analytical system!

**Try it**:
```powershell
$env:ANTHROPIC_API_KEY = "your-key"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
# Ask: "How did sales change by region over time?"
# See chart + answer!
```

Good luck! 🚀
