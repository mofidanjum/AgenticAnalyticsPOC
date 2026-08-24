# 🤖 Agentic Analytics POC - Complete Guide

**Build a Claude-powered analytics dashboard that answers natural language questions over your data.**

## 🎯 What is This?

An **Agentic Analytics POC** that demonstrates:
- 📥 **Data Pipeline**: Download → Load → Transform
- 📚 **Metadata Layer**: YAML schema for semantic understanding
- 🤖 **Claude AI**: Text-to-SQL translation & chart generation
- 📊 **Interactive Dashboard**: Filters, tabs (Visual/Data/SQL)
- 🚀 **Cloud Deployment**: Live on Streamlit Cloud 24/7

**Example**: User says *"Show me sales by region"* → Claude generates SQL → Executes → Returns chart ✨

---

## 🏗️ Architecture

```
Kaggle Dataset (CSV)
    ↓ [Script 1: Download]
data/raw/Sample - Superstore.csv
    ↓ [Script 2: Load]
data/processed/superstore.duckdb
    ↓ [Script 3: Metadata]
analytics/metadata/orders.yaml
    ↓ [Script 4: Dashboard]
Streamlit App (http://localhost:8501)
    ↓
User: "Show sales by region"
Claude AI analyzes → Generates SQL → Creates chart
```

---

## 📋 Scripts (in Build Order)

### **Script 1: Download Dataset**
**File**: `analytics/01_download_dataset.py`

**What it does**:
- Downloads Superstore dataset from Kaggle
- Creates sample fixture (200 rows for testing)

**Run**:
```powershell
python analytics/01_download_dataset.py
```

**Output**:
- `data/raw/Sample - Superstore.csv` (9,994 rows)
- `data/sample/superstore_sample.csv` (200 rows)

**Prerequisites**:
- Kaggle account
- API token at `~/.kaggle/kaggle.json`

---

### **Script 2: Load into DuckDB**
**File**: `analytics/02_load_duckdb.py`

**What it does**:
- Converts CSV to queryable DuckDB database
- Creates `orders` table (9,994 rows, 21 columns)
- Auto-deletes old database files to prevent lock conflicts

**Run**:
```powershell
python analytics/02_load_duckdb.py
```

**Output**:
- `data/processed/superstore.duckdb` (2.3 MB)

**Columns**:
Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Customer Name, Segment, Country, City, State, Postal Code, Region, Product ID, Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit

---

### **Script 3: Generate Metadata**
**File**: `analytics/03_generate_metadata_draft.py`

**What it does**:
- Introspects database schema
- Creates semantic metadata (YAML)
- Provides Claude with business context

**Run**:
```powershell
python analytics/03_generate_metadata_draft.py
```

**Output**:
- `analytics/metadata/orders.yaml` (column descriptions, roles, constraints)

---

### **Script 4: Dashboard App**
**File**: `app.py` (or `streamlit_app.py` for cloud)

**What it does**:
- Streamlit dashboard with 3 tabs (Visual, Data, SQL)
- Claude AI integration for chart generation
- Sidebar buttons: Refresh Data, Verify Data, Deploy

**Run Locally**:
```powershell
streamlit run app.py
```

**Access**: http://localhost:8501

**Features**:
- 📊 **Visual Tab**: Describe charts → Claude generates them
- 📋 **Data Tab**: Browse filtered data (4 regions, 3 categories, 3 segments)
- 🔍 **SQL Tab**: Write custom queries

---

### **Script 5: Test Script (Verification)**
**File**: `test_app.py`

**What it does**:
- Verifies all components working
- Tests database, KPIs, filters, visualizations, SQL, packages

**Run**:
```powershell
python test_app.py
```

**Output**:
```
✅ TEST 1: Database Connection
✅ TEST 2: KPI Metrics
✅ TEST 3: Filters
... (7 tests total)
🎉 ALL TESTS PASSED!
```

---

### **Script 6: SQL Shell (Interactive)**
**File**: `sql_shell.py`

**What it does**:
- Interactive SQL terminal for direct database queries
- Useful for exploration and debugging

**Run**:
```powershell
python sql_shell.py
```

**Example**:
```sql
SELECT Region, SUM(Sales) FROM orders GROUP BY Region
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Setup Environment
```powershell
# Create virtual environment
uv venv

# Activate
& .venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt

# Set Anthropic API key
$env:ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY"
```

### Step 2: Build Pipeline (Run Scripts 1-3)
```powershell
# Download data
python analytics/01_download_dataset.py

# Load to DuckDB
python analytics/02_load_duckdb.py

# Generate metadata
python analytics/03_generate_metadata_draft.py
```

### Step 3: Launch Dashboard (Script 4)
```powershell
streamlit run app.py
```

**Access**: http://localhost:8501 ✅

---

## 📊 Dashboard Features

### Sidebar Buttons
- **📥 Refresh Data** - Runs scripts 1-3 automatically
- **🧪 Verify Data** - Confirms database integrity (9,994 rows)
- **🚀 Deploy** - Pushes to GitHub (auto-redeploys on Streamlit Cloud)

### Three Tabs

**📊 Visual Tab** (Claude AI Chart Generation)
```
User Input: "Show sales by region as a bar chart"
↓
Claude generates Plotly code
↓
Chart displays automatically
```

**📋 Data Tab** (Filtered Data Browser)
- 21 columns from orders table
- Filter by Region, Category, Segment
- Sortable, searchable

**🔍 SQL Tab** (Custom Queries)
- Write any SQL
- Execute instantly
- See results in table

### KPI Cards
- 💰 Total Sales: $2,297,201
- 📈 Total Profit: $286,397
- 📋 Total Orders: 5,009
- 👥 Customers: 793

### Filters
- **Region**: East, West, Central, South
- **Category**: Furniture, Office Supplies, Technology
- **Segment**: Consumer, Corporate, Home Office

---

## 🌍 Deploy to Streamlit Cloud

### Prerequisites
- GitHub account (code must be pushed)
- Streamlit Cloud account
- Anthropic API key

### Steps

1. **Push to GitHub**
   ```powershell
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit: https://streamlit.io/cloud
   - Click "New app"

3. **Connect Repo**
   - Select: `AgenticAnalyticsPOC`
   - Branch: `main`
   - File: `streamlit_app.py`
   - Click "Deploy"

4. **Add Secrets** (while building)
   - Settings → Secrets
   - Paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY"
   KAGGLE_USERNAME = "YOUR_USERNAME"
   KAGGLE_API_TOKEN = "YOUR_TOKEN"
   ```

5. **Done!**
   - Live URL: `https://agenticanalyticspc-[random].streamlit.app`
   - Always on, shareable, auto-updates

---

## 📁 File Structure

```
agentic-data-pipeline/
├── README.md                           ← You are here
├── .claude/CLAUDE.md                   ← Project guide (detailed)
│
├── analytics/
│   ├── 01_download_dataset.py          ← Script 1: Download from Kaggle
│   ├── 02_load_duckdb.py               ← Script 2: Load to DuckDB
│   ├── 03_generate_metadata_draft.py   ← Script 3: Generate metadata
│   ├── metadata/
│   │   └── orders.yaml                 ← Semantic schema (auto-generated)
│   └── output/                         ← Generated charts (if any)
│
├── app.py                              ← Script 4: Main dashboard
├── streamlit_app.py                    ← Cloud entry point
├── test_app.py                         ← Script 5: Verification tests
├── sql_shell.py                        ← Script 6: Interactive SQL
│
├── data/
│   ├── raw/
│   │   └── Sample - Superstore.csv     ← Downloaded data (9,994 rows)
│   ├── processed/
│   │   └── superstore.duckdb           ← Database (queryable)
│   └── sample/
│       └── superstore_sample.csv       ← Test fixture (200 rows)
│
├── .streamlit/
│   ├── config.toml                     ← Dark theme settings
│   └── secrets.toml                    ← API keys (local template)
│
├── requirements.txt                    ← Python dependencies
├── .gitignore                          ← Git ignore rules
└── DEPLOY_LIVE.md                      ← Deployment guide
```

---

## 🔧 Technologies

| Technology | Purpose | Version |
|-----------|---------|---------|
| **Streamlit** | Web dashboard | 1.28+ |
| **DuckDB** | Database (in-process) | 0.10+ |
| **Pandas** | Data manipulation | 2.0+ |
| **Plotly** | Interactive charts | 5.0+ |
| **Claude API** | AI/LLM | Haiku model |
| **Python** | Runtime | 3.8+ |

---

## 📊 Data Summary

**Source**: Kaggle Superstore Dataset

| Metric | Value |
|--------|-------|
| Total Rows | 9,994 |
| Date Range | 2015-2016 |
| Regions | 4 (East, West, Central, South) |
| Categories | 3 (Furniture, Office Supplies, Technology) |
| Segments | 3 (Consumer, Corporate, Home Office) |
| Total Sales | $2,297,201 |
| Total Profit | $286,397 |
| Total Orders | 5,009 |
| Unique Customers | 793 |

---

## 🆘 Troubleshooting

### "Database not found"
**Solution**: Run Script 1 and 2
```powershell
python analytics/01_download_dataset.py
python analytics/02_load_duckdb.py
```

### "ANTHROPIC_API_KEY not found"
**Solution**: Set environment variable
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY"
```

### "Port 8501 already in use"
**Solution**: Use different port
```powershell
streamlit run app.py --server.port 8502
```

### "File is already open"
**Solution**: Close all Python processes
```powershell
Get-Process python | Stop-Process -Force
```

### Streamlit Cloud deployment fails
**Check**:
- Database file is committed to GitHub
- `requirements.txt` has no version conflicts
- API key added to Secrets

---

## 📚 Learning Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **DuckDB Docs**: https://duckdb.org/docs
- **Claude API**: https://console.anthropic.com
- **Plotly**: https://plotly.com/python

---

## ✅ Verification Checklist

Run this to verify everything works:
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

## 🎯 Next Steps

1. **Verify Locally**
   ```powershell
   python test_app.py
   ```

2. **Launch Dashboard**
   ```powershell
   streamlit run app.py
   ```

3. **Test Features**
   - Click "Refresh Data"
   - Click "Verify Data"
   - Go to Visual tab → Type "Show sales by region"
   - Go to Data tab → Browse data
   - Go to SQL tab → Run custom query

4. **Deploy to Cloud** (when ready)
   - Push to GitHub
   - Deploy on Streamlit Cloud
   - Add API key to secrets
   - Get live URL! 🚀

---

## 📞 Support

For issues or questions:
1. Check `.claude/CLAUDE.md` for detailed documentation
2. Run `test_app.py` to verify components
3. Check Streamlit logs if deploying
4. Review error messages for specific guidance

---

## 📝 License

This is a learning project. Feel free to modify and use as needed.

---

## 🎉 You're Ready!

All scripts are tested and working. Your analytics dashboard is ready to:
- ✅ Download data from Kaggle
- ✅ Load into DuckDB
- ✅ Generate smart visualizations with Claude
- ✅ Answer natural language questions
- ✅ Deploy 24/7 on Streamlit Cloud

**Start with**: `streamlit run app.py`

Enjoy! 🚀
