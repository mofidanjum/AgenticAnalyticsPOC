# Agentic Analytics POC — Complete Project Guide

## Project Overview

Building a Claude-powered agent that answers natural-language questions over structured data (Superstore sales dataset) stored in DuckDB, with charting capability.

**Goal**: Learn the Claude ecosystem hands-on while building a working analytics agent.

**Key Learning**: Each stage teaches a specific Claude concept, building from data ingestion → agent reasoning → visualization.

**📖 For step-by-step walkthrough**: See [README.md](../README.md) — explains how each piece works, testing workflows, and troubleshooting.

**⚡ Quick start (Static Superstore data)**: 
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
```

**🆕 Dynamic Dataset Selection** (Use any Kaggle dataset):
```powershell
& .venv\Scripts\python.exe analytics/dynamic_dataset_selector.py
# Type: "I want e-commerce data"
# Claude suggests matching dataset
# Auto-download, auto-schema, ready to query!
```

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

## Folder Structure (Organized by Stage)

```
agentic-data-pipeline/
├── .claude/
│   └── CLAUDE.md                              # This file (project guide)
├── .gitignore
│
├── stages/                                    # All stages organized here
│   ├── stage_0/                               # Environment Setup
│   │   └── (setup via .venv/)
│   │
│   ├── stage_1/                               # Download Dataset
│   │   ├── 01_download_dataset.py             # Download from Kaggle
│   │   └── STAGE_1_SETUP.md                   # Documentation
│   │
│   ├── stage_2/                               # Load into DuckDB
│   │   ├── 02_load_duckdb.py                  # Full load
│   │   ├── setup_dataset.py                   # Quick setup (recommended)
│   │   └── STAGE_2_SETUP.md                   # Documentation
│   │
│   ├── stage_3/                               # Generate Metadata
│   │   ├── 03_generate_metadata_draft.py      # Auto-generate
│   │   └── STAGE_3_SETUP.md                   # Documentation
│   │
│   ├── stage_4/                               # Text-to-SQL Agent
│   │   ├── agent.py                           # Main agent (Claude API)
│   │   ├── validate_agent.py                  # Validation
│   │   └── STAGE_4_SETUP.md                   # Documentation
│   │
│   └── stage_5/                               # Charting
│       ├── agent_with_charts.py               # Agent + charts
│       └── STAGE_5_SETUP.md                   # Documentation
│
├── data/                                      # Data storage
│   ├── raw/                                   # Raw CSV (from Stage 1)
│   │   └── Sample - Superstore.csv
│   ├── processed/                             # DuckDB (from Stage 2)
│   │   └── superstore.duckdb
│   └── sample/                                # Test fixtures
│       └── superstore_sample.csv
│
├── analytics/                                 # Metadata layer
│   ├── metadata/
│   │   └── orders.yaml                        # Column descriptions
│   └── output/                                # Generated charts
│       └── (PNG files)
│
├── 🔧 Utilities
│   ├── sql_shell.py                           # Interactive SQL terminal
│   ├── run_query.py                           # Direct SQL (no API key)
│   └── .venv/                                 # Virtual environment
│
└── 📖 Documentation
    ├── README.md                              # Complete guide (START HERE)
    ├── STAGES_OVERVIEW.md                     # Visual overview
    └── .claude/CLAUDE.md                      # Project runbook
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

**Current Model**: `claude-haiku-4-5-20251001` (latest, updated 2026-08-23)

**Validation**: Use `validate_agent.py` to verify agent results:

```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
& .venv\Scripts\python.exe validate_agent.py
```

Ask questions like "top 5 customers" and it will:
1. Run agent → get SQL from Claude
2. Execute same SQL directly
3. Compare results → show ✓ MATCH or ✗ MISMATCH

This proves Claude's answers are correct.

**Key concepts learned**:
- **Tool use**: Claude proposes function calls, your code executes them
- **System prompts**: Grounding LLM with semantic metadata
- **Agent loops**: Observe → Act (propose SQL) → Observe (results) → Respond
- **Tool execution**: Bridge between Claude (cloud) and DuckDB (local)
- **Cost optimization**: Model selection matters (Haiku vs Sonnet trade-off)
- **Validation**: Comparing LLM output with ground truth SQL results

---

### Stage 5: Add Charting Tool

**What**: Extend agent with a second tool for data visualization

**Script**: `analytics/agent_with_charts.py` (enhanced version of Stage 4)

**What it does**:
1. Keeps Stage 4 agent loop intact
2. Adds second tool: `render_chart(spec: dict)`
3. Claude picks chart type based on question:
   - Trend questions → line chart
   - Comparison questions → bar chart
   - Distributions → histogram
4. Generates PNG to `analytics/output/`
5. Returns chart path + natural language answer

**Chart spec format** (declarative, not raw code):
```python
{
    "type": "line",  # or "bar", "grouped_bar", "histogram"
    "x": "order_date",
    "y": "sales",
    "series": None,  # or column name for line color/bar grouping
    "title": "Sales Over Time"
}
```

**Prerequisites**:
- Stage 4 complete (agent working)
- matplotlib installed (already in `.venv`)

**Create the script**:
```powershell
# File: analytics/agent_with_charts.py
# Contents below in STAGE_5_SCRIPT section
```

**Run**:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
$env:ANTHROPIC_API_KEY = "your-api-key-here"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
```

**Usage example**:
```
Agent ready. Ask a question:
> How did sales change over time by region?

[Agent calls two tools]
1. run_sql("SELECT order_date, region, SUM(sales) FROM orders GROUP BY order_date, region")
2. render_chart({
     "type": "line",
     "x": "order_date",
     "y": "sales",
     "series": "region",
     "title": "Sales Trend by Region"
   })

Chart saved: analytics/output/chart_20260823_143022.png

Answer: Sales showed steady growth in West region, while Central region remained stable...
```

**Output files created**:
- ✅ `analytics/agent_with_charts.py`
- ✅ `analytics/output/*.png` (one chart per query)

**Key concepts learned**:
- Multi-tool agents: Coordinating multiple tool calls
- Declarative specs: Constraining LLM output format
- Agent composition: Combining tools into workflows

---

### Stage 5: Add Charting Tool

**What**: Extend agent with a second tool for data visualization

**Script**: `analytics/agent_with_charts.py` (enhanced version of Stage 4)

**What it does**:
1. Keeps Stage 4 agent loop intact
2. Adds second tool: `render_chart(spec: dict)`
3. Claude picks chart type based on question:
   - Trend questions → line chart
   - Comparison questions → bar chart
   - Distributions → histogram
4. Generates PNG to `analytics/output/`
5. Returns chart path + natural language answer

**Prerequisites**:
- Stage 4 complete (agent working with valid API key)
- matplotlib installed (already in `.venv`)

**Run**:
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
& .venv\Scripts\python.exe analytics/agent_with_charts.py
```

**Usage example**:
```
Agent ready. Ask a question:
> How did sales change over time by region?

[Agent calls two tools]
1. run_sql("SELECT order_date, region, SUM(sales) FROM orders GROUP BY order_date, region")
2. render_chart({
     "type": "line",
     "x": "order_date",
     "y": "sales",
     "series": "region",
     "title": "Sales Trend by Region"
   })

Chart saved: analytics/output/chart_20260823_143022.png

Answer: Sales showed steady growth in West region, while Central region remained stable...
```

**Chart spec format** (declarative, not raw code):
```python
{
    "type": "line",  # or "bar", "grouped_bar", "histogram"
    "x": "column_name",
    "y": "column_name",
    "series": None,  # or column name for line color/bar grouping
    "title": "Chart Title"
}
```

**Output files created**:
- ✅ `analytics/agent_with_charts.py` (when built)
- ✅ `analytics/output/*.png` (one chart per visual query)

**Key concepts learned**:
- Multi-tool agents: Coordinating multiple tool calls
- Declarative specs: Constraining LLM output format
- Data visualization: Matplotlib integration with agent
- Agent composition: Combining tools into workflows

---

### Stage 6: Package as Claude Skill (Optional, Later)

**What**: Wrap Stages 3-5 as a reusable Claude Skill

**Why later**:
- Skill useful once agent is proven and stable
- Requires understanding SKILL.md format
- Not needed for local POC validation

**Will add**: `.claude/skills/agentic-analytics/SKILL.md`

---

## Quick Command Reference

### Environment
```powershell
# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Run Scripts (By Stage)

**Stage 0: Setup**
```powershell
# Activate virtual environment
& .venv\Scripts\Activate.ps1
```

**Stage 1: Download Dataset**
```powershell
# Download from Kaggle (one-time)
& .venv\Scripts\python.exe stages/stage_1/01_download_dataset.py
```

**Stage 2: Load into DuckDB**
```powershell
# Option A: Full load from CSV
& .venv\Scripts\python.exe stages/stage_2/02_load_duckdb.py

# Option B: Quick setup (recommended)
& .venv\Scripts\python.exe stages/stage_2/setup_dataset.py
```

**Stage 3: Generate Metadata**
```powershell
# Auto-generate metadata draft
& .venv\Scripts\python.exe stages/stage_3/03_generate_metadata_draft.py
```

**Stage 4: Run Agent**
```powershell
# Set API key
$env:ANTHROPIC_API_KEY = "sk-ant-your-key"

# Run agent
& .venv\Scripts\python.exe stages/stage_4/agent.py

# Validate results (compare agent vs direct SQL)
& .venv\Scripts\python.exe stages/stage_4/validate_agent.py
```

**Stage 5: Run Agent with Charts**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key"
& .venv\Scripts\python.exe stages/stage_5/agent_with_charts.py
```

**Stage 0B: Dynamic Dataset Selection (Optional)**
```powershell
# Use any Kaggle dataset
& .venv\Scripts\python.exe analytics/dynamic_dataset_selector.py superstore
```

**Utilities**
```powershell
# Interactive SQL shell
& .venv\Scripts\python.exe sql_shell.py

# Direct SQL (no API key needed)
& .venv\Scripts\python.exe run_query.py
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
- Used in Stages 4-5

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

## Files Reference (Organized by Stage)

### 📖 Documentation
| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Complete step-by-step guide (START HERE) | ✅ Done |
| `STAGE_1_SETUP.md` | Stage 1: Download dataset details | ✅ Done |
| `STAGE_2_SETUP.md` | Stage 2: DuckDB loading details | ✅ Done |
| `STAGE_3_SETUP.md` | Stage 3: Metadata generation details | ✅ Done |
| `STAGE_4_SETUP.md` | Stage 4: Agent architecture details | ✅ Done |
| `STAGE_5_SETUP.md` | Stage 5: Charting integration details | ✅ Done |
| `STAGE_0B_DYNAMIC_DATASETS.md` | Stage 0B: Dynamic dataset selection | ✅ Done |

### 📥 Stage 1: Download Dataset
| File | Purpose | Status |
|------|---------|--------|
| `stages/stage_1/01_download_dataset.py` | Download Superstore from Kaggle | ✅ Done |
| `stages/stage_1/STAGE_1_SETUP.md` | Stage 1 documentation | ✅ Done |
| `data/raw/Sample - Superstore.csv` | Downloaded data (2.3 MB, 9,994 rows) | ✅ Done |
| `data/sample/superstore_sample.csv` | Sample fixture (200 rows for testing) | ✅ Done |

### 💾 Stage 2: Load into DuckDB
| File | Purpose | Status |
|------|---------|--------|
| `stages/stage_2/02_load_duckdb.py` | Load CSV into DuckDB (full dataset) | ✅ Done |
| `stages/stage_2/setup_dataset.py` | Quick setup without download | ✅ Done |
| `stages/stage_2/STAGE_2_SETUP.md` | Stage 2 documentation | ✅ Done |
| `data/processed/superstore.duckdb` | DuckDB database (queryable) | ✅ Done |

### 📋 Stage 3: Metadata Layer
| File | Purpose | Status |
|------|---------|--------|
| `stages/stage_3/03_generate_metadata_draft.py` | Auto-generate metadata from schema | ✅ Done |
| `stages/stage_3/STAGE_3_SETUP.md` | Stage 3 documentation | ✅ Done |
| `analytics/metadata/orders.yaml` | Hand-edited metadata (21 columns) | ✅ Done |

### 🤖 Stage 4: Text-to-SQL Agent
| File | Purpose | Status |
|------|---------|--------|
| `stages/stage_4/agent.py` | Main agent loop (Claude Haiku 4.5) | ✅ Done |
| `stages/stage_4/validate_agent.py` | Validation: Compare agent vs direct SQL | ✅ Done |
| `stages/stage_4/STAGE_4_SETUP.md` | Stage 4 documentation | ✅ Done |

### 📊 Stage 5: Charting
| File | Purpose | Status |
|------|---------|--------|
| `stages/stage_5/agent_with_charts.py` | Agent + matplotlib visualization | ✅ Done |
| `stages/stage_5/STAGE_5_SETUP.md` | Stage 5 documentation | ✅ Done |
| `analytics/output/` | Generated PNG charts (timestamped) | ✅ Done |

### 🔧 Utilities
| File | Purpose | Status |
|------|---------|--------|
| `sql_shell.py` | Interactive SQL terminal | ✅ Done |
| `run_query.py` | Direct SQL queries (no API key) | ✅ Done |
| `.gitignore` | Git ignore rules | ✅ Done |

---

---

## 🎉 Project Completion Status

**All 5 stages complete!**

| Stage | Status | Key File |
|-------|--------|----------|
| 0 | ✅ Environment | `.venv/` + dependencies |
| 1 | ✅ Data Download | `analytics/01_download_dataset.py` |
| 2 | ✅ Database Load | `analytics/02_load_duckdb.py` |
| 3 | ✅ Metadata | `analytics/metadata/orders.yaml` |
| 4 | ✅ Agent + Validation | `analytics/agent.py` + `validate_agent.py` |
| 5 | ✅ Charting | `analytics/agent_with_charts.py` |

**Next Steps**:
- Run `analytics/agent_with_charts.py` to start asking questions
- Use `validate_agent.py` to verify results
- Read `README.md` for detailed walkthroughs
- Refer to `STAGE_X_SETUP.md` files for deep dives

Good luck! 🚀