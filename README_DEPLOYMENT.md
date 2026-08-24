# Streamlit Cloud Deployment Guide

## Quick Setup (5 minutes)

### 1. Deploy to Streamlit Cloud

```bash
git add .
git commit -m "Ready for Streamlit Cloud"
git push origin main
```

Then go to: https://streamlit.io/cloud

1. Click **"New app"**
2. Select your GitHub repo: `AgenticAnalyticsPOC`
3. Select main branch
4. File path: `streamlit_app.py`
5. Click **Deploy**

### 2. Set Secrets (Required)

Once deployed, go to **Settings** → **Secrets**

Paste this into the secrets editor:
```toml
ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY_HERE"
```

Get your API key from: https://console.anthropic.com/

### 3. Done!

Your dashboard is now live at: `https://your-app-name.streamlit.app`

---

## Troubleshooting

**"Package not found" or "installer returned non-zero exit code"**
- This app uses only pure Python packages (no C dependencies)
- If deployment still fails, check Streamlit Cloud logs for the exact error
- Deployment takes 2-3 minutes; wait for the build to complete

**"ANTHROPIC_API_KEY not configured"**
- Go to Settings → Secrets
- Add your API key
- Click Save (the app will auto-redeploy)

**"Database not found"**
- This is expected on Streamlit Cloud
- The app will show an error prompting you to refresh data
- Use `auto_execute.py` locally to download and prepare the database

---

## Local Testing (Before Cloud Deployment)

```powershell
# Activate venv
& .venv\Scripts\Activate.ps1

# Run locally
streamlit run app.py
```

Visit: http://localhost:8501

---

## Files Deployed

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Cloud entry point |
| `app.py` | Main dashboard UI |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Streamlit theme |
| `.streamlit/secrets.toml` | API key template |

---

## After Deployment

Once live, you can:
- Share the URL with anyone
- Questions work instantly (Haiku model)
- Data refreshes automatically when you push to GitHub

To refresh data locally, run:
```powershell
python analytics/01_download_dataset.py  # Download from Kaggle
python analytics/02_load_duckdb.py      # Load into database
```

Then commit and push to trigger cloud redeploy:
```bash
git add data/
git commit -m "Update data"
git push origin main
```
