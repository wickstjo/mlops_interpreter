from common import cassandra_utils

def load_dataset(input_data: dict, unittesting=False):
    assert isinstance(input_data, dict), f"ARG 'input_data' MUST BE OF TYPE DICT"

    # EXTRACT INPUT VALUES
    db_table = input_data['db_table']
    stock_symbol = input_data['stock_symbol']
    start_date = input_data['timestamps']['start']
    end_date = input_data['timestamps']['end']

    # STITCH TOGETHER CQL QUERY STRING
    query_string: str = f"""
        SELECT * FROM {db_table}
        WHERE symbol = '{stock_symbol}'
        AND timestamp >= '{start_date}'
        AND timestamp <= '{end_date}' 
        ORDER BY timestamp ASC
    """

    # WHEN UNITTESTING, ENABLE LIMITED QUERIES
    if unittesting:
        assert isinstance(unittesting, int), 'UNITTEST LIMIT MUST BE AN INT'
        query_string += f" LIMIT {unittesting}"

    # FINALLY, ENABLE FILTERING
    query_string += " ALLOW FILTERING"

    # FETCH THE DATASET FROM CASSANDRA
    cassandra = cassandra_utils.create_instance()
    dataset: list[dict] = cassandra.read(query_string)

    return dataset

#######################################
### EXAMPLE USAGE

# load_dataset({
#     'db_table': 'shohel.refined_stock_data',
#     'stock_symbol': 'AAPL',
#     'timestamps': {
#         'start': '2019-01-01 00:00:00',
#         'end': '2019-01-10 00:00:00'
#     },
#     'min_length_threshold': 10
# })