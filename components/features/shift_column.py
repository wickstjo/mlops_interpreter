from pydantic import BaseModel, Field, field_validator
from components.features.base_feature import base_feature
from common.testing import base_unittest
from pandas import DataFrame
import random, time

# TODO: BLOCK SHIFT_BY FROM BEING 0
# TODO: MAKE SURE OUTPUT COL NAME IS >3 LEN

class input_schema(BaseModel):
    target_column: str
    shift_by: int
    output_column: str = Field(min_length=3, max_length=20)

    @field_validator("shift_by")
    def check_non_zero(cls, value):
        if value == 0:
            raise ValueError('Shift_column unit size be must a non-zero integer.')
        return value

##############################################################################################################
##############################################################################################################

class feature(base_feature):
    def __init__(self, input_params: dict):
        assert isinstance(input_params, dict), f"ARG 'input_params' MUST BE OF TYPE DICT, GOT {type(input_params)}"
        input_schema(**input_params)

        self.target_column = input_params['target_column']
        self.shift_by = input_params['shift_by']
        self.output_column = input_params['output_column']

    def __repr__(self):
        return f"shift_column(column={self.target_column}, shift_by={self.shift_by})"

    def transform(self, dataframe: DataFrame):

        # MAKE SURE OUTPUT COLUMN IS UNIQUE
        existing_columns = list(dataframe.columns)
        exists_error = f"OUTPUT COLUMN '{self.output_column}' ALREADY EXISTS IN DATASET"
        assert self.output_column not in existing_columns, exists_error

        dataframe[self.output_column] = dataframe[self.target_column].shift(periods=self.shift_by)
        return dataframe
    
##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_validate_input(self):
        feature(self.input_params)

    def test_01_target_column_exists(self):
        target_column = self.input_params['target_column']

        # MAKE SURE A SAMPLE DATASET WAS PROVIDED BY THE PARENT PROCESS
        sample_error = f"UNITTEST ERROR: SAMPLE DATASET MISSING"
        self.assertIn('_sample_dataset', self.input_params, msg=sample_error)

        dataset: DataFrame = self.input_params['_sample_dataset']
        dataset_columns = list(dataset.columns)

        missing_error = f"TARGET COLUMN '{target_column}' MISSING FROM SAMPLE DATASET"
        self.assertIn(target_column, dataset_columns, msg=missing_error)

    def test_02_forward_shifting_works(self):
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
        feature({
            'target_column': 'close',
            'shift_by': shift_by,
            'output_column': 'shifted_close',
        }).transform(dataset)

        # EXTRACT THE FEATURE VECTOR & AS WELL AS THE ORIGINAL COLUMN
        original_vector = dataset['close'].tolist()
        feature_vector = dataset['shifted_close'].tolist()

        # VERIFY THAT THE COLUMN WAS SHIFTED CORRECTLY
        self.assertEqual(original_vector[:-shift_by], feature_vector[shift_by:])

    def test_03_backwards_shifting_works(self):
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
        feature({
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