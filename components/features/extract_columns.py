from pydantic import BaseModel, Field
from components.features.base_feature import base_feature
from common.testing import base_unittest
from pandas import DataFrame
import random, time

class input_schema(BaseModel):
    columns: list[str] = Field(min_length=1)

##############################################################################################################
##############################################################################################################

class feature(base_feature):
    def __init__(self, input_params: dict):
        assert isinstance(input_params, dict), f"ARG 'input_params' MUST BE OF TYPE DICT, GOT {type(input_params)}"
        input_schema(**input_params)

        self.target_columns = input_params['columns']

    def __repr__(self):
        return f"extract_columns(columns={self.target_columns})"
    
    def transform(self, dataframe: DataFrame):
        df_columns = list(dataframe.columns)

        # MAKE SURE ALL THE COLUMNS EXIST
        for column_name in self.target_columns:
            assert column_name in df_columns, f"COLUMN '{column_name}' MISSING FROM DATASET"

        # EXTRACT JUST THE VALUES OF THE FEATURE COLUMNS
        return dataframe[self.target_columns]

##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_input_schema(self):
        feature(self.input_params)

    def test_01_demo(self):
        dataset_length = random.randrange(25, 50)

        # GENERATE A SYNTHETIC DATASET
        dataset = [{
            'symbol': 'SYNTH',
            'timestamp': int(time.time())  + x,
            'open': round(random.uniform(1, 3), 3),
            'close': round(random.uniform(1, 3), 3),
            'volume': random.randrange(50, 200),
        } for x in range(dataset_length)]

        # SELECT JUST THE OPEN & CLOSE COLUMNS
        expected_output = [{
            'open': x['open'],
            'close': x['close']
        } for x in dataset]

        # CONVERT TO DATAFRAME & PASS IT THROUGH THE FEATURE
        dataset_df = DataFrame(dataset)
        dataset_df = feature({ 'columns': ['open', 'close'] }).transform(dataset_df)

        # MAKE SURE OUTPUT CONTENTS MATCH EXPECTATION
        self.assertEqual(dataset_df.to_dict(orient='records'), expected_output)