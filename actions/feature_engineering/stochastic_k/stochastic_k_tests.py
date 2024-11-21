from stochastic_k import stochastic_k
from common.testing import unittest_base
from pandas import DataFrame
import random, time, numpy as np

class suite(unittest_base):
    def test_00_validate_input(self):

        # MAKE SURE INPUT PARAMS MATCH REFERENCE SCHEMA
        self.validate_schema(self.input_params, {
            'window_size': int,
            'output_column': str
        }, root_path='stochastic_k.feature_params')

        window_size = self.input_params['window_size']
        output_column = self.input_params['output_column']

        # MAKE SURE WINDOW SIZE IS LARGER THAN 1
        window_error = f"STOCHASTIC_K WINDOW SIZE TOO SMALL"
        self.assertGreaterEqual(window_size, 1, msg=window_error)

        # MAKE SURE OUTPUT COLUMN CONTAINS SOMETHING
        column_error = f"STOCHASTIC_K OUTPUT COLUMN NAME TOO SHORT"
        self.assertGreaterEqual(len(output_column), 3, msg=column_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_01_runs_with_mock_dataset(self):
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
        stochastic_k(self.input_params).transform(dataset)

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

    ##############################################################################################################
    ##############################################################################################################

    def test_02_sample_has_required_columns(self):

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

    ##############################################################################################################
    ##############################################################################################################