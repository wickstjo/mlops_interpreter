from actions.feature_engineering.base_feature import base_feature
from pandas import DataFrame

class stochastic_k(base_feature):
    def __init__(self, input_params: dict):
        self.window_size = input_params['window_size']
        self.output_column = input_params['output_column']

    def __repr__(self):
        return "stochastic_k()"

    def transform(self, dataframe: DataFrame):

        # CREATE THE FEATURE VECTOR
        p1 = dataframe['close'] - dataframe['low'].rolling(self.window_size).min()
        p2 = dataframe['high'].rolling(self.window_size).max() - dataframe['low'].rolling(self.window_size).min()
        feature_vector = 100 * (p1 / p2)

        # PUSH IT INTO THE DF
        dataframe[self.output_column] = feature_vector
        return dataframe