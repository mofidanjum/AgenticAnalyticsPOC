import streamlit as st
import os
import sys
from datetime import datetime, date
import pandas as pd
import duckdb
import yaml
from anthropic import Anthropic

# Add parent directory to path
sys.path.insert(0, str(os.path.dirname(__file__)))

try:
    from config import *
    from utils import *
except ImportError:
    # If imports fail, define defaults
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    DB_PATH = "data/processed/superstore.duckdb"
    METADATA_PATH = "analytics/metadata/orders.yaml"
    LOG_FILE = "stages/stage_6/query_logs.json"

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOAD METADATA ONCE (CACHE - NO TOKENS!)
# ============================================================================
@st.cache_resource
def load_metadata():
    """Load metadata from YAML (cached, not sent to Claude every time)"""
    with open(METADATA_PATH) as f:
        return yaml.safe_load(f)

@st.cache_resource
def get_duckdb_connection():
    """Create DuckDB connection (cached)"""
    return duckdb.connect(DB_PATH)

# Load resources
metadata = load_metadata()
con = get_duckdb_connection()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_history" not in st.session_state:
    st.session_state.query_history = get_query_history()

# ============================================================================
# SIMPLIFIED SYSTEM PROMPT (MINIMAL TOKENS!)
# ============================================================================
SIMPLIFIED_PROMPT = """You are a SQL expert for retail sales data (Superstore).
Generate SQL queries for a table called "orders" with columns:
Order ID, Order Date, Ship Date, Customer Name, Sales, Profit, Discount, Quantity, Region, Category, Sub-Category

Rules:
1. Return ONLY the SQL query, nothing else
2. Use proper WHERE clauses for filters
3. Quote column names with spaces: "Order Date", "Order ID", etc.
4. Sort results meaningfully
5. Add LIMIT 100 for large results
"""

# ============================================================================
# SIDEBAR: FILTERS & HISTORY
# ============================================================================
with st.sidebar:
    st.title("🔍 Filters")

    # Region filter
    region_options = ["West", "East", "Central", "South"]
    region_filter = st.multiselect(
        "📍 Region",
        region_options,
        default=region_options,
        key="region_filter"
    )

    # Date range filter
    date_range = st.date_input(
        "📅 Date Range",
        value=(date(2015, 1, 1), date(2016, 12, 31)),
        key="date_range"
    )

    # Category filter
    category_options = ["Furniture", "Office Supplies", "Technology"]
    category_filter = st.multiselect(
        "🏷️ Category",
        category_options,
        default=category_options,
        key="category_filter"
    )

    # Apply filters button
    if st.button("✅ Apply Filters", key="apply_filters"):
        st.success("✓ Filters applied to next query")

    # Reset filters button
    if st.button("🔄 Reset All", key="reset_filters"):
        st.session_state.region_filter = region_options
        st.session_state.date_range = (date(2015, 1, 1), date(2016, 12, 31))
        st.session_state.category_filter = category_options
        st.rerun()

    st.divider()

    # Query History
    st.title("📋 Query History")

    history = get_query_history(limit=20)
    if history:
        for i, log in enumerate(history):
            with st.expander(format_query_for_history(log), expanded=False):
                st.write(f"**Q:** {log['question']}")
                st.code(log['sql'], "sql")
                st.write(f"**Rows:** {log['rows_returned']}")
                st.write(f"**Time:** {log['timestamp']}")

        if st.button("🗑️ Clear History", key="clear_history"):
            import json
            from pathlib import Path
            Path(LOG_FILE).write_text("[]")
            st.session_state.query_history = []
            st.rerun()
    else:
        st.info("No queries yet. Ask a question to get started!")

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================
st.title("📊 Analytics Agent")
st.write("Ask questions about your Superstore sales data using natural language or voice! 🎤")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ============================================================================
# CHAT INPUT & PROCESSING
# ============================================================================
user_input = st.chat_input("Ask a question... e.g., 'What were total sales by region?'")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Process with agent
    with st.spinner("⏳ Generating SQL and getting results..."):
        try:
            # Initialize Claude client
            client = Anthropic()

            # Build filter information
            filter_info = build_filter_clause(region_filter, date_range, category_filter)

            # Build prompt with minimal tokens
            prompt_with_filters = build_filtered_prompt(user_input, {
                "region": region_filter,
                "date_range": date_range,
                "category": category_filter
            })

            # Send to Claude (MINIMAL TOKENS - only question + filters, not metadata)
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,  # Small response = fewer tokens
                system=SIMPLIFIED_PROMPT,
                messages=[
                    {"role": "user", "content": prompt_with_filters}
                ]
            )

            # Extract SQL from response
            sql_query = response.content[0].text.strip()

            # Add WHERE clause from filters if needed
            if filter_info and "WHERE" not in sql_query.upper():
                if "FROM" in sql_query.upper():
                    sql_query = sql_query.replace("FROM orders", f"FROM orders WHERE {filter_info}")
            elif filter_info and "WHERE" in sql_query.upper():
                sql_query = sql_query.replace("WHERE", f"WHERE {filter_info} AND")

            # Execute SQL
            results_df = con.sql(sql_query).fetchdf()

            # Display results
            with st.chat_message("assistant"):
                st.subheader("📈 Results")

                # Show SQL (collapsible)
                with st.expander("🔍 View SQL Query"):
                    st.code(sql_query, language="sql")

                # Show results table
                if len(results_df) > 0:
                    st.dataframe(results_df, use_container_width=True)

                    # Export options
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        csv_data, csv_filename = export_to_csv(results_df)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv_data,
                            file_name=csv_filename,
                            mime="text/csv"
                        )

                    with col2:
                        excel_data, excel_filename = export_to_excel(results_df)
                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_data,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    with col3:
                        st.metric("Rows", len(results_df))

                else:
                    st.info("No results found for this query.")

            # Add to session messages
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Query executed. Found {len(results_df)} row(s)."
            })

            # Log the query
            log_query(
                question=user_input,
                sql=sql_query,
                rows=len(results_df),
                filters={
                    "region": region_filter,
                    "date_range": str(date_range),
                    "category": category_filter
                }
            )

            # Refresh history sidebar
            st.session_state.query_history = get_query_history()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Make sure you have set ANTHROPIC_API_KEY environment variable.")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.caption("📊 Analytics Agent v1.0 | Powered by Claude AI + Streamlit")
st.caption(f"Metadata from: {METADATA_PATH} | Database: {DB_PATH}")
