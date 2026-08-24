# Agentic Analytics POC - Complete Setup Guide

## Overview
A production-ready **Agentic Analytics Dashboard** built with Claude AI, Streamlit, and DuckDB. Ask natural language questions about Superstore sales data and Claude automatically builds interactive visualizations and dashboards.

## ✨ Features
- 📊 **AI-Powered Dashboard Builder** - Ask Claude what you want to see
- 📈 **Multiple Visualizations** - Bar, Pie, Line charts automatically generated
- 🔍 **Interactive Filters** - Filter by Region, Category, Segment
- 📋 **Three-Tab Interface** - Visual, Data, and SQL tabs
- 🎨 **Professional Dark Theme** - Beautiful modern UI
- ⚡ **Real-time Processing** - Claude + DuckDB integration

## 📋 Prerequisites

Before running, ensure you have:
1. Python 3.8+ installed
2. DuckDB database at `data/processed/superstore.duckdb`
3. Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)
4. Virtual environment activated

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install streamlit duckdb pandas plotly anthropic
```

### Step 2: Set API Key
```bash
# On Windows PowerShell:
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# On Mac/Linux:
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📁 File Structure

```
agentic-data-pipeline/
├── app.py                          # Main Streamlit app (COMPLETE & VALIDATED)
├── .streamlit/
│   └── config.toml                 # Streamlit theme config
├── data/
│   └── processed/
│       └── superstore.duckdb       # DuckDB database
├── analytics/
│   └── metadata/
│       └── orders.yaml             # Data dictionary
└── AGENTIC_ANALYTICS_POC.md        # This file
```

## 🎯 How to Use

1. **View KPI Cards** - See Total Sales, Profit, Orders, Customers
2. **Apply Filters** - Select regions, categories, segments (optional)
3. **Describe Analysis** - Type what you want to explore in natural language
4. **Click Analyze** - Claude builds your dashboard
5. **Explore Results** - Switch between Visual, Data, and SQL tabs

## 📝 Example Prompts

```
"Show me sales by region and profit by category"
"Build a dashboard with top segments and orders by category"
"I want to see profit trends, sales distribution, and customer segments"
"Create charts for each region's performance"
```

## 🔧 Configuration

Edit `.streamlit/config.toml` to customize:
- **Primary Color**: `#6366f1` (Indigo)
- **Background**: `#0a0e27` (Dark blue)
- **Secondary BG**: `#1a1f3a` (Dark slate)
- **Text Color**: `#f1f5f9` (Off-white)

## 💾 Database

The app uses **DuckDB** with the `orders` table containing:
- **Sales**: Revenue (in USD)
- **Profit**: Net profit (in USD)
- **Region**: East, West, Central, South
- **Category**: Furniture, Office Supplies, Technology
- **Segment**: Consumer, Corporate, Home Office
- **Order Date**: Date (MM/DD/YYYY format)
- **And 14+ more columns**

## 🤖 How It Works

1. **User Input** → Natural language question
2. **Claude Analysis** → Understands intent, suggests 3-4 charts
3. **Claude Specification** → Provides chart dimensions & metrics
4. **SQL Generation** → App builds valid DuckDB queries
5. **Data Retrieval** → Executes queries with filters
6. **Visualization** → Creates bar, pie, or line charts
7. **Display** → Shows results in tabs (Visual, Data, SQL)

## ⚙️ Customization

### Change Chart Types
Modify the chart type mapping in the spec parsing section (around line 269)

### Add More Columns
Update `valid_cols` list in the parsing section (line 285)

### Change Theme
Edit `.streamlit/config.toml` theme section

### Adjust Chart Size
Change `height=350` in the chart creation section (line 356)

## 🐛 Troubleshooting

### "No charts generated"
- Check your ANTHROPIC_API_KEY is set
- Ensure DuckDB file exists at `data/processed/superstore.duckdb`
- Try a simpler prompt like "Show sales by region"

### "Column not found" errors
- The app has built-in fallback to "Region"
- Check column names in `.streamlit/config.toml`

### Streamlit connection refused
```bash
# Kill any running streamlit processes
taskkill /IM python.exe /F

# Then restart
streamlit run app.py
```

## 📊 Features Breakdown

### KPI Cards
- 4 metric cards at the top
- Color-coded (Indigo, Pink, Cyan, Green)
- Real-time data from DuckDB

### Filters
- Multi-select dropdowns
- Region, Category, Segment
- All filters optional (default: all selected)

### Analysis Input
- Text area for natural language prompts
- 100px height for easy typing
- Real-time Claude processing

### Dashboard Display

**Visual Tab**
- 2-column grid layout
- Compact charts (350px height)
- Horizontal bars for readability
- Pie charts for distributions

**Data Tab**
- Raw data tables for each chart
- Full precision numbers
- Scrollable containers

**SQL Tab**
- SQL queries used for each chart
- Useful for debugging/learning

## 🎓 Learning Resources

- **Streamlit**: https://docs.streamlit.io
- **Claude API**: https://anthropic.com/docs
- **DuckDB**: https://duckdb.org/docs
- **Plotly**: https://plotly.com/python

## 📄 License & Attribution

**Created**: August 2026
**Dataset**: Superstore Sales (Kaggle)
**Built With**: Claude AI, Streamlit, DuckDB, Plotly
**Author**: Agentic Analytics POC Team

## 🎯 Next Steps

1. ✅ Run the app
2. ✅ Try different prompts
3. ✅ Explore filters
4. ✅ Check SQL queries
5. ✅ Customize theme colors
6. ✅ Deploy to Streamlit Cloud (optional)

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review your ANTHROPIC_API_KEY setup
3. Ensure DuckDB file is accessible
4. Try simpler prompts first

---

**Agentic Analytics POC** - Your intelligent data exploration assistant! 🚀
