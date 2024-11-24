from datetime import datetime
import yaml, json, random

def unix_ts(date_string: str) -> int:
    date_format = '%Y-%m-%d %H:%M:%S'
    datetime_obj = datetime.strptime(date_string, date_format)
    return int(datetime_obj.timestamp())

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
    
def pprint(data_dict: dict):
    print(json.dumps(data_dict, indent=4))

class create_repository:
    def __init__(self, options_mapping: dict, label: str):
        self.options = options_mapping
        self.keys = list(options_mapping.keys())
        self.label = label.upper()

    # FETCH OPTION
    def get(self, option_name: str):
        assert isinstance(option_name, str), f"ARG '{option_name}' MUST BE OF TYPE STR, GOT {type(option_name)}"
        assert option_name in self.keys, f"{self.label} '{option_name}' WAS NOT FOUND\nOPTIONS: {self.keys}"

        return self.options[option_name].module
    
    # FETCH & INSTANTIATE OPTION
    def create(self, option_name: str, option_params: dict = {}):
        assert isinstance(option_name, str), f"ARG '{option_name}' MUST BE OF TYPE STR, GOT {type(option_name)}"
        assert isinstance(option_params, dict), f"ARG '{option_params}' MUST BE OF TYPE DICT, GOT {type(option_params)}"

        # WITH PARAMS
        if len(option_params) > 0:
            return self.get(option_name)(option_params)

        # WITHOUT PARAMS
        return self.get(option_name)()
    
    # FETCH UNITTESTS FOR OPTION
    def get_tests(self, option_name: str):
        assert isinstance(option_name, str), f"ARG '{option_name}' MUST BE OF TYPE STR, GOT {type(option_name)}"
        assert option_name in self.keys, f"{self.label} '{option_name}' WAS NOT FOUND\nOPTIONS: {self.keys}"

        return self.options[option_name].tests
    
class option:
    def __init__(self, module, tests):
        self.module = module
        self.tests = tests