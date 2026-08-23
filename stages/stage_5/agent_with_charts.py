"""
Stage 5: Text-to-SQL Agent with Charting
Extends Stage 4 agent with visualization capability using matplotlib.
"""

import os
import json
import duckdb
import yaml
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = "data/processed/superstore.duckdb"
con = duckdb.connect(DB_PATH)
OUTPUT_DIR = Path("analytics/output")
OUTPUT_DIR.mkdir(exist_ok=True)

with open("analytics/metadata/orders.yaml") as f:
    metadata = yaml.safe_load(f)

columns_info = []
for col_name, col_info in metadata["columns"].items():
    role = col_info.get("role", "unknown")
    unit = col_info.get("unit", "")
    desc = col_info.get("description", "")
    unit_str = f" (in {unit})" if unit else ""
    columns_info.append(f"- {col_name} ({col_info['type']}, {role}){unit_str}: {desc}")

columns_text = "\n".join(columns_info)
notable_values_text = "\n".join([f"- {v}" for v in metadata.get("notable_values", [])])

SYSTEM_PROMPT = f"""You are an analytics assistant that answers questions about retail sales data with visualizations.

You have access to a DuckDB database with one table: "orders"

TABLE DESCRIPTION:
{metadata['description']}

COLUMNS:
{columns_text}

IMPORTANT CONSTRAINTS:
{notable_values_text}

When answering questions:
1. You have two tools: "run_sql" to query data and "render_chart" to create visualizations
2. Always propose a SQL query first to get the data
3. If the question asks for trends, comparisons, or distributions, create a chart using render_chart
4. Then provide a natural language answer based on the results
5. Be precise with column names — quote column names with spaces like "Order Date", "Order ID", "Product Name"
6. Handle dates carefully — they are stored as VARCHAR strings (MM/DD/YYYY) in "Order Date" and "Ship Date" columns
7. Remember profit can be negative

Chart selection guide:
- Trend over time → type: "line"
- Comparing categories → type: "bar"
- Multiple series comparison → type: "grouped_bar"
- Distribution → type: "histogram"

When calling render_chart, ensure:
- x, y, series fields match actual column names from your query results
- title describes what the chart shows"""

tools = [
    {
        "name": "run_sql",
        "description": "Execute a SQL query against the orders table and return results",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT only)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "render_chart",
        "description": "Create a visualization of query results",
        "input_schema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["line", "bar", "grouped_bar", "histogram"],
                    "description": "Chart type"
                },
                "x": {
                    "type": "string",
                    "description": "Column name for x-axis"
                },
                "y": {
                    "type": "string",
                    "description": "Column name for y-axis (numeric)"
                },
                "series": {
                    "type": "string",
                    "description": "Optional column name for grouping/coloring (for line/bar charts)"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                }
            },
            "required": ["type", "x", "y", "title"]
        }
    }
]

def run_sql(query: str) -> str:
    """Execute SQL query and return results as formatted text."""
    try:
        result = con.sql(query).fetchdf()
        if len(result) == 0:
            return "Query returned no results."
        return result.to_string()
    except Exception as e:
        return f"SQL Error: {str(e)}"

def render_chart(chart_spec: dict, query_data: pd.DataFrame) -> str:
    """Create and save a chart from query results."""
    try:
        chart_type = chart_spec.get("type")
        x = chart_spec.get("x")
        y = chart_spec.get("y")
        series = chart_spec.get("series")
        title = chart_spec.get("title", "Chart")

        plt.figure(figsize=(10, 6))

        if chart_type == "line":
            if series:
                for s_val in query_data[series].unique():
                    subset = query_data[query_data[series] == s_val]
                    plt.plot(subset[x], subset[y], marker='o', label=s_val)
                plt.legend()
            else:
                plt.plot(query_data[x], query_data[y], marker='o')

        elif chart_type == "bar":
            if series:
                pivot = query_data.pivot_table(values=y, index=x, columns=series, aggfunc='sum')
                pivot.plot(kind='bar', ax=plt.gca())
                plt.legend(title=series)
            else:
                plt.bar(query_data[x], query_data[y])

        elif chart_type == "grouped_bar":
            pivot = query_data.pivot_table(values=y, index=x, columns=series, aggfunc='sum')
            pivot.plot(kind='bar', ax=plt.gca())
            plt.legend(title=series)

        elif chart_type == "histogram":
            plt.hist(query_data[y], bins=30, edgecolor='black')

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{timestamp}.png"
        filepath = OUTPUT_DIR / filename

        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.show()
        plt.close()

        return f"Chart saved: {filepath}"

    except Exception as e:
        return f"Chart Error: {str(e)}"

def agent_loop(user_message: str):
    """Run agent loop: user question → Claude proposes SQL + chart → execute → answer."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_message}]

    print(f"\n📊 User: {user_message}\n")

    latest_query_data = None
    iteration = 0

    while iteration < 5:
        iteration += 1
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            messages.append({"role": "assistant", "content": response.content})

            tool_results = []

            for tool_use in tool_uses:
                if tool_use.name == "run_sql":
                    query = tool_use.input.get("query", "")
                    print(f"🔍 SQL: {query}\n")

                    result = run_sql(query)
                    latest_query_data = con.sql(query).fetchdf()
                    print(f"📈 Results:\n{result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result
                    })

                elif tool_use.name == "render_chart":
                    chart_spec = tool_use.input
                    print(f"📊 Chart: {chart_spec.get('title')}")

                    if latest_query_data is not None:
                        result = render_chart(chart_spec, latest_query_data)
                    else:
                        result = "Error: No query data available for charting"

                    print(f"{result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })

            continue

        # Claude stopped with final answer
        answer = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None
        )

        if answer:
            print(f"💬 Answer: {answer}\n")

        break

def main():
    """Interactive REPL for asking questions."""
    print("=" * 80)
    print("Analytics Agent with Charts Ready (Haiku 4.5)")
    print("=" * 80)
    print("Ask questions about the Superstore sales data.")
    print("Charts will be saved to analytics/output/")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
            if question.lower() == "exit":
                print("Bye!")
                break
            if question:
                agent_loop(question)
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
