# Agentic Analytics POC — Complete Project Guide

## Project Overview

Building a Claude-powered agent that answers natural-language questions over structured data (Superstore sales dataset) stored in DuckDB, with charting capability.

**Goal**: Learn the Claude ecosystem hands-on while building a working analytics agent.

**Key Learning**: Each stage teaches a specific Claude concept, building from data ingestion → agent reasoning → visualization.

---

## Architecture

```
Kaggle CSV (raw data)
    ↓ [Stage 1: Download]
data/raw/Sample - Superstore.csv (2.3 MB)
    ↓ [Stage 2: Load]
data/processed/superstore.duckdb (queryable)
    ↓ [Stage 3: Describe]
analytics/metadata/orders.yaml (semantic layer)
    ↓ [Stage 4: Query]
LLM Agent (Claude API + tool use) ← Main agent loop
    ↓ [Stage 5: Visualize]
PNG charts + natural language answers
```

---

## Folder Structure

```
agentic-data-pipeline/
├── .claude/
│   └── CLAUDE.md                 # This file (project guide)
├── .gitignore                    # Ignore data/raw, .venv, analytics/output
├── data/
│   ├── raw/                      # Downloaded CSV (gitignored)
│   │   └── Sample - Superstore.csv
│   ├── processed/                # DuckDB database
│   │   └── superstore.duckdb
│   └── sample/                   # Sample fixtures (200 rows)
│       └── superstore_sample.csv
├── analytics/
│   ├── 01_download_dataset.py    # Stage 1 script
│   ├── 02_load_duckdb.py         # Stage 2 script
│   ├── 03_generate_metadata_draft.py  # Stage 3 helper
│   ├── metadata/                 # Stage 3 output
│   │   └── orders.yaml           # Column descriptions (hand-edited)
│   ├── agent.py                  # Stage 4: Main agent loop
│   └── output/                   # Stage 5: Charts
│       └── (PNG files)
├── sql_shell.py                  # Interactive SQL terminal
├── STAGE_1_SETUP.md              # Detailed Stage 1 documentation
└── STAGE_2_SETUP.md              # Detailed Stage 2 documentation
```

---

## Complete Stage Sequence

### Stage 0: Environment Setup (Initial One-Time)

**What**: Set up Python, virtual environment, and dependencies

**Done automatically when**:
- Virtual environment created at `.venv/`
- Packages installed: duckdb, pandas, pyyaml, matplotlib, anthropic, kaggle

**Manual setup (if needed)**:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline

# Create virtual environment
uv venv

# Activate (PowerShell)
& .venv\Scripts\Activate.ps1

# Install all dependencies
uv pip install duckdb pandas pyyaml matplotlib anthropic kaggle
```

**Verification**:
```powershell
& .venv\Scripts\python.exe -c "import duckdb, pandas, yaml; print('✓ All packages installed')"
```

---

### Stage 1: Download Dataset from Kaggle

**What**: Download Superstore sales data from Kaggle and create sample fixture

**Script**: `analytics/01_download_dataset.py`

**Prerequisites**:
- Kaggle account created
- API token saved to `C:\Users\Sarah\.kaggle\kaggle.json`
  - Username: `MOFIDANJUM`
  - Token: `KGAT_a17dca5ed3380c9e5a031ec8b17e6a31`

**Run**:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
& .venv\Scripts\python.exe analytics/01_download_dataset.py
```

**What happens**:
1. Downloads `vivek468/superstore-dataset-final` from Kaggle
2. Saves to `data/raw/Sample - Superstore.csv` (2.3 MB)
3. Creates sample fixture: `data/sample/superstore_sample.csv` (first 200 rows)

**Output files created**:
- ✅ `data/raw/Sample - Superstore.csv` (9,994 rows, 21 columns)
- ✅ `data/sample/superstore_sample.csv` (200 rows for testing)

**Verification**:
```powershell
# Check file sizes
Get-ChildItem data/raw, data/sample

# Should show:
# data/raw/Sample - Superstore.csv  ~2.3 MB
# data/sample/superstore_sample.csv ~600 KB
```

**Notes**:
- Encoding: `latin-1` (handles special characters)
- Date range: 2015-2016
- All US orders (Country = "United States")

---

### Stage 2: Load Data into DuckDB

**What**: Convert CSV into a queryable DuckDB database (single file)

**Script**: `analytics/02_load_duckdb.py`

**Prerequisites**:
- Stage 1 complete (CSV downloaded at `data/raw/Sample - Superstore.csv`)

**Run**:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
& .venv\Scripts\python.exe analytics/02_load_duckdb.py
```

**What happens**:
1. Reads CSV with `latin-1` encoding
2. Creates `data/processed/superstore.duckdb`
3. Creates table `orders` with all 9,994 rows
4. Prints schema verification

**Output files created**:
- ✅ `data/processed/superstore.duckdb` (~2.3 MB, queryable)

**Verification**:
```powershell
# Check database was created
Get-ChildItem data/processed/

# Should show: superstore.duckdb

# Test query
& .venv\Scripts\python.exe -c "
import duckdb
con = duckdb.connect('data/processed/superstore.duckdb')
result = con.sql('SELECT COUNT(*) FROM orders').fetchall()
print(f'✓ Table has {result[0][0]} rows')
"
```

**Table Schema**:
| Column | Type | Purpose |
|--------|------|---------|
| Row ID | BIGINT | Unique row identifier |
| Order ID | VARCHAR | Groups line items (not unique per row) |
| Order Date | VARCHAR | When ordered (MM/DD/YYYY) |
| Ship Date | VARCHAR | When shipped |
| Ship Mode | VARCHAR | Delivery method |
| Customer ID | VARCHAR | Customer identifier |
| Customer Name | VARCHAR | Full name |
| Segment | VARCHAR | Consumer/Corporate/Home Office |
| Country | VARCHAR | Country (all US) |
| City | VARCHAR | City |
| State | VARCHAR | State code |
| Postal Code | BIGINT | ZIP code |
| Region | VARCHAR | East/West/Central/South |
| Product ID | VARCHAR | Product identifier |
| Category | VARCHAR | Furniture/Office Supplies/Technology |
| Sub-Category | VARCHAR | Chair/Table/Bookcase/etc |
| Product Name | VARCHAR | Full product description |
| Sales | DOUBLE | Revenue (USD) |
| Quantity | BIGINT | Units ordered |
| Discount | DOUBLE | Discount (0.0-1.0) |
| Profit | DOUBLE | Profit (can be negative) |

**Data Summary**:
- Total rows: 9,994
- Categories: 3 (Office Supplies: 6,026, Furniture: 2,121, Technology: 1,847)
- Regions: 4 (West: $725k, East: $679k, Central: $501k, South: $392k)
- Profit range: -$6,599 to +$8,400

**Notes**:
- Grain: Order line (one row per product in order, multiple rows per Order ID)
- Dates stored as VARCHAR, not DATE type
- Profit can be negative (don't assume sums are positive)

---

### Stage 3: Generate Metadata Layer

**What**: Create YAML descriptions of table and columns for LLM understanding

**Purpose**: Give the LLM agent semantic knowledge (not just column names/types)
- Example: Know that `profit` can be negative
- Example: Know that `region` has exactly 4 values  
- Example: Know that `discount` is a percentage, not a raw value

**Status**: ✅ **COMPLETE**

**Step 1: Auto-generate metadata draft**

Script: `analytics/03_generate_metadata_draft.py`

Run it:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
& .venv\Scripts\python.exe analytics/03_generate_metadata_draft.py
```

What happens:
1. Introspects DuckDB table schema
2. Gets column types, distinct counts, min/max values
3. Infers column roles (id, dimension, measure, timestamp)
4. Creates YAML template at `analytics/metadata/orders.yaml`

**Step 2: Hand-edit metadata for business meaning** (✅ DONE)

File: `analytics/metadata/orders.yaml`

Hand-edited to include:
- `table.description`: Grain, scope, date range (order-line grain, 9,994 rows, 2015-2016 US sales)
- `columns[*].role`: All 21 columns classified as id/dimension/measure/timestamp
- `columns[*].description`: Business meanings for agent understanding
- `columns[*].unit`: USD for sales/profit, percent for discount, count for quantity
- `notable_values`: Key constraints (profit can be negative, dates are strings, etc.)

**Actual metadata created**:
```yaml
table: orders
description: >
  One row per line item in a retail order. Grain is order-line (not order).
  An order with 3 products spans 3 rows sharing the same Order ID.
  Data covers US retail sales 2015-2016.

columns:
  order_id:
    type: VARCHAR
    role: id
    description: Groups line items into one order (not unique per row, can repeat for multi-item orders)
  
  sales:
    type: DOUBLE
    role: measure
    unit: usd
    description: Revenue for this line item before discount (in USD)
  
  profit:
    type: DOUBLE
    role: measure
    unit: usd
    description: Profit after discount and costs (in USD; can be negative due to returns/deep discounts)
  
  region:
    type: VARCHAR
    role: dimension
    description: US region; one of East, West, Central, or South
  
  discount:
    type: DOUBLE
    role: measure
    unit: percent
    description: Discount applied to line item (0.0 = no discount, 0.5 = 50% off)

notable_values:
  - "profit can be negative — don't assume SUM(profit) > 0"
  - "order_id is not unique per row — use (order_id, product_id) to uniquely identify"
  - "dates are stored as VARCHAR strings (MM/DD/YYYY), not DATE type"
  - "discount can exceed sales value on loss-making items"
  - "all orders are US-based (Country = United States)"
```

**Output files created**:
- ✅ `analytics/03_generate_metadata_draft.py` (auto-generation script)
- ✅ `analytics/metadata/orders.yaml` (complete, hand-edited metadata)
- ✅ `STAGE_3_SETUP.md` (detailed Stage 3 documentation)

**Verification**:
```powershell
# Check metadata file
Get-ChildItem analytics/metadata/

# Should show: orders.yaml

# Validate YAML syntax
& .venv\Scripts\python.exe -c "
import yaml
with open('analytics/metadata/orders.yaml') as f:
    meta = yaml.safe_load(f)
print(f'✓ Metadata loaded: {meta[\"table\"]} table with {len(meta[\"columns\"])} columns')
"
```

---

### Stage 4: Build Text-to-SQL Agent (LLM Core Loop)

**What**: Create an agent that converts natural language → SQL → results → answer

**Script**: `analytics/agent.py`

**Status**: ✅ **COMPLETE**

**What it does**:
1. Reads metadata from `analytics/metadata/orders.yaml`
2. Takes a natural language question from user
3. Calls Claude API (Haiku model for cost efficiency) with:
   - System prompt (metadata + instructions)
   - Tool definition: `run_sql(query: str)`
   - User question
4. Claude proposes SQL query
5. Your script executes SQL against local DuckDB
6. Feeds results back to Claude
7. Claude provides natural language answer

**Agent Loop Flow**:
```
User Question → Load Metadata → Send to Claude API → Claude proposes SQL
    ↓
Execute SQL locally → Get Results → Send results back to Claude → Claude answers
```

**Prerequisites**:
- ✅ Stage 3 complete (metadata.yaml created and enriched)
- Anthropic API key from https://console.anthropic.com/

**Get API key**:
1. Go to https://console.anthropic.com/
2. Copy your API key (starts with `sk-ant-`)
3. Set environment variable before running:
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxx"
```

**Run agent**:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
$env:ANTHROPIC_API_KEY = "your-actual-api-key"
& .venv\Scripts\python.exe analytics/agent.py
```

**Interactive usage example**:
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
- West region: $725,457.82 (highest)
- East region: $678,781.24
- Central region: $501,239.89
- South region: $391,721.91

You: exit
Bye!
```

**Output files created**:
- ✅ `analytics/agent.py` (main agent loop with tool use)
- ✅ `STAGE_4_SETUP.md` (detailed Stage 4 documentation)

**Why Haiku model?**:
- 80% cheaper than Sonnet
- Fast enough for SQL generation
- Reduces token usage significantly
- Perfect for this use case

**Key concepts learned**:
- **Tool use**: Claude proposes function calls, your code executes them
- **System prompts**: Grounding LLM with semantic metadata
- **Agent loops**: Observe → Act (propose SQL) → Observe (results) → Respond
- **Tool execution**: Bridge between Claude (cloud) and DuckDB (local)
- **Cost optimization**: Model selection matters (Haiku vs Sonnet trade-off)

---

### Stage 4 Enhanced: Integrated Charting

**What**: Charting capability is now built directly into Stage 4 agent

**Tools available**:
1. `run_sql()` - Execute SQL queries against DuckDB
2. `render_chart()` - Create visualizations from query results

**What it does**:
1. Keeps Stage 4 agent loop intact
2. Adds `render_chart()` tool for visualization
3. Claude intelligently picks chart type based on data:
   - Trends/time series → line chart
   - Comparisons → bar chart
   - Distributions → pie chart
   - Correlations → scatter chart
4. Generates PNG to `analytics/output/`
5. Returns chart path + natural language answer

**Usage examples**:
```
📊 User: Show me sales by region

🔍 SQL: SELECT region, SUM(sales) FROM orders GROUP BY region

📊 Chart saved to analytics/output/chart_20260824_143022.png

💬 Answer: West region leads with $725K in sales...

---

📊 User: How did sales trend over time?

🔍 SQL: SELECT order_date, SUM(sales) FROM orders GROUP BY order_date

📊 Chart saved to analytics/output/chart_20260824_143045.png

💬 Answer: Sales showed an upward trend throughout 2016...
```

**Run**:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
$env:ANTHROPIC_API_KEY = "your-api-key"
& .venv\Scripts\python.exe analytics/agent.py
```

**Key concepts learned**:
- **Multi-tool agents**: Coordinating multiple tool calls in sequence
- **Tool chaining**: SQL data → Chart visualization
- **LLM-guided visualization**: Claude chooses optimal chart type for data

---

## Quick Command Reference

### Environment
```powershell
# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Run Scripts
```powershell
# Stage 1: Download
& .venv\Scripts\python.exe analytics/01_download_dataset.py

# Stage 2: Load DuckDB
& .venv\Scripts\python.exe analytics/02_load_duckdb.py

# Stage 3: Generate metadata draft
& .venv\Scripts\python.exe analytics/03_generate_metadata_draft.py

# Stage 4: Run agent (with integrated charting)
$env:ANTHROPIC_API_KEY = "sk-ant-xxx"
& .venv\Scripts\python.exe analytics/agent.py
```

### Interactive SQL
```powershell
& .venv\Scripts\python.exe sql_shell.py
```

Then type SQL:
```sql
SELECT * FROM orders LIMIT 5
SELECT Category, COUNT(*) FROM orders GROUP BY Category
SELECT Region, SUM(Sales) FROM orders GROUP BY Region
PRAGMA table_info(orders)
```

### Test Database
```powershell
& .venv\Scripts\python.exe -c "
import duckdb
con = duckdb.connect('data/processed/superstore.duckdb')
result = con.sql('SELECT COUNT(*) FROM orders').fetchall()
print(f'✓ {result[0][0]} rows')
"
```

---

## Important Notes

**Encoding**:
- Raw CSV: `latin-1` encoding (Windows-1252)
- Handled during load in Stage 2

**Dates**:
- Stored as VARCHAR (strings), not DATE type
- Format: MM/DD/YYYY (e.g., "11/8/2016")
- Agent queries must parse as strings

**Profit**:
- Can be negative (discounts, returns, shipping costs)
- Don't assume `SUM(profit) > 0`

**Order grain**:
- One row per line item, not per order
- Multiple rows can share same `Order ID`
- Use `(Order ID, Product ID)` to uniquely identify

**Kaggle setup**:
- Token at: `C:\Users\Sarah\.kaggle\kaggle.json`
- Username: `MOFIDANJUM`
- Token: `KGAT_a17dca5ed3380c9e5a031ec8b17e6a31`

**Claude API**:
- Set `ANTHROPIC_API_KEY` environment variable
- Get key from: https://console.anthropic.com/
- Used in Stage 4 (agent + charting)

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'duckdb'"**
→ Activate venv first: `& .venv\Scripts\Activate.ps1`

**"Kaggle API key not found"**
→ Create token at https://www.kaggle.com/settings/account → API

**"ANTHROPIC_API_KEY not set"**
→ Set it: `$env:ANTHROPIC_API_KEY = "sk-ant-xxx"`

**"SQL query too slow"**
→ Add `LIMIT` for testing, then remove for full results

**DuckDB file corrupted**
→ Delete `data/processed/superstore.duckdb` and re-run Stage 2

---

## Files Reference

| File | Purpose | Stage | Status |
|------|---------|-------|--------|
| `STAGE_1_SETUP.md` | Stage 1 documentation | 1 | ✅ Done |
| `STAGE_2_SETUP.md` | Stage 2 documentation | 2 | ✅ Done |
| `STAGE_3_SETUP.md` | Stage 3 documentation | 3 | ✅ Done |
| `STAGE_4_SETUP.md` | Stage 4 documentation (SQL + Charts) | 4 | ✅ Done |
| `analytics/01_download_dataset.py` | Download from Kaggle | 1 | ✅ Done |
| `analytics/02_load_duckdb.py` | Load into DuckDB | 2 | ✅ Done |
| `analytics/03_generate_metadata_draft.py` | Auto-generate metadata | 3 | ✅ Done |
| `analytics/metadata/orders.yaml` | Hand-edited metadata | 3 | ✅ Done |
| `analytics/agent.py` | Text-to-SQL agent + charting (Haiku) | 4 | ✅ Done |
| `analytics/output/` | Generated chart PNGs | 4 | ✅ Ready |
| `sql_shell.py` | Interactive SQL | All | ✅ Done |
| `.gitignore` | Git ignore rules | All | ✅ Done |

---

## Next Session

When you return:
1. This file will load automatically
2. Refer to the stage you want to run
3. Follow the "Run" command for that stage
4. All prerequisites will be listed clearly

Good luck! 🚀