import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from config import LOG_FILE

def log_query(question: str, sql: str, rows: int, filters: dict = None):
    """Log query to JSON file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "sql": sql,
        "rows_returned": rows,
        "filters": filters or {}
    }

    # Read existing logs
    logs = []
    if Path(LOG_FILE).exists():
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []

    # Append new log
    logs.append(log_entry)

    # Write back
    Path(LOG_FILE).parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def get_query_history(limit: int = 10) -> list:
    """Get past queries from log file"""
    if not Path(LOG_FILE).exists():
        return []

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
        return logs[-limit:][::-1]  # Last 10, reversed (newest first)
    except:
        return []

def format_query_for_history(query_log: dict) -> str:
    """Format query log entry for display"""
    timestamp = datetime.fromisoformat(query_log["timestamp"])
    time_str = timestamp.strftime("%H:%M")
    question = query_log["question"][:40]  # First 40 chars
    return f"🕐 {time_str} - {question}..."

def export_to_csv(df: pd.DataFrame, filename: str = None) -> str:
    """Convert DataFrame to CSV string"""
    if filename is None:
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    csv_data = df.to_csv(index=False)
    return csv_data, filename

def export_to_excel(df: pd.DataFrame, filename: str = None) -> bytes:
    """Convert DataFrame to Excel bytes"""
    if filename is None:
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    excel_bytes = df.to_excel(index=False)
    return excel_bytes, filename

def build_filter_clause(region_filter: list, date_range: tuple, category_filter: list) -> str:
    """Build WHERE clause from filters"""
    conditions = []

    if region_filter:
        regions = "', '".join(region_filter)
        conditions.append(f"region IN ('{regions}')")

    if date_range:
        start_date = date_range[0].strftime("%m/%d/%Y")
        end_date = date_range[1].strftime("%m/%d/%Y")
        conditions.append(f"\"Order Date\" >= '{start_date}' AND \"Order Date\" <= '{end_date}'")

    if category_filter:
        categories = "', '".join(category_filter)
        conditions.append(f"category IN ('{categories}')")

    if conditions:
        return " AND ".join(conditions)
    return ""

def build_filtered_prompt(question: str, filters: dict) -> str:
    """Build prompt with filter information"""
    filter_info = ""

    if filters.get("region"):
        filter_info += f"Filter by regions: {', '.join(filters['region'])}. "
    if filters.get("date_range"):
        filter_info += f"Filter by date range: {filters['date_range'][0]} to {filters['date_range'][1]}. "
    if filters.get("category"):
        filter_info += f"Filter by categories: {', '.join(filters['category'])}. "

    if filter_info:
        return f"{question} ({filter_info})"
    return question

def format_results_for_display(df: pd.DataFrame) -> str:
    """Format results for display in chat"""
    if len(df) == 0:
        return "No results found."

    # Show summary
    summary = f"Found {len(df)} row(s)"
    return summary
