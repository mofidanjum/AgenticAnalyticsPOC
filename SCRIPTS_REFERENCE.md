# 📋 Scripts Reference Guide - All 6 Scripts Numbered

Quick lookup for all scripts in this POC. Run in order (1 → 6).

---

## **SCRIPT 1️⃣: Download from Kaggle**

| Property | Value |
|----------|-------|
| **File** | `analytics/01_download_dataset.py` |
| **Purpose** | Download Superstore dataset from Kaggle |
| **Input** | Kaggle API token |
| **Output** | `data/raw/Sample - Superstore.csv` (9,994 rows) |
| **Time** | 1-2 minutes |
| **Run** | `python analytics/01_download_dataset.py` |

**What it creates**:
- ✅ `data/raw/Sample - Superstore.csv` - 9,994 rows of sales data
- ✅ `data/sample/superstore_sample.csv` - 200 row test fixture

**Prerequisites**:
- Kaggle account: https://www.kaggle.com
- API token at: `~/.kaggle/kaggle.json`
- Username: `MOFIDANJUM`
- Token: `KGAT_a17dca5ed3380c9e5a031ec8b17e6a31`

---

## **SCRIPT 2️⃣: Load into DuckDB**

| Property | Value |
|----------|-------|
| **File** | `analytics/02_load_duckdb.py` |
| **Purpose** | Convert CSV to queryable database |
| **Input** | CSV from Script 1 |
| **Output** | `data/processed/superstore.duckdb` (2.3 MB) |
| **Time** | 10-15 seconds |
| **Run** | `python analytics/02_load_duckdb.py` |

**What it creates**:
- ✅ DuckDB database file (single file, no server)
- ✅ `orders` table (9,994 rows, 21 columns)
- ✅ Ready for SQL queries

**Features**:
- Auto-deletes old database (prevents file locks)
- Properly closes connections
- Shows table schema verification

---

## **SCRIPT 3️⃣: Generate Metadata**

| Property | Value |
|----------|-------|
| **File** | `analytics/03_generate_metadata_draft.py` |
| **Purpose** | Create semantic metadata for Claude |
| **Input** | DuckDB from Script 2 |
| **Output** | `analytics/metadata/orders.yaml` |
| **Time** | 5-10 seconds |
| **Run** | `python analytics/03_generate_metadata_draft.py` |

**What it creates**:
- ✅ YAML metadata file
- ✅ Column descriptions
- ✅ Column roles (id/dimension/measure/timestamp)
- ✅ Notable constraints and values

**Purpose**:
Claude uses this to understand:
- What each column means
- Valid value ranges
- Special handling (e.g., profit can be negative)
- Measure units (USD, percent, count)

---

## **SCRIPT 4️⃣: Dashboard (Main Application)**

| Property | Value |
|----------|-------|
| **Files** | `app.py` (local) or `streamlit_app.py` (cloud) |
| **Purpose** | Interactive dashboard with Claude AI |
| **Input** | Database from Script 2 |
| **Output** | Web dashboard at http://localhost:8501 |
| **Time** | Instant |
| **Run** | `streamlit run app.py` |

**What it provides**:

**Sidebar Buttons**:
- 📥 **Refresh Data** - Auto-runs Scripts 1-3
- 🧪 **Verify Data** - Confirms 9,994 rows loaded
- 🚀 **Deploy** - Pushes to GitHub

**KPI Cards**:
- 💰 Total Sales: $2,297,201
- 📈 Total Profit: $286,397
- 📋 Total Orders: 5,009
- 👥 Customers: 793

**Filters**:
- 📍 Region (4): East, West, Central, South
- 📦 Category (3): Furniture, Office Supplies, Technology
- 👥 Segment (3): Consumer, Corporate, Home Office

**Tabs**:

1. **📊 Visual** - Claude AI chart generation
   - Type: "Show sales by region"
   - Claude generates Plotly code
   - Chart displays automatically

2. **📋 Data** - Browse filtered data
   - All 21 columns
   - Respects filters
   - Sortable, searchable

3. **🔍 SQL** - Custom SQL queries
   - Write any SQL
   - Click execute
   - See results

---

## **SCRIPT 5️⃣: Verification Tests**

| Property | Value |
|----------|-------|
| **File** | `test_app.py` |
| **Purpose** | Verify all components working |
| **Input** | Database from Script 2 |
| **Output** | PASS/FAIL report |
| **Time** | 5-10 seconds |
| **Run** | `python test_app.py` |

**Tests (7 total)**:
1. ✅ Database Connection
2. ✅ KPI Metrics
3. ✅ Filters
4. ✅ Filtered Data Query
5. ✅ Visualization Data
6. ✅ Custom SQL Query
7. ✅ Required Packages

**Success Output**:
```
✅ ALL TESTS PASSED! APP IS READY!
```

---

## **SCRIPT 6️⃣: Interactive SQL Shell**

| Property | Value |
|----------|-------|
| **File** | `sql_shell.py` |
| **Purpose** | Interactive SQL terminal |
| **Input** | Database from Script 2 |
| **Output** | SQL query results |
| **Time** | Interactive (until exit) |
| **Run** | `python sql_shell.py` |

**Usage**:
```sql
> SELECT Region, SUM(Sales) FROM orders GROUP BY Region
East      | 678781.24
West      | 725457.82
Central   | 501239.89
South     | 391721.91

> SELECT COUNT(*) FROM orders
9994

> exit
```

**Useful Queries**:
- `PRAGMA table_info(orders)` - Show schema
- `SELECT COUNT(*) FROM orders` - Verify row count
- `SELECT DISTINCT Region FROM orders` - List values
- `SELECT * FROM orders LIMIT 5` - Preview data

---

## 🚀 Execution Sequence

```
Step 1: SCRIPT 1 (Download)
        └─ Creates: data/raw/Sample - Superstore.csv
        
Step 2: SCRIPT 2 (Load)
        └─ Creates: data/processed/superstore.duckdb
        
Step 3: SCRIPT 3 (Metadata)
        └─ Creates: analytics/metadata/orders.yaml
        
Step 4: SCRIPT 4 (Dashboard)
        └─ Launches: http://localhost:8501
           Features: 3 tabs, filters, Claude AI
           
Step 5: SCRIPT 5 (Verify - optional)
        └─ Confirms: All components working
        
Step 6: SCRIPT 6 (SQL Shell - optional)
        └─ Explores: Database interactively
        
DEPLOY: Push to Streamlit Cloud
        └─ Live URL: https://agenticanalyticspc-[random].streamlit.app
```

---

## 📊 Data Summary

| Metric | Value |
|--------|-------|
| **Total Rows** | 9,994 |
| **Columns** | 21 |
| **Regions** | 4 (East, West, Central, South) |
| **Categories** | 3 (Furniture, Office Supplies, Technology) |
| **Segments** | 3 (Consumer, Corporate, Home Office) |
| **Total Sales** | $2,297,201 |
| **Total Profit** | $286,397 |
| **Total Orders** | 5,009 |
| **Unique Customers** | 793 |
| **Date Range** | 2015-2016 |

---

## 🔧 Command Cheat Sheet

```powershell
# Setup
uv venv
& .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

# Set API key
$env:ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY"

# Run Scripts 1-3
python analytics/01_download_dataset.py
python analytics/02_load_duckdb.py
python analytics/03_generate_metadata_draft.py

# Run Script 4 (Dashboard)
streamlit run app.py

# Run Script 5 (Verify)
python test_app.py

# Run Script 6 (SQL Shell)
python sql_shell.py

# Deploy to Cloud
git add .
git commit -m "Ready for deployment"
git push origin main
```

---

## ✅ Success Checklist

- [ ] Script 1 runs - CSV downloaded
- [ ] Script 2 runs - DuckDB created
- [ ] Script 3 runs - Metadata generated
- [ ] Script 4 launches - Dashboard opens
- [ ] Script 5 passes - All tests pass
- [ ] Script 6 works - SQL queries execute
- [ ] Deploy - Pushed to GitHub
- [ ] Cloud URL - Streamlit app live

---

## 📚 Quick Links

- **README**: Quick start guide
- **CLAUDE.md**: Detailed implementation
- **Requirements**: Python packages (`requirements.txt`)
- **API Key**: https://console.anthropic.com
- **Kaggle**: https://www.kaggle.com
- **Streamlit Cloud**: https://streamlit.io/cloud

---

## 🎯 Next Step

**Choose one**:

1. **Quick Test**
   ```powershell
   python test_app.py
   ```

2. **Launch Dashboard**
   ```powershell
   streamlit run app.py
   ```

3. **Explore Database**
   ```powershell
   python sql_shell.py
   ```

**All scripts ready to use! Pick one and start!** 🚀
