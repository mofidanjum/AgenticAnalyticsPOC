"""
Simple query runner - no API key needed, just SQL + answers
"""

import duckdb

DB_PATH = "data/processed/superstore.duckdb"
con = duckdb.connect(DB_PATH)

def run_query(sql):
    """Execute SQL and return results."""
    try:
        result = con.sql(sql).fetchdf()
        return result.to_string() if len(result) > 0 else "No results"
    except Exception as e:
        return f"Error: {str(e)}"

# Test queries
print("=" * 60)
print("Direct SQL Query Runner (No API Key Needed)")
print("=" * 60)

print("\n📊 Query 1: Total sales by region\n")
sql = "SELECT region, SUM(sales) as total_sales FROM orders GROUP BY region ORDER BY total_sales DESC"
print(f"SQL: {sql}\n")
result = run_query(sql)
print(f"Results:\n{result}")

print("\n" + "=" * 60)
print("\n📊 Query 2: Average profit by category\n")
sql = "SELECT category, AVG(profit) as avg_profit, COUNT(*) as item_count FROM orders GROUP BY category ORDER BY avg_profit DESC"
print(f"SQL: {sql}\n")
result = run_query(sql)
print(f"Results:\n{result}")

print("\n" + "=" * 60)
print("\n📊 Query 3: Top 5 products by profit\n")
sql = "SELECT \"Product Name\", SUM(profit) as total_profit FROM orders GROUP BY \"Product Name\" ORDER BY total_profit DESC LIMIT 5"
print(f"SQL: {sql}\n")
result = run_query(sql)
print(f"Results:\n{result}")

print("\n" + "=" * 60)
print("\n📊 Query 4: Orders by segment\n")
sql = "SELECT segment, COUNT(DISTINCT \"Order ID\") as order_count, SUM(sales) as total_sales FROM orders GROUP BY segment ORDER BY total_sales DESC"
print(f"SQL: {sql}\n")
result = run_query(sql)
print(f"Results:\n{result}")

print("\n" + "=" * 60)
print("\nDone!")
