"""
Interactive SQL shell for DuckDB
Type SQL queries and see results immediately
"""

import duckdb
import sys

DB_PATH = "data/processed/superstore.duckdb"
con = duckdb.connect(DB_PATH)

print(f"Connected to {DB_PATH}")
print("Type SQL queries (press Enter twice to execute)")
print("Type 'exit' to quit\n")

while True:
    try:
        lines = []
        while True:
            line = input("SQL> " if not lines else "   > ").strip()
            if line.lower() == "exit":
                sys.exit(0)
            if line:
                lines.append(line)
            elif lines:
                break

        query = " ".join(lines)
        if not query:
            continue

        result = con.sql(query).fetchdf()
        print(result.to_string())
        print()
    except KeyboardInterrupt:
        print("\nBye!")
        break
    except Exception as e:
        print(f"Error: {e}\n")

con.close()
