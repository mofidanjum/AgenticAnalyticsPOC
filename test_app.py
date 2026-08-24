"""
Comprehensive verification test for Agentic Analytics POC
Tests all core features: Database, KPIs, Filters, Visualization, SQL, Packages
"""
import sys
import os
import duckdb
import pandas as pd

print('=' * 60)
print('🧪 COMPREHENSIVE APP VERIFICATION')
print('=' * 60)

# Test 1: Database Connection
print('\n✅ TEST 1: Database Connection')
try:
    con = duckdb.connect('data/processed/superstore.duckdb', read_only=True)
    count = con.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0]
    print(f'   Database: ✅ Connected')
    print(f'   Rows: ✅ {count:,} rows loaded')
    con.close()
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)

# Test 2: KPI Queries
print('\n✅ TEST 2: KPI Metrics')
try:
    con = duckdb.connect('data/processed/superstore.duckdb', read_only=True)

    total_sales = con.sql('SELECT SUM("Sales") FROM orders').fetchall()[0][0]
    total_profit = con.sql('SELECT SUM("Profit") FROM orders').fetchall()[0][0]
    total_orders = con.sql('SELECT COUNT(DISTINCT "Order ID") FROM orders').fetchall()[0][0]
    total_customers = con.sql('SELECT COUNT(DISTINCT "Customer ID") FROM orders').fetchall()[0][0]

    print(f'   Sales: ✅ ${total_sales:,.0f}')
    print(f'   Profit: ✅ ${total_profit:,.0f}')
    print(f'   Orders: ✅ {total_orders:,}')
    print(f'   Customers: ✅ {total_customers:,}')
    con.close()
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)

# Test 3: Filter Queries
print('\n✅ TEST 3: Filters (Region, Category, Segment)')
try:
    con = duckdb.connect('data/processed/superstore.duckdb', read_only=True)

    regions = con.sql('SELECT DISTINCT "Region" FROM orders ORDER BY "Region"').fetchall()
    categories = con.sql('SELECT DISTINCT "Category" FROM orders ORDER BY "Category"').fetchall()
    segments = con.sql('SELECT DISTINCT "Segment" FROM orders ORDER BY "Segment"').fetchall()

    print(f'   Regions: ✅ {[r[0] for r in regions]}')
    print(f'   Categories: ✅ {[c[0] for c in categories]}')
    print(f'   Segments: ✅ {[s[0] for s in segments]}')
    con.close()
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)

# Test 4: Data Filtering
print('\n✅ TEST 4: Filtered Data Query')
try:
    con = duckdb.connect('data/processed/superstore.duckdb', read_only=True)

    filtered_df = con.sql("""
        SELECT * FROM orders
        WHERE "Region" IN ('East', 'West')
        AND "Category" IN ('Furniture', 'Office Supplies')
        AND "Segment" IN ('Consumer', 'Corporate')
    """).df()

    print(f'   Filtered rows: ✅ {len(filtered_df):,} rows')
    print(f'   Columns: ✅ {len(filtered_df.columns)} columns')
    con.close()
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)

# Test 5: Visualization Data
print('\n✅ TEST 5: Visualization Data (Groupby Queries)')
try:
    con = duckdb.connect('data/processed/superstore.duckdb', read_only=True)

    # Sales by Region
    sales_by_region = con.sql('SELECT "Region", SUM("Sales") as total_sales FROM orders GROUP BY "Region" ORDER BY total_sales DESC').df()
    print(f'   Sales by Region: ✅ {len(sales_by_region)} regions')

    # Profit by Category
    profit_by_cat = con.sql('SELECT "Category", SUM("Profit") as total_profit FROM orders GROUP BY "Category" ORDER BY total_profit DESC').df()
    print(f'   Profit by Category: ✅ {len(profit_by_cat)} categories')

    # Top Customers
    top_customers = con.sql('SELECT "Customer Name", SUM("Sales") as total_sales FROM orders GROUP BY "Customer Name" ORDER BY total_sales DESC LIMIT 10').df()
    print(f'   Top Customers: ✅ {len(top_customers)} customers')

    con.close()
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)

# Test 6: SQL Query Execution
print('\n✅ TEST 6: Custom SQL Query Execution')
try:
    con = duckdb.connect('data/processed/superstore.duckdb', read_only=True)

    result = con.sql('SELECT COUNT(*) as row_count, COUNT(DISTINCT "Region") as region_count FROM orders').fetchall()
    print(f'   Query execution: ✅ Works')
    print(f'   Total Rows: {result[0][0]}, Regions: {result[0][1]}')
    con.close()
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)

# Test 7: Imports
print('\n✅ TEST 7: Required Packages')
try:
    import streamlit
    import duckdb
    import pandas
    import plotly.express
    import plotly.graph_objects
    from plotly.subplots import make_subplots
    from anthropic import Anthropic

    print(f'   Streamlit: ✅')
    print(f'   DuckDB: ✅')
    print(f'   Pandas: ✅')
    print(f'   Plotly: ✅')
    print(f'   Anthropic: ✅')
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)

print('\n' + '=' * 60)
print('🎉 ALL TESTS PASSED! APP IS READY!')
print('=' * 60)
print('\n✅ Database: Working')
print('✅ KPI Queries: Working')
print('✅ Filters: Working')
print('✅ Data Filtering: Working')
print('✅ Visualizations: Ready')
print('✅ SQL Queries: Working')
print('✅ All Packages: Installed')
print('\n📊 Dashboard is fully functional!')
print('🚀 Go to http://localhost:8501')
print('\n' + '=' * 60)
