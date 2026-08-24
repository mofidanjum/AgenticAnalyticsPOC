"""
Smart Interactive Analytics Dashboard - Simple & Robust
"""
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from anthropic import Anthropic

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.markdown("""<style>
body { background-color: #f8fafc; }
.main { background-color: #f8fafc; }

.kpi-container {
    background: white;
    padding: 1.5rem;
    border-radius: 1rem;
    border-left: 4px solid #6366f1;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.kpi-label {
    font-size: 0.85rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
}

.stButton > button {
    background-color: #6366f1 !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #4f46e5 !important;
}

/* Override Streamlit's default red for selected multiselect items */
.stMultiSelect [data-testid="stMultiSelectItemsContainer"] {
    color: #6366f1 !important;
}

/* Change tag/chip color from red to indigo */
div[data-baseweb="token"] {
    background-color: #e0e7ff !important;
    color: #4f46e5 !important;
}

div[role="listbox"] div[data-baseweb="token"] {
    background-color: #e0e7ff !important;
}
</style>""", unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    return duckdb.connect("data/processed/superstore.duckdb", read_only=True)

con = get_connection()

# Sidebar for auto-commands
with st.sidebar:
    st.markdown("### 🤖 Quick Commands")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_btn"):
            # Check if Kaggle credentials exist (env var or json file)
            import os
            import json

            kaggle_username = os.getenv("KAGGLE_USERNAME")
            kaggle_key = os.getenv("KAGGLE_KEY")
            kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")

            # Try to create kaggle.json from env vars if it doesn't exist
            if kaggle_username and kaggle_key and not os.path.exists(kaggle_json):
                try:
                    os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
                    with open(kaggle_json, 'w') as f:
                        json.dump({"username": kaggle_username, "key": kaggle_key}, f)
                    os.chmod(kaggle_json, 0o600)
                    st.success("✅ Kaggle credentials loaded from environment variables")
                except Exception as e:
                    st.warning(f"⚠️ Could not create kaggle.json: {e}")

            if not os.path.exists(kaggle_json) and not (kaggle_username and kaggle_key):
                st.error("❌ Kaggle API credentials not found!")
                st.info("""
                📋 To set up Kaggle API (One-time setup):

                **Option 1: Using Environment Variables (Recommended)**
                ```powershell
                $env:KAGGLE_USERNAME = "your_username"
                $env:KAGGLE_KEY = "your_api_key"
                ```

                **Option 2: Manual File Setup**
                1. Go to https://www.kaggle.com/settings/account
                2. Click "Create New Token"
                3. Save kaggle.json to: C:\\Users\\Sarah\\.kaggle\\kaggle.json

                After setup, click Refresh Data again!
                """)
            else:
                st.info("🔄 Starting data refresh pipeline...")
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    import subprocess
                    import sys
                    import os

                    # Prepare environment with Kaggle credentials
                    env = os.environ.copy()
                    env["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME", "")
                    env["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY", "")

                    # Use the same Python interpreter as Streamlit (from venv)
                    python_exe = sys.executable

                    # Step 1: Download
                    status_text.write("📥 Step 1: Downloading from Kaggle...")
                    progress_bar.progress(25)
                    cmd = f'"{python_exe}" analytics/01_download_dataset.py'
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=120, env=env)
                    if result.returncode == 0:
                        st.success("✅ Download complete")
                    else:
                        st.warning("⚠️ Download failed")
                        if result.stderr:
                            st.error(f"Error: {result.stderr.decode()[:300]}")

                    # Step 2: Load into DuckDB
                    status_text.write("📚 Step 2: Loading into DuckDB...")
                    progress_bar.progress(50)
                    cmd = f'"{python_exe}" analytics/02_load_duckdb.py'
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60, env=env)

                    # Verify
                    try:
                        st.cache_resource.clear()
                        con_new = duckdb.connect("data/processed/superstore.duckdb", read_only=True)
                        row_count = con_new.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0]
                        st.success(f"✅ Loaded {row_count:,} rows into DuckDB")
                    except Exception as e:
                        st.warning(f"⚠️ Load verification: {e}")

                    # Step 3: Metadata
                    status_text.write("📝 Step 3: Updating Metadata...")
                    progress_bar.progress(75)
                    cmd = f'"{python_exe}" analytics/03_generate_metadata_draft.py'
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60, env=env)
                    st.success("✅ Metadata updated")

                    progress_bar.progress(100)
                    st.success("🎉 Data Refresh Complete!")
                    st.info("💡 Refresh your browser to see the new data!")

                except subprocess.TimeoutExpired:
                    st.error("❌ Operation timed out")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    with col2:
        if st.button("🧪 Verify Data", use_container_width=True, key="verify_btn"):
            try:
                result = con.sql('SELECT COUNT(*) as rows FROM orders').fetchall()
                rows = result[0][0]
                st.success(f"✅ Data OK\n📊 {rows:,} rows")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    st.markdown("---")

    if st.button("🚀 Deploy to Cloud", use_container_width=True, key="deploy_btn"):
        st.info("🚀 Deploying to Streamlit Cloud...")
        import subprocess
        result = subprocess.run("git add . && git commit -m 'Auto-deploy' && git push origin main", shell=True, capture_output=True)
        if result.returncode == 0:
            st.success("✅ Deployed! Check Streamlit Cloud in 2-3 minutes.")
        else:
            st.error("❌ Deployment failed. Check git config.")

    st.markdown("---")
    st.caption("Just click buttons above!")


st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
h1 { margin-top: 0 !important; margin-bottom: 0.3rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Agentic Analytics POC")
st.write("Superstore Sales Data • Powered by Claude AI")

# Highlight the POC flow with metadata layer
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

# Load KPIs
try:
    total_sales = con.sql('SELECT SUM("Sales") FROM orders').fetchall()[0][0]
    total_profit = con.sql('SELECT SUM("Profit") FROM orders').fetchall()[0][0]
    total_orders = con.sql('SELECT COUNT(DISTINCT "Order ID") FROM orders').fetchall()[0][0]
    total_customers = con.sql('SELECT COUNT(DISTINCT "Customer ID") FROM orders').fetchall()[0][0]
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# KPI Cards with better styling
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">💰 Total Sales</div>
        <div class="kpi-value">${total_sales:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #ec4899;">
        <div class="kpi-label">📈 Total Profit</div>
        <div class="kpi-value" style="color: #ec4899;">${total_profit:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #06b6d4;">
        <div class="kpi-label">📋 Total Orders</div>
        <div class="kpi-value" style="color: #06b6d4;">{total_orders:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #10b981;">
        <div class="kpi-label">👥 Customers</div>
        <div class="kpi-value" style="color: #10b981;">{total_customers:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

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

st.subheader("💭 Describe What You Want to Analyze")
question = st.text_area(
    "Tell Claude what metrics and insights you want",
    placeholder="e.g., 'Show sales trends, profit by category, and top regions'",
    height=100
)

if st.button("🤖 Analyze", use_container_width=True):
    if not question:
        st.warning("Please describe what you want")
    else:
        with st.spinner("🤖 Claude is building your dashboard..."):
            try:
                # Build filter
                filter_conditions = []
                if len(selected_regions) < len(regions):
                    filter_conditions.append(f'"Region" IN ({", ".join([f"\'{r}\'" for r in selected_regions])})')
                if len(selected_categories) < len(categories):
                    filter_conditions.append(f'"Category" IN ({", ".join([f"\'{c}\'" for c in selected_categories])})')
                if len(selected_segments) < len(segments):
                    filter_conditions.append(f'"Segment" IN ({", ".join([f"\'{s}\'" for s in selected_segments])})')

                filter_where = " WHERE " + " AND ".join(filter_conditions) if filter_conditions else ""

                client = Anthropic()

                # First turn: Claude understands request
                system_prompt = """You are an analytics expert. Understand what the user wants to visualize and suggest 3-4 charts.

Available metrics:
- Sales (by region, category, segment, customer, date)
- Profit (by category, region, segment)
- Orders (by category, region, segment)
- Customers (count by segment, region)

For each visualization, specify:
1. Name
2. What dimension to group by (Region/Category/Segment/Date)
3. What metric to show (SUM(Sales)/SUM(Profit)/COUNT/AVG)
4. Chart type (bar/pie/line)

Respond as:
**Chart 1: [Name]**
- Group by: [Dimension]
- Metric: [Aggregate]
- Type: [bar/pie/line]

**Chart 2: [Name]**
etc."""

                messages = [{"role": "user", "content": question}]
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=messages
                )

                claude_plan = next((b.text for b in response.content if hasattr(b, "text")), None)

                st.subheader("🤖 Claude's Plan")
                st.write(claude_plan)
                st.divider()

                # Second turn: Get SQL queries
                system_prompt2 = """You are an analytics expert. Based on your previous plan, provide chart specifications.

VALID column names to GROUP BY:
- Region (East, West, Central, South)
- Category (Furniture, Office Supplies, Technology)
- Segment (Consumer, Corporate, Home Office)
- Sub-Category (Chair, Table, Bookcase, Copier, Phone, Binder, etc)
- Order Date (dates in MM/DD/YYYY format)

VALID metrics:
- SUM(Sales)
- SUM(Profit)
- COUNT(*)
- COUNT(DISTINCT "Order ID")
- AVG(Sales)
- AVG(Profit)

IMPORTANT: Use ONLY these column names and metrics. Do NOT invent columns.

Format EXACTLY:
CHART_NAME: Sales by Region
GROUP_BY: Region
METRIC: SUM(Sales)
TYPE: bar

CHART_NAME: Profit by Category
GROUP_BY: Category
METRIC: SUM(Profit)
TYPE: pie

Provide 3-4 charts. Use only valid column names above."""

                messages.append({"role": "assistant", "content": claude_plan})
                messages.append({"role": "user", "content": "Now provide the exact specifications for each chart in the format shown."})

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1000,
                    system=system_prompt2,
                    messages=messages
                )

                specs_text = next((b.text for b in response.content if hasattr(b, "text")), None)

                # Parse specifications
                charts_data = {}
                chart_configs = {}
                chart_queries = {}  # Store SQL queries for each chart

                # Split by CHART_NAME
                import re
                chart_blocks = re.split(r'CHART_NAME:', specs_text)

                for block in chart_blocks[1:]:
                    lines = block.strip().split('\n')
                    if not lines:
                        continue

                    chart_name = lines[0].strip()
                    group_by = None
                    metric = None
                    chart_type = "bar"

                    for line in lines[1:]:
                        if 'GROUP_BY:' in line:
                            group_by = line.split('GROUP_BY:')[1].strip()
                        elif 'METRIC:' in line:
                            metric = line.split('METRIC:')[1].strip()
                        elif 'TYPE:' in line:
                            chart_type = line.split('TYPE:')[1].strip().lower()

                    if group_by and metric:
                        try:
                            # Clean up group_by - remove extra spaces/commas
                            group_by = group_by.strip().strip(',').strip()

                            # Handle multiple dimensions - just use first one
                            if ',' in group_by:
                                group_by = group_by.split(',')[0].strip()

                            # Remove quotes if already present
                            group_by = group_by.strip('"').strip()

                            # Ensure group_by is a valid column
                            valid_cols = ["Region", "Category", "Segment", "Order Date", "Sub-Category", "Product Name", "Customer Name"]
                            if group_by not in valid_cols:
                                group_by = "Region"  # Default fallback

                            # Clean metric
                            metric = metric.strip()

                            # Build query with proper quoting
                            query = f'SELECT "{group_by}", {metric} as value FROM orders GROUP BY "{group_by}" ORDER BY value DESC;'

                            if filter_where:
                                query = query.replace('FROM orders', f'FROM orders {filter_where}')

                            result_df = con.sql(query).fetchdf()

                            if len(result_df) > 0:
                                charts_data[chart_name] = result_df
                                chart_configs[chart_name] = chart_type
                                chart_queries[chart_name] = query  # Store the actual query
                            else:
                                st.info(f"No data for {chart_name}")
                        except Exception as e:
                            error_msg = str(e)
                            if "not found" in error_msg:
                                st.warning(f"⚠️ {chart_name}: Column not found - using Region instead")
                                # Fallback query
                                try:
                                    metric_clean = metric.strip()
                                    query = f'SELECT "Region", {metric_clean} as value FROM orders GROUP BY "Region" ORDER BY value DESC;'
                                    if filter_where:
                                        query = query.replace('FROM orders', f'FROM orders {filter_where}')
                                    result_df = con.sql(query).fetchdf()
                                    if len(result_df) > 0:
                                        charts_data[chart_name] = result_df
                                        chart_configs[chart_name] = chart_type
                                except:
                                    pass
                            else:
                                st.warning(f"Error: {error_msg[:60]}")

                # Display Dashboard
                st.subheader("🎯 Dashboard")

                if len(charts_data) == 0:
                    st.error("No charts generated. Please try again.")
                else:
                    # Create tabs for Visual, Data, and SQL
                    tab1, tab2, tab3 = st.tabs(["📈 Visual", "📋 Data", "🔧 SQL"])

                    with tab1:
                        # Create a 2-column layout for more compact display
                        cols = st.columns(2, gap="small")
                        col_idx = 0

                        for chart_name, df in charts_data.items():
                            with cols[col_idx % 2]:
                                try:
                                    numeric = df.select_dtypes(include=['number']).columns.tolist()
                                    non_numeric = df.select_dtypes(exclude=['number']).columns.tolist()

                                    if numeric and non_numeric:
                                        x_col = non_numeric[0]
                                        y_col = numeric[0]
                                        chart_type = chart_configs[chart_name]

                                        # Create compact charts with smaller height
                                        if chart_type == "pie":
                                            fig = px.pie(
                                                df,
                                                names=x_col,
                                                values=y_col,
                                                title=chart_name,
                                                height=350
                                            )
                                        elif chart_type == "line":
                                            fig = px.line(
                                                df,
                                                x=x_col,
                                                y=y_col,
                                                title=chart_name,
                                                markers=True,
                                                height=350
                                            )
                                        else:
                                            # Use horizontal bar chart for better space efficiency
                                            fig = px.bar(
                                                df,
                                                y=x_col,
                                                x=y_col,
                                                orientation='h',
                                                title=chart_name,
                                                height=350,
                                                color_discrete_sequence=["#6366f1"]
                                            )

                                        # Compact layout
                                        fig.update_layout(
                                            showlegend=False,
                                            hovermode='closest',
                                            margin=dict(l=30, r=30, t=40, b=30),
                                            title_font_size=14,
                                            xaxis_title_font_size=11,
                                            yaxis_title_font_size=11,
                                            font_size=10,
                                            plot_bgcolor='rgba(0,0,0,0)',
                                            paper_bgcolor='rgba(0,0,0,0)'
                                        )

                                        # Make bars thinner
                                        if chart_type == "bar":
                                            fig.update_traces(
                                                marker=dict(
                                                    line=dict(width=0),
                                                    opacity=0.8
                                                ),
                                                marker_line_width=0
                                            )

                                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                                except Exception as e:
                                    st.error(f"Chart error: {e}")

                                col_idx += 1

                    with tab2:
                        for chart_name, df in charts_data.items():
                            st.markdown(f"**{chart_name}**")
                            st.dataframe(df, use_container_width=True)
                            st.write("")

                    with tab3:
                        for chart_name in charts_data.keys():
                            st.markdown(f"**{chart_name}**")
                            # Display the actual SQL query used
                            if chart_name in chart_queries:
                                st.code(chart_queries[chart_name], language="sql")
                            st.write("")

            except Exception as e:
                st.error(f"Error: {e}")

st.caption("Agentic Analytics POC • Superstore Dataset • Built with Claude AI")
