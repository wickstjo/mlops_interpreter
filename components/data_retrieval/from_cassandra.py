from pydantic import BaseModel
from common import cassandra_utils, misc
from common.testing import base_unittest
from assertpy import assert_that
import random

class timestamp_schema(BaseModel):
    start: str
    end: str

class input_schema(BaseModel):
    db_table: str
    stock_symbol: str
    timestamps: timestamp_schema

##############################################################################################################
##############################################################################################################

def load_dataset(raw_params: dict, unittest_limit: int = -1):

    # MAKE SURE INPUT PARAMS FOLLOW INTENDED SCHEMA
    assert_that(raw_params).is_type_of(dict)
    params = input_schema(**raw_params)

    # STITCH TOGETHER CQL QUERY STRING
    query_string: str = f"""
        SELECT * FROM {params.db_table}
        WHERE symbol = '{params.stock_symbol}'
        AND timestamp >= '{params.timestamps.start}'
        AND timestamp <= '{params.timestamps.end}'
        ORDER BY timestamp ASC
    """

    # WHEN UNITTESTING, ENABLE LIMITED QUERIES
    if unittest_limit > 0:
        query_string += f" LIMIT {unittest_limit}"

    # FINALLY, ENABLE FILTERING
    query_string += " ALLOW FILTERING"

    # FETCH THE DATASET FROM CASSANDRA
    cassandra = cassandra_utils.create_instance()
    dataset: list[dict] = cassandra.read(query_string)

    return dataset

##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_input_schema(self):

        # MAKE SURE INPUT IS A DICT
        dict_error = f"ARG 'input_params' IS OF THE WRONG TYPE"
        self.assertEqual(type(self.input_params), dict, msg=dict_error)

        # ENFORCE PARAM SCHEMA
        try:
            input_schema(**self.input_params)
        except Exception as error:
            self.fail(error)

    ##############################################################################################################
    ##############################################################################################################

    def test_01_timestamp_format(self):
        for key, value in self.input_params['timestamps'].items():

            # CHECK LENGTH FOR '%Y-%m-%d %H:%M:%S' FORMAT
            # length_error = f"TIMESTAMP '{key}' DOES NOT FOLLOW THE FORMAT '%Y-%m-%d %H:%M:%S'"
            length_error = f"TIMESTAMP '{key}' DOES NOT FOLLOW THE FORMAT 'YYYY-MM-DD HH:MM:SS'"
            self.assertEqual(len(value), 19, msg=length_error)

            # MAKE SURE WE CAN CONVERT IT TO AN UNIX TIMESTAMP
            try:
                misc.unix_ts(value)
            except Exception as e:
                self.fail(f"TIMESTAMP '{key}' COULD NOT BE CAST TO UNIX FORMAT")

    ##############################################################################################################
    ##############################################################################################################

    def test_02_timestamp_order(self):

        # CONVERT DATESTRINGS TO UNIX TIMESTAMPS
        params = input_schema(**self.input_params)
        start_ts: int = misc.unix_ts(params.timestamps.start)
        end_ts: int = misc.unix_ts(params.timestamps.end)

        # MAKE SURE END IS LARGER THAN START
        order_error = f"END-DATE IS SMALLER THAN START-DATE"
        self.assertGreater(end_ts, start_ts, msg=order_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_03_cassandra_connection(self):
        try:
            cassandra_utils.create_instance()
        except Exception as e:
            self.fail('COULD NOT CONNECT TO CASSANDRA CLUSTER')

    ##############################################################################################################
    ##############################################################################################################

    def test_04_ascending_order(self):
        row_limit = random.randrange(50, 150)
        subset = load_dataset(self.input_params, row_limit)

        # LOOP THROUGH SEQUENTIAL ENTRYPAIRS
        for nth in range(1, len(subset)):
            predecessor: dict = subset[nth-1]['timestamp']
            successor: dict = subset[nth]['timestamp']

            # MAKE SURE TIMESTAMPS ARE IN ASCENDING ORDER
            order_error = f"DATASET NOT IN ASCENDING ORDER"
            self.assertGreater(successor, predecessor, msg=order_error)