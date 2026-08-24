# Streamlit Cloud Deployment Checklist

## ✅ Pre-Deployment (Local)

- [x] Clone repo: `AgenticAnalyticsPOC` on GitHub
- [x] Create `.venv/` and install dependencies
- [x] Test app locally: `streamlit run app.py`
- [x] Verify database loads correctly
- [x] All commits pushed to GitHub `main` branch

## 🚀 Streamlit Cloud Setup

1. **Create Streamlit Account**
   - Go to https://streamlit.io/cloud
   - Sign up (use your GitHub account)

2. **Connect GitHub Repo**
   - Click "New app"
   - Select your repo: `mofidanjum/AgenticAnalyticsPOC`
   - Branch: `main`
   - File path: `streamlit_app.py`
   - Click "Deploy"

3. **Wait for Build** (2-3 minutes)
   - Streamlit Cloud will build and deploy
   - URL will be: `https://agenticanalyticspc-[random].streamlit.app`

4. **Configure Secrets** (Required!)
   - While building, go to Settings → Secrets
   - Paste:
     ```toml
     ANTHROPIC_API_KEY = "sk-ant-YOUR_API_KEY_HERE"
     ```
   - Get key from: https://console.anthropic.com/
   - Click "Save" → app auto-redeploys

5. **Test the App**
   - Click the app URL
   - Verify KPIs load
   - Try asking a question (e.g., "Show sales by region")
   - Verify Claude responds

## 🔧 Common Issues

| Issue | Fix |
|-------|-----|
| "Database not found" | Expected on cloud; data must be uploaded via git commit |
| "ANTHROPIC_API_KEY not set" | Add to Secrets in Streamlit Cloud dashboard |
| "Build failed" | Check logs in Streamlit Cloud; likely a package dependency |
| "Very slow to respond" | First request takes 10-15s; Claude is warming up |

## 📱 After Deployment

**Share the URL**: Anyone can use the dashboard now!

**Update Data**:
```powershell
# Locally:
python analytics/01_download_dataset.py
python analytics/02_load_duckdb.py

# Then push to GitHub:
git add data/processed/superstore.duckdb
git commit -m "Update sales data"
git push origin main
```

**Redeploy**: Any push to `main` auto-redeploys the app

---

## Next Steps

- [ ] Deploy to Streamlit Cloud
- [ ] Add API key to secrets
- [ ] Share dashboard URL
- [ ] Test with real questions
- [ ] Monitor Streamlit Cloud dashboard for errors
