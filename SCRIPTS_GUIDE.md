# 🚀 Agentic Analytics POC - Scripts Guide

**All scripts organized and numbered (1-6) in execution order.**

---

## 📋 Complete Script List

### **Script 1️⃣: Download Dataset from Kaggle**
📁 **Path**: `analytics/01_download_dataset.py`

**Purpose**: Download Superstore sales data from Kaggle

**Command**:
```powershell
python analytics/01_download_dataset.py
```

**Output**:
- ✅ `data/raw/Sample - Superstore.csv` (9,994 rows)
- ✅ `data/sample/superstore_sample.csv` (200 rows - test fixture)

**Time**: 1-2 minutes

**Prerequisites**:
- Kaggle account
- API token at `~/.kaggle/kaggle.json`

---

### **Script 2️⃣: Load Data into DuckDB**
📁 **Path**: `analytics/02_load_duckdb.py`

**Purpose**: Convert CSV to queryable DuckDB database

**Command**:
```powershell
python analytics/02_load_duckdb.py
```

**Output**:
- ✅ `data/processed/superstore.duckdb` (2.3 MB)
- ✅ `orders` table with 9,994 rows × 21 columns

**Time**: 10-15 seconds

**Prerequisites**: Script 1 complete

---

### **Script 3️⃣: Generate Metadata**
📁 **Path**: `analytics/03_generate_metadata_draft.py`

**Purpose**: Create semantic metadata for Claude AI understanding

**Command**:
```powershell
python analytics/03_generate_metadata_draft.py
```

**Output**:
- ✅ `analytics/metadata/orders.yaml` (semantic schema)

**Time**: 5-10 seconds

**Prerequisites**: Script 2 complete

---

### **Script 4️⃣: Main Dashboard Application**
📁 **Path**: `app.py` (Local) or `streamlit_app.py` (Cloud entry point)

**Purpose**: Interactive dashboard with Claude AI integration

**Command**:
```powershell
streamlit run app.py
```

**Access**: http://localhost:8501

**Features**:
- 📊 **Visual Tab**: Claude AI chart generation
- 📋 **Data Tab**: Filtered data browser
- 🔍 **SQL Tab**: Custom SQL queries
- **Sidebar**: Refresh Data, Verify Data, Deploy buttons
- **KPIs**: Sales, Profit, Orders, Customers
- **Filters**: Region, Category, Segment

**Time**: Instant (always running)

**Prerequisites**: Scripts 1-3 complete

---

### **Script 5️⃣: Verification Tests**
📁 **Path**: `test_app.py`

**Purpose**: Verify all components working

**Command**:
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

**Output**: 
```
🎉 ALL TESTS PASSED! APP IS READY!
```

**Time**: 5-10 seconds

**Prerequisites**: Scripts 1-3 complete

---

### **Script 6️⃣: Interactive SQL Shell**
📁 **Path**: `sql_shell.py`

**Purpose**: Interactive SQL terminal for database exploration

**Command**:
```powershell
python sql_shell.py
```

**Usage**:
```sql
> SELECT Region, SUM(Sales) FROM orders GROUP BY Region
East      | 678781.24
West      | 725457.82
Central   | 501239.89
South     | 391721.91

> exit
```

**Time**: Interactive (until exit)

**Prerequisites**: Scripts 1-2 complete

---

## 🚀 Quick Start

### Full Setup (Scripts 1-4)
```powershell
# Create environment
uv venv
& .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

# Set API key
$env:ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY"

# Run Scripts 1-3 (pipeline)
python analytics/01_download_dataset.py
python analytics/02_load_duckdb.py
python analytics/03_generate_metadata_draft.py

# Launch Script 4 (dashboard)
streamlit run app.py
```

### Access: http://localhost:8501 ✅

---

## ✅ Verification

**Test everything**:
```powershell
python test_app.py
```

**Result**:
```
✅ ALL TESTS PASSED! APP IS READY!
```

---

## 📊 Data Summary

| Metric | Value |
|--------|-------|
| Rows | 9,994 |
| Columns | 21 |
| Regions | 4 |
| Categories | 3 |
| Segments | 3 |
| Total Sales | $2,297,201 |
| Total Profit | $286,397 |

---

## 🌍 Deploy to Cloud

```powershell
git add .
git commit -m "Ready for deployment"
git push origin main
```

Then on Streamlit Cloud:
1. Deploy from repo
2. Add API key to secrets
3. Get live URL 🚀

---

## 📁 Final File Structure

```
agentic-data-pipeline/
├── README.md                         ← Start here
├── SCRIPTS_GUIDE.md                  ← This file
├── SCRIPTS_REFERENCE.md              ← Detailed script reference
├── .claude/CLAUDE.md                 ← Technical documentation
│
├── analytics/
│   ├── 01_download_dataset.py        ← Script 1
│   ├── 02_load_duckdb.py             ← Script 2
│   ├── 03_generate_metadata_draft.py ← Script 3
│   └── metadata/orders.yaml          ← Auto-generated metadata
│
├── app.py                            ← Script 4 (main)
├── streamlit_app.py                  ← Script 4 (cloud entry)
├── test_app.py                       ← Script 5 (tests)
├── sql_shell.py                      ← Script 6 (SQL terminal)
│
├── data/
│   ├── raw/Sample - Superstore.csv   ← From Script 1
│   ├── processed/superstore.duckdb   ← From Script 2
│   └── sample/superstore_sample.csv  ← Test fixture
│
├── .streamlit/config.toml            ← Theme configuration
└── requirements.txt                  ← Dependencies
```

---

## 🎯 Execution Flow

```
START
  ↓
[Script 1] python analytics/01_download_dataset.py
  ↓ Creates: data/raw/Sample - Superstore.csv
  ↓
[Script 2] python analytics/02_load_duckdb.py
  ↓ Creates: data/processed/superstore.duckdb
  ↓
[Script 3] python analytics/03_generate_metadata_draft.py
  ↓ Creates: analytics/metadata/orders.yaml
  ↓
[Script 4] streamlit run app.py
  ↓ Access: http://localhost:8501
  ↓
[Script 5] python test_app.py (optional - verify)
  ↓ Output: ✅ ALL TESTS PASSED
  ↓
[Script 6] python sql_shell.py (optional - explore)
  ↓ Interactive SQL terminal
  ↓
[Deploy] git push origin main
  ↓ Streamlit Cloud auto-redeploys
  ↓
END - Live on https://agenticanalyticspc-[random].streamlit.app
```

---

## ✨ Features

**Dashboard**:
- ✅ 4 KPI cards (Sales, Profit, Orders, Customers)
- ✅ 3 dynamic filters (Region, Category, Segment)
- ✅ 3 interactive tabs (Visual, Data, SQL)
- ✅ Claude AI chart generation
- ✅ Real-time filtering

**Automation**:
- ✅ One-click data refresh
- ✅ One-click verification
- ✅ One-click deployment

**Technology**:
- ✅ Streamlit (web UI)
- ✅ DuckDB (database)
- ✅ Claude AI (analytics)
- ✅ Plotly (visualizations)

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Database not found | Run Script 1 & 2 |
| API Key error | `$env:ANTHROPIC_API_KEY = "sk-ant-..."` |
| Port in use | `streamlit run app.py --server.port 8502` |
| Tests fail | Verify Scripts 1-3 completed |

---

## ✅ Status: READY! 🎉

All scripts tested and working. Pick one and start:

1. **Quick Test**: `python test_app.py`
2. **Launch Dashboard**: `streamlit run app.py`
3. **Explore Data**: `python sql_shell.py`

**Everything is organized, numbered, and ready!** 🚀
