# Agentic Analytics POC — Complete Project Guide

## Project Overview

Building a Claude-powered agent that answers natural language questions over structured data (Superstore sales dataset) stored in DuckDB, with interactive charting capability.

**Goal**: Learn the Claude ecosystem hands-on while building a working analytics dashboard.

**Result**: A complete POC showing: Data Pipeline → Metadata Layer → Claude AI → Interactive Dashboard → Cloud Deployment

---

## 📋 Scripts (Numbered in Build Order)

### **SCRIPT 1: Download Dataset from Kaggle**
**File**: `analytics/01_download_dataset.py`

**What it does**:
- Downloads Superstore sales data from Kaggle
- Creates sample fixture (200 rows) for testing
- Handles encoding issues (latin-1)

**Run**:
```powershell
python analytics/01_download_dataset.py
```

**Requires**:
- Kaggle account
- API token at: `~/.kaggle/kaggle.json`

**Output**:
- ✅ `data/raw/Sample - Superstore.csv` (9,994 rows, 21 columns)
- ✅ `data/sample/superstore_sample.csv` (200 rows, test fixture)

---

### **SCRIPT 2: Load Data into DuckDB**
**File**: `analytics/02_load_duckdb.py`

**What it does**:
- Reads CSV with proper encoding (latin-1)
- Creates queryable DuckDB database
- Creates `orders` table (9,994 rows)
- Closes connection to prevent file locks
- Auto-deletes old database before loading

**Run**:
```powershell
python analytics/02_load_duckdb.py
```

**Output**:
- ✅ `data/processed/superstore.duckdb` (2.3 MB, queryable)

---

### **SCRIPT 3: Generate Metadata Schema**
**File**: `analytics/03_generate_metadata_draft.py`

**What it does**:
- Introspects DuckDB schema
- Creates YAML metadata (semantic layer)
- Provides Claude with business context for all columns

**Run**:
```powershell
python analytics/03_generate_metadata_draft.py
```

**Output**:
- ✅ `analytics/metadata/orders.yaml` (auto-generated semantic metadata)

---

### **SCRIPT 4: Main Dashboard Application**
**File**: `app.py` (or `streamlit_app.py` for cloud)

**What it does**:
- Streamlit web dashboard (responsive, interactive)
- Three-tab interface: Visual, Data, SQL
- Claude AI integration for chart generation
- Sidebar automation buttons: Refresh Data, Verify Data, Deploy
- Real-time data filtering and analysis

**Run Locally**:
```powershell
streamlit run app.py
```

**Access**: http://localhost:8501

**Key Components**:

#### **Sidebar Automation**
1. **📥 Refresh Data** - Runs Scripts 1-3 automatically
2. **🧪 Verify Data** - Confirms database integrity
3. **🚀 Deploy** - Pushes to GitHub

#### **KPI Cards**
- 💰 Total Sales: $2,297,201
- 📈 Total Profit: $286,397
- 📋 Total Orders: 5,009
- 👥 Customers: 793

#### **Filters**
- 📍 Region (4 options): East, West, Central, South
- 📦 Category (3 options): Furniture, Office Supplies, Technology
- 👥 Segment (3 options): Consumer, Corporate, Home Office

#### **Tab 1: 📊 Visual (Claude AI Chart Generation)**
User enters → Claude generates code → Chart displays

**Examples**:
- "Show sales by region as a bar chart"
- "Create a pie chart of profit by category"
- "Build a dashboard with sales trends"

#### **Tab 2: 📋 Data (Filtered Data Browser)**
- All 21 columns from orders table
- Respects filter selections
- Sortable and searchable

#### **Tab 3: 🔍 SQL (Custom Query Interface)**
- Write any DuckDB SQL
- Click to execute
- See results in table

---

### **SCRIPT 5: Verification Test Suite**
**File**: `test_app.py`

**What it does**:
- Runs 7 comprehensive tests
- Verifies all components working

**Run**:
```powershell
python test_app.py
```

**Tests**:
1. Database Connection
2. KPI Metrics
3. Filters
4. Filtered Data Query
5. Visualization Data
6. Custom SQL Query
7. Required Packages

---

### **SCRIPT 6: Interactive SQL Shell**
**File**: `sql_shell.py`

**What it does**:
- Interactive terminal for database queries
- Useful for exploration and debugging

**Run**:
```powershell
python sql_shell.py
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Setup
```powershell
uv venv
& .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY"
```

### Step 2: Build Pipeline (Scripts 1-3)
```powershell
python analytics/01_download_dataset.py
python analytics/02_load_duckdb.py
python analytics/03_generate_metadata_draft.py
```

### Step 3: Launch Dashboard (Script 4)
```powershell
streamlit run app.py
```

**Access**: http://localhost:8501 ✅

---

## 📁 File Structure

```
agentic-data-pipeline/
├── README.md                        ← Quick start guide
├── .claude/CLAUDE.md                ← This file (detailed)
│
├── analytics/
│   ├── 01_download_dataset.py       ← Script 1
│   ├── 02_load_duckdb.py            ← Script 2
│   ├── 03_generate_metadata_draft.py ← Script 3
│   └── metadata/orders.yaml         ← Auto-generated
│
├── app.py                           ← Script 4 (local)
├── streamlit_app.py                 ← Script 4 (cloud)
├── test_app.py                      ← Script 5
├── sql_shell.py                     ← Script 6
│
├── data/
│   ├── raw/Sample - Superstore.csv  ← From Script 1
│   ├── processed/superstore.duckdb  ← From Script 2
│   └── sample/superstore_sample.csv ← Test fixture
│
├── .streamlit/config.toml           ← Theme settings
└── requirements.txt                 ← Dependencies
```

---

## ✅ Verification

Run to verify everything:
```powershell
python test_app.py
```

Should show:
```
✅ TEST 1: Database Connection
✅ TEST 2: KPI Metrics
✅ TEST 3: Filters
✅ TEST 4: Filtered Data Query
✅ TEST 5: Visualization Data
✅ TEST 6: Custom SQL Query
✅ TEST 7: Required Packages

🎉 ALL TESTS PASSED! APP IS READY!
```

---

## 🌍 Deploy to Cloud

1. Push to GitHub: `git push origin main`
2. Go to: https://streamlit.io/cloud
3. Deploy from repo
4. Add secrets: ANTHROPIC_API_KEY
5. Get live URL! 🚀

---

## 📞 Support

Refer to README.md for quick start, this file for detailed implementation.

**You're ready to build!** 🎉
