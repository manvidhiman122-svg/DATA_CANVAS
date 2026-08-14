# Data Canvas - Deployment Guide 🚀

Complete step-by-step guide to test, deploy, and share your Data Canvas application.

---

## Part 1: LOCAL TESTING

### Step 1: Install Python Dependencies

```bash
cd e:\project_AI
pip install -r requirements.txt
```

### Step 2: Run the Application Locally

```bash
streamlit run app.py
```

**What happens:**
- Streamlit starts a local web server on `http://localhost:8501`
- Your browser automatically opens the app
- Changes to code auto-reload (hot reload)

### Step 3: Test All Features

#### Load Data
```
1. Click "Load dataset" in sidebar
2. Upload a CSV/Excel or use default Employee_Data.xlsx
3. Verify metrics show in "Quick settings"
```

#### Test Dashboard Tab
```
1. Go to "📊 Dashboard" tab
2. Scroll through all sections:
   - Executive Summary (top metrics)
   - Data Quality Overview (missing/type distribution)
   - Statistical Summary (mean, median, std, etc.)
   - Correlation Heatmap
   - Feature Distributions
   - Categorical Features
```

#### Test Data Cleaning
```
1. Go to "Clean" tab
2. Try "Quick clean" - check all boxes and click "Apply quick clean"
3. Verify cleaned data appears
4. Click "Download cleaned data" button
```

#### Test Model Training
```
1. Go to "Model" tab
2. Select any column as Target
3. Choose "classification" or "regression"
4. Pick a model (e.g., "random_forest")
5. Click "Train model"
6. Verify metrics appear
```

#### Test Performance Analysis
```
1. After training model(s), go to "📈 Performance" tab
2. Check:
   - Model Comparison table
   - Selected model's metrics
   - Performance visualizations (confusion matrix, ROC curve, etc.)
   - Download report button
```

#### Test Project Management
```
1. In sidebar, enter "test_project" as project name
2. Click "💾 Save Project"
3. Verify success message
4. Expand "📂 Recent Projects"
5. See "test_project" listed
6. Click "Load" to reload
7. Try export options
```

### Step 4: Check for Errors

**Monitor console output:**
```
- No red error messages
- "Server running on..." confirmation
- Watch for any Python warnings
```

**Browser console (F12):**
- No critical JavaScript errors
- Network requests successful

### Step 5: Stop the Server

Press `Ctrl+C` in terminal to stop Streamlit.

---

## Part 2: GITHUB SETUP

### Step 1: Create GitHub Account (if needed)

1. Go to [github.com](https://github.com)
2. Click "Sign up"
3. Complete registration
4. Verify email

### Step 2: Create New Repository

1. Click "+" in top-right corner
2. Select "New repository"
3. Fill in:
   - **Repository name**: `project_AI`
   - **Description**: "A beautiful interactive workspace for cleaning, exploring, and building ML models"
   - **Visibility**: Public (so others can see/use it)
   - **Add .gitignore**: Already included in your project
4. Click "Create repository"

### Step 3: Get Your GitHub SSH Key (One-time Setup)

#### Check for existing key:
```bash
ls ~/.ssh
```

#### Generate SSH key (if needed):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for all prompts
```

#### Add SSH key to GitHub:
```bash
# Copy SSH key
cat ~/.ssh/id_ed25519.pub
# On Windows PowerShell:
type $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
```

1. Go to GitHub → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste key from above
4. Click "Add SSH key"

#### Test SSH connection:
```bash
ssh -T git@github.com
# Should output: "Hi username! You've successfully authenticated..."
```

### Step 4: Push Code to GitHub

```bash
cd e:\project_AI

# Initialize git (first time only)
git init

# Configure git
git config user.name "Your Name"
git config user.email "your_email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Data Canvas application with dashboard, performance analysis, and project management"

# Add remote repository (replace YOUR_USERNAME)
git remote add origin git@github.com:YOUR_USERNAME/project_AI.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**Expected output:**
```
Enumerating objects: XXX, done.
Counting objects: 100% (XXX/XXX), done.
Delta compression using up to X threads
Compressing objects: 100% (XXX/XXX), done.
Writing objects: 100% (XXX/XXX), XXX bytes
...
To github.com:YOUR_USERNAME/project_AI.git
 * [new branch]      main -> main
```

### Step 5: Verify on GitHub

1. Go to `https://github.com/YOUR_USERNAME/project_AI`
2. Verify files appear:
   - app.py
   - requirements.txt
   - README.md
   - src/ folder with all modules
   - .gitignore
   - Procfile
   - .streamlit/

---

## Part 3: DEPLOYMENT OPTIONS

### Option 1: Streamlit Cloud (RECOMMENDED - Free & Easiest)

#### Prerequisites:
- GitHub account with your code pushed ✓
- Streamlit account (free)

#### Deploy Steps:

1. **Create Streamlit Account**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "Sign up with GitHub"
   - Authorize Streamlit
   - Verify email

2. **Deploy Your App**
   - Click "New app" button
   - Select GitHub repo: `YOUR_USERNAME/project_AI`
   - Select branch: `main`
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Wait for Deployment** (2-3 minutes)
   - You'll see build logs
   - When complete, you get a public URL
   - Share the URL: `https://YOUR_USERNAME-project-ai.streamlit.app`

4. **Auto-Updates**
   - Every push to GitHub auto-deploys
   - Check "Advanced settings" to disable if needed

#### Test Deployed App:
- Open the URL in browser
- Test all features (same as local testing)
- Share with others!

---

### Option 2: Heroku Deployment

#### Prerequisites:
- Heroku account (free, but paid dynos recommended)
- Heroku CLI installed
- Code pushed to GitHub

#### Deploy Steps:

```bash
# Login to Heroku
heroku login

# Create app (replace with your app name)
heroku create your-data-canvas-app

# Push to Heroku
git push heroku main

# View logs
heroku logs --tail

# Open app in browser
heroku open
```

**Access your app:**
- `https://your-data-canvas-app.herokuapp.com`

**Common Issues:**

```bash
# Check if app is running
heroku ps

# Scale up if needed
heroku ps:scale web=1

# View detailed logs
heroku logs --tail --app your-data-canvas-app

# Rebuild
heroku rebuild -a your-data-canvas-app
```

---

### Option 3: Google Cloud Run (Fast & Scalable)

1. **Install Google Cloud SDK**
   ```bash
   # Download from https://cloud.google.com/sdk/docs/install
   gcloud init
   gcloud auth login
   ```

2. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "--server.port=8501", "--server.address=0.0.0.0", "app.py"]
   ```

3. **Deploy**
   ```bash
   gcloud run deploy data-canvas \
     --source . \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated
   ```

---

### Option 4: Docker (Local or Any Cloud)

1. **Build Docker Image**
   ```bash
   docker build -t data-canvas:latest .
   ```

2. **Run Locally**
   ```bash
   docker run -p 8501:8501 data-canvas:latest
   # Access on http://localhost:8501
   ```

3. **Push to Docker Hub**
   ```bash
   docker login
   docker tag data-canvas:latest YOUR_USERNAME/data-canvas:latest
   docker push YOUR_USERNAME/data-canvas:latest
   ```

4. **Deploy on any cloud** (AWS, GCP, Azure, DigitalOcean)
   - Pull your image: `docker pull YOUR_USERNAME/data-canvas:latest`
   - Run it with exposed port

---

## Part 4: POST-DEPLOYMENT TESTING

### Test Production App

1. **Visit your deployment URL**
   ```
   Streamlit Cloud: https://YOUR_USERNAME-project-ai.streamlit.app
   Heroku: https://your-data-canvas-app.herokuapp.com
   Google Cloud: https://data-canvas-XXXXX-uc.a.run.app
   ```

2. **Run same tests as local:**
   - Load data ✓
   - Test each tab ✓
   - Train model ✓
   - Save project ✓
   - Check performance analysis ✓

3. **Check Performance**
   - Page load time
   - Upload/download speed
   - Model training response time
   - No timeout errors

---

## Part 5: SHARING & COLLABORATION

### Share Your App

1. **Share URL**
   ```
   Send link to: https://YOUR_USERNAME-project-ai.streamlit.app
   ```

2. **Create GitHub Badge** (Add to README.md)
   ```markdown
   [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR_USERNAME-project-ai.streamlit.app)
   ```

3. **Add to Portfolio**
   - Link on your website
   - Add to LinkedIn profile
   - Include in GitHub profile README

### Collaborate on GitHub

1. **Fork Workflow**
   - Others fork your repo
   - They make changes
   - Submit Pull Request (PR)

2. **Managing PRs**
   - Review code changes
   - Comment on PR
   - Request changes if needed
   - Merge approved PRs

3. **Create Issues**
   - Report bugs
   - Request features
   - Track improvements
   - Label issues

---

## Part 6: MAINTENANCE & UPDATES

### Make Updates

```bash
# Make changes to your code
# Test locally with: streamlit run app.py

# When satisfied:
git add .
git commit -m "Clear description of changes"
git push origin main

# Streamlit Cloud auto-deploys in 1-2 minutes
# View deployment status on share.streamlit.io
```

### Monitor Production

**Streamlit Cloud:**
- Dashboard shows usage analytics
- View app health
- Check for errors in "Logs"

**Heroku:**
```bash
heroku logs --tail --app your-data-canvas-app
```

**Google Cloud Run:**
```bash
gcloud logging read "resource.type=cloud_run_revision"
```

### Update Dependencies

```bash
# Upgrade packages
pip install --upgrade -r requirements.txt

# Generate new requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

---

## Part 7: TROUBLESHOOTING DEPLOYMENT

### Streamlit Cloud Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check logs in "Manage app" → "Settings" → "Logs" |
| App crashes | Check requirements.txt has all imports |
| Slow performance | Use `@st.cache` for expensive operations |
| Large file upload error | Increase session timeout in `.streamlit/config.toml` |

### Heroku Issues

```bash
# App crashes
heroku logs --tail

# Port error
# Heroku provides port via $PORT env var
# Already configured in Procfile

# Timeout on deploy
git push heroku main --force

# Scale up for better performance
heroku ps:scale web=2
```

### Docker Issues

```bash
# Check if container is running
docker ps

# View container logs
docker logs CONTAINER_ID

# Stop container
docker stop CONTAINER_ID

# Remove container
docker rm CONTAINER_ID
```

---

## Checklist: Ready to Deploy?

- [ ] All features tested locally
- [ ] requirements.txt updated
- [ ] .gitignore configured
- [ ] README.md complete
- [ ] Code committed and pushed to GitHub
- [ ] GitHub repository is public
- [ ] Streamlit Cloud (or other platform) configured
- [ ] Deployment successful
- [ ] Production URL tested
- [ ] Ready to share!

---

## Quick Command Reference

```bash
# Git
git init                                    # Initialize repo
git add .                                   # Stage all files
git commit -m "message"                     # Commit
git push origin main                        # Push to GitHub
git pull origin main                        # Pull from GitHub

# Streamlit
streamlit run app.py                        # Run locally
streamlit run app.py --server.port 8502     # Different port
streamlit cache clear                       # Clear cache

# Heroku
heroku login                                # Login
heroku create app-name                      # Create app
git push heroku main                        # Deploy
heroku logs --tail                          # View logs
heroku open                                 # Open app

# Docker
docker build -t name:tag .                  # Build image
docker run -p 8501:8501 name:tag           # Run container
docker push username/name:tag               # Push to Docker Hub
```

---

## Next Steps

1. ✅ Test locally
2. ✅ Push to GitHub
3. ✅ Deploy to Streamlit Cloud (recommended)
4. ✅ Test production app
5. ✅ Share with others
6. ✅ Iterate on feedback

**Your Data Canvas is now live! 🎉**

---

For more help:
- Streamlit Docs: https://docs.streamlit.io
- GitHub Docs: https://docs.github.com
- Heroku Docs: https://devcenter.heroku.com
