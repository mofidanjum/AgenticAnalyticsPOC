"""
Stage 4: Text-to-SQL Agent with Charting
Converts natural language questions into SQL queries and visualizations.
Uses Haiku model for cost efficiency.
"""

import os
import json
import duckdb
import yaml
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
2. If the question asks about trends, comparisons, or distributions, use "render_chart" to visualize
3. For trends → use line chart, comparisons → use bar chart, distributions → use pie chart
4. Then provide a natural language answer based on the results
5. Be precise with column names (they are case-insensitive in SQL but check metadata)
6. Handle dates carefully — they are stored as VARCHAR strings (MM/DD/YYYY)
7. Remember profit can be negative

If a question is ambiguous, ask for clarification before running SQL."""

DB_PATH = "data/processed/superstore.duckdb"
con = duckdb.connect(DB_PATH)
OUTPUT_DIR = Path("analytics/output")
OUTPUT_DIR.mkdir(exist_ok=True)

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

def run_sql(query: str) -> str:
    """Execute SQL query and return results as formatted text."""
    try:
        result = con.sql(query).fetchdf()
        if len(result) == 0:
            return "Query returned no results."
        return result.to_string()
    except Exception as e:
        return f"SQL Error: {str(e)}"

def render_chart(chart_type: str, title: str, x_column: str, y_column: str, series_column: str = None) -> str:
    """Create and display an interactive chart from the last query results."""
    try:
        if not hasattr(render_chart, 'last_data'):
            return "No query results available. Run a SQL query first."

        df = render_chart.last_data
        fig = None

        if chart_type == "bar":
            if series_column and series_column in df.columns:
                fig = px.bar(df, x=x_column, y=y_column, color=series_column,
                            title=title, barmode='group', height=600)
            else:
                fig = px.bar(df, x=x_column, y=y_column, title=title, height=600)

        elif chart_type == "line":
            if series_column and series_column in df.columns:
                fig = px.line(df, x=x_column, y=y_column, color=series_column,
                             title=title, markers=True, height=600)
            else:
                fig = px.line(df, x=x_column, y=y_column, title=title,
                             markers=True, height=600)

        elif chart_type == "pie":
            fig = px.pie(df, names=x_column, values=y_column, title=title, height=600)

        elif chart_type == "scatter":
            if series_column and series_column in df.columns:
                fig = px.scatter(df, x=x_column, y=y_column, color=series_column,
                                title=title, height=600, size_max=15)
            else:
                fig = px.scatter(df, x=x_column, y=y_column, title=title, height=600)

        if fig:
            fig.update_layout(
                font=dict(size=12),
                hovermode='closest',
                showlegend=True,
                template='plotly_white'
            )
            fig.show()
            return f"✓ Interactive {chart_type} chart displayed"
        else:
            return f"Chart Error: Unknown chart type {chart_type}"

    except Exception as e:
        return f"Chart Error: {str(e)}"

def agent_loop(user_message: str):
    """Run agent loop: user question → Claude proposes SQL → execute → optional chart → answer."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_message}]

    print(f"\n📊 User: {user_message}\n")

    # Agent loop
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

        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use":
            tool_use = next(
                (block for block in response.content if block.type == "tool_use"),
                None
            )

            if tool_use:
                if tool_use.name == "run_sql":
                    query = tool_use.input.get("query", "")
                    print(f"🔍 SQL: {query}\n")

                    # Execute query and store results
                    try:
                        result_df = con.sql(query).fetchdf()
                        render_chart.last_data = result_df
                        result = result_df.to_string() if len(result_df) > 0 else "Query returned no results."
                        print(f"📈 Results:\n{result}\n")
                    except Exception as e:
                        result = f"SQL Error: {str(e)}"
                        print(f"❌ {result}\n")

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

                # Add Claude's message and tool result to messages
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

        # Claude stopped with final answer (stop_reason == "end_turn")
        answer = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None
        )

        if answer:
            print(f"💬 Answer: {answer}\n")

        break

def main():
    """Interactive REPL for asking questions."""
    print("=" * 60)
    print("Analytics Agent Ready (Haiku)")
    print("=" * 60)
    print("Ask questions about the Superstore sales data.")
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