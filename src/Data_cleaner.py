from Data_loader import load_data
from preprocessing import DataCleaner
from overview import Dataset_Overview

class Data_cleaner:

    def __init__(self, data):
        self.data = data

    def clean(
        self,
        drop_duplicates=True,
        drop_constant=True,
        standardize_columns=True,
        fill_missing=True,
        fill_strategy="mean",
        fill_values=None,
    ):
        """Perform basic cleaning and update the dataset."""
        cleaner = DataCleaner(self.data)

        if standardize_columns:
            cleaner.standardize_column_names()
        if drop_duplicates:
            cleaner.drop_duplicates()
        if drop_constant:
            cleaner.drop_constant_columns()

        if fill_missing:
            cleaner.fill_missing_values(
                strategy=fill_strategy,
                fill_values=fill_values,
            )

        self.data = cleaner.data
        return self

    def basic_overview(self):
        overview = Dataset_Overview(self.data)
        return overview.basic_overview()

    def generate_eda_report(self, target_column=None):
        """Returns a basic EDA report for model training."""
        overview = Dataset_Overview(self.data)
        report = {
            "overview": overview.generate_overview(),
            "missing_values": overview.missing_value_summary(),
            "feature_types": overview.feature_type_summary(),
            "correlation_matrix": overview.correlation_matrix(),
            "top_categorical_values": overview.top_categorical_values(),
        }

        if target_column is not None and target_column in self.data.columns:
            report["target_distribution"] = self.data[target_column].value_counts(dropna=False)

        return report

    def generate_warnings(self):
        overview = Dataset_Overview(self.data)
        return overview.generate_warnings()

    def generate_overview(self):
        overview = Dataset_Overview(self.data)
        return overview.generate_overview()


def prompt_yes_no(prompt, default="y"):
    default = default.lower()
    choices = " [Y/n] " if default == "y" else " [y/N] "

    while True:
        answer = input(prompt + choices).strip().lower()
        if not answer:
            answer = default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please enter 'y' or 'n'.")


def prompt_choice(prompt, choices, default=None):
    choices_str = "/".join(choices)
    prompt_text = f"{prompt} [{choices_str}]"
    while True:
        answer = input(prompt_text + (f" (default={default}) " if default else " ")).strip().lower()
        if not answer and default is not None:
            return default
        if answer in choices:
            return answer
        print(f"Please choose one of: {choices_str}.")


def prompt_fill_values():
    raw = input(
        "Enter custom fill values as column=value pairs separated by commas, or leave blank: "
    ).strip()

    if not raw:
        return None

    fill_values = {}
    for pair in raw.split(","):
        if "=" not in pair:
            continue
        column, value = pair.split("=", 1)
        fill_values[column.strip()] = value.strip()

    return fill_values or None


def main():
    data = load_data("E:\\project_AI\\Employee_Data.xlsx", "excel")

    if data is None:
        raise SystemExit("Failed to load data.")

    cleaner = Data_cleaner(data)
    basic = cleaner.basic_overview()

    print("=== Basic Data Overview ===")
    for key, value in basic.items():
        print(f"{key}: {value}")

    if not prompt_yes_no("Would you like to preprocess the data?"):
        print("Preprocessing skipped. You can rerun the script when you are ready.")
        return

    drop_duplicates = prompt_yes_no("Drop duplicate rows?")
    drop_constant = prompt_yes_no("Drop constant columns?")
    standardize_columns = prompt_yes_no("Standardize column names?")

    fill_missing = False
    fill_strategy = "mean"
    fill_values = None

    if basic["total_missing_values"] > 0 and prompt_yes_no("Fill missing values?"):
        fill_missing = True
        fill_strategy = prompt_choice(
            "Choose a fill strategy",
            ["mean", "median", "mode", "zero", "constant"],
            default="mean",
        )
        fill_values = prompt_fill_values()

    cleaner.clean(
        drop_duplicates=drop_duplicates,
        drop_constant=drop_constant,
        standardize_columns=standardize_columns,
        fill_missing=fill_missing,
        fill_strategy=fill_strategy,
        fill_values=fill_values,
    )

    print("\n=== Cleaned Basic Overview ===")
    cleaned_basic = cleaner.basic_overview()
    for key, value in cleaned_basic.items():
        print(f"{key}: {value}")

    if prompt_yes_no("Show full EDA report?"):
        eda_report = cleaner.generate_eda_report()
        print("\n=== Full EDA Report ===")
        print(eda_report["overview"])
        print("\nMissing values:\n", eda_report["missing_values"])
        print("\nFeature types:\n", eda_report["feature_types"])
        print("\nCorrelation matrix:\n", eda_report["correlation_matrix"])

        if "target_distribution" in eda_report:
            print("\nTarget distribution:\n", eda_report["target_distribution"])


if __name__ == "__main__":
    main()

