from components.features.base_feature import base_feature
from common.testing import base_unittest
from pandas import DataFrame
import random, time

class feature(base_feature):
    def __repr__(self): return "to_dataframe()"

    def transform(self, dataset: list[dict]):
        return DataFrame(dataset)
    
##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_demo(self):
        dataset_length = random.randrange(25, 50)

        # GENERATE A SYNTHETIC DATASET
        dataset = [{
            'symbol': 'SYNTH',
            'timestamp': int(time.time())  + x,
            'open': round(random.uniform(1, 3), 3),
            'close': round(random.uniform(1, 3), 3),
            'volume': random.randrange(50, 200),
        } for x in range(dataset_length)]

        transposed = {}

        # BUILD TRANSPOSED DATASET
        for item in dataset:
            for column_name, column_value in item.items():
                if column_name not in transposed:
                    transposed[column_name] = []
                transposed[column_name].append(column_value)

        # CONVERT DATASET TO DATAFRAME
        dataframe = feature().transform(dataset)

        # MAKE SURE THE DATAFRAME COLUMN VALUES MATCH THE TRANSPOSED DATASET VALUES
        for column_name in list(dataframe.columns):
            self.assertEqual(dataframe[column_name].tolist(), transposed[column_name])