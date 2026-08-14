import pandas as pd
import sqlite3
import openpyxl 

class DataLoader:
    def __init__(self, file_path, file_type, sql_query=None, db_path=None):
        self.file_path = file_path
        self.file_type = file_type
        self.sql_query = sql_query
        self.db_path = db_path

    """
    Load dataset based on file type.
    file_type: 'csv', 'excel', 'sql'
    file_path: path to CSV/Excel
    sql_query: SQL query string (for SQL option)
    db_path: path to SQLite database (for SQL option)
    """

    def load_data(self):
        try:
            if self.file_type == "csv":
                data = pd.read_csv(self.file_path)
            elif self.file_type == "sql":
                conn = sqlite3.connect(self.db_path)
                data = pd.read_sql_query(self.sql_query, conn)
                conn.close()
            elif self.file_type == 'excel':
                data = pd.read_excel(self.file_path)
            else:
                print(f"Unsupported file type: {self.file_type}")
                return None
            print(f"Data loaded successfully")
            return data

        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return None

        except Exception as e:
            print(f"An error occurred while loading the data: {e}")
            return None


def load_data(file_path, file_type, sql_query=None, db_path=None):
    return DataLoader(file_path, file_type, sql_query, db_path).load_data()


if __name__ == "__main__":
    df = load_data("E:\\project_AI\\Employee_Data.xlsx", "excel")
    if df is not None:
        print(df.head())

