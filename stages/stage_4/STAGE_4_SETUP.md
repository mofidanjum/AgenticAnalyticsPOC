# Stage 4: Build Text-to-SQL Agent

## What is Stage 4?

Building a **text-to-SQL agent** that converts natural language questions into SQL queries using Claude API with tool use.

**Goal**: User asks "What were total sales by region?" → Agent generates SQL → Executes it → Claude answers naturally.

---

## How It Works (Agent Loop)

```
1. User Question
   "What were total sales by region?"
         ↓
2. Agent loads metadata from orders.yaml
   (Claude learns all column descriptions, types, constraints)
         ↓
3. Agent sends to Claude API:
   - System prompt (metadata + instructions)
   - Tool definition: run_sql(query)
   - User question
         ↓
4. Claude thinks and proposes SQL
   "I need to SELECT region, SUM(sales) FROM orders GROUP BY region"
         ↓
5. Your script (agent.py) executes the SQL locally against DuckDB
         ↓
6. SQL Results returned:
   West: $725,457.82
   East: $678,781.24
   Central: $501,239.89
   South: $391,721.91
         ↓
7. Agent sends results back to Claude
         ↓
8. Claude writes natural language answer:
   "West region had highest sales at $725,457.82, followed by East..."
         ↓
9. Answer printed to terminal
```

**Key insight**: Claude never touches DuckDB directly. Your script is the bridge.

---

## Prerequisites

- ✅ Stage 1-3 complete (data downloaded, loaded, metadata created)
- ✅ `.venv` activated with all packages installed
- ✅ Anthropic API key (get from https://console.anthropic.com/)

---

## Script: `analytics/agent.py`

### Structure

```python
# 1. LOAD METADATA
with open("analytics/metadata/orders.yaml") as f:
    metadata = yaml.safe_load(f)
    # Claude will learn all column descriptions

# 2. BUILD SYSTEM PROMPT
SYSTEM_PROMPT = f"""
You are an analytics assistant...
TABLE DESCRIPTION: {metadata['description']}
COLUMNS: {columns_text}
CONSTRAINTS: {notable_values_text}
"""
# This is what Claude "reads" before answering

# 3. DEFINE TOOL
tools = [
    {
        "name": "run_sql",
        "description": "Execute a SQL query",
        "input_schema": {"query": "SQL to execute"}
    }
]
# Claude knows it can call run_sql

# 4. TOOL IMPLEMENTATION
def run_sql(query: str) -> str:
    result = con.sql(query).fetchdf()
    return result.to_string()
# This executes SQL locally against DuckDB

# 5. AGENT LOOP
while True:
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Haiku for cost efficiency
        system=SYSTEM_PROMPT,               # Metadata context
        tools=tools,                        # Tool definition
        messages=messages                   # Conversation history
    )
    
    if response.stop_reason == "tool_use":
        # Claude proposed SQL
        query = extract_sql_from_response(response)
        results = run_sql(query)
        # Send results back to Claude
        messages.append(tool_result)
        continue
    
    else:  # stop_reason == "end_turn"
        # Claude gave final answer
        answer = extract_answer(response)
        print(answer)
        break
```

### Key Components

**1. Metadata Loading**
- Reads `analytics/metadata/orders.yaml`
- Extracts column roles, descriptions, units, constraints
- Formats into readable text for system prompt

**2. System Prompt**
- Tells Claude what table exists (orders)
- Lists all 21 columns with descriptions
- States constraints (profit can be negative, dates are strings, etc.)
- Instructions on how to use the run_sql tool

**3. Tool Definition**
- Defines `run_sql` tool that Claude can call
- Specifies input schema (requires `query` parameter)
- Claude will propose: "Call run_sql with query=SELECT..."

**4. Agent Loop**
- Send question + metadata + tools to Claude
- If Claude calls a tool: execute it, send results back
- If Claude finishes: print answer and exit
- Loop continues until Claude is done

**5. SQL Execution**
- `run_sql()` takes proposed SQL string
- Executes against local DuckDB connection
- Returns results as formatted text
- Handles errors gracefully

---

## Running Stage 4

### Step 1: Get API Key

1. Go to https://console.anthropic.com/
2. Copy your API key (starts with `sk-ant-`)
3. Keep it safe (don't commit to git)

### Step 2: Run Agent

```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline

# Set API key (one-time per session)
$env:ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"

# Run agent
& .venv\Scripts\python.exe analytics/agent.py
```

### Step 3: Ask Questions

```
========================================
Analytics Agent Ready (Haiku)
========================================
Ask questions about the Superstore sales data.
Type 'exit' to quit.

You: What were total sales by region?

📊 User: What were total sales by region?

🔍 SQL: SELECT region, SUM(sales) as total_sales FROM orders GROUP BY region ORDER BY total_sales DESC

📈 Results:
   region  total_sales
0    West   725457.8245
1    East   678781.2400
2 Central   501239.8908
3   South   391721.9050

💬 Answer: Based on the data, here are the total sales by region:

- **West region**: $725,457.82 (highest)
- **East region**: $678,781.24
- **Central region**: $501,239.89
- **South region**: $391,721.91

The West region generated the most sales, followed by the East region.

You: What was average profit by category?

[Agent repeats process...]

You: exit
Bye!
```

---

## Example Questions to Try

**1. Sales analysis**
```
What were total sales by region?
What was average profit by category?
Which product had the highest profit?
```

**2. Trend analysis**
```
How many orders were placed in 2015 vs 2016?
What was the trend of sales over time?
```

**3. Customer segmentation**
```
How many customers are in each segment?
Which segment has the highest average order value?
```

**4. Discount impact**
```
What was the average discount applied?
How does discount affect profit?
```

---

## Why Haiku Model?

**Sonnet**: 
- More powerful
- Slower
- More expensive
- Overkill for SQL generation

**Haiku** (chosen):
- Fast enough for SQL
- 80% cheaper
- Responds in milliseconds
- Perfect for simple queries

**Token usage**:
- Sonnet: ~4,000 tokens per query (metadata + question + SQL)
- Haiku: ~800 tokens per query

---

## Model Options

If Haiku struggles with complex queries, upgrade to:

```python
model="claude-3-5-sonnet-20241022"  # More powerful but slower/expensive
max_tokens=1024  # Increase from 512
```

---

## Error Handling

**API Key not found**
```
Error: ANTHROPIC_API_KEY environment variable not set
```
Fix:
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxx"
```

**SQL Error**
```
🔍 SQL: SELECT invalid_column FROM orders
📈 Results:
SQL Error: Binder Error: column "invalid_column" not found
```
Claude will see this error and retry with a different query.

**DuckDB file not found**
```
Error: Cannot open file "data/processed/superstore.duckdb"
```
Run Stage 2 first: `& .venv\Scripts\python.exe analytics/02_load_duckdb.py`

---

## Key Learning: Tool Use

This stage teaches **tool use pattern**:

1. **Define tool** (what Claude can do)
   ```python
   tools = [{"name": "run_sql", "description": "...", "input_schema": {...}}]
   ```

2. **Claude proposes tool call** (what Claude wants to do)
   ```
   Claude thinks: "I need to call run_sql with: SELECT region, SUM(sales)..."
   ```

3. **You execute tool** (what your code does)
   ```python
   if response.stop_reason == "tool_use":
       query = extract_query(response)
       result = run_sql(query)
   ```

4. **Send results back** (close the loop)
   ```python
   messages.append(tool_result)
   # Continue loop
   ```

5. **Claude gives answer** (final response)
   ```
   Claude reads results and writes natural language answer
   ```

This is the foundation for agentic AI: Claude proposes, you execute, Claude reasons over results.

---

## Next: Stage 5 - Add Charting

Stage 5 will:
1. Keep agent loop intact
2. Add second tool: `render_chart(spec)`
3. Claude proposes both SQL and chart types
4. Agent generates PNG charts
5. Returns both data answer AND visualization

---

## Checklist

✅ Stage 1: Download dataset
✅ Stage 2: Load into DuckDB
✅ Stage 3: Generate and edit metadata
✅ Stage 4: Build text-to-SQL agent ← **YOU ARE HERE**
→ Stage 5: Add charting capability
→ Stage 6: Package as Claude Skill (optional)

