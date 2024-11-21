from datetime import datetime
import yaml, json

def unix_ts(date_string: str) -> int:
    date_format = '%Y-%m-%d %H:%M:%S'
    datetime_obj = datetime.strptime(date_string, date_format)
    return int(datetime_obj.timestamp())

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
    
def pprint(data_dict: dict):
    print(json.dumps(data_dict, indent=4))