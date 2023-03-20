import json
import os
import yaml

from dictionaryutils import load_yaml
from utils import add_codes



path = "../../gdcdictionary/schemas/_terms.yaml"
if not os.path.isfile(path):
    print("_terms.yaml file not found im path {}!".format(path))
    exit()

# open _terms.yaml file
_terms_file = load_yaml(path)


# Load the variables from the JSON version of our DD
json_dd = "./all_variables.json"
with open(json_dd) as dd_file:
    dd_file_json = json.load(dd_file)

    for category, table_value in dd_file_json.items():
        add_codes(table_value, _terms_file, category)

        if "values" in table_value:
            for value_key, value_value in table_value["values"].items():
                add_codes(value_value, _terms_file, category)
    


# Save file _terms.yaml
with open(path, 'w') as f:
    yaml.dump(_terms_file, f)


