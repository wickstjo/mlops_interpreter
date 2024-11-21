from common.testing import unittest_base
from pandas import DataFrame
from to_feature_matrix import to_feature_matrix
import random, time

class validation_tests(unittest_base):
    def test_00_validate_input(self):

        # MAKE SURE INPUT PARAMS MATCH REFERENCE SCHEMA
        self.validate_schema(self.input_params, {
            'feature_columns': list,
        }, root_path='to_feature_matrix.feature_params')

        # MAKE SURE FEATURE COLUMN CONTAINS AT LEAST ONE NAME
        feature_columns = self.input_params['feature_columns']
        length_error = f"PROP 'feature_columns' CANNOT BE EMPTY"
        self.assertGreaterEqual(len(feature_columns), 1, msg=length_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_02_sample_has_required_columns(self):

        # MAKE SURE A SAMPLE DATASET WAS PROVIDED BY THE PARENT PROCESS
        sample_error = f"UNITTEST ERROR: SAMPLE DATASET MISSING"
        self.assertIn('_sample_dataset', self.input_params, msg=sample_error)

        dataset: DataFrame = self.input_params['_sample_dataset']
        dataset_columns = list(dataset.columns)

        # MAKE SURE THAT EACH REQUIRED COLUMN EXISTS
        for column_name in self.input_params['feature_columns']:
            missing_error = f"REQUIRED COLUMN MISSING FROM DATASET"
            self.assertIn(column_name, dataset_columns, msg=missing_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_03_value_extraction_works(self):

        # CREATE A DATASET WITH STATIC OPEN & CLOSE COLUMNS
        dataset = DataFrame([{
            'symbol': 'SYNTH',
            'timestamp': int(time.time()) + x,
            'open': 6.674 + x,
            'close': 2.452 + x,
            'high': round(random.uniform(1, 3), 3),
            'low': round(random.uniform(1, 3), 3),
            'volume': random.randrange(50, 200),
        } for x in range(10)])

        # GENERATE THE FEATURE MATRIX
        # OF THE OPEN & CLOSE COLUMNS
        real_output = to_feature_matrix({
            'feature_columns': ['open', 'close']
        }).transform(dataset)

        # WHAT WE EXPECT TO RECEIVE
        expected_output = [
            [6.674, 2.452], [7.674, 3.452], [8.674, 4.452], [9.674, 5.452], 
            [10.674, 6.452], [11.674, 7.452], [12.674, 8.452], [13.674, 9.452], 
            [14.674, 10.452], [15.674, 11.452]
        ]

        # MAKE SURE THEY MATCH
        output_error = f"OUTPUT MATRIX DOES NOT MATCH EXPECTED VALUE"
        self.assertEqual(real_output, expected_output, msg=output_error)

    ##############################################################################################################
    ##############################################################################################################