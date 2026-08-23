# Stage 1: Setup & Dataset Download

## What was done

### 1. Kaggle Authentication
- Created free Kaggle account at https://www.kaggle.com
- Generated API token from Account → Settings → API → "Create New Token"
- Token: `KGAT_a17dca5ed3380c9e5a031ec8b17e6a31`
- Username: `MOFIDANJUM`
- Saved to: `C:\Users\Sarah\.kaggle\kaggle.json`

### 2. Python Virtual Environment
- Created `.venv` using `uv venv`
- Python version: 3.14.7

### 3. Installed Packages
All installed via `uv pip install`:
- **kaggle** (2.2.4) — for downloading datasets
- **duckdb** (1.5.5) — database layer
- **pandas** (3.0.5) — data handling
- **pyyaml** (6.0.3) — metadata files
- **matplotlib** (3.11.1) — charting
- **anthropic** (1.0.0) — Claude API
- **duckdb-cli** (1.5.5) — CLI for interactive queries

### 4. Downloaded Superstore Dataset
- Source: Kaggle dataset `vivek468/superstore-dataset-final`
- Downloaded to: `data/raw/Sample - Superstore.csv`
- Size: ~2.3 MB
- Rows: 9,994
- Columns: 21 (Order ID, Sales, Profit, Region, Category, etc.)
- Encoding: latin-1 (handles special characters)

### 5. Created Project Structure
```
agentic-data-pipeline/
├── .venv/                    # Virtual environment
├── data/
│   ├── raw/                  # Downloaded CSV (gitignored)
│   ├── processed/            # DuckDB files
│   └── sample/               # Sample fixtures (200 rows)
├── analytics/
│   ├── output/               # Chart outputs
│   ├── metadata/             # Column metadata (YAML)
│   └── 01_download_dataset.py
│   └── 02_load_duckdb.py
├── .gitignore
└── sql_shell.py              # Interactive SQL terminal
```

### 6. Loaded Data into DuckDB
- Script: `analytics/02_load_duckdb.py`
- Database: `data/processed/superstore.duckdb`
- Table: `orders` (9,994 rows)
- Created via pandas → DuckDB for handling encoding issues

### 7. Enabled SQL Terminal
- Created `sql_shell.py` for interactive SQL queries
- Provides a prompt-based interface to query DuckDB

## How to use the SQL terminal

```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
& .venv\Scripts\python.exe sql_shell.py
```

Then type SQL queries at the `SQL>` prompt:
- Type query
- Press Enter to go to next line (or blank line to execute)
- Press Enter again to execute

### Example queries tested:
```sql
-- Show first 5 rows
SELECT * FROM orders LIMIT 5

-- Count rows by category
SELECT Category, COUNT(*) as count FROM orders GROUP BY Category

-- Sales by region (sorted)
SELECT Region, SUM(Sales) as total_sales FROM orders GROUP BY Region ORDER BY total_sales DESC

-- Table schema
PRAGMA table_info(orders)

-- Total row count
SELECT COUNT(*) FROM orders
```

## Columns in orders table
| Column | Type | Purpose |
|--------|------|---------|
| Row ID | BIGINT | Unique row identifier |
| Order ID | VARCHAR | Groups line items into orders |
| Order Date | VARCHAR | When order was placed |
| Ship Date | VARCHAR | When order shipped |
| Ship Mode | VARCHAR | Delivery method |
| Customer ID | VARCHAR | Customer identifier |
| Customer Name | VARCHAR | Customer name |
| Segment | VARCHAR | Consumer/Corporate/Home Office |
| Country | VARCHAR | Country (all US in this dataset) |
| City | VARCHAR | City |
| State | VARCHAR | State |
| Postal Code | BIGINT | ZIP code |
| Region | VARCHAR | East/West/Central/South |
| Product ID | VARCHAR | Product identifier |
| Category | VARCHAR | Furniture/Office Supplies/Technology |
| Sub-Category | VARCHAR | Detailed product type |
| Product Name | VARCHAR | Full product name |
| Sales | DOUBLE | Revenue (USD) |
| Quantity | BIGINT | Units ordered |
| Discount | DOUBLE | Discount applied |
| Profit | DOUBLE | Profit (can be negative) |

## Data Summary
- **Total Orders**: 9,994 line items
- **Categories**: 3 (Furniture: 2,121, Office Supplies: 6,026, Technology: 1,847)
- **Regions**: 4 (West: $725k, East: $679k, South: $392k, Central: $501k total sales)
- **Date Range**: 2015-2016

## Next: Stage 2 Verification
✅ DuckDB database created and queryable
✅ SQL terminal working
→ Ready for Stage 3: Metadata layer
