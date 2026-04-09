"""
This module provides the DataTrafsormer class which includes methods for
- missing values,
- type coercion, and
- reporting on the transformations applied to a DataFrame.
"""

import pandas as pd
import numpy as np

class DataTransformer:
    def __init__(self, df, strategy: str = 'mean'):
        self.df = df
        self.strategy = strategy
        self.report_ = {}

    def fill_nulls(self) -> pd.DataFrame:
        df = self.df.copy()

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        before = df[numeric_cols].isna().sum().to_dict()

        if self.strategy == "median":
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        elif self.strategy == "mean":
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        elif self.strategy == "mode":
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mode().iloc[0])
        else:
            raise ValueError(f"Unsupported strategy: {self.strategy}")

        after = df[numeric_cols].isna().sum().to_dict()
        filled = {c: int(before.get(c, 0) - after.get(c, 0)) for c in numeric_cols}

        self.report_["fill_strategy"] = self.strategy
        self.report_["nulls_filled_numeric"] = filled
        self.df = df
        return self
        
    def coerce_types(self) -> pd.DataFrame:

        """
        To Do: Need to carry report dataframe to logging file. 
        """
        df = self.df.copy()

        report = {
            "expected_types": {},
            "type_casted": {},
            "type_to_nan": {}
        }

        for col in df.columns:
            non_null = df[col].dropna()

            if non_null.empty:
                continue

            expected_type = non_null.apply(type).mode()[0]
            report["expected_types"][col] = expected_type.__name__

            print(f"Column '{col}' expected type: {expected_type.__name__}")

            casted = 0
            to_nan = 0

            for idx, value in df[col].items():
                if pd.isna(value):
                    continue

                if isinstance(value, expected_type):
                    continue

                try:
                    df.at[idx, col] = expected_type(value)
                    casted += 1
                except Exception:
                    df.at[idx, col] = np.nan
                    to_nan += 1

            if casted:
                report["type_casted"][col] = casted
            if to_nan:
                report["type_to_nan"][col] = to_nan

        self.df = df
        self.report_.update(report)
        return self 
    
    def to_json_safe(self):
        df = self.df.copy()

        df = df.astype(object)
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)

        try:
            df.to_excel("processed_data.xlsx", index=False)
        except Exception as e:
            print(f"Error occurred while saving Excel file: {e}")

        return df.to_dict(orient="records")
        

