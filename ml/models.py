from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class RegressionJob():
    def __init__(self, *model_names, X, y):
        self.model_names = model_names
        self.X = X
        self.y = y

    def linear_regression(self):
        reg = LinearRegression().fit(self.X, self.y)
        return reg
    
    def logistic_regression(self):
        reg = LogisticRegression().fit(self.X, self.y)
        return reg
    
    def random_forest_regression(self):
        reg = RandomForestRegressor().fit(self.X, self.y)
        return reg
    

class ClassificationJob():
    def __init__(self, *model_names, X, y):
        self.model_names = model_names
        self.X = X
        self.y = y

    def random_forest_classification(self):
        clf = RandomForestClassifier().fit(self.X, self.y)


class ClusteringJob():
    def __init__(self, *model_names):
        self.model_names = model_names


class TimeSeriesJob():
    def __init__(self, *model_names):
        self.model_names = model_names

