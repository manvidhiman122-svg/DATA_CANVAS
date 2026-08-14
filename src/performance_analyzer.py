"""
Performance Analyzer module for Data Canvas.
Provides model evaluation, metrics computation, and performance reporting.
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    roc_curve,
    auc,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
from datetime import datetime


class PerformanceAnalyzer:
    """Analyzes and tracks model performance metrics."""

    def __init__(self):
        """Initialize performance analyzer."""
        self.models = {}
        self.metrics = {}
        self.created_at = datetime.now()

    def add_model_performance(self, model_name, y_true, y_pred, y_pred_proba=None, problem_type="classification"):
        """Add model performance metrics."""
        self.models[model_name] = {
            "y_true": y_true,
            "y_pred": y_pred,
            "y_pred_proba": y_pred_proba,
            "problem_type": problem_type,
            "timestamp": datetime.now(),
        }

        if problem_type == "classification":
            self.metrics[model_name] = self._compute_classification_metrics(y_true, y_pred, y_pred_proba)
        else:
            self.metrics[model_name] = self._compute_regression_metrics(y_true, y_pred)

    def _compute_classification_metrics(self, y_true, y_pred, y_pred_proba=None):
        """Compute classification metrics."""
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="weighted", zero_division=0),
            "recall": recall_score(y_true, y_pred, average="weighted", zero_division=0),
            "f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        }

        if y_pred_proba is not None and len(np.unique(y_true)) == 2:
            try:
                metrics["roc_auc"] = roc_auc_score(y_true, y_pred_proba[:, 1])
            except:
                metrics["roc_auc"] = None

        metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred)
        metrics["classification_report"] = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

        return metrics

    def _compute_regression_metrics(self, y_true, y_pred):
        """Compute regression metrics."""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100 if np.all(y_true != 0) else np.inf

        metrics = {
            "r2": r2_score(y_true, y_pred),
            "rmse": rmse,
            "mae": mae,
            "mape": mape,
            "mse": mse,
        }

        return metrics

    def render_classification_metrics(self, model_name):
        """Render classification metrics."""
        metrics = self.metrics.get(model_name)
        if not metrics:
            st.error(f"No metrics found for {model_name}")
            return

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Accuracy", f"{metrics['accuracy']:.4f}")

        with col2:
            st.metric("Precision", f"{metrics['precision']:.4f}")

        with col3:
            st.metric("Recall", f"{metrics['recall']:.4f}")

        with col4:
            st.metric("F1-Score", f"{metrics['f1']:.4f}")

        if metrics.get("roc_auc"):
            st.metric("ROC-AUC", f"{metrics['roc_auc']:.4f}")

    def render_regression_metrics(self, model_name):
        """Render regression metrics."""
        metrics = self.metrics.get(model_name)
        if not metrics:
            st.error(f"No metrics found for {model_name}")
            return

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("R² Score", f"{metrics['r2']:.4f}")

        with col2:
            st.metric("RMSE", f"{metrics['rmse']:.4f}")

        with col3:
            st.metric("MAE", f"{metrics['mae']:.4f}")

        with col4:
            if metrics["mape"] != np.inf:
                st.metric("MAPE", f"{metrics['mape']:.2f}%")
            else:
                st.metric("MAPE", "N/A")

    def render_confusion_matrix(self, model_name):
        """Render confusion matrix visualization."""
        metrics = self.metrics.get(model_name)
        if not metrics or "confusion_matrix" not in metrics:
            return

        cm = metrics["confusion_matrix"]
        st.markdown("### Confusion Matrix")

        cm_df = pd.DataFrame(
            cm,
            index=[f"True {i}" for i in range(cm.shape[0])],
            columns=[f"Pred {i}" for i in range(cm.shape[1])],
        )
        st.dataframe(cm_df, use_container_width=True)

    def render_roc_curve(self, model_name):
        """Render ROC curve."""
        model_data = self.models.get(model_name)
        metrics = self.metrics.get(model_name)

        if not model_data or not metrics or metrics.get("roc_auc") is None:
            st.info("ROC curve not available for this model (requires binary classification with probabilities)")
            return

        y_true = model_data["y_true"]
        y_pred_proba = model_data["y_pred_proba"]

        if len(np.unique(y_true)) == 2 and y_pred_proba is not None:
            fpr, tpr, _ = roc_curve(y_true, y_pred_proba[:, 1])

            roc_df = pd.DataFrame({"False Positive Rate": fpr, "True Positive Rate": tpr})

            chart = alt.Chart(roc_df).mark_line(point=True).encode(
                x=alt.X("False Positive Rate:Q"),
                y=alt.Y("True Positive Rate:Q"),
                tooltip=["False Positive Rate", "True Positive Rate"],
            ).properties(title=f"ROC Curve (AUC: {metrics['roc_auc']:.4f})", width=500, height=400)

            st.altair_chart(chart, use_container_width=True)

    def render_residuals_plot(self, model_name):
        """Render residuals plot for regression models."""
        model_data = self.models.get(model_name)
        metrics = self.metrics.get(model_name)

        if not model_data or metrics.get("problem_type") != "regression":
            return

        y_true = model_data["y_true"]
        y_pred = model_data["y_pred"]
        residuals = y_true - y_pred

        residuals_df = pd.DataFrame({"Predicted": y_pred, "Residuals": residuals})

        st.markdown("### Residuals Plot")
        chart = alt.Chart(residuals_df).mark_point().encode(
            x=alt.X("Predicted:Q"),
            y=alt.Y("Residuals:Q"),
            tooltip=["Predicted", "Residuals"],
        ).properties(width=600, height=400)

        st.altair_chart(chart, use_container_width=True)

    def render_prediction_scatter(self, model_name):
        """Render actual vs predicted scatter plot."""
        model_data = self.models.get(model_name)

        if not model_data:
            return

        y_true = model_data["y_true"]
        y_pred = model_data["y_pred"]

        scatter_df = pd.DataFrame({"Actual": y_true, "Predicted": y_pred})

        st.markdown("### Actual vs Predicted")
        chart = alt.Chart(scatter_df).mark_point(opacity=0.6).encode(
            x=alt.X("Actual:Q"),
            y=alt.Y("Predicted:Q"),
            tooltip=["Actual", "Predicted"],
        ).properties(width=600, height=400)

        st.altair_chart(chart, use_container_width=True)

    def generate_performance_report(self, model_name):
        """Generate comprehensive performance report."""
        model_data = self.models.get(model_name)
        metrics = self.metrics.get(model_name)

        if not model_data or not metrics:
            st.error(f"No data found for model: {model_name}")
            return

        report = {
            "model_name": model_name,
            "problem_type": model_data["problem_type"],
            "timestamp": model_data["timestamp"].isoformat(),
            "metrics": {key: value for key, value in metrics.items() if not isinstance(value, np.ndarray)},
        }

        return report

    def render_model_comparison_table(self):
        """Render comparison table for all models."""
        if not self.metrics:
            st.info("No models to compare. Train at least one model first.")
            return

        comparison_data = []
        for model_name, metrics in self.metrics.items():
            row = {"Model": model_name}
            if "accuracy" in metrics:  # Classification
                row.update(
                    {
                        "Accuracy": f"{metrics['accuracy']:.4f}",
                        "Precision": f"{metrics['precision']:.4f}",
                        "Recall": f"{metrics['recall']:.4f}",
                        "F1-Score": f"{metrics['f1']:.4f}",
                    }
                )
            else:  # Regression
                row.update(
                    {
                        "R²": f"{metrics['r2']:.4f}",
                        "RMSE": f"{metrics['rmse']:.4f}",
                        "MAE": f"{metrics['mae']:.4f}",
                    }
                )
            comparison_data.append(row)

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
