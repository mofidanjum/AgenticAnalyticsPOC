# Stage 4: Text-to-SQL Agent with Integrated Charting

## Overview

Stage 4 builds an intelligent agent that:
1. Understands natural language questions
2. Generates SQL queries using Claude (Haiku model)
3. Executes queries against local DuckDB
4. Creates visualizations automatically
5. Returns answers with charts

This is a complete analytics solution.

## Quick Start

`powershell
cd C:\Users\Sarah\projects\agentic-data-pipeline
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
& .venv\Scripts\python.exe analytics/agent.py
`

Then ask:
`
You: Show me sales by region
You: Profit trends by category?
You: exit
`

## Tools

- un_sql() — Execute SQL queries
- ender_chart() — Create visualizations (bar, line, pie, scatter)

## Chart Types

- Bar chart → Comparisons (sales by region)
- Line chart → Trends over time (profit by month)
- Pie chart → Distributions (orders by segment %)
- Scatter chart → Relationships (discount vs profit)

## Output

Charts saved to: nalytics/output/chart_*.png

Each chart is 1000x600px, PNG format, high quality.

## Cost

Haiku model: \.0004 per query (~0.04¢)
\ credit = 12,500+ test queries
