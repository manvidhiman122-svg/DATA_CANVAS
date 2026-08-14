import pandas as pd

class Dataset_Overview:
    def __init__(self, data):
        self.data = data.copy()

    def basic_information(self):
        '''returns basic information about the dataset'''
        return {
            "rows": self.data.shape[0],
            "columns": self.data.shape[1],
            "duplicate_rows": self.data.duplicated().sum(),
            "memory_usage": self.data.memory_usage(deep=True).sum()
        }

    def basic_overview(self):
        overview = self.basic_information()
        overview["total_missing_values"] = int(self.data.isna().sum().sum())
        return overview

    def generate_warnings(self):
        warnings = []

        missing_columns = self.data.columns[self.data.isna().any()]
        if len(missing_columns) > 0:
            warnings.append(f"{len(missing_columns)} column(s) contain missing values.")

        duplicate_count = self.data.duplicated().sum()
        if duplicate_count > 0:
            warnings.append(f"{duplicate_count} duplicate row(s) detected.")

        constant_columns = [
            column
            for column in self.data.columns
            if self.data[column].nunique(dropna=False) <= 1
        ]
        if constant_columns:
            warnings.append(f"Constant column(s) detected: {constant_columns}")

        duplicate_columns = self.duplicate_column_names()
        if duplicate_columns:
            warnings.append(f"Duplicate column name(s) detected: {duplicate_columns}")

        return warnings

    def generate_overview(self):
        return {
            "basic_information": self.basic_information(),
            "column_information": self.column_information(),
            "numerical_summary": self.numerical_summary(),
            "categorical_summary": self.categorical_summary(),
            "duplicate_column_names": self.duplicate_column_names(),
            "warnings": self.generate_warnings(),
        }

    def duplicate_column_names(self):
        """Finds columns with duplicate names."""
    
        duplicate_columns = self.data.columns[
            self.data.columns.duplicated()
        ].tolist()
    
        return duplicate_columns

    def column_information(self):
        """Returns information about every column."""

        information = pd.DataFrame({
            "Data Type": self.data.dtypes,
            "Non-Null": self.data.notna().sum(),
            "Missing": self.data.isna().sum(),
            "Unique": self.data.nunique()
        })

        return information

    def numerical_summary(self):
        """Returns statistical summary of numerical columns."""

        return self.data.describe()

    def categorical_summary(self):
        """Returns summary of categorical columns."""

        categorical_columns = self.data.select_dtypes(
            include=["object", "category"]
        ).columns

        if len(categorical_columns) == 0:
            return None

        return self.data[categorical_columns].describe()

    def missing_value_summary(self):
        """Returns missing-value counts per column."""
        return self.data.isna().sum().rename("missing_count").to_frame()

    def feature_type_summary(self):
        """Returns column type counts."""
        return self.data.dtypes.value_counts().rename("count").to_frame()

    def correlation_matrix(self, numeric_only=True):
        """Returns correlation matrix for numeric columns."""
        return self.data.corr(numeric_only=numeric_only)

    def top_categorical_values(self, n=10):
        """Returns top values for each categorical column."""
        categorical_columns = self.data.select_dtypes(include=["object", "category"]).columns
        return {
            col: self.data[col].value_counts(dropna=False).head(n)
            for col in categorical_columns
        }

   