"""
Validation agent: Compares agent.py output with direct SQL execution
"""

import duckdb
import yaml
from anthropic import Anthropic

DB_PATH = "data/processed/superstore.duckdb"
con = duckdb.connect(DB_PATH)

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
4. Be precise with column names
5. Handle dates carefully — they are stored as VARCHAR strings (MM/DD/YYYY)
6. Remember profit can be negative"""

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

def get_agent_sql_and_results(user_message: str):
    """Run agent and capture SQL + results."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_message}]

    sql_query = None
    sql_results = None

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_use = next(
                (block for block in response.content if block.type == "tool_use"),
                None
            )

            if tool_use and tool_use.name == "run_sql":
                sql_query = tool_use.input.get("query", "")
                sql_results = run_sql(sql_query)

                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": sql_results
                        }
                    ]
                })
                continue

        break

    return sql_query, sql_results

def validate_query(user_message: str):
    """Compare agent output with direct SQL execution."""
    print("=" * 80)
    print(f"🔍 Question: {user_message}")
    print("=" * 80)

    # Get agent's SQL and results
    sql_query, agent_results = get_agent_sql_and_results(user_message)

    if not sql_query:
        print("❌ Agent did not generate SQL")
        return

    print(f"\n📝 Generated SQL:\n{sql_query}\n")

    # Run same SQL directly
    direct_results = run_sql(sql_query)

    # Compare
    print("━" * 80)
    print("✅ COMPARISON RESULTS")
    print("━" * 80)

    if agent_results == direct_results:
        print("\n✓ MATCH: Agent results match direct SQL execution!\n")
        print(f"Results:\n{direct_results}\n")
    else:
        print("\n✗ MISMATCH: Results differ!\n")
        print(f"Agent results:\n{agent_results}\n")
        print(f"Direct SQL results:\n{direct_results}\n")

def main():
    print("\n" + "=" * 80)
    print("Validation Agent - Compare LLM Output with Direct SQL")
    print("=" * 80)
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Ask a question: ").strip()
            if question.lower() == "exit":
                print("Bye!")
                break
            if question:
                validate_query(question)
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
