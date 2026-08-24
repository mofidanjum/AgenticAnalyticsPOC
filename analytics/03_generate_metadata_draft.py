"""
Stage 3: Generate metadata draft from DuckDB introspection
Analyzes the orders table and creates a YAML template describing columns semantically.
The output is a starting point for hand-editing with business meanings.
"""

import duckdb
import yaml
from pathlib import Path
import time

DB_PATH = "data/processed/superstore.duckdb"
METADATA_DIR = Path("analytics/metadata")
METADATA_FILE = METADATA_DIR / "orders.yaml"

METADATA_DIR.mkdir(parents=True, exist_ok=True)

# Wait a moment to ensure DB is fully ready
time.sleep(0.5)

con = duckdb.connect(DB_PATH)

try:
    # Get schema
    schema = con.sql("DESCRIBE orders").fetchall()
    columns = {}

    print(f"Introspecting {DB_PATH}...")
    for col_name, col_type, *_ in schema:
        col_name_lower = col_name.lower()

        # Get distinct count and sample values
        try:
            distinct_count = con.sql(f"SELECT COUNT(DISTINCT \"{col_name}\") FROM orders").fetchall()[0][0]
            min_val = con.sql(f"SELECT MIN(\"{col_name}\") FROM orders").fetchall()[0][0]
            max_val = con.sql(f"SELECT MAX(\"{col_name}\") FROM orders").fetchall()[0][0]
        except:
            distinct_count = None
            min_val = None
            max_val = None

        # Infer role and unit based on column name and type
        role = "dimension"
        unit = None

        if "id" in col_name_lower or "name" in col_name_lower:
            role = "id" if "id" in col_name_lower else "dimension"
        elif "date" in col_name_lower:
            role = "timestamp"
        elif col_name_lower in ["sales", "profit", "discount", "quantity"]:
            role = "measure"
            if "sales" in col_name_lower or "profit" in col_name_lower:
                unit = "usd"
            elif "discount" in col_name_lower:
                unit = "percent"
            elif "quantity" in col_name_lower:
                unit = "count"

        columns[col_name_lower] = {
            "type": col_type,
            "role": role,
            "unit": unit,
            "distinct_count": distinct_count,
            "description": f"[Edit: describe what {col_name} means]"
        }

    # Build metadata structure
    metadata = {
        "table": "orders",
        "description": "[Edit: describe the table, grain, and notable characteristics]",
        "columns": columns,
        "relationships": [],
        "notable_values": [
            "[Edit: add constraints, gotchas, edge cases]"
        ]
    }

    # Write to YAML
    print(f"Writing metadata draft to {METADATA_FILE}...")
    with open(METADATA_FILE, "w") as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✓ Metadata draft created at {METADATA_FILE}")
    print(f"Next: Open the file and hand-edit column descriptions and roles")
finally:
    # Close connection to release file lock
    con.close()
    print("✓ Connection closed, file lock released")
