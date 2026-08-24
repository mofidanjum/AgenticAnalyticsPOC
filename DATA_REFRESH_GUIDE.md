# Data Refresh Guide - Kaggle to Target

## Overview
Complete instructions to refresh your Superstore dataset from Kaggle and update the entire pipeline.

---

## 🔄 Full Data Refresh Pipeline (Source → Target)

### Step 1: Download Fresh Data from Kaggle
```bash
python analytics/01_download_dataset.py
```

**What it does:**
- Downloads latest `vivek468/superstore-dataset-final` from Kaggle
- Saves to `data/raw/Sample - Superstore.csv`
- Creates sample fixture at `data/sample/superstore_sample.csv`
- **Prerequisites:** Kaggle API token at `~/.kaggle/kaggle.json`

**Output:**
```
✅ data/raw/Sample - Superstore.csv (2.3 MB, 9,994 rows)
✅ data/sample/superstore_sample.csv (200 rows)
```

---

### Step 2: Load into DuckDB
```bash
python analytics/02_load_duckdb.py
```

**What it does:**
- Reads CSV with `latin-1` encoding
- Creates/updates `data/processed/superstore.duckdb`
- Creates `orders` table with all 9,994 rows
- Validates schema

**Output:**
```
✅ data/processed/superstore.duckdb (queryable database)
📊 Table: orders (21 columns, 9,994 rows)
```

---

### Step 3: Generate/Update Metadata
```bash
python analytics/03_generate_metadata_draft.py
```

**What it does:**
- Introspects DuckDB table schema
- Auto-generates column descriptions
- Updates `analytics/metadata/orders.yaml`
- Infers data types and roles

**Output:**
```
✅ analytics/metadata/orders.yaml (updated with new data stats)
```

---

### Step 4: Verify Data Quality
```bash
python -c "
import duckdb
con = duckdb.connect('data/processed/superstore.duckdb', read_only=True)
result = con.sql('SELECT COUNT(*) as rows, COUNT(DISTINCT \"Order ID\") as orders FROM orders').fetchall()
print(f'✅ Total rows: {result[0][0]}, Unique orders: {result[0][1]}')
"
```

---

## 🤖 Prompting Claude for Data Refresh

### Full Refresh Command (Copy-Paste Ready)

```
I need to refresh my Agentic Analytics POC with fresh Kaggle data. Here's the complete pipeline:

1. Download: python analytics/01_download_dataset.py
2. Load: python analytics/02_load_duckdb.py  
3. Metadata: python analytics/03_generate_metadata_draft.py
4. Verify: python -c "import duckdb; con = duckdb.connect('data/processed/superstore.duckdb', read_only=True); print(con.sql('SELECT COUNT(*) FROM orders').fetchall())"

Please:
- Run all 4 steps in sequence
- Check for errors after each step
- Verify final row count matches expected
- Tell me if any step fails
```

---

## 📋 Individual Prompts to Claude

### Prompt 1: Just Download Data
```
Download fresh Superstore data from Kaggle:
python analytics/01_download_dataset.py

Verify:
- data/raw/Sample - Superstore.csv exists
- data/sample/superstore_sample.csv created
- Both files have correct row counts
```

### Prompt 2: Load into DuckDB
```
Load CSV data into DuckDB:
python analytics/02_load_duckdb.py

Verify:
- data/processed/superstore.duckdb created
- orders table has 9,994 rows
- All 21 columns present
```

### Prompt 3: Update Metadata
```
Generate updated metadata from fresh data:
python analytics/03_generate_metadata_draft.py

Then manually edit analytics/metadata/orders.yaml to add:
- Accurate column descriptions
- Data constraints (profit can be negative)
- Notable values section
```

### Prompt 4: Full Pipeline (Recommended)
```
Execute complete data refresh pipeline:

Step 1: python analytics/01_download_dataset.py
Step 2: python analytics/02_load_duckdb.py
Step 3: python analytics/03_generate_metadata_draft.py

Then verify with:
python -c "import duckdb; con = duckdb.connect('data/processed/superstore.duckdb'); print('Rows:', con.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0])"

Report:
- ✅/❌ Each step status
- Final row count
- Any errors encountered
```

---

## 🔄 Automated Refresh Script

Create `refresh_data.py`:

```python
#!/usr/bin/env python3
"""Complete data refresh pipeline"""
import subprocess
import sys

print("🔄 Starting Data Refresh Pipeline...\n")

steps = [
    ("📥 Downloading from Kaggle", "python analytics/01_download_dataset.py"),
    ("📚 Loading into DuckDB", "python analytics/02_load_duckdb.py"),
    ("📝 Generating Metadata", "python analytics/03_generate_metadata_draft.py"),
]

for step_name, command in steps:
    print(f"\n{step_name}")
    print(f"$ {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed at: {step_name}")
        sys.exit(1)
    print(f"✅ Complete: {step_name}")

print("\n🎉 Data refresh complete!")
```

**Run with:**
```bash
python refresh_data.py
```

---

## 📊 Source → Target Flow

```
📥 Source (Kaggle)
    ↓
🔽 Download (01_download_dataset.py)
    ↓
📄 Raw CSV (data/raw/Sample - Superstore.csv)
    ↓
🔄 Load (02_load_duckdb.py)
    ↓
🗄️ DuckDB (data/processed/superstore.duckdb)
    ↓
📚 Metadata (03_generate_metadata_draft.py)
    ↓
📋 YAML Schema (analytics/metadata/orders.yaml)
    ↓
🤖 Claude AI (Natural Language Processing)
    ↓
🎯 Target (Interactive Dashboard)
    ├─ Visual Charts
    ├─ Data Tables
    └─ SQL Queries
```

---

## 🔑 Environment Setup (One-Time)

### Kaggle API Token
```bash
# 1. Go to https://www.kaggle.com/settings/account
# 2. Download kaggle.json
# 3. Place at ~/.kaggle/kaggle.json
# 4. Run chmod 600 ~/.kaggle/kaggle.json (Mac/Linux)
```

### API Keys
```bash
# Set ANTHROPIC_API_KEY for Claude
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

---

## ✅ Verification Checklist

After refresh, verify:

```bash
# Check file sizes
ls -lh data/raw/Sample* data/processed/superstore.duckdb

# Count rows
python -c "import duckdb; con = duckdb.connect('data/processed/superstore.duckdb'); print('Rows:', con.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0])"

# Check metadata
python -c "import yaml; print(yaml.safe_load(open('analytics/metadata/orders.yaml'))['table'])"

# Test DuckDB query
python -c "import duckdb; con = duckdb.connect('data/processed/superstore.duckdb'); print(con.sql('SELECT Region, SUM(Sales) FROM orders GROUP BY Region').fetchdf())"
```

---

## 🚀 Redeploy After Refresh

Once data is refreshed locally:

```bash
# 1. Test locally
streamlit run app.py

# 2. Commit changes
git add data/processed/superstore.duckdb analytics/metadata/orders.yaml
git commit -m "Refresh: Updated Superstore data from Kaggle"

# 3. Push to GitHub
git push origin main

# 4. Streamlit Cloud auto-deploys!
# (Watch dashboard at https://share.streamlit.io)
```

---

## 🔧 Troubleshooting Refresh

| Error | Solution |
|-------|----------|
| **Kaggle API key not found** | Place token at `~/.kaggle/kaggle.json` |
| **DuckDB connection error** | Delete `data/processed/superstore.duckdb` and retry step 2 |
| **Row count mismatch** | Verify Kaggle dataset hasn't changed; check `01_download_dataset.py` encoding |
| **Metadata not updating** | Run `03_generate_metadata_draft.py` and manually edit YAML |

---

## 📝 Summary

**Quick Refresh Command to Give Claude:**

```
Run complete data refresh:

python analytics/01_download_dataset.py && \
python analytics/02_load_duckdb.py && \
python analytics/03_generate_metadata_draft.py && \
python -c "import duckdb; con = duckdb.connect('data/processed/superstore.duckdb'); print('✅ Final rows:', con.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0])"
```

**Then:**
1. Test with `streamlit run app.py`
2. Commit & push
3. Streamlit Cloud auto-deploys ✨

---

**All commands are production-ready. Copy-paste into Claude Code terminal!** 🚀
