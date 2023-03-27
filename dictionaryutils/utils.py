import requests

def get_info(ontology, code):
    ret = {}
    
    if ontology == 'ncit':
        ret["termDef"] = {}
        url = "https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code=" + code

        response = None
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
            print("ERROR: network error with {} url".format(url))
            return {}

        if not response or response.status_code != 200:
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


def add_codes(value, yaml_file_dict, category, dest_attribute_name=None, dest_attribute_obj=None, value_key= None):
    if "codes" in value:
        for code_pair in value["codes"]:
            if not code_pair or code_pair == "":
                continue
            split_codes = code_pair.split(':')
            if len(split_codes) != 2:
                print("ERROR: wrong code format {} for variable {}.".format(code_pair, category))
                continue
            ontology,code = split_codes
            composite_code = ontology + "_" + code
            if composite_code in yaml_file_dict:
                print("INFO: value {} already present in _terms file or already added.".format(composite_code))
            else:
                data = get_info(ontology,code)
                if "termDef" in data:
                    yaml_file_dict[composite_code] = data

            if composite_code in yaml_file_dict:
                if dest_attribute_name and dest_attribute_obj:
                    if dest_attribute_name not in dest_attribute_obj:
                        dest_attribute_obj[dest_attribute_name] = []
                    tmp_obj = {"$ref": "_terms.yaml#/" + composite_code}
                    if dest_attribute_name == "enumDef":
                        if not value_key:
                            print("ERROR: missing value_key for enum")
                        tmp_obj["enumeration"] = value_key
                    dest_attribute_obj[dest_attribute_name].append(tmp_obj)


def node_values_to_codes(data_dictionary_node, record_value, ontology):
    # ontology -> 'ncit'
    # record_value -> [('type', 'lab'), ('submitter_id', 'lab_COG_PAWTBX_6'), ... ]
    # data_dictionary_node -> "stem_cell_transplant.yaml":
    # {
    #     "$schema": "http://json-schema.org/draft-04/schema#",
    #     "id": "stem_cell_transplant",
    #     "title": "Stem Cell Transplant",
    #     "type": "object",
    #     "namespace": "http://cri.uchicago.edu/",
    #     "category": "clinical",
    #     "program": "*",
    #     "project": "*",
    #     "description": "Stem Cell Transplant",
    #     "additionalProperties": false,
    #     "submittable": true,
    #     "validators": null,
    #     "systemProperties":
    #     [
    #         "id",
    #         "project_id",
    #         "created_datetime",
    #         "updated_datetime",
    #         "state"
    #     ],
    #     "links":
    #     [
    #         {
    #             "name": "subjects",
    #             "bac ...

                
    if "properties" not in data_dictionary_node:
        print("ERROR: missing properties on node")
        return record_value

    return_value = []
    for variable,value in record_value:
        if variable not in data_dictionary_node["properties"].keys():
            print("ERROR: Missing variable in data dictionary - - Returning not coded value")
            return_value.append((variable,value))
            continue
        if "enumDef" not in data_dictionary_node["properties"][variable]:
            print("ERROR: Missing enumDef in data dictionary - - Returning not coded value")
            return_value.append((variable,value))
            continue
        values = [ definition for definition in data_dictionary_node["properties"][variable]["enumDef"] if definition["enumeration"] == value and "termDef" in definition and "source" in definition["termDef"] and definition["termDef"]["source"] == ontology and  definition["termDef"]["cde_id"] ]

        if len(values) > 1 or len(values) == 0:
            print("ERROR: Expected only one value per ontology per value - - Returning not coded value")
            return_value.append((variable,value))
            continue

        return_value.append((variable,values[0]["termDef"]["cde_id"]))

    return return_value







            