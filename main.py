import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from Data_loader import load_data
from Data_cleaner import Data_cleaner, prompt_choice, prompt_fill_values, prompt_yes_no
from preprocessing import DataCleaner
from overview import Dataset_Overview

try:
    from sklearn.ensemble import (
        RandomForestClassifier,
        RandomForestRegressor,
        GradientBoostingClassifier,
        GradientBoostingRegressor,
    )
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.svm import SVC, SVR
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def format_columns(columns):
    return ", ".join(str(col) for col in columns)


def pick_columns(columns):
    if not columns:
        return []

    print("Available columns:")
    for idx, col in enumerate(columns, start=1):
        print(f"  {idx}. {col}")

    selection = input("Enter column names or numbers separated by commas (leave blank for all): ").strip()
    if not selection:
        return columns

    selected = []
    for token in selection.split(","):
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            index = int(token) - 1
            if 0 <= index < len(columns):
                selected.append(columns[index])
        elif token in columns:
            selected.append(token)
        else:
            print(f"Warning: '{token}' is not a valid column and will be ignored.")

    return selected or columns


def choose_model(problem_type):
    if problem_type == "classification":
        choices = [
            "logistic_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "svc",
            "knn",
        ]
    else:
        choices = [
            "linear_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "svr",
            "knn",
        ]

    choice = prompt_choice(
        f"Choose a {problem_type} model",
        choices,
        default=choices[0],
    )
    return choice


def build_model(choice, problem_type):
    if choice == "logistic_regression":
        return LogisticRegression(max_iter=1000)
    if choice == "linear_regression":
        return LinearRegression()
    if choice == "decision_tree":
        return DecisionTreeClassifier(random_state=42) if problem_type == "classification" else DecisionTreeRegressor(random_state=42)
    if choice == "random_forest":
        return RandomForestClassifier(random_state=42) if problem_type == "classification" else RandomForestRegressor(random_state=42)
    if choice == "gradient_boosting":
        return GradientBoostingClassifier(random_state=42) if problem_type == "classification" else GradientBoostingRegressor(random_state=42)
    if choice == "svc":
        return SVC(probability=True, random_state=42) if problem_type == "classification" else SVR()
    if choice == "svr":
        return SVR()
    if choice == "knn":
        return KNeighborsClassifier() if problem_type == "classification" else KNeighborsRegressor()
    raise ValueError(f"Unsupported model choice: {choice}")


def preprocess_data(data):
    print("\n--- Preprocessing options ---")
    drop_duplicates = prompt_yes_no("Drop duplicate rows?", default="y")
    drop_constant = prompt_yes_no("Drop constant columns?", default="y")
    standardize_columns = prompt_yes_no("Standardize column names?", default="y")

    fill_missing = False
    fill_strategy = "mean"
    fill_values = None
    if data.isna().sum().sum() > 0 and prompt_yes_no("Fill missing values?", default="y"):
        fill_missing = True
        fill_strategy = prompt_choice(
            "Choose a fill strategy",
            ["mean", "median", "mode", "zero", "constant"],
            default="mean",
        )
        fill_values = prompt_fill_values()

    cleaner = Data_cleaner(data)
    cleaner.clean(
        drop_duplicates=drop_duplicates,
        drop_constant=drop_constant,
        standardize_columns=standardize_columns,
        fill_missing=fill_missing,
        fill_strategy=fill_strategy,
        fill_values=fill_values,
    )
    return cleaner.data


def encode_data(data):
    categorical_columns = data.select_dtypes(include=["object", "category"]).columns.tolist()
    if not categorical_columns:
        print("No categorical columns available for encoding.")
        return data

    print("\n--- Encoding options ---")
    if prompt_yes_no("Encode categorical columns now?", default="y"):
        selected = pick_columns(categorical_columns)
        encoder = DataCleaner(data)
        encoder.encode_categorical(columns=selected)
        return encoder.data

    return data


def build_custom_pipeline(data):
    steps = []
    print("\n--- Custom preprocessing pipeline ---")

    while True:
        step = prompt_choice(
            "Choose a preprocessing step",
            [
                "drop_duplicates",
                "drop_constant_columns",
                "standardize_column_names",
                "fill_missing_values",
                "encode_categorical",
                "drop_columns",
                "scale_numeric",
                "done",
            ],
            default="done",
        )

        if step == "done":
            break

        params = {}
        if step == "standardize_column_names":
            params["lower"] = prompt_yes_no("Lowercase column names?", default="y")
            params["strip"] = prompt_yes_no("Strip whitespace from column names?", default="y")
            replace_space = input("Replacement for whitespace in column names [underscore]: ").strip()
            if replace_space:
                params["replace_space"] = replace_space
        elif step == "fill_missing_values":
            params["strategy"] = prompt_choice(
                "Choose a fill strategy",
                ["mean", "median", "mode", "zero", "constant"],
                default="mean",
            )
            if prompt_yes_no("Choose specific columns to fill?", default="n"):
                params["columns"] = pick_columns(data.columns[data.isna().any()].tolist())
            if prompt_yes_no("Provide custom fill values per column?", default="n"):
                params["fill_values"] = prompt_fill_values()
        elif step == "encode_categorical":
            if prompt_yes_no("Encode all categorical columns?", default="y"):
                params["columns"] = None
            else:
                categorical_columns = data.select_dtypes(include=["object", "category"]).columns.tolist()
                params["columns"] = pick_columns(categorical_columns)
        elif step == "drop_columns":
            params["columns"] = pick_columns(data.columns.tolist())
        elif step == "scale_numeric":
            if prompt_yes_no("Scale all numeric columns?", default="y"):
                params["columns"] = None
            else:
                numeric_columns = data.select_dtypes(include=["number"]).columns.tolist()
                params["columns"] = pick_columns(numeric_columns)
            params["method"] = prompt_choice(
                "Choose scaling method",
                ["standard", "minmax"],
                default="standard",
            )

        steps.append({"name": step, "params": params})
        if not prompt_yes_no("Add another step?", default="y"):
            break

    if not steps:
        print("No pipeline steps selected. Skipping custom pipeline.")
        return data

    cleaner = DataCleaner(data.copy())
    cleaner.apply_pipeline(steps)
    return cleaner.data


def display_custom_report(data):
    overview = Dataset_Overview(data)
    print("\n--- Custom report ---")

    if prompt_yes_no("Show basic overview?", default="y"):
        print(overview.basic_overview())

    if prompt_yes_no("Show missing-value summary?", default="y"):
        print("\nMissing values:\n", overview.missing_value_summary())

    if prompt_yes_no("Show feature type summary?", default="y"):
        print("\nFeature types:\n", overview.feature_type_summary())

    if prompt_yes_no("Show warnings?", default="y"):
        print("\nWarnings:\n", overview.generate_warnings())

    if prompt_yes_no("Show correlation matrix?", default="y"):
        print("\nCorrelation matrix:\n", overview.correlation_matrix())

    if prompt_yes_no("Show top categorical values?", default="y"):
        print("\nTop categorical values:\n", overview.top_categorical_values())


def save_cleaned_data(data):
    if not prompt_yes_no("Save cleaned data to disk?", default="n"):
        return

    output_path = input("Enter output path [cleaned_data.csv]: ").strip() or "cleaned_data.csv"
    if output_path.lower().endswith(".xlsx"):
        data.to_excel(output_path, index=False)
    else:
        data.to_csv(output_path, index=False)
    print(f"Saved cleaned data to {output_path}")


def train_model(data):
    if not SKLEARN_AVAILABLE:
        print("Scikit-learn is not installed. Install it to use the model training features.")
        return

    print("\n--- Model training ---")
    print(format_columns(data.columns))
    target_column = input("Enter the target column name: ").strip()
    if target_column not in data.columns:
        print(f"Target column '{target_column}' not found.")
        return

    X = data.drop(columns=[target_column])
    y = data[target_column].copy()

    target_is_numeric = y.dtype.kind in "biufc"
    problem_type = "classification" if not target_is_numeric else prompt_choice(
        "Choose the problem type",
        ["classification", "regression"],
        default="classification",
    )

    if problem_type == "classification" and y.dtype == "object":
        y = LabelEncoder().fit_transform(y.astype(str))

    if X.select_dtypes(include=["object", "category"]).shape[1] > 0:
        X = pd.get_dummies(X, drop_first=True)

    model_choice = choose_model(problem_type)
    model = build_model(model_choice, problem_type)

    test_size = float(input("Enter test size as a decimal (default 0.2): ").strip() or 0.2)
    random_state = 42

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y if problem_type == "classification" else None,
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("\n=== Model results ===")
    if problem_type == "classification":
        print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    else:
        print(f"MSE: {mean_squared_error(y_test, predictions):.4f}")
        print(f"R2: {r2_score(y_test, predictions):.4f}")


def display_eda_report(data):
    overview = Dataset_Overview(data)
    report = {
        "overview": overview.generate_overview(),
        "missing_values": overview.missing_value_summary(),
        "feature_types": overview.feature_type_summary(),
        "correlation_matrix": overview.correlation_matrix(),
        "top_categorical_values": overview.top_categorical_values(),
    }

    print("\n=== EDA report ===")
    print(report["overview"])
    print("\nMissing values:\n", report["missing_values"])
    print("\nFeature types:\n", report["feature_types"])
    print("\nCorrelation matrix:\n", report["correlation_matrix"])
    print("\nTop categorical values:\n", report["top_categorical_values"])


def main():
    data_path = input(f"Enter dataset path [{ROOT / 'Employee_Data.xlsx'}]: ").strip() or str(ROOT / "Employee_Data.xlsx")
    file_type = prompt_choice("Choose file type", ["csv", "excel", "sql"], default="excel")

    sql_query = None
    db_path = None
    if file_type == "sql":
        sql_query = input("Enter SQL query: ").strip()
        db_path = input("Enter SQLite database path: ").strip()

    data = load_data(data_path, file_type, sql_query=sql_query, db_path=db_path)
    if data is None:
        print("Failed to load data. Exiting.")
        return

    print("\n=== Initial overview ===")
    initial_overview = Dataset_Overview(data).basic_overview()
    for key, value in initial_overview.items():
        print(f"{key}: {value}")

    if prompt_yes_no("Would you like to preprocess the data?", default="y"):
        if prompt_yes_no("Use a custom preprocessing pipeline?", default="n"):
            data = build_custom_pipeline(data)
        else:
            data = preprocess_data(data)

        print("\n=== Cleaned overview ===")
        cleaned_overview = Dataset_Overview(data).basic_overview()
        for key, value in cleaned_overview.items():
            print(f"{key}: {value}")

        save_cleaned_data(data)

    if prompt_yes_no("Would you like to see a custom EDA report?", default="y"):
        display_custom_report(data)

    data = encode_data(data)

    if prompt_yes_no("Would you like to train a model?", default="y"):
        train_model(data)


if __name__ == "__main__":
    main()
