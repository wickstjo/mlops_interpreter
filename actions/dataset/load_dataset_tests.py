from common import misc, cassandra_utils
from common.testing import unittest_base
from actions.dataset.load_dataset import load_dataset
import random

class validation_tests(unittest_base):
    def test_dataset_00_schema(self):

        # WHAT SCHEMA WE EXPECT THE INPUT TO FOLLOW
        reference_schema = {
            'db_table': str,
            'stock_symbol': str,
            'timestamps': {
                'start': str,
                'end': str,
            },
            'min_length_threshold': int,
            'expected_schema': dict
        }
        
        # MAKE SURE INPUT DICT FITS REFERENCE SCHEMA
        self.validate_schema(self.input_params, reference_schema, root_path='dataset')

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_01_timestamp_format(self):
        length_error = lambda x: f"TIMESTAMP '{x}' DOES NOT FOLLOW THE FORMAT '%Y-%m-%d %H:%M:%S'"
        unix_error = lambda x: f"TIMESTAMP '{x}' COULD NOT BE CAST TO UNIX FORMAT"

        for key, value in self.input_params['timestamps'].items():

            # CHECK LENGTH FOR '%Y-%m-%d %H:%M:%S' FORMAT
            self.assertTrue(len(value) == 19, msg=length_error(key))

            # MAKE SURE WE CAN CONVERT IT TO AN UNIX TIMESTAMP
            try:
                misc.unix_ts(value)
            except Exception as e:
                self.fail(unix_error(key))

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_02_timestamp_order(self):

        # CONVERT DATESTRINGS TO UNIX TIMESTAMPS
        start_ts: int = misc.unix_ts(self.input_params['timestamps']['start'])
        end_ts: int = misc.unix_ts(self.input_params['timestamps']['end'])

        # MAKE SURE END IS LARGER THAN START
        self.assertTrue(start_ts < end_ts)

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_03_cassandra_connection(self):
        try:
            cassandra_utils.create_instance()
        except Exception as e:
            self.fail('COULD NOT CONNECT TO CASSANDRA CLUSTER')

    # ##############################################################################################################
    # ##############################################################################################################

    def test_dataset_04_min_length_exceeded(self):
        dataset = load_dataset(self.input_params)
        dataset_length = len(dataset)
        min_length_threshold = self.input_params['min_length_threshold']

        # MAKE SURE MINIMUM LENGTH WAS REACHED
        dataset_error = f"QUERY DID NOT YIELD A DATASET OF SUFFICIENT LENGTH (MIN EXPECTED {min_length_threshold}, GOT {dataset_length})"
        self.assertTrue(dataset_length >= min_length_threshold, msg=dataset_error)

    # ##############################################################################################################
    # ##############################################################################################################

    def test_dataset_05_ascending_order(self):
        min_length_threshold = self.input_params['min_length_threshold']
        row_limit = min(random.randrange(50, 150), min_length_threshold)
        subset = load_dataset(self.input_params, row_limit)

        # LOOP THROUGH SEQUENTIAL ENTRYPAIRS
        for nth in range(1, len(subset)):
            predecessor: dict = subset[nth-1]['timestamp']
            successor: dict = subset[nth]['timestamp']

            # MAKE SURE TIMESTAMPS ARE IN ASCENDING ORDER
            order_error = f"DATASET NOT IN ASCENDING ORDER ({predecessor} !< {successor})"
            self.assertTrue(predecessor < successor, msg=order_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_06_expected_row_schema(self):
        subset = load_dataset(self.input_params, 5)
        reference_schema = {}

        # YAML REFERS TO TYPES BY STRING NAME
        type_mapping = {
            'str': str,
            'int': int,
            'float': float,
        }

        # BUILD THE REFERENCE SCHEMA
        for key, key_type in self.input_params['expected_schema'].items():
            key_error = f"TYPE '{key_type}' MISSING FROM UNITTEST MAPPING"
            self.assertTrue(key_type in type_mapping, msg=key_error)

            reference_schema[key] = type_mapping[key_type]

        # MAKE SURE EACH ROW SCHEMA MATCHES
        for row in subset:
            self.validate_schema(row, reference_schema)

    ##############################################################################################################
    ##############################################################################################################