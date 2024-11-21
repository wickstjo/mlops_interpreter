from common.testing import unittest_base
from pandas import DataFrame
import random, time
from shift_column import shift_column

class validation_tests(unittest_base):
    def test_00_validate_input(self):

        # MAKE SURE INPUT PARAMS MATCH REFERENCE SCHEMA
        self.validate_schema(self.input_params, {
            'target_column': str,
            'shift_by': int,
            'output_column': str
        }, root_path='shift_column.feature_params')

        shift_by = self.input_params['shift_by']
        output_column = self.input_params['output_column']

        # PREVENT SHIFTING BY ZERO BECAUSE IT MAKES NO SENSE
        # ANY POSITIVE/NEGATIVE INT IS ALLOWED
        window_error = f"PROPERTY 'shift_by' MUST BE A NON-ZERO INTEGER"
        self.assertNotEqual(shift_by, 0, msg=window_error)

        # MAKE SURE OUTPUT COLUMN NAME IS LONG ENOUGH
        column_error = f"PROPERTY 'output_column' TOO SHORT"
        self.assertGreaterEqual(len(output_column), 3, msg=column_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_01_forward_shifting_works(self):
        dataset = DataFrame([{
            'symbol': 'SYNTH',
            'timestamp': int(time.time()) + x,
            'open': round(random.uniform(1, 3), 3),
            'close': round(random.uniform(1, 3), 3),
            'high': round(random.uniform(1, 3), 3),
            'low': round(random.uniform(1, 3), 3),
            'volume': random.randrange(50, 200),
        } for x in range(50)])

        # PICK A _POSITIVE_ NUMBER
        shift_by = random.randrange(5, 25)

        # APPLY THE FEATURE
        shift_column({
            'target_column': 'close',
            'shift_by': shift_by,
            'output_column': 'shifted_close',
        }).transform(dataset)

        # EXTRACT THE FEATURE VECTOR & AS WELL AS THE ORIGINAL COLUMN
        original_vector = dataset['close'].tolist()
        feature_vector = dataset['shifted_close'].tolist()

        # VERIFY THAT THE COLUMN WAS SHIFTED CORRECTLY
        self.assertEqual(original_vector[:-shift_by], feature_vector[shift_by:])

    ##############################################################################################################
    ##############################################################################################################

    def test_02_backwards_shifting_works(self):
        dataset = DataFrame([{
            'symbol': 'SYNTH',
            'timestamp': int(time.time()) + x,
            'open': round(random.uniform(1, 3), 3),
            'close': round(random.uniform(1, 3), 3),
            'high': round(random.uniform(1, 3), 3),
            'low': round(random.uniform(1, 3), 3),
            'volume': random.randrange(50, 200),
        } for x in range(10)])

        # PICK A _NEGATIVE_ NUMBER
        shift_by = random.randrange(5, 25) * -1

        # APPLY THE FEATURE
        shift_column({
            'target_column': 'close',
            'shift_by': shift_by,
            'output_column': 'shifted_close',
        }).transform(dataset)

        # EXTRACT THE FEATURE VECTOR & AS WELL AS THE ORIGINAL COLUMN
        original_vector = dataset['close'].tolist()
        feature_vector = dataset['shifted_close'].tolist()

        # VERIFY THAT THE COLUMN WAS SHIFTED CORRECTLY
        inverted_shift = shift_by * -1
        self.assertEqual(original_vector[inverted_shift:], feature_vector[:-inverted_shift])

    ##############################################################################################################
    ##############################################################################################################

    def test_03_sample_has_required_columns(self):

        # MAKE SURE A SAMPLE DATASET WAS PROVIDED BY THE PARENT PROCESS
        sample_error = f"UNITTEST ERROR: SAMPLE DATASET MISSING"
        self.assertIn('_sample_dataset', self.input_params, msg=sample_error)

        dataset: DataFrame = self.input_params['_sample_dataset']
        dataset_columns = list(dataset.columns)

        # MAKE SURE THE TARGET COLUMN EXISTS
        target_column = self.input_params['target_column']
        missing_error = f"TARGET COLUMN '{target_column}' MISSING FROM DATASET"
        self.assertIn(target_column, dataset_columns, msg=missing_error)

    ##############################################################################################################
    ##############################################################################################################