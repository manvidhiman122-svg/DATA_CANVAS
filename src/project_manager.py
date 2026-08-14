"""
Project Manager module for Data Canvas.
Handles project save/load, export, and version management.
"""

import streamlit as st
import pandas as pd
import json
import pickle
import zipfile
import io
from pathlib import Path
from datetime import datetime
import os


class ProjectManager:
    """Manages project lifecycle: save, load, export, version control."""

    def __init__(self, projects_dir="projects"):
        """Initialize project manager."""
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
        self.current_project = None

    def create_project(self, project_name, description=""):
        """Create a new project."""
        project_path = self.projects_dir / project_name
        project_path.mkdir(exist_ok=True)

        metadata = {
            "name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat(),
            "version": "1.0",
            "status": "active",
        }

        with open(project_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        self.current_project = project_name
        return project_path

    def save_project_data(
        self,
        project_name,
        original_data=None,
        cleaned_data=None,
        preprocessing_config=None,
        models=None,
        metrics=None,
        notes="",
    ):
        """Save project data and configurations."""
        project_path = self.projects_dir / project_name
        project_path.mkdir(exist_ok=True)

        # Save original data
        if original_data is not None:
            original_data.to_csv(project_path / "original_data.csv", index=False)

        # Save cleaned data
        if cleaned_data is not None:
            cleaned_data.to_csv(project_path / "cleaned_data.csv", index=False)

        # Save preprocessing config
        if preprocessing_config is not None:
            with open(project_path / "preprocessing_config.json", "w") as f:
                json.dump(preprocessing_config, f, indent=2, default=str)

        # Save models
        if models:
            models_dir = project_path / "models"
            models_dir.mkdir(exist_ok=True)
            for model_name, model in models.items():
                with open(models_dir / f"{model_name}.pkl", "wb") as f:
                    pickle.dump(model, f)

        # Save metrics
        if metrics:
            with open(project_path / "metrics.json", "w") as f:
                json.dump(metrics, f, indent=2, default=str)

        # Save notes
        if notes:
            with open(project_path / "notes.txt", "w") as f:
                f.write(notes)

        # Update metadata
        metadata_path = project_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        else:
            metadata = {"name": project_name, "created_at": datetime.now().isoformat(), "version": "1.0"}

        metadata["modified_at"] = datetime.now().isoformat()
        metadata["last_saved"] = datetime.now().isoformat()

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def load_project(self, project_name):
        """Load project data and configurations."""
        project_path = self.projects_dir / project_name

        if not project_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found.")

        project_data = {
            "name": project_name,
            "path": str(project_path),
        }

        # Load metadata
        metadata_path = project_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                project_data["metadata"] = json.load(f)

        # Load original data
        original_data_path = project_path / "original_data.csv"
        if original_data_path.exists():
            project_data["original_data"] = pd.read_csv(original_data_path)

        # Load cleaned data
        cleaned_data_path = project_path / "cleaned_data.csv"
        if cleaned_data_path.exists():
            project_data["cleaned_data"] = pd.read_csv(cleaned_data_path)

        # Load preprocessing config
        config_path = project_path / "preprocessing_config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                project_data["preprocessing_config"] = json.load(f)

        # Load models
        models_dir = project_path / "models"
        if models_dir.exists():
            models = {}
            for model_file in models_dir.glob("*.pkl"):
                with open(model_file, "rb") as f:
                    models[model_file.stem] = pickle.load(f)
            project_data["models"] = models

        # Load metrics
        metrics_path = project_path / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                project_data["metrics"] = json.load(f)

        # Load notes
        notes_path = project_path / "notes.txt"
        if notes_path.exists():
            with open(notes_path, "r") as f:
                project_data["notes"] = f.read()

        self.current_project = project_name
        return project_data

    def get_recent_projects(self, limit=10):
        """Get list of recent projects."""
        projects = []

        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                metadata_path = project_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    projects.append(metadata)

        # Sort by modified_at date
        projects.sort(key=lambda x: x.get("modified_at", ""), reverse=True)
        return projects[:limit]

    def export_project_as_zip(self, project_name):
        """Export project as a zip file."""
        project_path = self.projects_dir / project_name

        if not project_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found.")

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_path.parent)
                    zipf.write(file_path, arcname)

        zip_buffer.seek(0)
        return zip_buffer

    def export_data_only(self, project_name, include_cleaned=True):
        """Export only data files from project."""
        project_path = self.projects_dir / project_name

        if not project_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found.")

        export_data = {}

        original_path = project_path / "original_data.csv"
        if original_path.exists():
            export_data["original_data"] = pd.read_csv(original_path)

        if include_cleaned:
            cleaned_path = project_path / "cleaned_data.csv"
            if cleaned_path.exists():
                export_data["cleaned_data"] = pd.read_csv(cleaned_path)

        return export_data

    def export_models_only(self, project_name):
        """Export only model files from project."""
        project_path = self.projects_dir / project_name
        models_dir = project_path / "models"

        if not models_dir.exists():
            return {}

        models = {}
        for model_file in models_dir.glob("*.pkl"):
            with open(model_file, "rb") as f:
                models[model_file.stem] = pickle.load(f)

        return models

    def export_reports_only(self, project_name):
        """Export only report files from project."""
        project_path = self.projects_dir / project_name

        reports = {}

        metrics_path = project_path / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                reports["metrics"] = json.load(f)

        config_path = project_path / "preprocessing_config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                reports["preprocessing_config"] = json.load(f)

        notes_path = project_path / "notes.txt"
        if notes_path.exists():
            with open(notes_path, "r") as f:
                reports["notes"] = f.read()

        return reports

    def generate_project_summary(self, project_name):
        """Generate HTML summary of project."""
        try:
            project_data = self.load_project(project_name)
        except FileNotFoundError:
            return None

        html = f"""
        <html>
        <head>
            <title>{project_name} - Data Canvas Project</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #0f4c81; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #ff6f61; }}
                .metric {{ display: inline-block; margin-right: 30px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #0f4c81; }}
                .metric-label {{ color: #666; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Project: {project_name}</h1>
        """

        # Metadata section
        if "metadata" in project_data:
            meta = project_data["metadata"]
            html += f"""
            <div class="section">
                <h2>Project Information</h2>
                <div class="metric">
                    <div class="metric-label">Created:</div>
                    <div class="metric-value">{meta.get('created_at', 'N/A')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Last Modified:</div>
                    <div class="metric-value">{meta.get('modified_at', 'N/A')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Version:</div>
                    <div class="metric-value">{meta.get('version', 'N/A')}</div>
                </div>
            </div>
            """

        # Data section
        if "original_data" in project_data:
            data = project_data["original_data"]
            html += f"""
            <div class="section">
                <h2>Dataset Information</h2>
                <div class="metric">
                    <div class="metric-label">Rows:</div>
                    <div class="metric-value">{data.shape[0]}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Columns:</div>
                    <div class="metric-value">{data.shape[1]}</div>
                </div>
            </div>
            """

        # Metrics section
        if "metrics" in project_data:
            html += """
            <div class="section">
                <h2>Model Performance Metrics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
            """
            for key, value in project_data["metrics"].items():
                if isinstance(value, (int, float)):
                    html += f"<tr><td>{key}</td><td>{value:.4f}</td></tr>"

            html += """
                </table>
            </div>
            """

        html += """
        </body>
        </html>
        """

        return html

    def delete_project(self, project_name):
        """Delete a project."""
        project_path = self.projects_dir / project_name

        if not project_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found.")

        import shutil

        shutil.rmtree(project_path)

    def get_project_stats(self, project_name):
        """Get statistics about a project."""
        project_path = self.projects_dir / project_name

        if not project_path.exists():
            return None

        stats = {"project_name": project_name}

        # Size
        total_size = sum(f.stat().st_size for f in project_path.rglob("*") if f.is_file())
        stats["total_size_mb"] = total_size / (1024 * 1024)

        # File counts
        stats["csv_files"] = len(list(project_path.glob("*.csv")))
        stats["model_files"] = len(list(project_path.glob("models/*.pkl")))

        # Metadata
        metadata_path = project_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                stats["metadata"] = json.load(f)

        return stats
