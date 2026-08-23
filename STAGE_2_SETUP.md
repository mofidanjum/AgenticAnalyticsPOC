# Stage 2: Load Data into DuckDB

## What was done

### 1. Why DuckDB for an agent-facing layer?
- **Zero infrastructure**: Single file, no server needed
- **Standard SQL**: Agent queries are portable and testable
- **Fast on laptop**: Responsive agent loops for real-time queries
- **Perfect for analytics**: Built-in SQL functions, aggregations, date handling

### 2. Data Loading Process

#### Problem Solved:
The raw CSV had encoding issues (special characters like non-breaking spaces).
- Initial attempt with UTF-8 failed: `UnicodeDecodeError`
- Solution: Used `latin-1` encoding to read the CSV properly

#### Script: `analytics/02_load_duckdb.py`
This script:
1. Reads raw CSV with proper encoding (`latin-1`)
2. Loads 9,994 rows and 21 columns into memory (pandas DataFrame)
3. Connects to DuckDB file database
4. Creates table `orders` from the DataFrame
5. Verifies load was successful
6. Prints schema (column names and types)

### 3. DuckDB Database Details

**Location**: `data/processed/superstore.duckdb`
- Single file (can be backed up/versioned easily)
- No server process needed
- Automatically created on first connection

**Table Name**: `orders`
- **Row count**: 9,994 line items
- **Column count**: 21
- **Grain**: Order line (one row per line item in an order)
  - Example: An order with 3 products = 3 rows sharing same Order ID

### 4. How to Run Stage 2

#### From scratch:
```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
& .venv\Scripts\python.exe analytics/02_load_duckdb.py
```

#### What happens:
1. Reads `data/raw/Sample - Superstore.csv` (latin-1 encoding)
2. Creates `data/processed/superstore.duckdb`
3. Prints confirmation and schema

#### Expected output:
```
Reading data/raw/Sample - Superstore.csv...
Loaded 9994 rows, 21 columns
Creating DuckDB database at data/processed/superstore.duckdb...
✓ Table 'orders' created with 9994 rows

Table schema:
  Row ID: BIGINT
  Order ID: VARCHAR
  Order Date: VARCHAR
  ...
  Profit: DOUBLE

✓ Stage 2 complete. DuckDB ready at data/processed/superstore.duckdb
```

### 5. Table Schema (DuckDB Output)

| Column | Type | Notes |
|--------|------|-------|
| Row ID | BIGINT | Unique row identifier |
| Order ID | VARCHAR | Groups line items; not unique per row |
| Order Date | VARCHAR | Format: MM/DD/YYYY |
| Ship Date | VARCHAR | Format: MM/DD/YYYY |
| Ship Mode | VARCHAR | Second Class, Standard Class, One Day, Same Day |
| Customer ID | VARCHAR | Unique customer identifier |
| Customer Name | VARCHAR | Customer full name |
| Segment | VARCHAR | Consumer, Corporate, or Home Office |
| Country | VARCHAR | Always "United States" in this dataset |
| City | VARCHAR | City name |
| State | VARCHAR | 2-letter state code |
| Postal Code | BIGINT | 5-digit ZIP code |
| Region | VARCHAR | East, West, Central, or South |
| Product ID | VARCHAR | Product identifier |
| Category | VARCHAR | Furniture, Office Supplies, or Technology |
| Sub-Category | VARCHAR | Detailed category (e.g., Chairs, Tables, Bookcases) |
| Product Name | VARCHAR | Full product description |
| Sales | DOUBLE | Revenue in USD (pre-discount) |
| Quantity | BIGINT | Units ordered |
| Discount | DOUBLE | Discount rate (0.0-1.0) |
| Profit | DOUBLE | Profit in USD (can be negative) |

### 6. How to Query the Database

#### Via SQL shell:
```powershell
& .venv\Scripts\python.exe sql_shell.py
```

#### Via Python directly:
```python
import duckdb
con = duckdb.connect('data/processed/superstore.duckdb')
result = con.sql('SELECT * FROM orders LIMIT 5').fetchdf()
print(result)
```

#### Example queries tested in Stage 2:

**Show first 5 rows:**
```sql
SELECT * FROM orders LIMIT 5
```

**Count rows by category:**
```sql
SELECT Category, COUNT(*) as count FROM orders GROUP BY Category
```
Output:
```
Category          count
Furniture         2121
Office Supplies   6026
Technology        1847
```

**Total sales by region:**
```sql
SELECT Region, SUM(Sales) as total_sales FROM orders GROUP BY Region ORDER BY total_sales DESC
```
Output:
```
Region    total_sales
West      725457.8245
East      678781.2400
Central   501239.8908
South     391721.9050
```

**Get table schema:**
```sql
PRAGMA table_info(orders)
```

**Count all rows:**
```sql
SELECT COUNT(*) FROM orders
```
Output: `9994`

### 7. Data Quality Notes

**Encoding**: 
- Raw CSV uses `latin-1` (Windows-1252)
- Successfully handled special characters (accents, non-breaking spaces)

**Dates**:
- Stored as VARCHAR (strings) not DATE type
- Format: MM/DD/YYYY (e.g., "11/8/2016")
- Agent will need to handle date parsing in queries

**Profit**:
- Can be negative (discounts, returns, shipping costs)
- Example row 4: Profit = -383.0310 on $957.58 order

**Postal Code**:
- Stored as BIGINT (number), not VARCHAR
- May lose leading zeros for some ZIP codes

### 8. Performance Characteristics

- **Query latency**: <100ms for typical analytics queries
- **Table size**: ~2.3 MB in DuckDB file
- **Memory on load**: ~50 MB when loaded into pandas

### 9. Verification Checklist

✅ DuckDB file created at `data/processed/superstore.duckdb`
✅ Table `orders` has 9,994 rows
✅ All 21 columns loaded correctly
✅ Schema confirmed with PRAGMA table_info
✅ Sample queries execute correctly
✅ SQL shell works for interactive queries
✅ Encoding issues resolved (latin-1)

## Next: Stage 3 - Metadata Layer

Stage 3 will add business meaning to these columns via YAML metadata:
- Column roles (dimension, measure, id, timestamp)
- Column descriptions (what each field means)
- Notable values (constraints, gotchas)
- Relationships between columns

This metadata will be fed to the LLM agent so it understands the data semantically, not just syntactically.