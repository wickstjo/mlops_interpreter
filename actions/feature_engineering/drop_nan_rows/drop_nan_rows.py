from actions.feature_engineering.base_feature import base_feature
from pandas import DataFrame

class drop_nan_rows(base_feature):
    def __repr__(self): return "drop_nan_rows()"

    def transform(self, dataframe: DataFrame):
        dataframe.dropna(inplace=True)
        return dataframe