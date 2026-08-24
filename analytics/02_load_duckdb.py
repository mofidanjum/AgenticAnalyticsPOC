"""
Stage 2: Load Superstore CSV into DuckDB
Converts raw CSV (with encoding issues) into a queryable DuckDB database.

Why DuckDB for an agent-facing layer:
- Zero infrastructure (single file, no server)
- Speaks standard SQL so agent queries are portable
- Fast enough on laptop for responsive agent loops
"""

import duckdb
import pandas as pd
from pathlib import Path

# Paths
RAW_CSV = "data/raw/Sample - Superstore.csv"
DB_PATH = "data/processed/superstore.duckdb"

# Create output directory if it doesn't exist
Path("data/processed").mkdir(parents=True, exist_ok=True)

# Read CSV (with latin-1 encoding to handle special chars)
print(f"Reading {RAW_CSV}...")
df = pd.read_csv(RAW_CSV, encoding="latin-1")
print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

# Connect to DuckDB and create table
print(f"Creating DuckDB database at {DB_PATH}...")
con = duckdb.connect(DB_PATH)

try:
    # Create table from dataframe
    con.sql("CREATE OR REPLACE TABLE orders AS SELECT * FROM df")

    # Verify
    result = con.sql("SELECT COUNT(*) as row_count FROM orders").fetchall()
    print(f"✓ Table 'orders' created with {result[0][0]} rows")

    # Show schema
    schema = con.sql("DESCRIBE orders").fetchall()
    print("\nTable schema:")
    for col_name, col_type, *_ in schema:
        print(f"  {col_name}: {col_type}")

    print(f"\n✓ Stage 2 complete. DuckDB ready at {DB_PATH}")
finally:
    # Close connection to release file lock
    con.close()
    print("✓ Connection closed, file lock released")
