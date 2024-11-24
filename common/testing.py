import unittest, inspect, os, json
from abc import ABC
from pandas import DataFrame
# import coverage

# THE ENVIRONMENT VAR THAT UNITTESTS REQUIRE TO OBTAIN DYNAMIC ARGUMENTS
env_var_name: str = '_UNITTEST_ARGS'

################################################################################################
################################################################################################

# SHARED CONSTRUCTOR FOR ALL UNITTESTS
class base_unittest(unittest.TestCase, ABC):
    def setUp(self):
        stringified_dict: str = os.environ.get(env_var_name)
        self.input_params: dict = json.loads(stringified_dict)

        # HANDLE SAMPLE DATASET FORMATTING
        if '_sample_dataset' in self.input_params:
            self.input_params['_sample_dataset'] = DataFrame(self.input_params['_sample_dataset'])

    # COMPARE TWO DICTS FOR SCHEMATIC DIFFERENCES
    def validate_schema(self, user_dict: dict, ref_dict: dict, root_path=''):
        for key in ref_dict.keys():

            # CONSTRUCT KEY PATH FOR DEBUGGING CLARITY
            path: str = f'{root_path}.{key}'
            if len(root_path) == 0: path = key

            # MAKE SURE THE KEY EXISTS
            key_error: str = f"KEY '{path}' NOT FOUND"
            self.assertTrue(key in user_dict, msg=key_error)

            # KEEP UNRAVELING DICTS
            if isinstance(ref_dict[key], dict):
                self.validate_schema(user_dict[key], ref_dict[key], path)

            # OTHERWISE, VERIFY THAT VALUE TYPE IS CORRECT
            else:
                value_type = type(user_dict[key])
                expected_type = ref_dict[key]

                value_error: str = f"KEY VALUE '{path}' IS OF WRONG TYPE"
                self.assertEqual(value_type, expected_type, msg=value_error)

################################################################################################
################################################################################################

class StopOnFirstErrorResult(unittest.TextTestResult):
    def addError(self, test, err):
        super().addError(test, err)
        self.stop()  # Stop further tests on error

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stop()  # Stop further tests on failure

def run_tests(module, input_params: dict):

    # HANDLE SAMPLE DATASET FORMATTING
    if '_sample_dataset' in input_params:
        input_params['_sample_dataset'] = input_params['_sample_dataset'].to_dict(orient='records')

    # MAKE INPUT ARGS AVAILABLE FOR THE UNITTESTS THROUGH ENVIRONMENT
    os.environ[env_var_name] = json.dumps(input_params)

    # CREATE THE TESTING SUITE
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(module))
    
    # RAISE ERROR IF NO UNITTESTS WERE FOUND
    if len(suite._tests) == 0:
        raise Exception(f"MODULE '{module}' HAS NO UNITTESTS")
    
    # OTHERWISE, RUN THE TESTS
    runner = unittest.TextTestRunner(verbosity=2, resultclass=StopOnFirstErrorResult)
    output = runner.run(suite)

    # KILL PARENT PROCESS IF YOU FIND ANY ERRORS/FAILS
    if len(output.errors) > 0 or len(output.failures) > 0:
        raise Exception(output)

    return output

################################################################################################
################################################################################################

# COMPARE TWO DICTS FOR SCHEMATIC DIFFERENCES
def validate_schema(user_dict: dict, ref_dict: dict, root_path=''):
    for key in ref_dict.keys():

        # CONSTRUCT KEY PATH FOR DEBUGGING CLARITY
        path: str = f'{root_path}.{key}'
        if len(root_path) == 0: path = key

        # MAKE SURE THE KEY EXISTS
        key_error: str = f"KEY '{path}' NOT FOUND"
        assert key in user_dict, key_error

        # KEEP UNRAVELING DICTS
        if isinstance(ref_dict[key], dict):
            validate_schema(user_dict[key], ref_dict[key], path)

        # OTHERWISE, VERIFY THAT VALUE TYPE IS CORRECT
        else:
            value_type = type(user_dict[key])
            expected_type = ref_dict[key]

            value_error: str = f"KEY '{path}' IS OF WRONG TYPE"
            assert value_type == expected_type, value_error

################################################################################################
################################################################################################

def build_and_validate_schema(sample_row, expected_schema):
    reference_schema = {}

    # YAML REFERS TO TYPES BY STRING NAME
    type_mapping = {
        'str': str,
        'int': int,
        'float': float,
    }

    # BUILD THE REFERENCE SCHEMA
    for key, key_type in expected_schema.items():
        key_error = f"TYPE '{key_type}' FOR COLUMN '{key}' MISSING FROM UNITTEST TYPE MAPPING"
        assert key_type in type_mapping, key_error
        reference_schema[key] = type_mapping[key_type]

    # MAKE SURE EACH ROW SCHEMA MATCHES
    validate_schema(sample_row, reference_schema)