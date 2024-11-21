from common.testing import unittest_base
from actions.segmentation.segmentation import segment_dataset

class validation_tests(unittest_base):
    def test_segmentation_00_single_property(self):
        for item in self.input_params:

            # MAKE SURE THE ITEM IS A DICT
            type_error = f"SEGMENT ITEM HAS THE WRONG TYPE"
            self.assertEqual(type(item), dict, msg=type_error)
            
            num_properties = len(item)
            count_error = f"SEGMENT SHOULD ONLY HAVE 1 PROPERTY"
            self.assertEqual(num_properties, 1, msg=count_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_segmentation_01_segment_labels(self):
        required_segments = ['train', 'test', 'validate']
        found_properties = []

        for item in self.input_params:
            segment_name = list(item.keys())[0]

            # MAKE SURE SEGMENT LABEL HAS NOT BEEN SEEN BEFORE
            duplicate_error = f"SEGMENT LABEL '{segment_name}' WAS FOUND TWICE"
            self.assertTrue(segment_name not in found_properties, msg=duplicate_error)

            found_properties.append(segment_name)
        
        # FIND THE INTERSECTION
        missing_properties = set(required_segments) - set(found_properties)

        # MAKE SURE NO PROPERTIES ARE MISSING
        label_error = f"MISSING ONE OR MORE SEGMENT TYPES: {missing_properties}"
        self.assertEqual(len(missing_properties), 0, msg=label_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_segmentation_02_segment_sum(self):
        list_values = [list(item.values())[0] for item in self.input_params]
        total_sum = sum(list_values)

        # MAKE SURE THE SUM OF ALL THE SEGMENTS ADD UP TO 1
        sum_error = f"SUM OF SEGMENTS MUST EQUAL 1"
        self.assertEqual(total_sum, 1, msg=sum_error)

    ##############################################################################################################
    ##############################################################################################################

    def validate_simulation(self, mock_input):

        # SEGMENT USING THE REAL FUNCTION
        segments = segment_dataset(mock_input['segmentation'], mock_input['dataset'])
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

    ##############################################################################################################
    ##############################################################################################################

    def test_segmentation_03_train_test_validate(self):
        self.validate_simulation({
            'dataset': [x for x in range(100)],
            'segmentation': [
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

    ##############################################################################################################
    ##############################################################################################################

    def test_segmentation_04_test_train_validate(self):
        self.validate_simulation({
            'dataset': [x for x in range(69)],
            'segmentation': [
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

    ##############################################################################################################
    ##############################################################################################################

    def test_segmentation_05_test_validate_train(self):
        self.validate_simulation({
            'dataset': [x for x in range(420)],
            'segmentation': [
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

    ##############################################################################################################
    ##############################################################################################################

    def test_segmentation_06_no_validation(self):
        self.validate_simulation({
            'dataset': [x for x in range(123)],
            'segmentation': [
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

    ##############################################################################################################
    ##############################################################################################################