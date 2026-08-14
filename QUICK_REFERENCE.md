# Quick Reference Guide 🚀

Fast commands to test, deploy, and manage your Data Canvas project.

## 1. LOCAL TESTING (5 minutes)

### Windows
```bash
# One-click run
run.bat

# Or manually:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS/Linux
```bash
# One-click run
bash run.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Access:** http://localhost:8501

---

## 2. GITHUB SETUP (10 minutes)

### First Time
```bash
cd e:\project_AI

# Configure git
git config user.name "Your Name"
git config user.email "your_email@example.com"

# Initialize and push
git init
git add .
git commit -m "Initial commit: Data Canvas"
git remote add origin git@github.com:YOUR_USERNAME/project_AI.git
git branch -M main
git push -u origin main
```

### Ongoing Updates
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

---

## 3. DEPLOYMENT OPTIONS

### 🌟 STREAMLIT CLOUD (Recommended - Free)
**⏱️ Time: 5 minutes**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select: YOUR_USERNAME / project_AI / main / app.py
5. Click "Deploy"
6. Get URL: https://YOUR_USERNAME-project-ai.streamlit.app

✅ Auto-deploys on every GitHub push
✅ Free tier available
✅ Easiest option

---

### Heroku (Free tier may be limited)
**⏱️ Time: 10 minutes**

```bash
# Install Heroku CLI (https://devcenter.heroku.com/articles/heroku-cli)

heroku login
heroku create your-app-name
git push heroku main
heroku open
```

Access: https://your-app-name.herokuapp.com

---

### Google Cloud Run
**⏱️ Time: 15 minutes**

```bash
# Install gcloud SDK

gcloud auth login
gcloud run deploy data-canvas \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

---

### Docker (Any cloud)
**⏱️ Time: 20 minutes**

```bash
# Build locally
docker build -t data-canvas:latest .

# Run locally
docker run -p 8501:8501 data-canvas:latest

# Push to Docker Hub
docker login
docker tag data-canvas:latest USERNAME/data-canvas:latest
docker push USERNAME/data-canvas:latest
```

---

## 4. TESTING CHECKLIST

```
☐ Load CSV/Excel file
☐ Dashboard renders all charts
☐ Clean data with various options
☐ EDA reports generate
☐ Train classification model
☐ Train regression model
☐ Performance tab shows metrics
☐ Save and load project
☐ Export data/models/reports
```

---

## 5. ESSENTIAL GIT COMMANDS

```bash
# Check status
git status

# View history
git log --oneline

# Create feature branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge feature
git merge feature-name

# Delete branch
git branch -d feature-name

# Undo changes
git restore filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See what changed
git diff
```

---

## 6. TROUBLESHOOTING

### App won't start locally
```bash
# Clear Streamlit cache
streamlit cache clear

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### GitHub push fails
```bash
# Check SSH connection
ssh -T git@github.com

# Re-add remote
git remote remove origin
git remote add origin git@github.com:YOUR_USERNAME/project_AI.git
```

### Deployment fails
```bash
# Check logs (Streamlit Cloud)
# View "Settings" → "Logs"

# Check logs (Heroku)
heroku logs --tail

# Check logs (Google Cloud)
gcloud logging read "resource.type=cloud_run_revision"
```

### Port already in use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

---

## 7. PROJECT STRUCTURE

```
project_AI/
├── app.py                    # Main app
├── requirements.txt          # Dependencies
├── README.md                # Documentation
├── DEPLOYMENT_GUIDE.md      # Detailed guide
├── run.bat / run.sh         # Quick start scripts
├── Dockerfile               # Docker config
├── docker-compose.yml       # Docker Compose config
├── Procfile                 # Heroku config
├── .gitignore               # Git ignore patterns
├── .streamlit/
│   └── config.toml         # Streamlit config
└── src/
    ├── dashboard.py
    ├── performance_analyzer.py
    ├── project_manager.py
    ├── Data_loader.py
    ├── Data_cleaner.py
    ├── overview.py
    └── preprocessing.py
```

---

## 8. DEPLOYMENT STATUS MATRIX

| Platform | Time | Cost | Ease | Auto-Deploy |
|----------|------|------|------|------------|
| Streamlit Cloud | 5 min | Free | ⭐⭐⭐⭐⭐ | ✅ |
| Heroku | 10 min | Free/Paid | ⭐⭐⭐⭐ | ✅ |
| Google Cloud Run | 15 min | Free/Paid | ⭐⭐⭐ | ✅ |
| Docker Hub | 20 min | Free | ⭐⭐⭐ | ❌ |
| AWS | 30 min | Paid | ⭐⭐ | ❌ |

---

## 9. SHARING YOUR APP

```markdown
# Share on GitHub
Your repo: https://github.com/YOUR_USERNAME/project_AI

# Share live app
https://YOUR_USERNAME-project-ai.streamlit.app

# Markdown badge
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR_USERNAME-project-ai.streamlit.app)

# LinkedIn profile link
Add to "Featured" or "Projects" section

# Personal website
Link to deployed app

# Portfolio
Add screenshot and link
```

---

## 10. PERFORMANCE OPTIMIZATION

### For Large Datasets
```python
import streamlit as st

# Cache expensive operations
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Cache model training
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier()
    model.fit(X, y)
    return model
```

### For Faster Loads
- Use smaller sample data for testing
- Enable caching in `.streamlit/config.toml`
- Optimize images/charts
- Clean up old project files

---

## 11. MONITORING & ANALYTICS

### Streamlit Cloud
- Dashboard shows usage stats
- Track visitor counts
- Monitor performance

### Heroku
```bash
heroku metrics web
```

### Google Cloud Run
- Cloud Console shows metrics
- Monitor CPU, memory, requests

---

## 12. CONTINUOUS DEPLOYMENT WORKFLOW

```
1. Make code changes locally
2. Test with: streamlit run app.py
3. Commit: git commit -m "message"
4. Push: git push origin main
5. Auto-deploys to Streamlit Cloud (2 min)
6. Verify on live URL
7. Share changes
```

---

## 13. ADVANCED: CI/CD PIPELINE

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: streamlit run app.py --logger.level=debug
```

---

## 14. SECURITY BEST PRACTICES

```python
# Never hardcode secrets
import streamlit as st

# Use Streamlit secrets management
# .streamlit/secrets.toml (gitignored)
api_key = st.secrets["api_key"]

# Or use environment variables
import os
api_key = os.getenv("API_KEY")
```

### GitHub
- Keep `.streamlit/secrets.toml` in `.gitignore` ✅
- Don't commit API keys/passwords ✅
- Use GitHub Secrets for CI/CD ✅

---

## 15. ROLLBACK & UPDATES

### Revert to Previous Version
```bash
git log --oneline
git revert COMMIT_HASH
git push origin main
```

### Update Dependencies
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

---

## QUICK LINKS

- 🌐 Streamlit Docs: https://docs.streamlit.io
- 📖 GitHub Docs: https://docs.github.com
- 🚀 Streamlit Cloud: https://share.streamlit.io
- 💻 Heroku Docs: https://devcenter.heroku.com
- ☁️ Google Cloud: https://cloud.google.com
- 🐳 Docker Docs: https://docs.docker.com

---

## NEED HELP?

1. **Streamlit Issues**: https://discuss.streamlit.io
2. **GitHub Issues**: https://github.com/YOUR_USERNAME/project_AI/issues
3. **Stack Overflow**: Tag with `streamlit` and `python`
4. **Streamlit Slack**: https://streamlit.io/community

---

**🎉 You're ready to deploy! Start with Streamlit Cloud for the fastest experience.**
