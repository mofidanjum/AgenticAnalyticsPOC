# Stage 3: Generate Metadata Layer

## What was done

### 1. What is the metadata layer?

The metadata layer is a YAML file that describes the `orders` table semantically (not syntactically). It tells the LLM agent:
- What each column represents (role: id, dimension, measure, timestamp)
- Business meaning (not just type)
- Units (USD, percent, count, etc.)
- Notable constraints (e.g., profit can be negative)

This is fed to the agent's system prompt so Claude understands the data at a business level, not just column names and types.

### 2. Why YAML?

- **Human-readable** and easy to hand-edit
- **Machine-parseable** by Python (yaml module)
- **Hierarchical** structure (table → columns → column properties)
- **Version-control friendly** (plain text, easy diffs)

### 3. Two-step process

#### Step 1: Auto-generate metadata draft

Script: `analytics/03_generate_metadata_draft.py`

This script:
1. Connects to DuckDB
2. Introspects the `orders` table schema
3. Counts distinct values per column
4. Infers column roles based on names (e.g., "date" → timestamp, "sales" → measure)
5. Generates a YAML template at `analytics/metadata/orders.yaml`

**What it creates**:
- Column list with auto-inferred roles and units
- Placeholder descriptions: `[Edit: describe what X means]`
- Distinct counts and min/max values for each column

#### Step 2: Hand-edit with business meaning

File to edit: `analytics/metadata/orders.yaml`

Manually add:
- **Table description**: Grain, scope, notable characteristics
- **Column descriptions**: Business meaning (not just type)
- **Units**: USD, percent, count, days, etc.
- **Notable values**: Gotchas, constraints, edge cases

### 4. How to Run Stage 3

#### From scratch:

```powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
& .venv\Scripts\python.exe analytics/03_generate_metadata_draft.py
```

#### Then edit:
Open `analytics/metadata/orders.yaml` and update descriptions and constraints.

### 5. Metadata File Structure

**Location**: `analytics/metadata/orders.yaml`

**Structure**:
```yaml
table: orders                          # Table name
description: >                         # What this table is
  One row per line item...
  
columns:
  order_id:
    type: VARCHAR                      # SQL type
    role: id                          # id | dimension | measure | timestamp
    unit: null                        # Optional: usd, percent, count, etc.
    distinct_count: 5009              # Cardinality (from introspection)
    description: Groups line items... # Business meaning
  
  sales:
    type: DOUBLE
    role: measure
    unit: usd
    description: Revenue for this line item...

notable_values:                        # Constraints and gotchas
  - "profit can be negative..."
  - "order_id is not unique per row..."
```

### 6. Column Metadata Reference

| Column | Role | Unit | Description |
|--------|------|------|-------------|
| row_id | id | — | Unique row identifier per line item |
| order_id | id | — | Groups line items (not unique per row) |
| order_date | timestamp | — | When placed (MM/DD/YYYY string) |
| ship_date | timestamp | — | When shipped (MM/DD/YYYY string) |
| ship_mode | dimension | — | Same Day, One Day, Second Class, Standard Class |
| customer_id | id | — | Unique customer identifier |
| customer_name | dimension | — | Full name of customer |
| segment | dimension | — | Consumer, Corporate, Home Office |
| country | dimension | — | Always "United States" |
| city | dimension | — | Shipping city |
| state | dimension | — | 2-letter state code |
| postal_code | dimension | — | ZIP code |
| region | dimension | — | East, West, Central, South |
| product_id | id | — | Unique product identifier |
| category | dimension | — | Furniture, Office Supplies, Technology |
| sub_category | dimension | — | Chairs, Tables, Bookcases, Copiers, etc. |
| product_name | dimension | — | Full product description |
| sales | measure | usd | Revenue pre-discount |
| quantity | measure | count | Units ordered |
| discount | measure | percent | 0.0 (no discount) to 1.0 (100% off) |
| profit | measure | usd | Profit after costs (can be negative) |

### 7. Notable Values (Gotchas)

1. **Profit can be negative**
   - Caused by deep discounts, returns, or shipping costs exceeding revenue
   - Don't assume `SUM(profit) > 0`
   - Example: An item with $100 sales might have -$50 profit due to discount

2. **Order ID is not unique per row**
   - One order can span multiple rows (one per product)
   - Example: Order #12345 has 3 products = 3 rows with order_id = #12345
   - Use `(order_id, product_id)` to uniquely identify a line item

3. **Dates are VARCHAR strings**
   - Not DATE type, so queries must handle as strings
   - Format: MM/DD/YYYY (e.g., "11/8/2016")
   - Agent queries will need to parse or convert

4. **Discount can exceed sales value**
   - On loss-making items, discount percentage can be >100% of original price
   - Indicates business absorbing loss to clear inventory

5. **All orders are US-based**
   - Country column always = "United States"
   - Simplifies geographic queries (no international filtering needed)

### 8. Metadata Verification

✅ `analytics/metadata/orders.yaml` created and hand-edited
✅ Table description captures grain and scope
✅ All 21 columns documented with roles and descriptions
✅ Units specified for measure columns
✅ Notable values documented
✅ YAML syntax validated (parseable by Python yaml module)

### 9. How the Agent Will Use This

**In Stage 4** (Text-to-SQL agent):
1. Agent's system prompt loads this metadata
2. Claude sees column roles, descriptions, and units
3. When user asks "What were total sales by region?", Claude understands:
   - `sales` is a measure in USD (not just a column)
   - `region` is a dimension with exactly 4 values
   - Can write SQL: `SELECT region, SUM(sales) FROM orders GROUP BY region`

**In Stage 5** (Agent with charts):
1. Agent knows column units and types
2. Claude proposes meaningful chart specs
3. Example: For "sales trend" → suggests line chart with USD y-axis
4. For "category breakdown" → suggests pie chart

### 10. Next: Stage 4 - Build Text-to-SQL Agent

Stage 4 will:
1. Load this metadata into the agent's system prompt
2. Define a `run_sql(query)` tool for Claude
3. Create an agent loop that converts questions → SQL → answers
4. Use Claude API with tool use to reason about data

The agent will reference this metadata to understand what it's querying.

---

## Checklist

✅ Stage 1: Download dataset
✅ Stage 2: Load into DuckDB  
✅ Stage 3: Generate and edit metadata ← **YOU ARE HERE**
→ Stage 4: Build text-to-SQL agent
→ Stage 5: Add charting capability
→ Stage 6: Package as Claude Skill (optional)
