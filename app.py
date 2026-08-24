"""
Agentic Analytics POC - Streamlit Dashboard
Full-featured version with automated pipeline
"""
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from anthropic import Anthropic
import os
import subprocess
import sys
from pathlib import Path

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# Dark theme config
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
h1 { margin-top: 0 !important; margin-bottom: 0.3rem !important; }
.sidebar .sidebar-content { padding-top: 0.5rem; }
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

def close_connection():
    """Close the cached connection to release file lock"""
    try:
        st.cache_resource.clear()
    except:
        pass

def run_python_script(script_path, step_name):
    """Execute a Python script and show progress"""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.returncode == 0:
            st.success(f"✅ {step_name} Complete")
            if result.stdout:
                st.text(result.stdout)
            return True
        else:
            st.error(f"❌ {step_name} Failed")
            if result.stderr:
                st.text(result.stderr)
            return False
    except Exception as e:
        st.error(f"❌ {step_name} Error: {e}")
        return False

# Sidebar automation
with st.sidebar:
    st.markdown("### 🤖 Pipeline Automation")
    st.markdown("---")

    if st.button("📥 Refresh Data", use_container_width=True):
        st.info("🔄 Starting data refresh pipeline...")

        # Close any open connections to release file lock
        close_connection()

        col1, col2, col3 = st.columns(3)
        with col1:
            progress1 = st.empty()
        with col2:
            progress2 = st.empty()
        with col3:
            progress3 = st.empty()

        all_success = True

        # Step 1: Download
        with progress1.container():
            st.write("📥 Downloading from Kaggle...")
        success1 = run_python_script("analytics/01_download_dataset.py", "Download")
        all_success = all_success and success1
        with progress1.container():
            if success1:
                st.success("✅ Downloaded")
            else:
                st.error("❌ Download Failed")

        # Step 2: Load (connection is closed, file should be unlocked)
        with progress2.container():
            st.write("📚 Loading into DuckDB...")
        success2 = run_python_script("analytics/02_load_duckdb.py", "Load")
        all_success = all_success and success2
        with progress2.container():
            if success2:
                st.success("✅ Loaded")
            else:
                st.error("❌ Load Failed")

        # Step 3: Metadata
        with progress3.container():
            st.write("📝 Updating Metadata...")
        success3 = run_python_script("analytics/03_generate_metadata_draft.py", "Metadata")
        all_success = all_success and success3
        with progress3.container():
            if success3:
                st.success("✅ Metadata Updated")
            else:
                st.error("❌ Metadata Failed")

        st.markdown("---")
        if all_success:
            st.success("🎉 All pipeline steps complete! Refresh the page to see updated data.")
            # Clear cache to reload database
            st.cache_resource.clear()
        else:
            st.warning("⚠️ Some steps failed. Check errors above.")

    if st.button("🧪 Verify Data", use_container_width=True):
        try:
            con = get_connection()
            if con is None:
                st.error("❌ Database not found")
            else:
                result = con.sql('SELECT COUNT(*) as rows FROM orders').fetchall()
                rows = result[0][0]
                st.success(f"✅ Data Verified\n📊 {rows:,} rows loaded")
        except Exception as e:
            st.error(f"❌ Verification Error: {e}")

    if st.button("🚀 Deploy to Cloud", use_container_width=True):
        st.info("📤 Deploying to Streamlit Cloud...")
        try:
            # Stage files
            subprocess.run(["git", "add", "."], check=True, capture_output=True)

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", "Auto-deploy: Updated data and dashboard"],
                capture_output=True,
                text=True
            )

            # Push
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True
            )

            if push_result.returncode == 0:
                st.success("✅ Deployed to Streamlit Cloud!")
                st.info("📍 Your app will redeploy automatically")
            else:
                st.error("❌ Push failed")
                st.text(push_result.stderr)
        except Exception as e:
            st.error(f"❌ Deploy Error: {e}")

    st.markdown("---")
    st.caption("🤖 Click buttons to automate the entire pipeline")

# Main content
con = get_connection()

if con is None:
    st.error("❌ Database not found. Click '📥 Refresh Data' in the sidebar to download and load data.")
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
    "What would you like to know about the data?",
    placeholder="e.g., 'Show total sales by region' or 'What is our profit margin by category?'",
    height=80
)

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
Available data: Orders table with columns like Sales, Profit, Region, Category, Segment.
The data covers US retail orders from 2015-2016.
When user asks a question:
1. Understand what metric or insight they want
2. Provide a clear, direct answer
3. Include specific numbers where relevant
4. Suggest related questions if helpful

Be concise and data-driven."""

                messages = [{"role": "user", "content": question}]

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=800,
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
