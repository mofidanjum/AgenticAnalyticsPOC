"""
Agentic Analytics POC - Streamlit Dashboard
Core version: Focus on reliability and core features
"""
import streamlit as st
import duckdb
import pandas as pd
import os
import subprocess
import sys
from pathlib import Path

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

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

def run_python_script(script_path):
    """Execute a Python script"""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

# ===== SIDEBAR: Pipeline Automation =====
with st.sidebar:
    st.markdown("### 🤖 Pipeline Automation")
    st.markdown("---")

    # Button 1: Refresh Data
    if st.button("📥 Refresh Data", use_container_width=True, key="refresh_btn"):
        st.cache_resource.clear()  # Close DB connection

        st.info("🔄 Starting data refresh pipeline...")

        steps_cols = st.columns(3)

        # Step 1: Download
        with steps_cols[0]:
            step1_placeholder = st.empty()

        step1_placeholder.write("📥 Downloading...")
        success1, out1, err1 = run_python_script("analytics/01_download_dataset.py")

        if success1:
            step1_placeholder.success("✅ Downloaded")
        else:
            step1_placeholder.error("❌ Download Failed")
            st.error(err1)

        # Step 2: Load
        with steps_cols[1]:
            step2_placeholder = st.empty()

        step2_placeholder.write("📚 Loading...")
        success2, out2, err2 = run_python_script("analytics/02_load_duckdb.py")

        if success2:
            step2_placeholder.success("✅ Loaded")
        else:
            step2_placeholder.error("❌ Load Failed")
            st.error(err2)

        # Step 3: Metadata
        with steps_cols[2]:
            step3_placeholder = st.empty()

        step3_placeholder.write("📝 Metadata...")
        success3, out3, err3 = run_python_script("analytics/03_generate_metadata_draft.py")

        if success3:
            step3_placeholder.success("✅ Metadata")
        else:
            step3_placeholder.error("❌ Metadata")
            st.error(err3)

        st.markdown("---")
        if success1 and success2 and success3:
            st.success("🎉 Pipeline complete! Refresh page to see data.")
            st.cache_resource.clear()
        else:
            st.warning("⚠️ Some steps failed. Check errors above.")

    # Button 2: Verify Data
    if st.button("🧪 Verify Data", use_container_width=True, key="verify_btn"):
        try:
            con = get_connection()
            if con:
                result = con.sql('SELECT COUNT(*) as rows FROM orders').fetchall()
                rows = result[0][0]
                st.success(f"✅ Data OK\n📊 {rows:,} rows")
            else:
                st.error("❌ Database not found")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.markdown("---")
    st.caption("Click buttons to automate pipeline")

# ===== MAIN CONTENT =====
con = get_connection()

if con is None:
    st.warning("⚠️ Database not found")
    st.info("📌 Click '📥 Refresh Data' in sidebar to get started")
else:
    # Load and display KPIs
    try:
        total_sales = con.sql('SELECT SUM("Sales") FROM orders').fetchall()[0][0]
        total_profit = con.sql('SELECT SUM("Profit") FROM orders').fetchall()[0][0]
        total_orders = con.sql('SELECT COUNT(DISTINCT "Order ID") FROM orders').fetchall()[0][0]
        total_customers = con.sql('SELECT COUNT(DISTINCT "Customer ID") FROM orders').fetchall()[0][0]

        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            st.metric("💰 Total Sales", f"${total_sales:,.0f}")
        with col2:
            st.metric("📈 Total Profit", f"${total_profit:,.0f}")
        with col3:
            st.metric("📋 Total Orders", f"{total_orders:,.0f}")
        with col4:
            st.metric("👥 Customers", f"{total_customers:,.0f}")

        # Filters
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

        # Ask Question
        st.subheader("💭 Ask a Question")
        question = st.text_area(
            "What would you like to know?",
            placeholder="e.g., 'Show sales by region' or 'What is profit by category?'",
            height=80
        )

        if st.button("🤖 Analyze", use_container_width=True):
            if not question:
                st.warning("Please ask a question")
            else:
                with st.spinner("🤖 Claude is thinking..."):
                    try:
                        from anthropic import Anthropic

                        api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
                        if not api_key:
                            st.error("❌ API Key not found. Set ANTHROPIC_API_KEY environment variable.")
                            st.stop()

                        client = Anthropic(api_key=api_key)

                        system_prompt = """You are an analytics assistant for retail sales data.
Data: Orders table with Sales, Profit, Region, Category, Segment columns.
US retail data from 2015-2016.
Answer questions clearly with specific numbers."""

                        response = client.messages.create(
                            model="claude-haiku-4-5-20251001",
                            max_tokens=500,
                            system=system_prompt,
                            messages=[{"role": "user", "content": question}]
                        )

                        answer = next((b.text for b in response.content if hasattr(b, "text")), None)
                        if answer:
                            st.success("✅ Response")
                            st.write(answer)
                        else:
                            st.error("No response generated")

                    except Exception as e:
                        st.error(f"Error: {e}")

    except Exception as e:
        st.error(f"Error loading data: {e}")

st.caption("Agentic Analytics POC • Superstore Dataset • Claude AI Powered")
