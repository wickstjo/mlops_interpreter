import math
from common.testing import base_unittest
from pydantic import BaseModel, Field

##############################################################################################################
##############################################################################################################

class input_schema(BaseModel):
    sequence_ratio: list[dict[str, float]] = Field(min_length=3, max_length=3)

##############################################################################################################
##############################################################################################################

def segment_dataset(input_params: dict, dataset: list[dict]):
    assert isinstance(input_params, dict), f"ARG 'input_params' MUST BE OF TYPE DICT, GOT ({type(input_params)})"
    assert isinstance(dataset, list), f"ARG 'dataset' MUST BE OF TYPE DICT, GOT ({type(dataset)})"

    # MAKE SURE INPUT PARAMS FOLLOW SCHEMA
    params = input_schema(**input_params)

    # AUDIT THE SEQUENCE -- DIE IF IT FAILS
    audit_sequence(params.sequence_ratio)

    container = {}
    old_limit = 0
    dataset_length = len(dataset)

    # LOOP THROUGH EACH SEQUENTIAL SEGMENT
    for block in params.sequence_ratio:
        for segment_name, segment_percentage in block.items():

            # HOW MANY ROWS DOES THE PERCENTAGE TRANSLATE TO?
            num_rows = math.ceil(dataset_length * segment_percentage)
            new_limit = min(old_limit + num_rows, dataset_length)

            # SELECT THE SUBSET & GENERATE LABELS FOR IT
            subset = dataset[old_limit:new_limit]
            container[segment_name] = subset

            # UPDATE LIMIT
            old_limit = new_limit

    return container

def audit_sequence(sequence: list[dict[str, float]]):
    required_segments = set(['train', 'test', 'validate'])
    found_segments = set()
    total_sum = 0

    for item in sequence:

        # MAKE SURE ITEM IS ONE DIMENSIONAL
        prop_type, prop_len = type(item), len(item)
        assert isinstance(item, dict), f'SEQUENCE ITEM MUST BE OF TYPE DICT, FOUND {prop_type}'
        assert prop_len == 1, f'SEQUENCE ITEM MUST BE OF LENGTH 1, FOUND {prop_len}'

        # EXTRACT THE NAME AND VALUE
        segment_name = list(item.keys())[0]
        segment_value = item[segment_name]

        # CATCH ANY UNLISTED SECTION NAMES
        unknown_name_error = f"BAD SEGMENT NAME '{segment_name}', EXPECTING ONE OF {required_segments}"
        assert segment_name in required_segments, unknown_name_error

        # UPDATE CONTAINERS
        found_segments.add(segment_name)
        total_sum += segment_value

    # MAKE SURE ALL REQUIRED SEGMENTS EXIST
    segment_intersection = required_segments - found_segments
    label_error = f"THE FOLLOWING SEGMENT NAME WAS MISSING {segment_intersection}"
    assert len(segment_intersection) == 0, label_error

    # MAKE SURE THE SUM OF ALL SEGMENTS ADDS UP TO 1
    sum_error = f"ALL SEGMENT VALUES MUST ADD UP TO 1, GOT {total_sum}"
    assert total_sum == 1, sum_error

##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_input_schema(self):
        input_schema(**self.input_params)

    def test_01_sequence_audit_passes(self):
        audit_sequence(self.input_params['sequence_ratio'])

    def mock_run(self, mock_input):

        # SEGMENT USING THE REAL FUNCTION
        segments = segment_dataset({ 'sequence_ratio': mock_input['sequence_ratio'] }, mock_input['dataset'])
        reconstructed_dataset = []

        for segment_name, segment_subset in segments.items():
            expected_length = mock_input['expected_output'][segment_name]
            subset_length = segment_subset

            # APPEND SUBSET TO SEPARATE ARRAY FOR LATER VERIFICATION
            reconstructed_dataset += segment_subset

            # MAKE SURE SUBSET LENGTHS MATCHES EXPECTATION
            length_error = f"SEGMENT '{segment_name}' IS INCORRECT (EXPECTED {expected_length}, GOT {subset_length})"
            self.assertEqual(subset_length, expected_length, msg=length_error)

        # MAKE SURE THERE ARE NO DUPLICATES OR LOST VALUES
        unequal_error = f"RECONSTRUCTED DATASET IS NOT EQUAL TO INPUT DATASET"
        self.assertEqual(reconstructed_dataset, mock_input['dataset'], msg=unequal_error)

    def test_02_train_test_validate(self):
        self.mock_run({
            'dataset': [x for x in range(100)],
            'sequence_ratio': [
                { 'train': 0.75 },
                { 'test': 0.15 },
                { 'validate': 0.1 },
            ],
            'expected_output': {
                'train': [x for x in range(75)],
                'test': [x for x in range(75, 90)],
                'validate': [x for x in range(90, 100)],
            }
        })

    def test_03_test_train_validate(self):
        self.mock_run({
            'dataset': [x for x in range(69)],
            'sequence_ratio': [
                { 'test': 0.19 },
                { 'train': 0.55 },
                { 'validate': 0.26 },
            ],
            'expected_output': {
                'test': [x for x in range(14)],
                'train': [x for x in range(14, 52)],
                'validate': [x for x in range(52, 69)],
            }
        })

    def test_04_test_validate_train(self):
        self.mock_run({
            'dataset': [x for x in range(420)],
            'sequence_ratio': [
                { 'test': 0.32 },
                { 'validate': 0.118 },
                { 'train': 0.562 },
            ],
            'expected_output': {
                'test': [x for x in range(135)],
                'validate': [x for x in range(135, 185)],
                'train': [x for x in range(185, 420)],
            }
        })

    def test_05_no_validation(self):
        self.mock_run({
            'dataset': [x for x in range(123)],
            'sequence_ratio': [
                { 'train': 0.5 },
                { 'test': 0.5 },
                { 'validate': 0 },
            ],
            'expected_output': {
                'train': [x for x in range(62)],
                'test': [x for x in range(62, 123)],
                'validate': [],
            }
        })
