"""
Agentic Analytics POC - Streamlit Dashboard
Simple, cloud-ready version
"""
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from anthropic import Anthropic
import os

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# Dark theme config
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
h1 { margin-top: 0 !important; margin-bottom: 0.3rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Agentic Analytics POC")
st.write("Superstore Sales Data • Powered by Claude AI")

# POC Flow
st.markdown("""
<div style="background: linear-gradient(90deg, #1a1f3a 0%, #0a0e27 50%, #1a1f3a 100%);
            padding: 1.2rem; border-radius: 0.5rem; border-left: 4px solid #6366f1; margin-bottom: 1rem; margin-top: -0.5rem;">
    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #f1f5f9; font-weight: 600;">
        <strong>📥 Source:</strong> DuckDB (Superstore Dataset)
    </p>
    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #f1f5f9; font-weight: 600;">
        <strong>📚 Metadata Layer:</strong> YAML Schema (Column Descriptions & Constraints)
    </p>
    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #f1f5f9; font-weight: 600;">
        <strong>🤖 Claude AI:</strong> Natural Language → SQL Translation & Analysis
    </p>
    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #f1f5f9; font-weight: 600;">
        <strong>🎯 Target:</strong> Interactive Dashboards (Visual, Data, SQL Queries)
    </p>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    try:
        return duckdb.connect("data/processed/superstore.duckdb", read_only=True)
    except:
        return None

con = get_connection()

if con is None:
    st.error("❌ Database not found. Please refresh data first.")
    st.stop()

# Load KPIs
try:
    total_sales = con.sql('SELECT SUM("Sales") FROM orders').fetchall()[0][0]
    total_profit = con.sql('SELECT SUM("Profit") FROM orders').fetchall()[0][0]
    total_orders = con.sql('SELECT COUNT(DISTINCT "Order ID") FROM orders').fetchall()[0][0]
    total_customers = con.sql('SELECT COUNT(DISTINCT "Customer ID") FROM orders').fetchall()[0][0]
except Exception as e:
    st.error(f"Error loading KPIs: {e}")
    st.stop()

# KPI Cards
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.metric("💰 Total Sales", f"${total_sales:,.0f}")

with col2:
    st.metric("📈 Total Profit", f"${total_profit:,.0f}")

with col3:
    st.metric("📋 Total Orders", f"{total_orders:,.0f}")

with col4:
    st.metric("👥 Customers", f"{total_customers:,.0f}")

st.subheader("🔍 Filters")
col1, col2, col3 = st.columns(3)

with col1:
    regions = [r[0] for r in con.sql('SELECT DISTINCT "Region" FROM orders ORDER BY "Region"').fetchall()]
    selected_regions = st.multiselect("📍 Region", regions, default=regions)

with col2:
    categories = [c[0] for c in con.sql('SELECT DISTINCT "Category" FROM orders ORDER BY "Category"').fetchall()]
    selected_categories = st.multiselect("📦 Category", categories, default=categories)

with col3:
    segments = [s[0] for s in con.sql('SELECT DISTINCT "Segment" FROM orders ORDER BY "Segment"').fetchall()]
    selected_segments = st.multiselect("👥 Segment", segments, default=segments)

st.subheader("💭 Ask a Question")
question = st.text_area(
    "What would you like to know?",
    placeholder="e.g., 'Show sales by region'",
    height=80
)

# Sidebar commands
with st.sidebar:
    st.markdown("### 🤖 Quick Commands")
    st.markdown("---")

    if st.button("🧪 Verify Data", use_container_width=True):
        try:
            result = con.sql('SELECT COUNT(*) as rows FROM orders').fetchall()
            rows = result[0][0]
            st.success(f"✅ Data OK\n📊 {rows:,} rows")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.markdown("---")
    st.caption("Dashboard ready to use!")

if st.button("🤖 Analyze", use_container_width=True):
    if not question:
        st.warning("Please ask a question")
    else:
        with st.spinner("🤖 Claude is analyzing..."):
            try:
                api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
                if not api_key:
                    st.error("❌ ANTHROPIC_API_KEY not configured. Set it in Streamlit Cloud secrets.")
                    st.stop()

                client = Anthropic(api_key=api_key)

                system_prompt = """You are an analytics assistant for retail sales data.
Available data: Orders table with Sales, Profit, Region, Category, Segment columns.
When user asks a question, provide SQL query and natural language answer."""

                messages = [{"role": "user", "content": question}]

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=500,
                    system=system_prompt,
                    messages=messages
                )

                answer = next((b.text for b in response.content if hasattr(b, "text")), None)

                if answer:
                    st.success("✅ Analysis Complete")
                    st.write(answer)
                else:
                    st.error("No answer generated")

            except Exception as e:
                st.error(f"Error: {e}")

st.caption("Agentic Analytics POC • Superstore Dataset • Built with Claude AI")
