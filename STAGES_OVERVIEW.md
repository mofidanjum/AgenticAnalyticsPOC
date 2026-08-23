# Stages Overview — Complete Project Alignment

Visual guide showing all stages, their code, inputs, and outputs.

---

## 🎯 Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 0: Environment Setup                                       │
├─────────────────────────────────────────────────────────────────┤
│ Input:  Python 3.9+, pip/uv                                     │
│ Code:   .venv/ (virtual environment)                            │
│ Output: .venv/ with dependencies (duckdb, pandas, yaml, etc.)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: Download Dataset from Kaggle                           │
├─────────────────────────────────────────────────────────────────┤
│ Input:  Kaggle API key + credentials                            │
│ Code:   analytics/01_download_dataset.py                        │
│ Output: data/raw/Sample - Superstore.csv (2.3 MB, 9,994 rows)   │
│         data/sample/superstore_sample.csv (200 rows)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: Load into DuckDB                                       │
├─────────────────────────────────────────────────────────────────┤
│ Input:  data/raw/Sample - Superstore.csv                        │
│ Code:   analytics/02_load_duckdb.py                             │
│         analytics/setup_dataset.py (quick option)               │
│ Output: data/processed/superstore.duckdb (queryable SQL DB)     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: Generate Metadata Layer                                │
├─────────────────────────────────────────────────────────────────┤
│ Input:  data/processed/superstore.duckdb                        │
│ Code:   analytics/03_generate_metadata_draft.py (auto)          │
│ Output: analytics/metadata/orders.yaml (hand-edited)            │
│         Column descriptions for LLM understanding               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: Text-to-SQL Agent (Claude API)                         │
├─────────────────────────────────────────────────────────────────┤
│ Input:  User question + metadata.yaml + ANTHROPIC_API_KEY       │
│ Code:   analytics/agent.py (main agent)                         │
│         validate_agent.py (verify results)                      │
│ Output: SQL query → Results → Natural language answer           │
│         Tools: run_sql                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: Agent with Charting (matplotlib)                       │
├─────────────────────────────────────────────────────────────────┤
│ Input:  User question + Agent (from Stage 4)                    │
│ Code:   analytics/agent_with_charts.py                          │
│ Output: SQL query → Chart (PNG) → Results → Answer              │
│         Tools: run_sql + render_chart                           │
│         Saves: analytics/output/chart_YYYYMMDD_HHMMSS.png       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Stage-by-Stage Breakdown

### Stage 0: Environment Setup
| Aspect | Details |
|--------|---------|
| **Purpose** | Set up Python environment with dependencies |
| **Input** | Python 3.9+, pip/uv package manager |
| **Code** | `.venv/` (virtual environment) |
| **Command** | `uv venv` then `uv pip install ...` |
| **Output** | `.venv/Scripts/python.exe` + all packages |
| **Duration** | ~2 minutes |
| **Docs** | CLAUDE.md Stage 0 section |

---

### Stage 1: Download Dataset
| Aspect | Details |
|--------|---------|
| **Purpose** | Fetch raw data from Kaggle |
| **Input** | Kaggle API credentials (`~/.kaggle/kaggle.json`) |
| **Script** | `analytics/01_download_dataset.py` |
| **Dataset** | vivek468/superstore-dataset-final |
| **Output Files** | • `data/raw/Sample - Superstore.csv` (2.3 MB) |
| | • `data/sample/superstore_sample.csv` (200 rows) |
| **Rows/Cols** | 9,994 rows × 21 columns |
| **Duration** | ~1-2 minutes |
| **Command** | `& .venv\Scripts\python.exe analytics/01_download_dataset.py` |
| **Docs** | STAGE_1_SETUP.md |

---

### Stage 2: Load into DuckDB
| Aspect | Details |
|--------|---------|
| **Purpose** | Convert CSV to queryable SQL database |
| **Input** | `data/raw/Sample - Superstore.csv` |
| **Scripts** | • `analytics/02_load_duckdb.py` (full) |
| | • `analytics/setup_dataset.py` (quick, recommended) |
| **Output** | `data/processed/superstore.duckdb` |
| **Table** | `orders` (9,994 rows, 21 columns) |
| **Columns** | Order ID, Order Date, Sales, Profit, Region, etc. |
| **Duration** | ~10 seconds |
| **Command** | `& .venv\Scripts\python.exe analytics/setup_dataset.py` |
| **Docs** | STAGE_2_SETUP.md |

---

### Stage 3: Generate Metadata
| Aspect | Details |
|--------|---------|
| **Purpose** | Create semantic layer for LLM understanding |
| **Input** | `data/processed/superstore.duckdb` |
| **Script** | `analytics/03_generate_metadata_draft.py` |
| **Output** | `analytics/metadata/orders.yaml` |
| **Content** | • Table description |
| | • 21 column definitions |
| | • Column roles (id, dimension, measure, timestamp) |
| | • Units (USD, percent, count) |
| | • Business constraints & notable values |
| **Edit** | ✅ Already hand-edited in `orders.yaml` |
| **Duration** | ~5 seconds |
| **Command** | `& .venv\Scripts\python.exe analytics/03_generate_metadata_draft.py` |
| **Docs** | STAGE_3_SETUP.md |

---

### Stage 4: Text-to-SQL Agent
| Aspect | Details |
|--------|---------|
| **Purpose** | Convert natural language questions to SQL |
| **Input** | User question + metadata.yaml + API key |
| **Script** | `analytics/agent.py` |
| **Model** | Claude Haiku 4.5 (cost-optimized) |
| **Tools** | `run_sql(query: str)` → Execute SQL locally |
| **Process** | 1. Load metadata |
| | 2. Send question to Claude |
| | 3. Claude generates SQL |
| | 4. Execute SQL against DuckDB |
| | 5. Claude generates answer |
| **Output** | Natural language answer + execution details |
| **Cost** | ~$0.0004 per query (Haiku) |
| **Duration** | ~2-3 seconds per query |
| **API Key** | `$env:ANTHROPIC_API_KEY = "sk-ant-xxx"` |
| **Commands** | • Run: `analytics/agent.py` |
| | • Validate: `validate_agent.py` |
| **Docs** | STAGE_4_SETUP.md |

---

### Stage 4.5: Validation (Optional)
| Aspect | Details |
|--------|---------|
| **Purpose** | Verify agent SQL correctness |
| **Input** | Same question + agent |
| **Script** | `validate_agent.py` |
| **Process** | 1. Run agent → get SQL |
| | 2. Execute same SQL directly |
| | 3. Compare results |
| **Output** | ✓ MATCH or ✗ MISMATCH |
| **Command** | `& .venv\Scripts\python.exe validate_agent.py` |
| **Use Case** | Production validation, accuracy checks |
| **Docs** | STAGE_4_SETUP.md |

---

### Stage 5: Agent with Charting
| Aspect | Details |
|--------|---------|
| **Purpose** | Add visualizations to agent responses |
| **Input** | User question + agent + matplotlib |
| **Script** | `analytics/agent_with_charts.py` |
| **Tools** | • `run_sql(query: str)` (Stage 4) |
| | • `render_chart(spec: dict)` (new) |
| **Chart Types** | • line (trends) |
| | • bar (comparisons) |
| | • grouped_bar (multi-series) |
| | • histogram (distributions) |
| **Output** | • SQL query result |
| | • Chart (PNG) displayed + saved |
| | • Natural language answer |
| **Chart Spec** | `{"type": "line", "x": "col", "y": "col", "series": "col", "title": "..."}` |
| **Saved Charts** | `analytics/output/chart_YYYYMMDD_HHMMSS.png` |
| **Duration** | ~2-4 seconds (includes chart generation) |
| **Command** | `& .venv\Scripts\python.exe analytics/agent_with_charts.py` |
| **Docs** | STAGE_5_SETUP.md |

---

### Stage 0B: Dynamic Dataset Selection (Optional)
| Aspect | Details |
|--------|---------|
| **Purpose** | Use any Kaggle dataset instead of hardcoded Superstore |
| **Input** | Dataset key or description |
| **Script** | `analytics/dynamic_dataset_selector.py` |
| **Datasets** | • superstore (default) |
| | • ecommerce |
| | • amazon |
| | • hotel |
| **Process** | 1. List available datasets |
| | 2. User selects or describes |
| | 3. Download from Kaggle |
| | 4. Auto-detect schema |
| | 5. Create DuckDB table |
| | 6. Generate metadata |
| **Output** | DuckDB + metadata for chosen dataset |
| **Command** | `& .venv\Scripts\python.exe analytics/dynamic_dataset_selector.py superstore` |
| **Fallback** | Uses Superstore if selection fails |
| **Docs** | STAGE_0B_DYNAMIC_DATASETS.md |

---

## 🔧 Utilities

### SQL Shell (Interactive)
| Aspect | Details |
|--------|---------|
| **Purpose** | Manual SQL queries without agent |
| **Script** | `sql_shell.py` |
| **Command** | `& .venv\Scripts\python.exe sql_shell.py` |
| **Use** | Test queries, explore data |
| **Example** | `SELECT region, SUM(sales) FROM orders GROUP BY region` |

### Run Query (No API Key)
| Aspect | Details |
|--------|---------|
| **Purpose** | Pre-built queries, no Claude needed |
| **Script** | `run_query.py` |
| **Command** | `& .venv\Scripts\python.exe run_query.py` |
| **Queries** | Sales by region, profit by category, top products, etc. |

---

## 📁 File Organization

```
Analytics Project
│
├─ DOCUMENTATION (Start here!)
│  ├─ README.md .......................... Complete guide with examples
│  ├─ CLAUDE.md .......................... This project's runbook
│  ├─ STAGES_OVERVIEW.md ................. This file
│  ├─ STAGE_1_SETUP.md ................... Stage 1 details
│  ├─ STAGE_2_SETUP.md ................... Stage 2 details
│  ├─ STAGE_3_SETUP.md ................... Stage 3 details
│  ├─ STAGE_4_SETUP.md ................... Stage 4 details
│  ├─ STAGE_5_SETUP.md ................... Stage 5 details
│  └─ STAGE_0B_DYNAMIC_DATASETS.md ....... Optional Stage 0B
│
├─ DATA PIPELINE
│  ├─ Stage 1: analytics/01_download_dataset.py
│  ├─ Stage 2: analytics/02_load_duckdb.py, setup_dataset.py
│  ├─ Stage 3: analytics/03_generate_metadata_draft.py
│  ├─ Stage 4: analytics/agent.py
│  ├─ Stage 5: analytics/agent_with_charts.py
│  └─ Stage 0B: analytics/dynamic_dataset_selector.py
│
├─ DATA STORAGE
│  ├─ data/raw/ .......................... Raw CSV (2.3 MB)
│  ├─ data/processed/ .................... DuckDB (queryable)
│  ├─ analytics/metadata/ ................ YAML descriptions
│  └─ analytics/output/ .................. Generated charts
│
└─ UTILITIES
   ├─ sql_shell.py ....................... Interactive SQL
   ├─ run_query.py ....................... Direct queries
   ├─ validate_agent.py .................. Agent validation
   └─ .venv/ ............................ Virtual environment
```

---

## ⚡ Quick Start Commands

### Complete Flow (5-10 minutes)
```powershell
# 1. Setup dataset
& .venv\Scripts\python.exe analytics/setup_dataset.py

# 2. Set API key
$env:ANTHROPIC_API_KEY = "sk-ant-your-key"

# 3. Run agent
& .venv\Scripts\python.exe analytics/agent_with_charts.py

# 4. Ask questions!
You: What were total sales by region?
You: top 5 customers
You: exit
```

### Alternative: Validate First
```powershell
# Verify correctness before using agent
& .venv\Scripts\python.exe validate_agent.py
# Ask: top 5 products
# See: ✓ MATCH
```

### Alternative: No API Key
```powershell
# Quick queries without Claude
& .venv\Scripts\python.exe run_query.py
```

---

## 🎓 Learning Path

**Beginner**: Read in this order
1. README.md (overview)
2. STAGE_1_SETUP.md (data download)
3. STAGE_2_SETUP.md (database basics)
4. Run: `analytics/setup_dataset.py`

**Intermediate**: Add LLM reasoning
1. STAGE_3_SETUP.md (semantic layer)
2. STAGE_4_SETUP.md (agent architecture)
3. Run: `analytics/agent.py` (text-to-SQL)

**Advanced**: Visualization + validation
1. STAGE_4_SETUP.md (tool use patterns)
2. STAGE_5_SETUP.md (multi-tool agents)
3. `validate_agent.py` (correctness verification)
4. Run: `analytics/agent_with_charts.py` (full system)

**Bonus**: Multiple datasets
1. STAGE_0B_DYNAMIC_DATASETS.md
2. Run: `analytics/dynamic_dataset_selector.py`

---

## ✅ Project Completion Status

| Stage | Code File | Status | Docs |
|-------|-----------|--------|------|
| 0 | `.venv/` | ✅ Done | CLAUDE.md |
| 1 | `01_download_dataset.py` | ✅ Done | STAGE_1_SETUP.md |
| 2 | `02_load_duckdb.py`, `setup_dataset.py` | ✅ Done | STAGE_2_SETUP.md |
| 3 | `03_generate_metadata_draft.py` | ✅ Done | STAGE_3_SETUP.md |
| 4 | `agent.py`, `validate_agent.py` | ✅ Done | STAGE_4_SETUP.md |
| 5 | `agent_with_charts.py` | ✅ Done | STAGE_5_SETUP.md |
| 0B | `dynamic_dataset_selector.py` | ✅ Done | STAGE_0B_DYNAMIC_DATASETS.md |
| Util | `sql_shell.py`, `run_query.py` | ✅ Done | README.md |

**Everything complete! Ready to use.** 🚀
