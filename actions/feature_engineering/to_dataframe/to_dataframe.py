from actions.feature_engineering.base_feature import base_feature
from pandas import DataFrame

class to_dataframe(base_feature):
    def __repr__(self): return "to_dataframe()"

    def transform(self, dataset: list[dict]):
        return DataFrame(dataset)