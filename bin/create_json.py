import json
import os
import requests
from dotenv import load_dotenv

from dictionaryutils import dump_schemas_from_dir
from utils import add_codes


try:
    os.mkdir("../artifacts")
except OSError:
    pass

# Load env variables
load_dotenv('.env')

# path to the datadictionary/gdcdictionary/schemas/ folder
shema_path: str = os.environ.get('SCHEMA_PATH', '../../gdcdictionary/schemas/')

table_name_mapping = {"lesion_characteristic": "lesion_characteristics", "adverse_event": "adverse_events", "lab": "laboratory_test", "person": "demographics", "disease_characteristic": "disease_characteristics", "tumor_assessment": "tumor_characteristics", "biopsy_surgical_procedure": "biopsy_surgical_procedures", "survival_characteristic": "survival_characteristics",
                      "myeloid_sarcoma_involvement": "disease_characteristics", "total_dose": "medication", "molecular_analysis": "genetic_analysis", "subject": "subject_characteristics",  "study": "subject_characteristics", "off_protocol_therapy_study": "off_protocol_therapy_or_study", "protocol_treatment_modification": "protocol_treatment_modifications", "subject": "subject_characteristics", "late_effect": "late_effects"}


# make sure timing.yaml occurs first in output schema json
yaml_schemas = dump_schemas_from_dir(shema_path)
yaml_schemas_with_timing = {k: v for k,
                            v in yaml_schemas.items() if k == 'timing.yaml'}
yaml_schemas_without_timing = {k: v for k,
                               v in yaml_schemas.items() if k != 'timing.yaml'}
yaml_schemas = {**yaml_schemas_with_timing, **yaml_schemas_without_timing}


# Add NCIt codes from all_variables.json artifact generated by the pcdcmodel repo Michael is working on
# TODO the artifact from that repo will eventually be used to generate all the yaml file programmatically.
# It is not ready to fully replace this manual curation but it can be leveraged to populate long and time consuming enums
json_dd = "./all_variables.json"
excluded_variables = ["id", "state", "updated_datetime", "created_datetime",
                      "project_id", "type", "submitter_id", "projects", "timings", "subjects", "persons"]
with open(json_dd) as dd_file:
    dd_file_json_grouped = json.load(dd_file)

    # START PATCH
    # The JSON DD groups the tables by higher level categories. I checked with Michael, this are just for easiness when talking with consortia.
    # We Should generate a file without the grouping to avoid parsing the key and making changes here
    dd_file_json = {}
    for category, table_value in dd_file_json_grouped.items():
        dd_file_json[(category[category.index(".") +
                      1:len(category)]).lower()] = table_value
    # END PATCH

    for table_name, table_content in yaml_schemas.items():
        if "properties" not in table_content:
            print(
                "WARNING: file/table {} is missing the properties value.".format(table_name))
            continue

        for variable_name, variable_values in table_content["properties"].items():
            if variable_name in excluded_variables:
                continue

            composite_name = table_name.split(".")[0] + "." + variable_name
            if composite_name not in dd_file_json.keys():
                print("WARNING: variable {} is missing the properties value.".format(
                    composite_name))
                if table_name.split(".")[0] in table_name_mapping:
                    composite_name = table_name_mapping[table_name.split(
                        ".")[0]] + "." + variable_name
                    print("trying mapping for " + composite_name)
                    if composite_name not in dd_file_json.keys():
                        print("WARNING: variable {} is missing the properties value.".format(
                            composite_name))
                        continue
                else:
                    print("WARNING: Missing mapping for " + composite_name)
                    continue

            if "codes" in dd_file_json[composite_name]:
                add_codes(dd_file_json[composite_name], yaml_schemas["_terms.yaml"],
                        variable_name, "term", variable_values)

            # TODO need to finish doing the bulk load of the terms before re-enabling this, otherwise the generation of the schema.json will take a very long time
            if "values" in dd_file_json[composite_name]:
                enum_descriptions = []
                for value_key, value_value in dd_file_json[composite_name]["values"].items():
                    if "codes" in value_value:
                        add_codes(value_value, yaml_schemas["_terms.yaml"],
                                variable_name, "enumDef", variable_values, value_key)
                    else:
                        if "descriptions" in value_value:
                            description = list(value_value["descriptions"].keys())[0]
                            enum_descriptions.append({ "description": description, "enumeration": value_key })
                if len(enum_descriptions) > 0:
                    if "enumDef" in variable_values:
                        variable_values["enumDef"].append(enum_descriptions)
                    else:
                        variable_values["enumDef"] = enum_descriptions
            


# Save files
with open(os.path.join("../artifacts", "schema.json"), "w", encoding='utf-8') as f:
    json.dump(yaml_schemas, f)
