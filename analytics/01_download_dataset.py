"""
Stage 1: Download Kaggle Superstore Dataset
Requires: Kaggle API token at ~/.kaggle/kaggle.json

This script:
- Downloads the Superstore dataset from Kaggle
- Creates a trimmed sample file (first 200 rows) for fixtures
"""

import pandas as pd
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi
import os

# Create directories
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/sample").mkdir(parents=True, exist_ok=True)

# Download from Kaggle using Python API
print("Downloading Superstore dataset from Kaggle...")
try:
    api = KaggleApi()
    api.authenticate()

    # Download dataset
    api.dataset_download_files(
        'vivek468/superstore-dataset-final',
        path='data/raw',
        unzip=True
    )
    print("✓ Download complete")
except Exception as e:
    print(f"Error: {e}")
    raise

# Read the CSV (handle encoding issues)
print("Reading downloaded CSV...")
df = pd.read_csv("data/raw/Sample - Superstore.csv", encoding="latin-1")
print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")

# Show columns
print("\nColumns:")
for col in df.columns:
    print(f"  - {col}")

# Create sample fixture (first 200 rows)
print("\nCreating sample fixture...")
df.head(200).to_csv("data/sample/superstore_sample.csv", index=False)
print("✓ Sample saved to data/sample/superstore_sample.csv")

print("\n✓ Stage 1 complete.")
