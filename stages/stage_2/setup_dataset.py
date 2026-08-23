"""
Dataset Setup - No Download Needed
Uses existing data/raw/Sample - Superstore.csv
Creates DuckDB and metadata automatically
"""

import duckdb
import yaml
from pathlib import Path

def create_duckdb_table(csv_file, table_name, db_path):
    """Load CSV into DuckDB."""
    con = duckdb.connect(db_path)

    try:
        con.sql(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{csv_file}')
        """)

        row_count = con.sql(f"SELECT COUNT(*) FROM {table_name}").fetchall()[0][0]
        print(f"✅ Created table '{table_name}' with {row_count} rows")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

def generate_metadata(table_name, db_path):
    """Auto-generate metadata from DuckDB table."""
    con = duckdb.connect(db_path)

    columns = con.sql(f"PRAGMA table_info({table_name})").fetchall()

    metadata = {
        "table": table_name,
        "description": f"Superstore sales data - 9,994 rows, 21 columns. US retail sales 2015-2016.",
        "columns": {}
    }

    for col_name, col_type, *_ in columns:
        metadata["columns"][col_name] = {
            "type": col_type,
            "role": infer_role(col_name, col_type),
            "description": f"{col_name} ({col_type})"
        }

    metadata_file = f"analytics/metadata/{table_name}.yaml"
    Path("analytics/metadata").mkdir(exist_ok=True)

    with open(metadata_file, 'w') as f:
        yaml.dump(metadata, f)

    print(f"✅ Metadata saved to {metadata_file}")
    return metadata_file

def infer_role(col_name, col_type):
    """Infer column role from name and type."""
    col_lower = col_name.lower()

    if 'id' in col_lower:
        return 'id'
    elif any(x in col_lower for x in ['date', 'time']):
        return 'timestamp'
    elif col_type in ['BIGINT', 'DOUBLE']:
        return 'measure'
    else:
        return 'dimension'

def main():
    """Setup DuckDB and metadata."""
    try:
        print("\n" + "="*60)
        print("Dataset Setup - Superstore")
        print("="*60)

        csv_file = "data/raw/Sample - Superstore.csv"

        # Check if CSV exists
        if not Path(csv_file).exists():
            print(f"❌ CSV file not found: {csv_file}")
            print(f"\nPlease download the dataset first:")
            print(f"  & .venv\\Scripts\\python.exe analytics/01_download_dataset.py")
            return

        print(f"\n📄 Using: {csv_file}")

        db_path = "data/processed/superstore.duckdb"
        table_name = "orders"

        print(f"\n⏳ Creating DuckDB table...")
        if create_duckdb_table(csv_file, table_name, db_path):
            print(f"\n⏳ Generating metadata...")
            metadata_file = generate_metadata(table_name, db_path)

            print("\n" + "="*60)
            print("✅ Setup Complete!")
            print("="*60)
            print(f"Database: {db_path}")
            print(f"Table: {table_name}")
            print(f"Metadata: {metadata_file}")
            print("\nNow run:")
            print(f"  $env:ANTHROPIC_API_KEY = \"your-key\"")
            print(f"  & .venv\\Scripts\\python.exe analytics/agent_with_charts.py")
            print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
