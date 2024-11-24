from components.features.base_feature import base_feature
from common.testing import base_unittest
from pandas import DataFrame
import random, time, numpy as np
from pydantic import BaseModel, Field

class input_schema(BaseModel):
    window_size: int = Field(ge=1)
    output_column: str = Field(min_length=3, max_length=20)

# TODO: FORCE WINDOW SIZE TO BE 1 OR LARGER
# TODO: FORCE OUTPUT COL TO BE AT LEAST 3 CHARS

##############################################################################################################
##############################################################################################################

class feature(base_feature):
    def __init__(self, input_params: dict):
        assert isinstance(input_params, dict), f"ARG 'input_params' MUST BE OF TYPE DICT, GOT {type(input_params)}"
        input_schema(**input_params)

        self.window_size = input_params['window_size']
        self.output_column = input_params['output_column']

    def __repr__(self):
        return f"stochastic_k(window_size={self.window_size})"

    def transform(self, dataframe: DataFrame):

        # MAKE SURE OUTPUT COLUMN IS UNIQUE
        existing_columns = list(dataframe.columns)
        exists_error = f"OUTPUT COLUMN '{self.output_column}' ALREADY EXISTS IN DATASET"
        assert self.output_column not in existing_columns, exists_error

        for column_name in ['close', 'low', 'high']:
            missing_error = f"REQUIRED COLUMN '{column_name}' MISSING FROM DATASET"
            assert column_name in existing_columns, missing_error

        # CREATE THE FEATURE VECTOR
        p1 = dataframe['close'] - dataframe['low'].rolling(self.window_size).min()
        p2 = dataframe['high'].rolling(self.window_size).max() - dataframe['low'].rolling(self.window_size).min()
        feature_vector = 100 * (p1 / p2)

        # PUSH IT INTO THE DF
        dataframe[self.output_column] = feature_vector
        return dataframe
    
##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_validate_input(self):
        feature(self.input_params)

    def test_01_demo(self):
        window_size = self.input_params['window_size']
        output_column = self.input_params['output_column']

        # MAKE DATASET SIZE LARGER THAN WINDOW SIZE
        init_dataset_length = window_size + 5 # + random.randrange(10, 50)

        # CREATE A FAKE DATASET
        dataset = DataFrame([{
            'symbol': 'SYNTH',
            'timestamp': int(time.time()) + x,
            'open': 6.674,
            'close': 2.452,
            'high': 4.723,
            'low': 1.863,
            'volume': random.randrange(50, 200),
        } for x in range(init_dataset_length)])

        # INSTANTIATE THE FEATURE & TRANSFORM THE DATAFRAME
        feature(self.input_params).transform(dataset)

        # MAKE SURE THE LENGTH OF THE DATASET HASNT CHANGED
        # PREVENTS FEATURE FROM USING df.dropna()
        length_error = f"FEATURE ILLEGALLY CHANGED THE LENGTH OF THE DATASET"
        self.assertEqual(len(dataset), init_dataset_length, msg=length_error)

        # MAKE SURE THE OUTPUT COLUMN EXISTS
        columns_missing_error = f"OUTPUT COLUMN '{output_column}' MISSING FROM MUTATED DATASET"
        self.assertIn(output_column, list(dataset.columns), msg=columns_missing_error)

        # CONSTRUCT THE EXPECTED FEATURE VECTOR
        window_buffer = window_size - 1
        expected_feature_vector = [np.nan for _ in range(window_buffer)] + [20.594405594405593 for _ in range(init_dataset_length - window_buffer)]
        
        # ARRAYS MAY CONTAIN NAN VALUES, SO WE NEED TO COMPARE THEM WITH NUMPY
        true_feature_vector = dataset[output_column].tolist()
        numpy_array_comparison = np.array_equal(true_feature_vector, expected_feature_vector, equal_nan=True)

        # MAKE SURE THEY ARE IDENTICAL
        content_error = f"FEATURE VECTOR IS DIFFERENT THAN EXPECTED"
        self.assertTrue(numpy_array_comparison, msg=content_error)

    def test_02_required_columns(self):

        # MAKE SURE A SAMPLE DATASET WAS PROVIDED BY THE PARENT PROCESS
        sample_error = f"UNITTEST ERROR: SAMPLE DATASET MISSING"
        self.assertIn('_sample_dataset', self.input_params, msg=sample_error)

        dataset: DataFrame = self.input_params['_sample_dataset']
        dataset_columns = list(dataset.columns)
        required_column = ['low', 'high', 'close']

        # MAKE SURE THAT EACH REQUIRED COLUMN EXISTS
        for column_name in required_column:
            missing_error = f"REQUIRED COLUMN MISSING FROM DATASET"
            self.assertIn(column_name, dataset_columns, msg=missing_error)