# Agentic Analytics POC — Step-by-Step Guide

A Claude-powered agent that answers natural-language questions over Superstore sales data with visualizations.

---

## 🎯 Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Virtual environment at `.venv/` (with dependencies installed)
- Anthropic API key with $5+ credit balance

### Run the agent with charts
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
```

Ask questions like:
```
How did sales change over time by region?
top 5 customers by sales
Which category is most profitable?
```

Charts display inline + save to `analytics/output/`

---

## 📚 Complete Stage Breakdown

### **Stage 0B: Dynamic Dataset Selection (Optional)**

**What it does**: Instead of hardcoding Superstore data, let Claude suggest Kaggle datasets based on what you want to analyze.

**How it works**:
1. Describe what you want: "I want e-commerce data"
2. Claude suggests matching datasets
3. Script downloads automatically
4. Auto-generates schema + metadata
5. Ready to query!

**Command**:
```powershell
& .venv\Scripts\python.exe analytics/dynamic_dataset_selector.py
```

**Example**:
```
Enter dataset key (or describe what you want): I want to analyze e-commerce sales

🤔 Let Claude suggest a dataset for: 'I want to analyze e-commerce sales'
💡 Claude suggests: ecommerce

✅ Selected: ecommerce
   Brazilian e-commerce, 100K+ orders

📥 Downloading ecommerce...
✅ Downloaded to data/raw/
✅ Created table 'ecommerce' with 100,000 rows
✅ Metadata saved to analytics/metadata/ecommerce.yaml

✅ Setup Complete!
Database: data/processed/dynamic.duckdb
Table: ecommerce
```

**See**: [STAGE_0B_DYNAMIC_DATASETS.md](STAGE_0B_DYNAMIC_DATASETS.md) for details.

---

### **Stage 1: Download Dataset from Kaggle**

**What it does**: Downloads Superstore sales data (9,994 rows) from Kaggle and creates a sample fixture for testing.

**Why**: You need raw data to analyze. This stage handles authentication with Kaggle and creates a local CSV file.

**How it works**:
1. Reads Kaggle API credentials from `~/.kaggle/kaggle.json`
2. Downloads `vivek468/superstore-dataset-final` dataset
3. Saves full dataset to `data/raw/Sample - Superstore.csv` (~2.3 MB)
4. Creates sample fixture: `data/sample/superstore_sample.csv` (first 200 rows for testing)

**Command**:
```powershell
& .venv\Scripts\python.exe analytics/01_download_dataset.py
```

**What you should see**:
```
✓ Download complete
✓ Sample created
data/raw/Sample - Superstore.csv  2.3 MB
data/sample/superstore_sample.csv 0.6 MB
```

**Test it**:
```powershell
Get-ChildItem data/raw, data/sample
```

**Key concept**: **Data Ingestion** — Bringing external data into your local system

---

### **Stage 2: Load Data into DuckDB**

**What it does**: Converts the CSV into a queryable DuckDB database (single-file SQL engine).

**Why**: SQL queries are way faster than scanning CSV files. DuckDB gives you SQL power locally without needing a server.

**How it works**:
1. Reads `data/raw/Sample - Superstore.csv` with `latin-1` encoding (handles special chars)
2. Creates DuckDB database at `data/processed/superstore.duckdb`
3. Loads all 9,994 rows into table `orders`
4. Validates schema (21 columns)

**Command**:
```powershell
& .venv\Scripts\python.exe analytics/02_load_duckdb.py
```

**What you should see**:
```
✓ Database created
✓ 9,994 rows loaded
✓ Schema verified
```

**Test it**:
```powershell
& .venv\Scripts\python.exe -c "
import duckdb
con = duckdb.connect('data/processed/superstore.duckdb')
result = con.sql('SELECT COUNT(*) FROM orders').fetchall()
print(f'✓ {result[0][0]} rows')
"
```

Or use interactive SQL:
```powershell
& .venv\Scripts\python.exe sql_shell.py
# Then type: SELECT COUNT(*) FROM orders
```

**Key columns** (21 total):
- `Order ID`, `Order Date`, `Ship Date` — temporal
- `Customer Name`, `Customer ID` — customer info
- `Sales`, `Profit`, `Discount` — financial
- `Region`, `Category`, `Sub-Category` — dimensions
- `Quantity` — count

**Key concept**: **Data Storage** — Organizing data for efficient querying

---

### **Stage 3: Generate Metadata Layer**

**What it does**: Creates YAML descriptions of table structure and column semantics for the LLM to understand.

**Why**: Claude needs to know what columns mean, not just their types. Without metadata, it can't write good SQL.

**How it works**:

**Step 1: Auto-generate draft**
```powershell
& .venv\Scripts\python.exe analytics/03_generate_metadata_draft.py
```

This creates `analytics/metadata/orders.yaml` with:
- Column names, types, distinct counts
- Inferred roles (id, dimension, measure, timestamp)
- Min/max values for numeric columns

**Step 2: Hand-edit for business meaning** (✅ Already done)

File: `analytics/metadata/orders.yaml`

Example entries:
```yaml
table: orders
description: >
  One row per line item in a retail order.
  Data covers US retail sales 2015-2016. 9,994 rows.

columns:
  sales:
    type: DOUBLE
    role: measure
    unit: usd
    description: Revenue for this line item (in USD)
  
  profit:
    type: DOUBLE
    role: measure
    unit: usd
    description: Profit after discount and costs (can be negative)
  
  region:
    type: VARCHAR
    role: dimension
    description: US region; one of East, West, Central, or South

notable_values:
  - "profit can be negative — don't assume SUM(profit) > 0"
  - "dates are VARCHAR strings (MM/DD/YYYY), not DATE type"
  - "all orders are US-based"
```

**Test it**:
```powershell
& .venv\Scripts\python.exe -c "
import yaml
with open('analytics/metadata/orders.yaml') as f:
    meta = yaml.safe_load(f)
print(f'✓ {len(meta[\"columns\"])} columns defined')
"
```

**Key concept**: **Semantic Layer** — Teaching the LLM what your data means

---

### **Stage 4: Build Text-to-SQL Agent**

**What it does**: Creates an agent that converts natural language questions → SQL → results → natural language answers.

**Why**: This is the core intelligence layer. Claude reads your question, understands your metadata, and generates accurate SQL.

**How it works**:

```
User Question
    ↓
Load metadata from YAML
    ↓
Send to Claude API (Haiku model)
    ↓
Claude proposes SQL query
    ↓
Execute SQL locally against DuckDB
    ↓
Send results back to Claude
    ↓
Claude generates natural language answer
```

**Agent loop** (from `analytics/agent.py`):
```python
while True:
    # 1. Send question + metadata to Claude
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        tools=[{"name": "run_sql", ...}],
        messages=messages
    )
    
    # 2. Claude proposes SQL (tool use)
    if response.stop_reason == "tool_use":
        sql_query = tool_use.input["query"]
        
        # 3. Execute locally
        results = run_sql(sql_query)
        
        # 4. Send results back
        messages.append({"role": "user", "content": results})
        continue
    
    # 5. Claude gives final answer
    answer = response.content[0].text
    print(answer)
    break
```

**Command**:
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
& .venv\Scripts\python.exe analytics/agent.py
```

**Example interaction**:
```
========================================
Analytics Agent Ready (Haiku 4.5)
========================================

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
- West region leads with $725,457.82
- East region: $678,781.24
- Central region: $501,239.89
- South region: $391,721.91

You: exit
```

**Why Haiku model?**
- 80% cheaper than Sonnet (~$0.80/1M tokens)
- Fast enough for SQL generation
- Perfect for this use case
- $5 credit = 12,500+ test queries

**Test it**:
```powershell
& .venv\Scripts\python.exe analytics/agent.py
# Type: total sales by category
# Type: exit
```

**Key concept**: **Tool Use** — Claude proposes function calls, your code executes them

---

### **Stage 4.5: Validate Agent Results**

**What it does**: Compares agent's SQL + results with direct SQL execution to verify correctness.

**Why**: You need to know if Claude's answers are actually correct before trusting the agent.

**How it works**:
1. Run agent with your question
2. Capture SQL that Claude generated
3. Execute same SQL directly against DuckDB
4. Compare results: ✓ MATCH or ✗ MISMATCH

**Command**:
```powershell
& .venv\Scripts\python.exe validate_agent.py
```

**Example interaction**:
```
Ask a question: top 5 customers by sales

🔍 Question: top 5 customers by sales

📝 Generated SQL:
SELECT "Customer Name", SUM(sales) as total_sales 
FROM orders 
GROUP BY "Customer Name" 
ORDER BY total_sales DESC 
LIMIT 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ COMPARISON RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ MATCH: Agent results match direct SQL execution!

Results:
     Customer Name  total_sales
0  William Brown   $28,525.92
1  Tamara Chand    $24,187.19
...
```

**Test workflow**:
1. Ask a simple question you know the answer to
2. Check if results match
3. If MATCH → Claude is working correctly
4. If MISMATCH → Check Claude's SQL for errors

**Key concept**: **Validation** — Verifying LLM outputs against ground truth

---

### **Stage 5: Add Charting**

**What it does**: Extends the agent with a `render_chart` tool to create visualizations alongside SQL queries.

**Why**: A chart is worth 1000 words. Visualizations help understand trends, comparisons, and distributions better than raw numbers.

**How it works**:
```
User Question
    ↓
Agent runs SQL (as before)
    ↓
Agent decides if chart needed (trend? comparison? distribution?)
    ↓
Agent calls render_chart tool with spec:
   {
     "type": "line",  # or bar, grouped_bar, histogram
     "x": "Order Date",
     "y": "sales",
     "series": "region",
     "title": "Sales Trend by Region"
   }
    ↓
Matplotlib creates PNG
    ↓
Chart displays + saves to analytics/output/
    ↓
Agent gives natural language answer
```

**Chart types Claude can choose**:
- **line**: Trends over time (e.g., sales by month)
- **bar**: Category comparisons (e.g., sales by region)
- **grouped_bar**: Multiple series comparison (e.g., sales by region by category)
- **histogram**: Distributions (e.g., profit distribution)

**Command**:
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
```

**Example interaction**:
```
You: How did sales change over time by region?

📊 User: How did sales change over time by region?

🔍 SQL: SELECT "Order Date", region, SUM(sales) as sales 
FROM orders 
GROUP BY "Order Date", region 
ORDER BY "Order Date"

📊 Chart: Sales Trend by Region
[Chart displays in matplotlib window]
Chart saved: analytics/output/chart_20260823_143022.png

💬 Answer: The chart shows sales trends by region over time:
- West region shows strongest growth trajectory
- Central region remained relatively stable
- East and South regions show seasonal fluctuations
```

**Test it**:
```powershell
& .venv\Scripts\python.exe analytics/agent_with_charts.py
# Type: How did sales change over time?
# Type: What is the profit distribution by category?
# Type: exit
```

**Check saved charts**:
```powershell
Get-ChildItem analytics/output/ | Sort-Object LastWriteTime -Descending
```

**Key concept**: **Data Visualization** — Multi-tool agents coordinating SQL + charting

---

## 🧪 Testing Workflows

### **Test 1: Verify Data Loaded Correctly**

```powershell
# Check file exists
Get-ChildItem data/processed/superstore.duckdb

# Check row count
& .venv\Scripts\python.exe -c "
import duckdb
con = duckdb.connect('data/processed/superstore.duckdb')
print(con.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0])
"
# Should print: 9994
```

### **Test 2: Manual SQL Query**

```powershell
& .venv\Scripts\python.exe sql_shell.py
```

Then type:
```sql
-- See all columns
PRAGMA table_info(orders);

-- Total sales by region
SELECT region, SUM(sales) as total_sales FROM orders GROUP BY region;

-- Top 5 categories by count
SELECT category, COUNT(*) FROM orders GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5;

-- Profit statistics
SELECT category, AVG(profit) as avg_profit, MIN(profit), MAX(profit) FROM orders GROUP BY category;
```

### **Test 3: Agent with Simple Question**

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
& .venv\Scripts\python.exe analytics/agent.py
# Type: How many total orders?
# Should see: ~2572 unique Order IDs
```

### **Test 4: Agent Validation**

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
& .venv\Scripts\python.exe validate_agent.py
# Type: top 3 categories by sales
# Should see: ✓ MATCH
```

### **Test 5: Agent with Charting**

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
# Type: Show me sales by category
# Should see chart + answer
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ User (Voice/Chat)                                       │
│ "How did sales change by region?"                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│ Stage 4/5: Agent Loop (Claude API)                      │
│ - Reads user question                                  │
│ - Loads metadata from orders.yaml                       │
│ - Decides: SQL needed? Chart needed?                    │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
             ↓ (if SQL)                 ↓ (if Chart)
   ┌─────────────────────┐    ┌──────────────────────────┐
   │ run_sql tool        │    │ render_chart tool        │
   │ SELECT region, SUM  │    │ type: line               │
   │ FROM orders ...     │    │ x: Order Date            │
   └────────┬────────────┘    │ y: sales                 │
            │                  │ series: region          │
            ↓                  └──────────┬──────────────┘
   ┌─────────────────────┐              │
   │ Stage 2: DuckDB     │              ↓
   │ superstore.duckdb   │    ┌──────────────────────────┐
   │ 9,994 rows          │    │ Matplotlib               │
   └─────────────────────┘    │ Creates PNG chart        │
            │                  │ Saves to analytics/output│
            ↓                  └──────────┬──────────────┘
   ┌─────────────────────┐              │
   │ Results DataFrame   │              ↓
   │ region | total_sales│    ┌──────────────────────────┐
   │ West   | 725457.82  │    │ Chart PNG File           │
   │ East   | 678781.24  │    │ chart_20260823_143022.png
   │ ...                 │    └──────────────────────────┘
   └────────┬────────────┘
            │
            └──────────────────┬─────────────────────────┘
                               │
                               ↓
                   ┌──────────────────────────┐
                   │ Claude generates answer  │
                   │ "West region leads with  │
                   │  $725k in sales..."      │
                   └──────────────────────────┘
```

---

## 📊 Data Model

**Table**: `orders` (9,994 rows)

**Grain**: Order-line (one row per product in order, so multi-item orders have multiple rows with same Order ID)

**Key columns**:
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| Order ID | VARCHAR | "CA-2016-152156" | Not unique per row |
| Order Date | VARCHAR | "11/8/2016" | String, not DATE |
| Customer Name | VARCHAR | "Aaron Bergman" | Full name |
| Sales | DOUBLE | 262.966 | Revenue (USD) |
| Profit | DOUBLE | 41.957 | Can be negative |
| Discount | DOUBLE | 0.0 | Fraction (0.0 = no discount) |
| Region | VARCHAR | "West" | East, West, Central, South |
| Category | VARCHAR | "Technology" | Furniture, Office Supplies, Technology |
| Quantity | BIGINT | 2 | Units ordered |

**Constraints**:
- All orders are US-based
- Date range: 2015-2016
- Profit can be negative (returns, deep discounts)
- Dates stored as VARCHAR strings, not DATE type

---

## 🔐 API Key Setup

### Get API Key
1. Go to https://console.anthropic.com/
2. Click "API keys" → "Create new key"
3. Copy the key (starts with `sk-ant-`)

### Add Credit
1. Go to https://console.anthropic.com/account/billing/overview
2. Click "Add to credit balance"
3. Add $5 (minimum for testing, enough for ~12,500 queries)

### Set Environment Variable (PowerShell)
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
```

To make it permanent for your session:
```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-your-key", "User")
```

---

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'duckdb'` | Activate venv: `& .venv\Scripts\Activate.ps1` |
| `Referenced column "column_name" not found` | Use exact column names with spaces in quotes: `"Order Date"` |
| `Error code: 404 - model not found` | Update model name in agent scripts to latest: `claude-haiku-4-5-20251001` |
| `balance too low` | Add $5 credit at console.anthropic.com/account/billing |
| `DuckDB file corrupted` | Delete `data/processed/superstore.duckdb` and re-run Stage 2 |
| `Chart not displaying` | `plt.show()` requires GUI; check you're not in headless mode |

---

## 📖 File Reference

| File | Purpose | Stage |
|------|---------|-------|
| `analytics/01_download_dataset.py` | Download from Kaggle | 1 |
| `analytics/02_load_duckdb.py` | Load into DuckDB | 2 |
| `analytics/03_generate_metadata_draft.py` | Auto-generate metadata | 3 |
| `analytics/metadata/orders.yaml` | Hand-edited metadata | 3 |
| `analytics/agent.py` | Text-to-SQL agent | 4 |
| `validate_agent.py` | Validation: compare agent vs direct SQL | 4.5 |
| `analytics/agent_with_charts.py` | Agent + charting | 5 |
| `sql_shell.py` | Interactive SQL terminal | All |
| `run_query.py` | Direct SQL (no API key needed) | All |
| `README.md` | This file | All |
| `.claude/CLAUDE.md` | Project runbook | All |

---

## 🎓 Key Concepts Learned

| Stage | Concept | What You Learn |
|-------|---------|----------------|
| 1 | Data Ingestion | How to fetch external data programmatically |
| 2 | Data Storage | SQL databases vs flat files (performance) |
| 3 | Semantic Layer | Why LLMs need business metadata, not just schema |
| 4 | Tool Use | How Claude proposes function calls for you to execute |
| 4 | Agent Loops | Observe → Act → Observe → Respond pattern |
| 4.5 | Validation | Comparing LLM outputs with ground truth |
| 5 | Multi-Tool Agents | Coordinating multiple tools (SQL + charting) |
| 5 | Declarative Specs | Constraining LLM output format for safety |

---

## 💡 Next Steps

- **Extend metadata**: Add more business rules, example queries
- **Add filtering**: Let agent filter by date range, region, category
- **Cache results**: Store query results to avoid repeated API calls
- **Add logging**: Track all questions, SQLs, and answers
- **Deploy**: Wrap in a web API (FastAPI, Flask)
- **Skill**: Package as Claude Skill for reusability

---

## 📞 Support

For issues or questions:
- Check `.claude/CLAUDE.md` for detailed stage documentation
- Run `validate_agent.py` to test agent correctness
- Use `sql_shell.py` to test SQL queries manually
- Check troubleshooting section above

Good luck! 🚀
