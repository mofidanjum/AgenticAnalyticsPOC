import duckdb
import json

con = duckdb.connect('data/processed/superstore.duckdb')

data = {}

data['region'] = con.sql('SELECT Region, SUM(Sales) as sales, SUM(Profit) as profit FROM orders GROUP BY Region ORDER BY sales DESC').fetchall()
data['category'] = con.sql('SELECT Category, SUM(Sales) as sales, SUM(Profit) as profit FROM orders GROUP BY Category ORDER BY sales DESC').fetchall()
data['subcat'] = con.sql('SELECT "Sub-Category", SUM(Sales) as sales, SUM(Profit) as profit FROM orders GROUP BY "Sub-Category" ORDER BY sales DESC').fetchall()
data['segment'] = con.sql('SELECT Segment, SUM(Sales) as sales, COUNT(DISTINCT "Order ID") as orders FROM orders GROUP BY Segment ORDER BY sales DESC').fetchall()

data['trend'] = con.sql("""
  SELECT
    CAST(SPLIT_PART("Order Date", '/', 3) AS INT) as yr,
    CAST(SPLIT_PART("Order Date", '/', 1) AS INT) as mo,
    SUM(Sales) as sales,
    SUM(Profit) as profit
  FROM orders
  GROUP BY yr, mo
  ORDER BY yr, mo
""").fetchall()

data['top_products'] = con.sql('SELECT "Product Name", SUM(Sales) as sales, SUM(Profit) as profit FROM orders GROUP BY "Product Name" ORDER BY profit DESC LIMIT 10').fetchall()
data['bottom_products'] = con.sql('SELECT "Product Name", SUM(Sales) as sales, SUM(Profit) as profit FROM orders GROUP BY "Product Name" ORDER BY profit ASC LIMIT 10').fetchall()
data['kpi'] = con.sql('SELECT SUM(Sales), SUM(Profit), COUNT(DISTINCT "Order ID"), COUNT(DISTINCT "Customer ID"), AVG(Discount) FROM orders').fetchall()
data['ship'] = con.sql('SELECT "Ship Mode", COUNT(*) as cnt, SUM(Sales) as sales FROM orders GROUP BY "Ship Mode" ORDER BY sales DESC').fetchall()
data['state'] = con.sql('SELECT State, SUM(Sales) as sales, SUM(Profit) as profit FROM orders GROUP BY State ORDER BY sales DESC LIMIT 15').fetchall()

with open('scratch_dashboard_data.json', 'w') as f:
    json.dump(data, f, default=str, indent=2)

print("Exported successfully")
print(json.dumps(data, default=str, indent=2)[:3000])
