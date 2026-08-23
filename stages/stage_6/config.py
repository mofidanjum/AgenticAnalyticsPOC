import os
from pathlib import Path

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Database Paths
DB_PATH = "data/processed/superstore.duckdb"
METADATA_PATH = "analytics/metadata/orders.yaml"

# App Configuration
APP_TITLE = "📊 Analytics Agent"
APP_DESCRIPTION = "Chat-based analytics with AI"
PAGE_ICON = "📊"

# Log Configuration
LOG_FILE = "stages/stage_6/query_logs.json"
Path("stages/stage_6").mkdir(exist_ok=True)

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "theme": {
        "primaryColor": "#1f77b4",
        "backgroundColor": "#ffffff",
        "secondaryBackgroundColor": "#f0f0f0",
        "textColor": "#333333",
        "font": "sans serif"
    }
}
