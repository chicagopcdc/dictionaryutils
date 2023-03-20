import json
import os
import requests
import yaml

from dictionaryutils import load_yaml

def get_info(ontology, code):
    ret = {}
    ret["termDef"] = {}

    if ontology == 'ncit':
        url = "https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code=" + code

        response = requests.get(url)
        if response.status_code != 200:
            print("ERROR getting NCIt page for {} !!!!!".format(url))
            return {}
        page = response.text

        ret["termDef"]["source"] = ontology
        ret["termDef"]["cde_id"] = code
        ret["termDef"]["term_url"] = url

        index = page.find("<b>Preferred Name:&nbsp;</b>")
        if index == -1:
            print("Name not found in page {}".format(url))
        else:
            index += len("<b>Preferred Name:&nbsp;</b>")
            end_index = page.index("</p>", index)
            ret["termDef"]["term"] = page[index:end_index].strip()

        index = page.find("<b>Definition:&nbsp;</b>")
        if index == -1:
            print("definition not found in page {}".format(url))
        else:
            index += len("<b>Definition:&nbsp;</b>")
            end_index = page.index("</p>", index)
            ret["description"] = page[index:end_index].strip()

        index = page.find("<span class=\"vocabularynamelong_ncit\">")
        if index == -1:
            print("Version not found in page {}".format(url))
        else:
            index += len("<span class=\"vocabularynamelong_ncit\">")
            end_index = page.index("</span>", index)
            ret["termDef"]["cde_version"] = page[index:end_index].strip()

    return ret

path = "../../gdcdictionary/schemas/_terms.yaml"
if not os.path.isfile(path):
    print("_terms.yaml file not found im path {}!".format(path))
    exit()

# open _terms.yaml file
_terms_file = load_yaml(path)


# Load the variables from the JSON version of our DD
json_dd = "./all_variables.json"
excluded_variables = ["id", "state", "updated_datetime", "created_datetime", "project_id", "type", "submitter_id", "projects", "timings", "subjects", "persons"]
with open(json_dd) as dd_file:
    dd_file_json = json.load(dd_file)

    for category, table_value in dd_file_json.items():
        if "codes" in table_value:
            for code_pair in table_value["codes"]:
                if not code_pair or code_pair == "":
                    continue
                ontology,code = code_pair.split(':')
                composite_code = ontology + "_" + code
                if composite_code in _terms_file:
                    print("INFO: value {} already present in _terms file or already added.".format(composite_code))
                else:
                    _terms_file[composite_code] = get_info(ontology,code)
                    

        if "values" in table_value:
            for value_key, value_value in table_value["values"].items():
                if "codes" in value_value:
                    for code_value in value_value["codes"]:
                        if not code_value or code_value == "":
                            continue
                        ontology,code = code_value.split(':')
                        composite_code = ontology + "_" + code
                        if composite_code in _terms_file:
                            print("INFO: value {} already present in _terms file or already added.".format(composite_code))
                        else:
                            _terms_file[composite_code] = get_info(ontology,code)
    


# Save file _terms.yaml
with open(path, 'w') as f:
    yaml.dump(_terms_file, f)


