from components.features.base_feature import base_feature
from common.testing import base_unittest
from pandas import DataFrame

class feature(base_feature):
    def __repr__(self):
        return "to_float_matrix()"
    
    def transform(self, dataframe: DataFrame):
        return dataframe.values.tolist()
    
##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_demo(self):

        # CREATE A DATASET WITH STATIC OPEN & CLOSE COLUMNS
        dataset = DataFrame([{
            'open': 6.674 + x,
            'close': 2.452 + x,
        } for x in range(10)])

        # GENERATE THE FEATURE MATRIX
        # OF THE OPEN & CLOSE COLUMNS
        real_output = feature().transform(dataset)

        # WHAT WE EXPECT TO RECEIVE
        expected_output = [
            [6.674, 2.452], [7.674, 3.452], [8.674, 4.452], [9.674, 5.452], 
            [10.674, 6.452], [11.674, 7.452], [12.674, 8.452], [13.674, 9.452], 
            [14.674, 10.452], [15.674, 11.452]
        ]

        # MAKE SURE THEY MATCH
        output_error = f"OUTPUT MATRIX DOES NOT MATCH EXPECTED VALUE"
        self.assertEqual(real_output, expected_output, msg=output_error)