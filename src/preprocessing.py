import pandas as pd

try:
    from sklearn.model_selection import train_test_split
except ImportError:  # pragma: no cover
    train_test_split = None


class DataCleaner:
    """Basic data cleaning utilities for pandas DataFrames."""

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def drop_duplicates(self):
        """Remove duplicate rows."""
        self.data = self.data.drop_duplicates().reset_index(drop=True)
        return self

    def drop_constant_columns(self):
        """Drop columns that have the same value in every row."""
        constant_columns = [
            column
            for column in self.data.columns
            if self.data[column].nunique(dropna=False) <= 1
        ]
        self.data = self.data.drop(columns=constant_columns)
        return self

    def standardize_column_names(
        self,
        lower: bool = True,
        strip: bool = True,
        replace_space: str = "_",
    ):
        """Normalize column names for easier downstream use."""
        columns = self.data.columns
        if strip:
            columns = columns.str.strip()
        if lower:
            columns = columns.str.lower()
        if replace_space is not None:
            columns = columns.str.replace(r"\s+", replace_space, regex=True)
        self.data.columns = columns
        return self

    def fill_missing_values(
        self,
        strategy: str = "mean",
        columns=None,
        fill_values: dict = None,
    ):
        """Fill missing values in a DataFrame.

        strategy: one of 'mean', 'median', 'mode', 'zero', 'constant'
        columns: list of columns to apply; default is all columns with missing values.
        fill_values: mapping of specific values per column.
        """
        if fill_values is None:
            fill_values = {}

        if columns is None:
            columns = self.data.columns[self.data.isna().any()].tolist()

        for column in columns:
            if column in fill_values:
                self.data[column] = self.data[column].fillna(fill_values[column])
                continue

            if strategy == "mean" and pd.api.types.is_numeric_dtype(self.data[column]):
                self.data[column] = self.data[column].fillna(self.data[column].mean())
            elif strategy == "median" and pd.api.types.is_numeric_dtype(self.data[column]):
                self.data[column] = self.data[column].fillna(self.data[column].median())
            elif strategy == "mode":
                mode_value = self.data[column].mode(dropna=True)
                if not mode_value.empty:
                    self.data[column] = self.data[column].fillna(mode_value.iloc[0])
            elif strategy == "zero":
                self.data[column] = self.data[column].fillna(0)
            elif strategy == "constant":
                self.data[column] = self.data[column].fillna("")
            else:
                self.data[column] = self.data[column].fillna(self.data[column].mode(dropna=True).iloc[0] if not self.data[column].mode(dropna=True).empty else self.data[column].fillna(0))

        return self

    def encode_categorical(self, columns=None, drop_original: bool = False):
        """Encode categorical columns to integer codes."""
        if columns is None:
            columns = self.data.select_dtypes(include=["object", "category"]).columns.tolist()

        for column in columns:
            self.data[column] = self.data[column].astype("category")
            self.data[column] = self.data[column].cat.codes.replace({-1: None})

        return self

    def drop_columns(self, columns):
        """Drop one or more columns from the DataFrame."""
        self.data = self.data.drop(columns=columns, errors="ignore")
        return self

    def scale_numeric(self, columns=None, method="standard"):
        """Scale numeric columns using standard or min-max scaling."""
        if columns is None:
            columns = self.data.select_dtypes(include=["number"]).columns.tolist()

        if len(columns) == 0:
            return self

        if method == "standard":
            try:
                from sklearn.preprocessing import StandardScaler
            except ImportError:
                raise ImportError("scikit-learn is required for scaling. Install it with 'pip install scikit-learn'.")
            scaler = StandardScaler()
        elif method == "minmax":
            try:
                from sklearn.preprocessing import MinMaxScaler
            except ImportError:
                raise ImportError("scikit-learn is required for scaling. Install it with 'pip install scikit-learn'.")
            scaler = MinMaxScaler()
        else:
            raise ValueError("Unsupported scaling method: {method}")

        self.data[columns] = scaler.fit_transform(self.data[columns])
        return self

    def apply_pipeline(self, steps):
        """Apply a list of named preprocessing steps in order."""
        for step in steps:
            name = step.get("name")
            params = step.get("params", {})

            if name == "drop_duplicates":
                self.drop_duplicates()
            elif name == "drop_constant_columns":
                self.drop_constant_columns()
            elif name == "standardize_column_names":
                self.standardize_column_names(**params)
            elif name == "fill_missing_values":
                self.fill_missing_values(**params)
            elif name == "encode_categorical":
                self.encode_categorical(**params)
            elif name == "drop_columns":
                self.drop_columns(**params)
            elif name == "scale_numeric":
                self.scale_numeric(**params)
            else:
                raise ValueError(f"Unsupported pipeline step: {name}")

        return self

    def prepare_for_training(
        self,
        target_column: str,
        drop_columns=None,
        categorical_columns=None,
        fill_strategy: str = "mean",
        fill_values: dict = None,
    ):
        """Return X, y for model training."""
        if target_column not in self.data.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")

        clean_data = self.data.copy()

        if drop_columns is not None:
            clean_data = clean_data.drop(columns=drop_columns, errors="ignore")

        cleaner = DataCleaner(clean_data)
        cleaner.fill_missing_values(strategy=fill_strategy, columns=categorical_columns, fill_values=fill_values)

        if categorical_columns is None:
            categorical_columns = cleaner.data.select_dtypes(include=["object", "category"]).columns.tolist()
        cleaner.encode_categorical(columns=categorical_columns)

        X = cleaner.data.drop(columns=[target_column])
        y = cleaner.data[target_column]
        return X, y

    def split_train_test(
        self,
        target_column: str,
        test_size: float = 0.2,
        random_state: int = 42,
        stratify=None,
    ):
        """Split the dataset into train/test sets using scikit-learn."""
        if train_test_split is None:
            raise ImportError(
                "scikit-learn is required for train/test split. Install it with 'pip install scikit-learn'."
            )

        if target_column not in self.data.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")

        X = self.data.drop(columns=[target_column])
        y = self.data[target_column]
        return train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify,
        )
