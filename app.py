"""
Agentic Analytics POC - Streamlit Dashboard
Full-featured version with Data, SQL, and Visualization tabs
"""
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import subprocess
import sys
import time
from pathlib import Path
from anthropic import Anthropic

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
    """Execute a Python script in a fresh process"""
    try:
        # Close any open connections first
        st.cache_resource.clear()
        time.sleep(0.5)

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=120,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
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
        st.cache_resource.clear()
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

    # Button 3: Deploy
    if st.button("🚀 Deploy to Cloud", use_container_width=True, key="deploy_btn"):
        st.info("📤 Deploying to Streamlit Cloud...")
        try:
            subprocess.run(["git", "add", "."], check=False, capture_output=True)
            result = subprocess.run(
                ["git", "commit", "-m", "Auto-deploy: Updated data and dashboard"],
                capture_output=True,
                text=True
            )
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if push_result.returncode == 0:
                st.success("✅ Deployed to GitHub!")
                st.info("📍 Streamlit Cloud auto-redeploys in 2-3 minutes")
            else:
                st.error("❌ Push failed")
                st.text(push_result.stderr)
        except Exception as e:
            st.error(f"❌ Deploy Error: {e}")

    st.markdown("---")
    st.caption("Click buttons to automate pipeline")

# ===== MAIN CONTENT =====
con = get_connection()

if con is None:
    st.warning("⚠️ Database not found")
    st.info("📌 Click '📥 Refresh Data' in sidebar to get started")
    st.stop()

# Load KPIs
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

except Exception as e:
    st.error(f"Error loading KPIs: {e}")
    st.stop()

# Filters
st.subheader("🔍 Filters")
col1, col2, col3 = st.columns(3)

with col1:
    regions = [r[0] for r in con.sql('SELECT DISTINCT "Region" FROM orders ORDER BY "Region"').fetchall()]
    selected_regions = st.multiselect("📍 Region", regions, default=regions, key="region_filter")

with col2:
    categories = [c[0] for c in con.sql('SELECT DISTINCT "Category" FROM orders ORDER BY "Category"').fetchall()]
    selected_categories = st.multiselect("📦 Category", categories, default=categories, key="category_filter")

with col3:
    segments = [s[0] for s in con.sql('SELECT DISTINCT "Segment" FROM orders ORDER BY "Segment"').fetchall()]
    selected_segments = st.multiselect("👥 Segment", segments, default=segments, key="segment_filter")

# Build filter query
filter_regions = "', '".join(selected_regions) if selected_regions else "East"
filter_categories = "', '".join(selected_categories) if selected_categories else "Furniture"
filter_segments = "', '".join(selected_segments) if selected_segments else "Consumer"

filtered_df = con.sql(f"""
    SELECT * FROM orders
    WHERE "Region" IN ('{filter_regions}')
    AND "Category" IN ('{filter_categories}')
    AND "Segment" IN ('{filter_segments}')
""").df()

# ===== TABS: Visual, Data, SQL =====
tab1, tab2, tab3 = st.tabs(["📊 Visual", "📋 Data", "🔍 SQL"])

# ===== TAB 1: VISUAL =====
with tab1:
    st.subheader("📊 Build Visualizations with Claude")

    col1, col2 = st.columns([3, 1])

    with col1:
        user_request = st.text_area(
            "What visualization would you like?",
            placeholder="e.g., 'Build a complete dashboard with sales by region, category, and segment', 'Create subplots showing profit trends and top customers', 'Show me sales comparison across all dimensions'",
            height=80,
            key="viz_request"
        )

    with col2:
        st.write("")
        st.write("")
        build_viz = st.button("🎨 Build Visualization", use_container_width=True)

    if build_viz and user_request:
        with st.spinner("🤖 Claude is creating visualization..."):
            try:
                api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
                if not api_key:
                    st.error("❌ API Key not found")
                    st.stop()

                client = Anthropic(api_key=api_key)

                system_prompt = """You are a Python/Plotly visualization expert. Write ONLY valid Python code, no explanations.

The dataframe 'filtered_df' has these columns (use exact names with quotes):
"Sales", "Profit", "Region", "Category", "Segment", "Order Date", "Customer Name", "Quantity", "Discount", "Sub-Category"

Rules:
1. Start with: import plotly.express as px
2. For simple charts: use px.bar(), px.pie(), px.scatter(), px.line()
3. For dashboards: use make_subplots() from plotly.subplots
4. Always end with: st.plotly_chart(fig, use_container_width=True)
5. Use column names EXACTLY as shown above
6. Group/aggregate data with .groupby() before plotting
7. Handle NaN values with .dropna()

Examples:
- Bar chart: fig = px.bar(filtered_df.groupby("Region")["Sales"].sum(), title="Sales by Region")
- Pie chart: fig = px.pie(filtered_df, values="Sales", names="Region", title="Sales by Region")
- Subplots: from plotly.subplots import make_subplots; fig = make_subplots(rows=1, cols=2); fig.add_trace(...)

Return ONLY Python code. No markdown, no explanations, no comments."""

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_request}]
                )

                code = next((b.text for b in response.content if hasattr(b, "text")), None)

                if code:
                    try:
                        # Clean up code (remove markdown if present)
                        code = code.strip()
                        if code.startswith("```python"):
                            code = code[9:]
                        if code.startswith("```"):
                            code = code[3:]
                        if code.endswith("```"):
                            code = code[:-3]
                        code = code.strip()

                        # Execute the code
                        from plotly.subplots import make_subplots
                        exec_globals = {
                            "filtered_df": filtered_df,
                            "px": px,
                            "go": go,
                            "st": st,
                            "make_subplots": make_subplots,
                            "pd": pd,
                            "import": __import__
                        }
                        exec(code, exec_globals)
                        st.success("✅ Visualization created!")
                    except SyntaxError as e:
                        st.error(f"❌ Syntax Error in generated code")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.write("**Error:**")
                            st.text(f"Line {e.lineno}: {e.msg}")
                        with col2:
                            st.write("**Code:**")
                            st.code(code, language="python")
                    except Exception as e:
                        st.error(f"❌ Runtime Error: {type(e).__name__}: {e}")
                        with st.expander("Show generated code"):
                            st.code(code, language="python")
                else:
                    st.error("No code generated")

            except Exception as e:
                st.error(f"Error: {e}")

# ===== TAB 2: DATA =====
with tab2:
    st.subheader("📋 Data Table")
    st.write(f"Showing {len(filtered_df):,} rows")
    st.dataframe(filtered_df, use_container_width=True, height=600)

# ===== TAB 3: SQL =====
with tab3:
    st.subheader("🔍 SQL Query")

    sql_query = st.text_area(
        "Enter SQL query:",
        value=f"""SELECT * FROM orders
WHERE "Region" IN ('{filter_regions}')
AND "Category" IN ('{filter_categories}')
AND "Segment" IN ('{filter_segments}')
LIMIT 100""",
        height=120,
        key="sql_input"
    )

    if st.button("▶️ Execute Query", use_container_width=True):
        try:
            result_df = con.sql(sql_query).df()
            st.success(f"✅ Query executed: {len(result_df)} rows")
            st.dataframe(result_df, use_container_width=True, height=600)
        except Exception as e:
            st.error(f"SQL Error: {e}")

st.caption("Agentic Analytics POC • Superstore Dataset • Claude AI Powered")
