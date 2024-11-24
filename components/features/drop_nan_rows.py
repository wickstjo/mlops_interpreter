from components.features.base_feature import base_feature
from common.testing import base_unittest
from pandas import DataFrame
from random import randrange
from numpy import nan

class feature(base_feature):
    def __repr__(self): return "drop_nan_rows()"

    def transform(self, dataframe: DataFrame):
        assert isinstance(dataframe, DataFrame), f"ARG 'dataframe' MUST BE A PANDAS DATAFRAME, GOT {type(dataframe)}"
        
        dataframe.dropna(inplace=True)
        return dataframe
    
##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_demo(self):
        dataset = [
            { 'foo': randrange(1, 3), 'bar': nan },
            { 'foo': randrange(1, 3), 'bar': randrange(1, 3) },
            { 'foo': nan, 'bar': randrange(1, 3) },
            { 'foo': randrange(1, 3), 'bar': randrange(1, 3) },
            { 'foo': nan, 'bar': nan },
        ]

        expected_output = [dataset[1], dataset[3]]

        # CONVERT DATASET TO DATAFRAME & TRANSFORM IT
        dataframe = DataFrame(dataset)
        feature().transform(dataframe)

        # MAKE SURE THE CORRECT ROWS WERE DROPPED
        self.assertEqual(dataframe.to_dict(orient='records'), expected_output)