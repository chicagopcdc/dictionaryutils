""" create _terms.yaml file from 'all_variables.json' file """
# pylint: disable=line-too-long
import json
import os
import sys
import typing
import yaml
from dotenv import load_dotenv

from utils import add_codes
from dictionaryutils import load_yaml


# Load env variables
load_dotenv('.env')

# path to the datadictionary/gdcdictionary/schemas/ folder
path: str = os.path.join(os.environ.get('SCHEMA_PATH', '../../gdcdictionary/schemas/'), "_terms.yaml")

if not os.path.isfile(path):
    print(f"_terms.yaml file not found im path {path}!")
    sys.exit()

# open _terms.yaml file
terms_file: dict[str, any] = load_yaml(path)

# Load the variables from the JSON version of our DD
all_vars_path: str = "./all_variables.json"
all_vars_fd: typing.TextIO
with open(all_vars_path, encoding="utf-8") as all_vars_fd:
    all_vars: dict[str, any] = json.load(all_vars_fd)
    num_vars: int = len(all_vars)
    print(f"Processing {num_vars} vars from 'all_variables.json' file")

    category: str
    table_value: dict[str, any]
    num_processed: int = 0
    for category, table_value in all_vars.items():
        num_processed += 1
        if num_processed % 100 == 0:
            print(f"processed {num_processed} of {num_vars} vars (current var: '{category}')")
        add_codes(table_value, terms_file, category)

        if "values" in table_value:
            value_key: str
            value_value: dict[str, any]
            for value_key, value_value in table_value["values"].items():
                add_codes(value_value, terms_file, category)

print(f"Processed {num_vars} vars, saving to file")

# Save file _terms.yaml
terms_file_fd: typing.TextIO
with open(path, 'w', encoding="utf-8") as terms_file_fd:
    yaml.dump(terms_file, terms_file_fd)
