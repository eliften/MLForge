import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

from core.preprocessing.transform import DataTransformer


def make_df():
    data = [
        {"name": "Alice", "age": 30., "city": "New York"},
        {"name": "Bob", "age": None, "city": "Los Angeles"},
        {"name": "Charlie", "age": 25., "city": None},
        {"name": "David", "age": 35., "city": "Chicago"},
        {"name": "Eve", "age": None, "city": None},
        {"name": "Frank", "age": 28., "city": "San Francisco"},
        {"name": "Grace", "age": 22, "city": "Boston"},
        {"name": "Heidi", "age": None, "city": "Seattle"},
        {"name": "Ivan", "age": "40", "city": None},
        {"name": "Judy", "age": 27, "city": "Austin"},
    ]
    return pd.DataFrame(data)


def run_pipeline(df):
    t = DataTransformer(df)
    df1 = t.coerce_types()
    report1 = getattr(t, "report_", {})
    print("report1", report1)

    out = t.fill_nulls()
    report2 = getattr(t, "report_", {})
    print("report2", report2)

    report = {}
    report.update(report1)
    report.update(report2)

    print("Report:", report)

    return out, report


def test_cast_then_fill_removes_age_nans():
    print("Running test_cast_then_fill_removes_age_nans...")
    df = make_df()
    out, report = run_pipeline(df)

    assert is_numeric_dtype(out["age"])
    assert out["age"].isna().sum() == 0
    assert float(out.loc[out["name"] == "Ivan", "age"].iloc[0]) == 40.0


def test_string_column_not_forced():
    df = make_df()
    out, report = run_pipeline(df)

    assert "city" in out.columns
    assert not (out["city"].astype("string") == "nan").any()


def test_report_has_expected_keys():
    df = make_df()
    out, report = run_pipeline(df)

    assert "expected_types" in report
    assert "type_casted" in report
    assert "type_to_nan" in report

    assert "nulls_filled_numeric" in report