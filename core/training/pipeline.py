from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    OneHotEncoder,
    LabelEncoder,
    OrdinalEncoder,
)
from sklearn.metrics import (
    accuracy_score,
    mean_squared_error,
    silhouette_score,
    classification_report,
    confusion_matrix,
    r2_score,
    mean_absolute_error,
    adjusted_rand_score,
)
from model_factory import ModelFactory


class PreprocessingPipeline:
    def __init__(self, data=None, task_type=None, model_name=None, params=None):
        self.data = data
        self.task_type = task_type
        self.model_name = model_name
        self.params = params or {}

        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

        self.preprocessor: ColumnTransformer | None = None
        self.y_encoder: LabelEncoder | None = None

    def _target_col(self) -> str:
        if self.data is None:
            raise ValueError("Data not provided.")
        return self.params.get("target_col", self.data.columns[-1])

    def train_test_split(self):
        if self.data is None:
            raise ValueError("Data not provided for train-test split.")

        test_size = self.params.get("test_size", 0.2)
        random_state = self.params.get("random_state", 42)

        if self.task_type == "clustering":
            self.X_train = self.data.copy()
            self.X_test = self.data.copy()
            self.y_train = None
            self.y_test = None
            return

        target_col = self._target_col()
        X = self.data.drop(columns=[target_col])
        y = self.data[target_col]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

    def scale_encode_data(self):
        if self.X_train is None or self.X_test is None:
            raise ValueError("Call train_test_split() before scale_encode_data().")

        if not isinstance(self.X_train, pd.DataFrame):
            return

        encoding = self.params.get("encoding")
        scaling = self.params.get("scaling")

        cat_cols = self.X_train.select_dtypes(include=["object", "category", "string"]).columns.tolist()
        num_cols = self.X_train.select_dtypes(exclude=["object", "category", "string"]).columns.tolist()

        if len(cat_cols) > 0 and encoding is None:
            raise ValueError(
                f"Categorical columns exist {cat_cols} but params['encoding'] is not set. "
                "Use encoding='onehot' or encoding='label'."
            )

        transformers = []

        if scaling == "standard" and len(num_cols) > 0:
            transformers.append(("num", StandardScaler(), num_cols))
        elif scaling == "minmax" and len(num_cols) > 0:
            transformers.append(("num", MinMaxScaler(), num_cols))

        if encoding == "onehot" and len(cat_cols) > 0:
            transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols))
        elif encoding == "label" and len(cat_cols) > 0:
            transformers.append(
                ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_cols)
            )

        if not transformers:
            return

        self.preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="passthrough",
        )

        self.X_train = self.preprocessor.fit_transform(self.X_train)
        self.X_test = self.preprocessor.transform(self.X_test)

        if self.task_type == "classification" and self.params.get("label_encode_y", False):
            if self.y_train is None or self.y_test is None:
                raise ValueError("y is missing for classification.")
            if pd.api.types.is_object_dtype(self.y_train) or pd.api.types.is_categorical_dtype(self.y_train):
                self.y_encoder = LabelEncoder()
                self.y_train = self.y_encoder.fit_transform(self.y_train)
                self.y_test = self.y_encoder.transform(self.y_test)

    def get_trainer(self):
        factory = ModelFactory()
        return factory.create_trainer(
            task_type=self.task_type,
            model_name=self.model_name,
            params=self.params.get("model_params", {}),
        )

    def train_model(self):
        trainer = self.get_trainer()

        if self.task_type == "clustering":
            trainer.fit(self.X_train)
        else:
            trainer.fit(self.X_train, self.y_train)
        return trainer

    def calc_metrics(self, trainer):
        metrics = self.params.get("metrics", [])
        results = {}

        y_pred = trainer.predict(self.X_test)

        if self.task_type == "classification":
            if "accuracy" in metrics:
                results["accuracy"] = accuracy_score(self.y_test, y_pred)
            if "classification_report" in metrics:
                results["classification_report"] = classification_report(self.y_test, y_pred)
            if "confusion_matrix" in metrics:
                results["confusion_matrix"] = confusion_matrix(self.y_test, y_pred)

        elif self.task_type == "regression":
            if "r2_score" in metrics:
                results["r2_score"] = r2_score(self.y_test, y_pred)
            if "mean_squared_error" in metrics:
                results["mean_squared_error"] = mean_squared_error(self.y_test, y_pred)
            if "mean_absolute_error" in metrics:
                results["mean_absolute_error"] = mean_absolute_error(self.y_test, y_pred)

        elif self.task_type == "clustering":
            if "silhouette_score" in metrics:
                results["silhouette_score"] = silhouette_score(self.X_test, y_pred)
            if "adjusted_rand_score" in metrics:
                results["adjusted_rand_score"] = None if self.y_test is None else adjusted_rand_score(self.y_test, y_pred)

        return results

    def run(self):
        self.train_test_split()
        self.scale_encode_data()
        trainer = self.train_model()
        metrics = self.calc_metrics(trainer)
        return trainer, metrics