"""
Stage 4: Text-to-SQL Agent
Converts natural language questions into SQL queries using Claude API with tool use.
Uses Haiku model for cost efficiency.
"""

import os
import json
import duckdb
import yaml
from pathlib import Path
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
1. You have a tool called "run_sql" to execute SQL queries
2. Always propose a SQL query first to get the data
3. Then provide a natural language answer based on the results
4. Be precise with column names (they are case-insensitive in SQL but check metadata)
5. Handle dates carefully — they are stored as VARCHAR strings (MM/DD/YYYY)
6. Remember profit can be negative

If a question is ambiguous, ask for clarification before running SQL."""

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

def agent_loop(user_message: str):
    """Run agent loop: user question → Claude proposes SQL → execute → answer."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_message}]

    print(f"\n📊 User: {user_message}\n")

    # Agent loop
    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Find the tool use block
            tool_use = next(
                (block for block in response.content if block.type == "tool_use"),
                None
            )

            if tool_use and tool_use.name == "run_sql":
                query = tool_use.input.get("query", "")
                print(f"🔍 SQL: {query}\n")

                # Execute query
                result = run_sql(query)
                print(f"📈 Results:\n{result}\n")

                # Add Claude's message and tool result to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": result
                        }
                    ]
                })

                # Continue loop to let Claude provide final answer
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