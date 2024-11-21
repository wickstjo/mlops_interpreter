from actions.feature_engineering.base_feature import base_feature
from pandas import DataFrame

class shift_column(base_feature):
    def __init__(self, input_params: dict):
        self.target_column = input_params['target_column']
        self.shift_by = input_params['shift_by']
        self.output_column = input_params['output_column']

    def __repr__(self):
        return "shift_column()"

    def transform(self, dataframe: DataFrame):
        dataframe[self.output_column] = dataframe[self.target_column].shift(periods=self.shift_by)
        return dataframe