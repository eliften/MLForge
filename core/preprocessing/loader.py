import pandas as pd

class DataLoader:
    def read_file(file_path: str) -> pd.DataFrame:
        print(f"Attempting to read file: {file_path}")
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only .csv and .xlsx are supported.")
        
    def validate_data(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise ValueError("The provided data is empty.")
        if df.isnull().all().any():
            raise ValueError("The provided data contains columns with all missing values.")
        if df.columns.duplicated().any():
            raise ValueError("The provided data contains duplicate column names.")
        return df
    