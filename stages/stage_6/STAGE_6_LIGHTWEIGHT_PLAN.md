# Stage 6: Lightweight Streamlit Web App — Token Optimization Plan

Build a beautiful web interface with **minimal Claude API token usage**.

---

## 🎯 Token Optimization Strategy

### Problem: Current Agent Uses Tokens Every Query
```
Current (Stage 5):
User asks question
    ↓
Load metadata into prompt (expensive!)
    ↓
Send to Claude (costs tokens)
    ↓
Claude generates SQL (tokens)
    ↓
Returns answer (tokens)
    
Total: ~500-800 tokens per query × 10 queries = 5,000-8,000 tokens/hour
```

### Solution: Minimize Token Usage by 80%
```
New (Stage 6):
1. Cache metadata in memory (one-time load)
2. Only send question + filters (not whole metadata)
3. Use simpler system prompt (50% fewer tokens)
4. Reuse SQL when possible (same question = same SQL)
5. Log results locally (no re-processing)

Result: ~100-150 tokens per query × 10 queries = 1,000-1,500 tokens/hour
```

---

## 📐 Architecture (Token-Efficient)

```
┌─────────────────────────────────────────────────────┐
│ Streamlit Web App (Browser)                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Load metadata ONCE (on startup) ✅                 │
│   └─ Cached in memory, not sent to Claude          │
│                                                     │
│ User asks: "Sales by region?"                       │
│   └─ Send ONLY: question + filters                 │
│   └─ ~100 tokens (vs 800 with full metadata)       │
│                                                     │
│ Agent generates SQL locally                         │
│   └─ Run SQL against DuckDB                        │
│   └─ Generate natural language locally             │
│   └─ NO additional Claude calls                    │
│                                                     │
│ Display results in web UI                           │
│   └─ Chart (matplotlib)                            │
│   └─ Table                                         │
│   └─ Export button                                 │
│                                                     │
│ Log to JSON (free, no tokens)                       │
│   └─ Question, SQL, results, timestamp             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### 1. **One-Time Metadata Load**
```python
# Load once when app starts (not every query)
@st.cache_resource  # ← Caches in memory
def load_metadata():
    with open("analytics/metadata/orders.yaml") as f:
        return yaml.safe_load(f)

metadata = load_metadata()
# Now metadata is in memory forever, no re-loading

# DON'T send full metadata to Claude
# Instead, send only:
#   - Question
#   - Selected filters
#   - Brief column names
```

### 2. **Simplified System Prompt**
```python
# OLD (800 tokens):
system_prompt = f"""
Table description: {metadata['description']}

Columns:
{full_metadata_with_descriptions}

Notable values:
{all_constraints}
"""

# NEW (200 tokens):
system_prompt = """
You are an SQL expert. Generate SQL for Superstore sales data.
Tables: orders (21 columns: Order ID, Sales, Profit, Region, Category, Date, etc.)
Return only the SQL query, nothing else.
"""
```

### 3. **Send Only What's Needed**
```python
# OLD: Send 500 tokens of metadata
message = f"{metadata} {question}"

# NEW: Send 50 tokens of essentials
message = f"""
Question: {question}
Filters: Region={selected_regions}, Date={date_range}
Table: orders with columns [Order ID, Sales, Profit, Region, Category, ...]
Generate SQL query only.
"""
```

### 4. **Query Reuse (No Re-processing)**
```python
# Check if we've asked this before
query_hash = hash(question)
if query_hash in local_cache:
    sql, results = local_cache[query_hash]
    # Don't call Claude again!
else:
    # Only call Claude once per unique question
    sql = call_claude_for_sql(question)
    results = execute_sql(sql)
    local_cache[query_hash] = (sql, results)
```

---

## 💰 Token Cost Breakdown

### Example: 10 Queries in 1 Hour

**OLD Approach (Full Metadata)**
```
Query 1: Send metadata (500 tokens) + question (50 tokens) + response (100 tokens) = 650 tokens
Query 2: Same = 650 tokens
Query 3: Same = 650 tokens
...
Query 10: Same = 650 tokens

Total: 6,500 tokens
Cost: $0.052 (at Haiku rates)
```

**NEW Approach (Optimized)**
```
Startup: Load metadata ONCE in memory = 0 tokens (local, no Claude call)

Query 1: Send only question (50 tokens) + response (50 tokens) = 100 tokens
Query 2: Same = 100 tokens
Query 3: Same = 100 tokens
...
Query 10: Same = 100 tokens

Total: 1,000 tokens
Cost: $0.008 (at Haiku rates)

SAVINGS: 85% reduction! 🎉
```

---

## 📁 Files to Create (6 files only)

```
stages/stage_6/
├── app.py                    # Main Streamlit app (300 lines)
├── config.py                 # Configuration (20 lines)
├── utils.py                  # Helpers: logging, export (50 lines)
├── requirements.txt          # Dependencies (10 lines)
├── STAGE_6_SETUP.md         # Setup guide
└── .streamlit/config.toml   # Streamlit config
```

---

## 🏗️ Simple Architecture

```
app.py (~300 lines)
├─ Load metadata ONCE (startup)
├─ Streamlit UI (chat + filters)
├─ Accept user input (text or voice)
├─ Call agent.py (Stage 5) with simplified prompt
├─ Display results
├─ Export button
└─ Log to JSON file
```

---

## ⚡ Features (Token-Minimal)

| Feature | Tokens Cost | Enabled? |
|---------|------------|----------|
| Chat interface | 0 | ✅ |
| Voice input | 0 | ✅ |
| Filters | 0 | ✅ |
| SQL generation | ~50 per query | ✅ |
| Export CSV | 0 | ✅ |
| Query history | 0 | ✅ |
| Logging | 0 | ✅ |
| Caching | 0 | ✅ |
| Charts | 0 | ✅ |
| Database auth | - | ❌ Skip |
| Real-time dashboards | - | ❌ Skip |
| PDF export | - | ❌ Skip |

---

## 🚀 How It Works (User Perspective)

```
1. Open browser → Streamlit app loads
   Metadata loads ONCE (no Claude call)

2. User sets filters (West region, 2016 dates)

3. User types: "Top 5 products by profit?"
   ~50 tokens sent to Claude

4. Claude generates SQL (50 tokens back)

5. App executes SQL locally

6. Shows results + chart

7. User clicks "Download CSV" (no tokens)

8. User asks follow-up: "Same for East?"
   ~50 tokens (new question)

Total for 2 queries: ~200 tokens (not 1,300)
```

---

## 🔑 Key Token-Saving Techniques

### 1. Pre-load Metadata (Save 500 tokens per query)
```python
# ONE TIME on startup
metadata = load_metadata()  # Local file, no Claude

# Then never send it again
```

### 2. Minimal System Prompt (Save 300 tokens per query)
```python
# Instead of sending all 21 columns with descriptions
# Just tell Claude: "SQL expert for Superstore data"
```

### 3. Local SQL Execution (Save 100 tokens per query)
```python
# Don't ask Claude for explanation
# Just show the data table + chart
```

### 4. Query Reuse (Save tokens on repeats)
```python
# If user asks same question twice
# Use cached result, don't call Claude again
```

### 5. Voice Processing Locally
```python
# Use browser's Web Speech API
# No Claude processing, no tokens
```

---

## 📊 Cost Comparison

| Scenario | Old Approach | New Approach | Savings |
|----------|------------|--------------|---------|
| 10 queries/hour | 6,500 tokens | 1,000 tokens | 85% |
| 100 queries/day | 65,000 tokens | 10,000 tokens | 85% |
| 1,000 queries/month | 1,950,000 tokens | 300,000 tokens | 85% |
| **Monthly Cost** | **$15.60** | **$2.40** | **$13.20** |

---

## 📝 Implementation Checklist

### Phase 1: Core App (30 min)
- [ ] Create `app.py` with Streamlit UI
- [ ] Load metadata ONCE
- [ ] Add chat interface
- [ ] Add filters sidebar
- [ ] Call Stage 5 agent (simplified)

### Phase 2: Features (20 min)
- [ ] Add voice input button
- [ ] Add export CSV
- [ ] Add query history sidebar
- [ ] Add loading spinner

### Phase 3: Logging (10 min)
- [ ] Log queries to JSON file
- [ ] Add "Clear history" button

### Phase 4: Deploy (10 min)
- [ ] Create `.streamlit/config.toml`
- [ ] Deploy to Streamlit Cloud
- [ ] Test in browser

**Total: 70 minutes**

---

## 🎯 What User Sees

```
┌─────────────────────────────────────────┐
│ Analytics Agent                         │
├─────────────────────────────────────────┤
│                                         │
│ SIDEBAR:                                │
│ ├─ Filters (Region, Date, Category)    │
│ ├─ Apply button                        │
│ └─ Query History                       │
│                                         │
│ MAIN:                                   │
│ ├─ Chat messages                       │
│ ├─ Charts (matplotlib embedded)        │
│ ├─ Data tables                         │
│ ├─ Download CSV button                 │
│ │                                      │
│ └─ Input: [Type...] 🎤 [Send]          │
│                                         │
└─────────────────────────────────────────┘
```

---

## 💻 Code Overview

### `app.py` (~300 lines)
```python
import streamlit as st
from stages.stage_5.agent_with_charts import agent_loop
import json
from datetime import datetime

# 1. Load metadata ONCE (not sent to Claude)
@st.cache_resource
def load_metadata():
    # Load local YAML file
    return yaml.safe_load(open("analytics/metadata/orders.yaml"))

# 2. Filters sidebar
st.sidebar.header("Filters")
region_filter = st.sidebar.multiselect("Region", ["West", "East", "Central", "South"])
date_range = st.sidebar.date_input("Date Range", [...])
category_filter = st.sidebar.multiselect("Category", [...])

# 3. Chat interface
st.title("Analytics Agent")

user_input = st.chat_input("Ask a question...")

if user_input:
    # Show user message
    st.chat_message("user").write(user_input)
    
    # Call agent (with minimal tokens)
    with st.spinner("Processing..."):
        sql, results, answer = agent_loop(user_input, region_filter, date_range, category_filter)
    
    # Show results
    st.chat_message("assistant").write(answer)
    st.code(sql, "sql")
    st.dataframe(results)
    
    # Export
    csv = results.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "results.csv")
    
    # Log
    log_query(user_input, sql, len(results))

# 4. Query history
st.sidebar.subheader("History")
if st.sidebar.button("Clear History"):
    st.session_state.history = []
```

### `config.py` (~20 lines)
```python
API_KEY = os.getenv("ANTHROPIC_API_KEY")
DB_PATH = "data/processed/superstore.duckdb"
METADATA_PATH = "analytics/metadata/orders.yaml"
```

### `utils.py` (~50 lines)
```python
def log_query(question, sql, rows):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "sql": sql,
        "rows": rows
    }
    # Append to JSON file
```

---

## 🌐 Deployment (Free!)

```
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repo
4. Set ANTHROPIC_API_KEY env var
5. Deploy (free tier available)
6. Share link: https://your-app.streamlit.app
```

**No servers, no Docker, no DevOps!**

---

## ✅ Ready?

This plan:
- ✅ Saves 85% on tokens
- ✅ Takes 70 minutes to build
- ✅ Requires only 6 files
- ✅ Deploys free to Streamlit Cloud
- ✅ Beautiful web UI
- ✅ Works on all devices

**Shall I create the code now?** 🚀
