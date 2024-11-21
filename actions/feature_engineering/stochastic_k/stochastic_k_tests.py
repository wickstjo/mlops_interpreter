from stochastic_k import stochastic_k
from common.testing import unittest_base
import pandas as pd
import random, time

class validation_tests(unittest_base):
    def test_feature_stochastic_k_00_validate_input(self):

        # MAKE SURE INPUT PARAMS MATCH REFERENCE SCHEMA
        self.validate_schema(self.input_params, {
            'window_size': int
        }, root_path='feature_params')

        # MAKE SURE WINDOW SIZE IS LARGER THAN 1
        window_size = self.input_params['window_size']
        length_error = f"STOCHASTIC_K WINDOW SIZE MUST BE AT LEAST 1"
        self.assertGreaterEqual(window_size, 1, msg=length_error)

    ##############################################################################################################
    ##############################################################################################################

    def create_feature_vector(self, dataset_list: list[dict]):

        # CONVERT THE LIST[DICT] TO A PANDAS DATAFRAME
        dataset = pd.DataFrame(dataset_list).set_index('timestamp')
        dataset_length = len(dataset)

        # CREATE THE FEATURE VECTOR
        feature_vector = stochastic_k(dataset, self.input_params)
        vector_length = len(feature_vector)

        # MAKE SURE THAT LENGTHS ARE EQUAL -- NO NAN DROPS
        length_error = f"FEATURE VECTOR HAS INCORRECT LENGTH"
        self.assertEqual(dataset_length, vector_length, msg=length_error)

        # MAKE SURE THE OUTPUT TYPE IS CORRECT
        type_error = f"FEATURE VECTOR HAS INCORRECT TYPE"
        self.assertEqual(list, type(feature_vector), msg=type_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_feature_stochastic_k_01_with_mock_dataset(self):

        # MAKE DATASET SIZE LARGER THAN WINDOW SIZE
        dataset_size = self.input_params['window_size'] + random.randrange(10, 50)

        # CREATE A FAKE DATASET
        dataset = [{
            'symbol': 'SYNTH',
            'timestamp': int(time.time()) + x,
            'open': round(random.uniform(1, 10), 3),
            'close': round(random.uniform(1, 10), 3),
            'high': round(random.uniform(1, 10), 3),
            'low': round(random.uniform(1, 10), 3),
            'volume': random.randrange(50, 200),
        } for x in range(dataset_size)]

        # VERIFY THAT FEATURE VECTOR IS CORRECT
        self.create_feature_vector(dataset)

    ##############################################################################################################
    ##############################################################################################################

    def test_feature_stochastic_k_02_with_real_dataset(self):

        # MAKE SURE A SAMPLE DATASET WAS PROVIDED BY THE PARENT PROCESS
        sample_error = f"PARENT PROCESS DID NOT PROVIDE SAMPLE DATASET"
        self.assertTrue('_sample_dataset' in self.input_params, msg=sample_error)

        # YANK OUT REAL DATASET FROM INPUT PARAMS
        dataset = self.input_params['_sample_dataset']
        window_size = self.input_params['window_size']
        dataset_length = len(dataset)

        # MAKE SURE ITS LARGER THAN THE FEATURE WINDOW
        window_error = f"FEATURE WINDOW IS LARGER THAN TESTING DATASET"
        self.assertGreater(dataset_length, window_size, window_error)

        # VERIFY THAT IT HAS THE CORRECT ROW SCHEMA
        for row in dataset:
            self.validate_schema(row, {
                'symbol': str,
                'timestamp': str,
                'open': float,
                'close': float,
                'high': float,
                'low': float,
                'volume': int,
            })

        # VERIFY THAT FEATURE VECTOR IS CORRECT
        self.create_feature_vector(dataset)

    ##############################################################################################################
    ##############################################################################################################