from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.cluster import KMeans, DBSCAN
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.svm import SVC, SVR
from sklearn.mixture import GaussianMixture

from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor


@dataclass
class RegressionTrainer:
    model_name: str = field(default="linear_regression")
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.model = self.build_model()

    def build_model(self):
        if self.model_name == "linear_regression":
            return LinearRegression(**self.params)
        elif self.model_name == "ridge":
            return Ridge(**self.params)
        elif self.model_name == "lasso":
            return Lasso(**self.params)
        elif self.model_name == "elasticnet":
            return ElasticNet(**self.params)
        elif self.model_name == "svm":
            return SVR(**self.params)
        elif self.model_name == "lightgbm":
            return LGBMRegressor(**self.params)
        elif self.model_name == "xgboost":
            return XGBRegressor(**self.params)
        elif self.model_name == "random_forest":
            return RandomForestRegressor(**self.params)
        elif self.model_name == "decision_tree":
            return tree.DecisionTreeRegressor(**self.params)
        else:
            raise ValueError(f"Unsupported regression model: {self.model_name}")

    # alias
    def train(self, X, y):
        return self.fit(X, y)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self  # ✅ trainer döndür

    def predict(self, X):
        return self.model.predict(X)

    def score(self, X, y):
        return self.model.score(X, y)


@dataclass
class ClassificationTrainer:
    model_name: str = field(default="logistic_regression")
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.model = self.build_model()

    def build_model(self):
        if self.model_name == "logistic_regression":
            return LogisticRegression(**self.params)
        elif self.model_name == "decision_tree":
            return tree.DecisionTreeClassifier(**self.params)
        elif self.model_name == "random_forest":
            return RandomForestClassifier(**self.params)
        elif self.model_name == "gradient_boosting":
            return GradientBoostingClassifier(**self.params)
        elif self.model_name == "xgboost":
            return XGBClassifier(**self.params)
        elif self.model_name == "lightgbm":
            return LGBMClassifier(**self.params)
        elif self.model_name == "svm":
            return SVC(**self.params)
        else:
            raise ValueError(f"Unsupported classification model: {self.model_name}")

    # alias
    def train(self, X, y):
        return self.fit(X, y)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self  # ✅ trainer döndür

    def predict(self, X):
        return self.model.predict(X)

    def score(self, X, y):
        return self.model.score(X, y)


@dataclass
class ClusteringTrainer:
    model_name: str = field(default="kmeans")
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.model = self.build_model()
        self._is_fitted = False

    def build_model(self):
        if self.model_name == "kmeans":
            return KMeans(**self.params)
        elif self.model_name == "dbscan":
            return DBSCAN(**self.params)
        elif self.model_name == "gaussian_mixture":
            return GaussianMixture(**self.params)
        else:
            raise ValueError(f"Unsupported clustering model: {self.model_name}")

    # alias
    def train(self, X, y=None):
        return self.fit(X, y)

    def fit(self, X, y=None):
        self.model.fit(X)
        self._is_fitted = True
        return self  # ✅ trainer döndür

    def predict(self, X):
        # ✅ DBSCAN-safe / generic fallback
        if hasattr(self.model, "predict"):
            return self.model.predict(X)

        # DBSCAN has fit_predict (but doesn't predict on new X meaningfully)
        if hasattr(self.model, "fit_predict"):
            if not self._is_fitted:
                labels = self.model.fit_predict(X)
                self._is_fitted = True
                return labels
            if hasattr(self.model, "labels_"):
                return self.model.labels_

        if hasattr(self.model, "labels_"):
            return self.model.labels_

        raise AttributeError(f"{self.model_name} does not support predict().")