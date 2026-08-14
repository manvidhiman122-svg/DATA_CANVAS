# Data Canvas 📊
*A beautiful interactive workspace for cleaning, exploring, and building ML models.*

## Features

✨ **Interactive Dashboard** - Comprehensive data visualization and analytics in one place
🧹 **Smart Data Cleaning** - Automated and custom preprocessing pipelines
📈 **Model Training** - Built-in ML algorithms with model comparison
📊 **Performance Analysis** - Detailed metrics, ROC curves, confusion matrices, and residual analysis
💾 **Project Management** - Save, load, and export your analysis projects
📥 **Data Export** - Multiple export options (CSV, ZIP, JSON, models)

## Project Structure

```
project_AI/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore patterns
├── Procfile                        # Deployment configuration
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── src/
│   ├── dashboard.py               # Interactive dashboard module
│   ├── performance_analyzer.py    # Model performance analysis
│   ├── project_manager.py         # Project save/load/export
│   ├── Data_loader.py
│   ├── Data_cleaner.py
│   ├── overview.py
│   └── preprocessing.py
└── projects/                       # Saved projects directory (auto-created)
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Git
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/project_AI.git
cd project_AI
```

2. **Create virtual environment** (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Running Locally

### Test the Application

```bash
streamlit run app.py
```

This will:
- Start a local Streamlit server (default: `http://localhost:8501`)
- Automatically open your browser
- Enable hot reload on file changes

### Features to Test

1. **Load Dataset**
   - Upload a CSV/Excel file or use default Employee_Data.xlsx
   - Check "Quick settings" metrics in sidebar

2. **Overview Tab**
   - View dataset snapshot
   - Check summary metrics and charts
   - Explore column types

3. **Dashboard Tab** 🆕
   - Executive summary cards
   - Data quality score
   - Missing values visualization
   - Statistical summaries
   - Correlation heatmaps
   - Feature distributions

4. **Clean Tab**
   - Quick clean or custom pipeline
   - Remove duplicates/constants
   - Fill missing values
   - Encode categorical columns
   - Scale numeric features
   - Download cleaned data

5. **EDA Tab**
   - Generate comprehensive reports
   - View correlations
   - Explore missing value patterns
   - Analyze categorical distributions

6. **Model Tab**
   - Select target column
   - Choose problem type (classification/regression)
   - Pick from 7 ML algorithms
   - Configure train/test split
   - Train model and view metrics

7. **Performance Tab** 🆕
   - Model comparison table
   - Classification metrics (accuracy, precision, recall, F1-score)
   - Regression metrics (R², RMSE, MAE, MAPE)
   - Confusion matrix visualization
   - ROC curves
   - Residual plots
   - Actual vs predicted scatter
   - Download performance reports

8. **Project Management** 🆕
   - Save project with name
   - Load recent projects
   - Export options (ZIP, data only, models only, reports)

## Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

**Easiest way to deploy - No server needed!**

1. **Push to GitHub**
   - Upload your project to GitHub (see GitHub section below)

2. **Connect to Streamlit Cloud**
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Click "New app"
   - Select your GitHub repo, branch, and app.py
   - Deploy!

3. **Access your app**
   - Share the public URL
   - App auto-updates on GitHub pushes

### Option 2: Heroku (Free tier may be limited)

1. **Install Heroku CLI**
   ```bash
   # Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
   # macOS: brew install heroku/brew/heroku
   # Linux: sudo snap install --classic heroku
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **View logs**
   ```bash
   heroku logs --tail
   ```

### Option 3: Docker (Advanced)

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["streamlit", "run", "app.py"]
   ```

2. **Build and run**
   ```bash
   docker build -t data-canvas .
   docker run -p 8501:8501 data-canvas
   ```

3. **Push to Docker Hub**
   ```bash
   docker tag data-canvas your-username/data-canvas
   docker push your-username/data-canvas
   ```

### Option 4: AWS, Google Cloud, Azure

See deployment guides in the `DEPLOYMENT_GUIDE.md` file for detailed instructions.

## Uploading to GitHub

### Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click "+" → "New repository"
3. **Repository name**: `project_AI` (or your preferred name)
4. **Description**: "A beautiful interactive workspace for cleaning, exploring, and building ML models"
5. **Public** (to allow others to see and clone)
6. Click "Create repository"

### Step 2: Initialize Git (First Time Only)

```bash
cd e:\project_AI

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Data Canvas with dashboard, performance analysis, and project management"

# Add remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/project_AI.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Verify on GitHub

Visit `https://github.com/YOUR_USERNAME/project_AI` to confirm files are uploaded.

### Step 4: Ongoing Updates

After making changes:

```bash
# Stage changes
git add .

# Commit with message
git commit -m "Describe your changes here"

# Push to GitHub
git push origin main
```

### Useful Git Commands

```bash
# Check status
git status

# View commit history
git log --oneline

# Create a new branch for features
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch back to main
git merge feature-name

# Delete branch
git branch -d feature-name
```

## GitHub Best Practices

### Create a `.github/workflows/` directory for CI/CD (optional)

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python -m pytest  # If you have tests
```

### Collaborate with Others

1. **Fork workflow** (for public contributions)
   - Others fork your repo
   - Make changes in their fork
   - Submit Pull Request (PR)

2. **Manage PRs**
   - Review code
   - Request changes
   - Approve and merge

## Testing Checklist

Before deploying, test these scenarios:

- [ ] App starts without errors
- [ ] Can upload and load CSV/Excel files
- [ ] Dashboard renders all charts correctly
- [ ] Can clean data with various options
- [ ] EDA reports generate without errors
- [ ] Can train multiple model types
- [ ] Performance metrics display correctly
- [ ] Can save and load projects
- [ ] Can export data in all formats
- [ ] All visualizations are responsive

## Troubleshooting

### "No module named 'X'"
```bash
pip install -r requirements.txt
```

### Port 8501 already in use
```bash
streamlit run app.py --server.port 8502
```

### Changes not reflecting
- Restart Streamlit: Press Ctrl+C and run again
- Clear browser cache
- Use Ctrl+Shift+Del to hard refresh

### Git authentication issues
```bash
# Use personal access token instead of password
# GitHub → Settings → Developer settings → Personal access tokens
# Use token as password when prompted
```

### Project files not saving
- Check write permissions in `projects/` folder
- Ensure disk space is available
- Check console for error messages

## Dependencies

| Package | Purpose |
|---------|---------|
| streamlit | Web framework |
| pandas | Data manipulation |
| scikit-learn | Machine learning |
| altair | Data visualization |
| openpyxl | Excel file handling |
| plotly | Interactive plots |
| joblib | Model serialization |

## Configuration

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Port number
- Run-on-save behavior
- Server settings

## API & Modules

### Dashboard Module
```python
from src.dashboard import Dashboard

dashboard = Dashboard(data)
dashboard.render_full_dashboard()
```

### Performance Analyzer
```python
from src.performance_analyzer import PerformanceAnalyzer

pa = PerformanceAnalyzer()
pa.add_model_performance(name, y_true, y_pred)
pa.render_model_comparison_table()
```

### Project Manager
```python
from src.project_manager import ProjectManager

pm = ProjectManager(projects_dir="projects")
pm.save_project_data(name, data, models, metrics)
pm.load_project(name)
```

## Performance Tips

- Use cleaned data for model training (in Clean tab)
- Start with smaller datasets to test features
- Use stratified split for imbalanced classification data
- Monitor memory with large datasets
- Export data regularly to avoid losing progress

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues or questions:
1. Check existing [GitHub Issues](https://github.com/YOUR_USERNAME/project_AI/issues)
2. Create a new issue with detailed description
3. Include steps to reproduce
4. Share error messages/logs

## Roadmap

- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Advanced cross-validation options
- [ ] Automated model recommendation
- [ ] Collaborative project sharing
- [ ] Real-time alerts for performance thresholds
- [ ] Custom dashboard templates
- [ ] API endpoint for predictions
- [ ] Mobile-responsive design improvements

## Authors

**MANVI DHIMAN** - Initial work and development

## Acknowledgments

- Streamlit for the excellent framework
- Scikit-learn for ML algorithms
- Altair for beautiful visualizations
- The open-source community



