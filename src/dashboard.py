"""
Dashboard module for Data Canvas.
Provides interactive dashboard components for data visualization and analytics.
"""

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from pathlib import Path


class Dashboard:
    """Interactive dashboard for data insights and metrics."""

    def __init__(self, data):
        """Initialize dashboard with data."""
        self.data = data
        self.missing_count = data.isna().sum().sum()
        self.duplicate_count = data.duplicated().sum()
        self.shape = data.shape

    def calculate_data_quality_score(self):
        """Calculate data quality score (0-100)."""
        total_cells = self.data.shape[0] * self.data.shape[1]
        missing_cells = self.data.isna().sum().sum()
        completeness = 100 * (1 - missing_cells / total_cells) if total_cells > 0 else 100

        duplicate_penalty = (self.duplicate_count / self.data.shape[0]) * 10 if self.data.shape[0] > 0 else 0
        duplicate_penalty = min(duplicate_penalty, 20)

        quality_score = completeness - duplicate_penalty
        return max(0, min(100, quality_score))

    def render_executive_summary(self):
        """Render executive summary cards."""
        st.markdown("## Executive Summary")

        col1, col2, col3, col4 = st.columns(4)

        quality_score = self.calculate_data_quality_score()
        with col1:
            st.metric(
                label="Data Quality Score",
                value=f"{quality_score:.1f}%",
                delta=None,
            )

        with col2:
            st.metric(label="Total Records", value=f"{self.shape[0]:,}")

        with col3:
            st.metric(label="Total Features", value=f"{self.shape[1]:,}")

        with col4:
            st.metric(label="Duplicate Rows", value=f"{self.duplicate_count:,}")

    def render_data_quality_overview(self):
        """Render data quality overview with visualizations."""
        st.markdown("## Data Quality Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Missing Values Distribution")
            missing = self.data.isna().sum()
            missing = missing[missing > 0].sort_values(ascending=False)

            if not missing.empty:
                missing_df = pd.DataFrame({
                    'Column': missing.index,
                    'Missing_Count': missing.values
                })
                
                chart = alt.Chart(missing_df).mark_bar(color="#ff6f61").encode(
                    x=alt.X("Missing_Count:Q", title="Missing Count"),
                    y=alt.Y("Column:N", sort="-x", title="Column"),
                    tooltip=["Column", "Missing_Count"],
                ).properties(width=400, height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.success("✓ No missing values detected")

        with col2:
            st.markdown("### Data Type Distribution")
            dtype_counts = self.data.dtypes.value_counts()
            dtype_df = pd.DataFrame({
                'Data_Type': dtype_counts.index.astype(str),
                'Count': dtype_counts.values
            })
            
            chart = alt.Chart(dtype_df).mark_bar(color="#6b5b95").encode(
                x=alt.X("Count:Q", title="Count"),
                y=alt.Y("Data_Type:N", title="Data Type"),
                tooltip=["Data_Type", "Count"],
            ).properties(width=400, height=300)
            st.altair_chart(chart, use_container_width=True)

    def render_statistical_summary(self):
        """Render statistical summary for numeric columns."""
        st.markdown("## Statistical Summary")

        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()

        if numeric_cols:
            summary_data = []
            for col in numeric_cols:
                summary_data.append(
                    {
                        "Column": col,
                        "Mean": f"{self.data[col].mean():.2f}",
                        "Median": f"{self.data[col].median():.2f}",
                        "Std Dev": f"{self.data[col].std():.2f}",
                        "Min": f"{self.data[col].min():.2f}",
                        "Max": f"{self.data[col].max():.2f}",
                    }
                )

            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        else:
            st.info("No numeric columns found in the dataset.")

    def render_correlation_heatmap(self):
        """Render correlation heatmap for numeric features."""
        st.markdown("## Correlation Analysis")

        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) > 1:
            corr_matrix = self.data[numeric_cols].corr()

            # Flatten correlation matrix for Altair
            corr_data = []
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    corr_data.append({"Feature1": col1, "Feature2": col2, "Correlation": corr_matrix.iloc[i, j]})

            corr_df = pd.DataFrame(corr_data)

            chart = alt.Chart(corr_df).mark_rect().encode(
                x=alt.X("Feature1:N", title="Feature"),
                y=alt.Y("Feature2:N", title="Feature"),
                color=alt.Color(
                    "Correlation:Q",
                    scale=alt.Scale(scheme="redblue", domainMin=-1, domainMax=1),
                ),
                tooltip=["Feature1", "Feature2", alt.Tooltip("Correlation:Q", format=".2f")],
            ).properties(width=600, height=400)

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("At least 2 numeric columns required for correlation analysis.")

    def render_feature_distributions(self):
        """Render feature distributions for all numeric columns."""
        st.markdown("## Feature Distributions")

        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()

        if numeric_cols:
            selected_col = st.selectbox("Select column to visualize", numeric_cols)

            chart = alt.Chart(self.data).mark_area(opacity=0.3, interpolate="step").encode(
                alt.X(f"{selected_col}:Q", bin=alt.Bin(maxbins=40), title=selected_col),
                y="count()",
            ).properties(title=f"Distribution of {selected_col}", height=400)

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No numeric columns found for distribution analysis.")

    def render_categorical_summary(self):
        """Render categorical column summaries."""
        st.markdown("## Categorical Features Summary")

        categorical_cols = self.data.select_dtypes(include=["object", "category"]).columns.tolist()

        if categorical_cols:
            for col in categorical_cols:
                with st.expander(f"{col} (Top 10 values)"):
                    value_counts = self.data[col].value_counts().head(10)
                    chart = alt.Chart(value_counts.reset_index()).mark_bar(color="#88b04b").encode(
                        x=alt.X("count:Q", title="Count"),
                        y=alt.Y(f"{col}:N", sort="-x"),
                        tooltip=[col, "count"],
                    ).properties(height=300)
                    st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No categorical columns found in the dataset.")

    def render_full_dashboard(self):
        """Render the complete dashboard."""
        self.render_executive_summary()
        st.divider()

        self.render_data_quality_overview()
        st.divider()

        self.render_statistical_summary()
        st.divider()

        self.render_correlation_heatmap()
        st.divider()

        self.render_feature_distributions()
        st.divider()

        self.render_categorical_summary()
