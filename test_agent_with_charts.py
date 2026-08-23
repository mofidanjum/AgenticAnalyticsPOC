"""
Test enhanced agent with charting capability
"""

import os
import duckdb
import yaml
from anthropic import Anthropic

# Load metadata
with open("analytics/metadata/orders.yaml") as f:
    metadata = yaml.safe_load(f)

# Format metadata for system prompt
columns_info = []
for col_name, col_info in metadata["columns"].items():
    role = col_info.get("role", "unknown")
    unit = col_info.get("unit", "")
    desc = col_info.get("description", "")
    unit_str = f" (in {unit})" if unit else ""
    columns_info.append(f"- {col_name} ({col_info['type']}, {role}){unit_str}: {desc}")

columns_text = "\n".join(columns_info)
notable_values_text = "\n".join([f"- {v}" for v in metadata.get("notable_values", [])])

SYSTEM_PROMPT = f"""You are an analytics assistant that answers questions about retail sales data.

You have access to a DuckDB database with one table: "orders"

TABLE DESCRIPTION:
{metadata['description']}

COLUMNS:
{columns_text}

IMPORTANT CONSTRAINTS:
{notable_values_text}

When answering questions:
1. First use "run_sql" to get the data
2. If the question asks about trends, comparisons, or distributions, use "render_chart"
3. For trends → line chart, comparisons → bar chart, distributions → pie chart
4. Then provide a natural language answer based on the results
5. Be precise with column names
6. Handle dates carefully — they are stored as VARCHAR strings (MM/DD/YYYY)
7. Remember profit can be negative"""

DB_PATH = "data/processed/superstore.duckdb"
con = duckdb.connect(DB_PATH)

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
        "description": "Create a visualization chart from query results",
        "input_schema": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": ["bar", "line", "pie", "scatter"],
                    "description": "Type of chart"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "x_column": {
                    "type": "string",
                    "description": "Column name for X axis"
                },
                "y_column": {
                    "type": "string",
                    "description": "Column name for Y axis"
                },
                "series_column": {
                    "type": "string",
                    "description": "Optional column for color grouping"
                }
            },
            "required": ["chart_type", "title", "x_column", "y_column"]
        }
    }
]

def run_sql(query: str):
    """Execute SQL query and return results as formatted text."""
    try:
        result = con.sql(query).fetchdf()
        if len(result) == 0:
            return "Query returned no results."
        run_sql.last_data = result
        return result.to_string()
    except Exception as e:
        return f"SQL Error: {str(e)}"

def render_chart(chart_type: str, title: str, x_column: str, y_column: str, series_column: str = None) -> str:
    """Create a chart from the last query results."""
    try:
        import matplotlib.pyplot as plt
        from datetime import datetime
        from pathlib import Path

        if not hasattr(run_sql, 'last_data'):
            return "No query results available. Run a SQL query first."

        df = run_sql.last_data
        OUTPUT_DIR = Path("analytics/output")
        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = OUTPUT_DIR / f"chart_{timestamp}.png"

        plt.figure(figsize=(10, 6))

        if chart_type == "bar":
            if series_column and series_column in df.columns:
                df.pivot_table(values=y_column, index=x_column, columns=series_column).plot(kind='bar', ax=plt.gca())
            else:
                df.plot(x=x_column, y=y_column, kind='bar', ax=plt.gca(), legend=False)

        elif chart_type == "line":
            if series_column and series_column in df.columns:
                for group in df[series_column].unique():
                    group_data = df[df[series_column] == group]
                    plt.plot(group_data[x_column], group_data[y_column], marker='o', label=group)
                plt.legend()
            else:
                plt.plot(df[x_column], df[y_column], marker='o')

        elif chart_type == "pie":
            plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')

        elif chart_type == "scatter":
            if series_column and series_column in df.columns:
                for group in df[series_column].unique():
                    group_data = df[df[series_column] == group]
                    plt.scatter(group_data[x_column], group_data[y_column], label=group)
                plt.legend()
            else:
                plt.scatter(df[x_column], df[y_column])

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return f"Chart saved to {filepath}"
    except Exception as e:
        return f"Chart Error: {str(e)}"

def agent_loop(user_message: str):
    """Run agent loop with SQL and charting."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_message}]

    print(f"\n📊 User: {user_message}\n")

    iteration = 0
    while iteration < 10:
        iteration += 1
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_use = next(
                (block for block in response.content if block.type == "tool_use"),
                None
            )

            if tool_use:
                if tool_use.name == "run_sql":
                    query = tool_use.input.get("query", "")
                    print(f"🔍 SQL: {query}\n")
                    result = run_sql(query)
                    print(f"📈 Results:\n{result}\n")

                elif tool_use.name == "render_chart":
                    chart_result = render_chart(
                        chart_type=tool_use.input.get("chart_type", "bar"),
                        title=tool_use.input.get("title", "Chart"),
                        x_column=tool_use.input.get("x_column", ""),
                        y_column=tool_use.input.get("y_column", ""),
                        series_column=tool_use.input.get("series_column")
                    )
                    print(f"📊 {chart_result}\n")
                    result = chart_result

                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": result if isinstance(result, str) else str(result)
                        }
                    ]
                })

                continue

        answer = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None
        )

        if answer:
            print(f"💬 Answer: {answer}\n")

        break

def main():
    """Run test questions."""
    print("=" * 60)
    print("Analytics Agent with Charting - Test Mode")
    print("=" * 60)

    test_questions = [
        "Show me sales by region in a bar chart",
        "What are profit trends by category?",
        "Create a pie chart of orders by segment"
    ]

    for question in test_questions:
        try:
            agent_loop(question)
            print("=" * 60)
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
