import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from Data_loader import load_data
from Data_cleaner import Data_cleaner
from overview import Dataset_Overview
from preprocessing import DataCleaner
from dashboard import Dashboard
from performance_analyzer import PerformanceAnalyzer
from project_manager import ProjectManager

try:
    from sklearn.ensemble import (
        GradientBoostingClassifier,
        GradientBoostingRegressor,
        RandomForestClassifier,
        RandomForestRegressor,
    )
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.svm import SVC, SVR
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def parse_fill_values(raw):
    values = {}
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, val = part.split("=", 1)
            values[key.strip()] = val.strip()
    return values


def build_model(choice, problem_type):
    if choice == "logistic_regression":
        return LogisticRegression(max_iter=1000)
    if choice == "linear_regression":
        return LinearRegression()
    if choice == "decision_tree":
        return (
            DecisionTreeClassifier(random_state=42)
            if problem_type == "classification"
            else DecisionTreeRegressor(random_state=42)
        )
    if choice == "random_forest":
        return (
            RandomForestClassifier(random_state=42)
            if problem_type == "classification"
            else RandomForestRegressor(random_state=42)
        )
    if choice == "gradient_boosting":
        return (
            GradientBoostingClassifier(random_state=42)
            if problem_type == "classification"
            else GradientBoostingRegressor(random_state=42)
        )
    if choice == "svc":
        return SVC(probability=True, random_state=42) if problem_type == "classification" else SVR()
    if choice == "knn":
        return KNeighborsClassifier() if problem_type == "classification" else KNeighborsRegressor()
    raise ValueError(f"Unsupported model choice: {choice}")


def session_data():
    if "data" not in st.session_state:
        st.session_state["data"] = None
    if "cleaned_data" not in st.session_state:
        st.session_state["cleaned_data"] = None
    if "project_manager" not in st.session_state:
        st.session_state["project_manager"] = ProjectManager(projects_dir=ROOT / "projects")
    if "performance_analyzer" not in st.session_state:
        st.session_state["performance_analyzer"] = PerformanceAnalyzer()
    if "current_project" not in st.session_state:
        st.session_state["current_project"] = None
    if "preprocessing_config" not in st.session_state:
        st.session_state["preprocessing_config"] = None
    if "trained_models" not in st.session_state:
        st.session_state["trained_models"] = {}


def render_metrics(data):
    overview = Dataset_Overview(data)
    basic = overview.basic_overview()
    cols = st.columns(4)
    colors = ["#ff6f61", "#6b5b95", "#88b04b", "#f7cac9"]

    for idx, (label, value) in enumerate(
        [
            ("Rows", basic["rows"]),
            ("Columns", basic["columns"]),
            ("Missing", basic["total_missing_values"]),
            ("Duplicate rows", basic["duplicate_rows"]),
        ]
    ):
        with cols[idx]:
            st.markdown(
                f"<div style='background:{colors[idx]}; padding:18px; border-radius:16px; color:white; box-shadow:2px 2px 10px rgba(0,0,0,0.12);'>"
                f"<h3 style='margin:0'>{label}</h3>"
                f"<p style='font-size:28px; margin:4px 0 0'>{value}</p>"
                "</div>",
                unsafe_allow_html=True,
            )


def render_chart(data, chart_key="default"):
    missing = data.isna().sum().reset_index()
    missing.columns = ["column", "missing_count"]
    missing = missing[missing["missing_count"] > 0]

    if not missing.empty:
        st.markdown("### Missing values by column")
        chart = alt.Chart(missing).mark_bar(color="#ff6f61").encode(
            x=alt.X("missing_count:Q", title="Missing count"),
            y=alt.Y("column:N", sort="-x", title="Column"),
            tooltip=["column", "missing_count"],
        )
        st.altair_chart(chart, use_container_width=True)

    numeric_columns = data.select_dtypes(include=["number"]).columns.tolist()
    if numeric_columns:
        hist_col = st.selectbox("Select numeric column for distribution", numeric_columns, key=f"hist_col_{chart_key}")
        chart = alt.Chart(data).mark_area(opacity=0.3, interpolate="step").encode(
            alt.X(hist_col, bin=alt.Bin(maxbins=40), title=hist_col),
            y="count()",
        ).properties(title=f"Distribution of {hist_col}")
        st.altair_chart(chart, use_container_width=True)


def render_report(data, items):
    overview = Dataset_Overview(data)
    if "overview" in items:
        st.markdown("### Full overview")
        overview_data = overview.generate_overview()
        st.json(overview_data)

    if "missing" in items:
        st.markdown("### Missing values")
        st.dataframe(overview.missing_value_summary())

    if "feature_types" in items:
        st.markdown("### Feature types")
        st.dataframe(overview.feature_type_summary())

    if "warnings" in items:
        st.markdown("### Warnings")
        warnings = overview.generate_warnings()
        if warnings:
            for warning in warnings:
                st.warning(warning)
        else:
            st.success("No issues detected.")

    if "correlation" in items:
        st.markdown("### Correlation matrix")
        matrix = overview.correlation_matrix()
        st.dataframe(matrix)

    if "top_categorical" in items:
        st.markdown("### Top categorical values")
        st.write(overview.top_categorical_values())


def apply_custom_pipeline(data, config):
    cleaner = DataCleaner(data.copy())
    steps = []

    if config["drop_duplicates"]:
        steps.append({"name": "drop_duplicates", "params": {}})
    if config["drop_constant_columns"]:
        steps.append({"name": "drop_constant_columns", "params": {}})
    if config["standardize_column_names"]:
        steps.append(
            {
                "name": "standardize_column_names",
                "params": {
                    "lower": config["lower"],
                    "strip": config["strip"],
                    "replace_space": config["replace_space"],
                },
            }
        )
    if config["fill_missing_values"]:
        steps.append(
            {
                "name": "fill_missing_values",
                "params": {
                    "strategy": config["fill_strategy"],
                    "columns": config["fill_columns"],
                    "fill_values": config["fill_values"],
                },
            }
        )
    if config["encode_categorical"]:
        steps.append({"name": "encode_categorical", "params": {"columns": config["encode_columns"]}})
    if config["drop_columns"] and config["drop_columns_list"]:
        steps.append({"name": "drop_columns", "params": {"columns": config["drop_columns_list"]}})
    if config["scale_numeric"]:
        steps.append(
            {
                "name": "scale_numeric",
                "params": {
                    "columns": config["scale_columns"],
                    "method": config["scale_method"],
                },
            }
        )

    cleaner.apply_pipeline(steps)
    return cleaner.data


def build_model_choice(problem_type):
    if problem_type == "classification":
        return [
            "logistic_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "svc",
            "knn",
        ]
    return [
        "linear_regression",
        "decision_tree",
        "random_forest",
        "gradient_boosting",
        "svr",
        "knn",
    ]


def main():
    st.set_page_config(
        page_title="Data Canvas",
        page_icon="📊",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .big-header {
            font-size: 48px;
            font-weight: 800;
            color: #0f4c81;
            line-height: 1.1;
        }
        .subheader-text {
            color: #5e5d5d;
            font-size: 18px;
            margin-bottom: 24px;
        }
        .card {
            background: linear-gradient(135deg, #ff6f61 0%, #ff9a8b 100%);
            border-radius: 20px;
            padding: 18px;
            color: white;
            box-shadow: 0 18px 40px rgba(17, 24, 39, 0.12);
        }
        .small-card {
            background: linear-gradient(135deg, #6b5b95 0%, #8d6cab 100%);
            border-radius: 16px;
            padding: 14px;
            color: white;
            box-shadow: 0 14px 30px rgba(17, 24, 39, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    container = st.container()
    with container:
        st.markdown("<div class='big-header'>Data Canvas</div>", unsafe_allow_html=True)
        st.markdown("<div class='subheader-text'>A beautiful interactive workspace for cleaning, exploring, and building ML models.</div>", unsafe_allow_html=True)

    session_data()

    with st.sidebar:
        st.header("Load your dataset")
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
        file_type = st.selectbox("File type", ["csv", "excel"], index=1)
        path_input = st.text_input("Or enter local path", str(ROOT / "Employee_Data.xlsx"))

        if st.button("Load dataset"):
            if uploaded_file is not None:
                st.session_state["data"] = (
                    pd.read_csv(uploaded_file)
                    if file_type == "csv"
                    else pd.read_excel(uploaded_file)
                )
            else:
                st.session_state["data"] = load_data(path_input or str(ROOT / "Employee_Data.xlsx"), file_type)

        st.markdown("---")
        
        # Project Management Section
        st.markdown("### 📁 Project Management")
        
        col_proj1, col_proj2 = st.columns(2)
        with col_proj1:
            project_name = st.text_input("Project name", value=st.session_state.get("current_project") or "my_project")
        with col_proj2:
            if st.button("💾 Save Project", use_container_width=True):
                pm = st.session_state["project_manager"]
                pm.create_project(project_name)
                pm.save_project_data(
                    project_name,
                    original_data=st.session_state["data"],
                    cleaned_data=st.session_state["cleaned_data"],
                    preprocessing_config=st.session_state["preprocessing_config"],
                    models=st.session_state["trained_models"],
                )
                st.session_state["current_project"] = project_name
                st.success(f"✓ Project '{project_name}' saved!")
        
        # Load recent projects
        with st.expander("📂 Recent Projects"):
            pm = st.session_state["project_manager"]
            recent_projects = pm.get_recent_projects(limit=5)
            if recent_projects:
                for proj in recent_projects:
                    col_proj_a, col_proj_b = st.columns([3, 1])
                    with col_proj_a:
                        st.write(f"**{proj['name']}** ({proj.get('modified_at', 'N/A')[:10]})")
                    with col_proj_b:
                        if st.button("Load", key=f"load_{proj['name']}", use_container_width=True):
                            try:
                                proj_data = pm.load_project(proj['name'])
                                st.session_state["data"] = proj_data.get("original_data")
                                st.session_state["cleaned_data"] = proj_data.get("cleaned_data")
                                st.session_state["preprocessing_config"] = proj_data.get("preprocessing_config")
                                st.session_state["current_project"] = proj['name']
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to load project: {e}")
            else:
                st.info("No projects yet. Save one to get started!")
        
        # Export options
        with st.expander("📥 Export Options"):
            export_type = st.selectbox("Export type", ["Full Project (ZIP)", "Data Only", "Models Only", "Reports Only"])
            if st.button("Export", use_container_width=True):
                if not st.session_state["current_project"]:
                    st.warning("No project to export. Save a project first.")
                else:
                    pm = st.session_state["project_manager"]
                    try:
                        if export_type == "Full Project (ZIP)":
                            zip_data = pm.export_project_as_zip(st.session_state["current_project"])
                            st.download_button(
                                label="Download Project ZIP",
                                data=zip_data.getvalue(),
                                file_name=f"{st.session_state['current_project']}.zip",
                                mime="application/zip",
                            )
                        elif export_type == "Data Only":
                            data_dict = pm.export_data_only(st.session_state["current_project"])
                            if data_dict.get("original_data") is not None:
                                st.download_button(
                                    label="Download Original Data",
                                    data=data_dict["original_data"].to_csv(index=False).encode(),
                                    file_name=f"{st.session_state['current_project']}_original.csv",
                                    mime="text/csv",
                                )
                            if data_dict.get("cleaned_data") is not None:
                                st.download_button(
                                    label="Download Cleaned Data",
                                    data=data_dict["cleaned_data"].to_csv(index=False).encode(),
                                    file_name=f"{st.session_state['current_project']}_cleaned.csv",
                                    mime="text/csv",
                                )
                        st.success("Export ready!")
                    except Exception as e:
                        st.error(f"Export failed: {e}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Quick settings")
        st.write("Use the tabs to explore, clean, and model your dataset.")
        if st.session_state["data"] is not None:
            st.metric("Rows", st.session_state["data"].shape[0])
            st.metric("Columns", st.session_state["data"].shape[1])

    data = st.session_state["data"]
    if data is None:
        st.info("Upload a dataset or enter a path to begin.")
        return

    overview_tab, dashboard_tab, clean_tab, eda_tab, model_tab, performance_tab = st.tabs(
        ["Overview", "📊 Dashboard", "Clean", "EDA", "Model", "📈 Performance"]
    )

    with overview_tab:
        st.markdown("### Dataset snapshot")
        st.dataframe(data.head(150), use_container_width=True)

        st.markdown("### Summary metrics")
        render_metrics(data)

        with st.expander("Column type summary"):
            st.dataframe(Dataset_Overview(data).feature_type_summary())

        render_chart(data, chart_key="overview")

    with dashboard_tab:
        st.markdown("## 📊 Interactive Dashboard")
        dashboard = Dashboard(data)
        dashboard.render_full_dashboard()

    with clean_tab:
        st.markdown("### Smart preprocessing")
        st.markdown("Configure cleaning steps and apply them in the order you want.")
        use_custom_pipeline = st.checkbox("Enable custom pipeline", value=False)

        pipeline_config = {
            "drop_duplicates": False,
            "drop_constant_columns": False,
            "standardize_column_names": False,
            "lower": True,
            "strip": True,
            "replace_space": "_",
            "fill_missing_values": False,
            "fill_strategy": "mean",
            "fill_columns": None,
            "fill_values": None,
            "encode_categorical": False,
            "encode_columns": None,
            "drop_columns": False,
            "drop_columns_list": None,
            "scale_numeric": False,
            "scale_columns": None,
            "scale_method": "standard",
        }

        if use_custom_pipeline:
            pipeline_config["drop_duplicates"] = st.checkbox("Remove duplicate rows", value=True)
            pipeline_config["drop_constant_columns"] = st.checkbox("Remove constant columns", value=True)
            pipeline_config["standardize_column_names"] = st.checkbox("Standardize column names", value=True)
            if pipeline_config["standardize_column_names"]:
                pipeline_config["lower"] = st.checkbox("Lowercase names", value=True)
                pipeline_config["strip"] = st.checkbox("Trim whitespace", value=True)
                pipeline_config["replace_space"] = st.text_input("Whitespace replacement", value="_")

            pipeline_config["fill_missing_values"] = st.checkbox("Fill missing values", value=False)
            if pipeline_config["fill_missing_values"]:
                pipeline_config["fill_strategy"] = st.selectbox(
                    "Missing-value strategy",
                    ["mean", "median", "mode", "zero", "constant"],
                )
                pipeline_config["fill_columns"] = st.multiselect(
                    "Columns to fill",
                    options=[col for col in data.columns if data[col].isna().any()],
                )
                pipeline_config["fill_values"] = parse_fill_values(
                    st.text_input("Custom fill values (col=value,...)"),
                )

            pipeline_config["encode_categorical"] = st.checkbox("Encode categorical columns", value=False)
            if pipeline_config["encode_categorical"]:
                categorical_columns = data.select_dtypes(include=["object", "category"]).columns.tolist()
                pipeline_config["encode_columns"] = st.multiselect(
                    "Columns to encode",
                    options=categorical_columns,
                    default=categorical_columns,
                )

            pipeline_config["drop_columns"] = st.checkbox("Drop selected columns", value=False)
            if pipeline_config["drop_columns"]:
                pipeline_config["drop_columns_list"] = st.multiselect("Columns to drop", options=list(data.columns))

            pipeline_config["scale_numeric"] = st.checkbox("Scale numeric columns", value=False)
            if pipeline_config["scale_numeric"]:
                numeric_columns = data.select_dtypes(include=["number"]).columns.tolist()
                pipeline_config["scale_columns"] = st.multiselect(
                    "Numeric columns to scale",
                    options=numeric_columns,
                    default=numeric_columns,
                )
                pipeline_config["scale_method"] = st.selectbox("Scaling method", ["standard", "minmax"], index=0)

            if st.button("Apply custom pipeline"):
                st.session_state["cleaned_data"] = apply_custom_pipeline(data, pipeline_config)
                st.success("Custom preprocessing applied.")
        else:
            st.markdown("#### Quick clean")
            drop_duplicates = st.checkbox("Remove duplicate rows", value=True)
            drop_constant = st.checkbox("Remove constant columns", value=True)
            standardize_columns = st.checkbox("Standardize column names", value=True)
            fill_missing = st.checkbox("Fill missing values", value=False)
            fill_strategy = st.selectbox(
                "Fill strategy",
                ["mean", "median", "mode", "zero", "constant"],
                index=0,
            )
            fill_values = parse_fill_values(st.text_input("Custom fill values (col=value,...)"))

            if st.button("Apply quick clean"):
                cleaner = Data_cleaner(data)
                cleaner.clean(
                    drop_duplicates=drop_duplicates,
                    drop_constant=drop_constant,
                    standardize_columns=standardize_columns,
                    fill_missing=fill_missing,
                    fill_strategy=fill_strategy,
                    fill_values=fill_values,
                )
                st.session_state["cleaned_data"] = cleaner.data
                st.success("Quick clean applied.")

        if st.session_state["cleaned_data"] is not None:
            st.markdown("### Cleaned dataset preview")
            st.dataframe(st.session_state["cleaned_data"].head(150), use_container_width=True)
            st.download_button(
                label="Download cleaned data",
                data=st.session_state["cleaned_data"].to_csv(index=False).encode("utf-8"),
                file_name="cleaned_data.csv",
                mime="text/csv",
            )

    with eda_tab:
            st.markdown("### Explore your data")
            report_options = st.multiselect(
                "Choose report sections",
                ["overview", "missing", "feature_types", "warnings", "correlation", "top_categorical"],
                default=["overview", "missing", "feature_types"],
            )
            dataset_for_report = st.session_state["cleaned_data"] if st.session_state["cleaned_data"] is not None else data
            if st.button("Generate EDA report"):
                render_report(dataset_for_report, report_options)
    
            st.markdown("### Interactive charts")
            render_chart(dataset_for_report, chart_key="eda")

    with model_tab:
        st.markdown("### Build and evaluate models")
        dataset_for_training = st.session_state["cleaned_data"] if st.session_state["cleaned_data"] is not None else data
        target_column = st.selectbox("Target column", options=list(dataset_for_training.columns))
        is_numeric = pd.api.types.is_numeric_dtype(dataset_for_training[target_column])
        problem_type = (
            "classification"
            if not is_numeric
            else st.selectbox("Problem type", ["classification", "regression"], index=0)
        )
        model_choice = st.selectbox("Model", build_model_choice(problem_type))
        test_size = st.slider("Test size", min_value=0.1, max_value=0.5, value=0.2, step=0.05)

        if st.button("Train model"):
            if not SKLEARN_AVAILABLE:
                st.error("scikit-learn is required to train models.")
            else:
                X = dataset_for_training.drop(columns=[target_column])
                y = dataset_for_training[target_column].copy()
                if problem_type == "classification" and not is_numeric:
                    y = LabelEncoder().fit_transform(y.astype(str))
                if X.select_dtypes(include=["object", "category"]).shape[1] > 0:
                    X = pd.get_dummies(X, drop_first=True)
                model = build_model(model_choice, problem_type)
                
                # Check if stratification is possible for classification
                stratify_y = None
                if problem_type == "classification":
                    # Only stratify if all classes have at least 2 samples
                    class_counts = pd.Series(y).value_counts()
                    if (class_counts >= 2).all():
                        stratify_y = y
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X,
                    y,
                    test_size=test_size,
                    random_state=42,
                    stratify=stratify_y,
                )
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
                
                # Get probabilities for classification models
                y_pred_proba = None
                if problem_type == "classification" and hasattr(model, "predict_proba"):
                    try:
                        y_pred_proba = model.predict_proba(X_test)
                    except:
                        pass

                st.success("Training complete")
                
                # Add to performance analyzer
                pa = st.session_state["performance_analyzer"]
                model_name = f"{model_choice}_{len(pa.models) + 1}"
                pa.add_model_performance(
                    model_name,
                    y_test,
                    predictions,
                    y_pred_proba=y_pred_proba,
                    problem_type=problem_type,
                )
                
                # Store the trained model
                st.session_state["trained_models"][model_name] = model
                
                # Display metrics
                metric_cols = st.columns(2)
                with metric_cols[0]:
                    if problem_type == "classification":
                        st.metric("Accuracy", f"{pa.metrics[model_name]['accuracy']:.4f}")
                    else:
                        st.metric("R²", f"{pa.metrics[model_name]['r2']:.4f}")
                with metric_cols[1]:
                    if problem_type == "classification":
                        st.metric("Model", model_choice.replace("_", " ").title())
                    else:
                        st.metric("RMSE", f"{pa.metrics[model_name]['rmse']:.4f}")

    with performance_tab:
        st.markdown("## 📈 Model Performance Analysis")
        
        pa = st.session_state["performance_analyzer"]
        
        if not pa.models:
            st.info("No models trained yet. Train at least one model in the Model tab to view performance analysis.")
        else:
            st.markdown("### Model Comparison")
            pa.render_model_comparison_table()
            
            st.markdown("---")
            st.markdown("### Detailed Performance Metrics")
            
            model_to_analyze = st.selectbox("Select model to analyze", list(pa.models.keys()))
            
            if model_to_analyze:
                model_data = pa.models[model_to_analyze]
                problem_type = model_data["problem_type"]
                
                if problem_type == "classification":
                    st.markdown("#### Classification Metrics")
                    pa.render_classification_metrics(model_to_analyze)
                    
                    st.divider()
                    pa.render_confusion_matrix(model_to_analyze)
                    
                    st.divider()
                    st.markdown("#### ROC Curve Analysis")
                    pa.render_roc_curve(model_to_analyze)
                else:
                    st.markdown("#### Regression Metrics")
                    pa.render_regression_metrics(model_to_analyze)
                    
                    st.divider()
                    st.markdown("#### Prediction Analysis")
                    pa.render_prediction_scatter(model_to_analyze)
                    
                    st.divider()
                    pa.render_residuals_plot(model_to_analyze)
                
                # Generate and download report
                st.divider()
                if st.button("📄 Generate Performance Report"):
                    report = pa.generate_performance_report(model_to_analyze)
                    report_json = st.session_state["performance_analyzer"].metrics[model_to_analyze]
                    
                    st.download_button(
                        label="Download Report (JSON)",
                        data=pd.DataFrame([report_json]).to_json(orient="records", indent=2).encode(),
                        file_name=f"{model_to_analyze}_performance_report.json",
                        mime="application/json",
                    )


if __name__ == "__main__":
    main()
