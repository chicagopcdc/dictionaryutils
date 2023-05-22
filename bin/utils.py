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

def add_enum_description(dest_enum_obj, enum_description_source, enumKey):
    if "descriptions" in enum_description_source:
        descriptions = list(enum_description_source["descriptions"].keys())
        if len(descriptions) > 0:
            description_sources = enum_description_source["descriptions"][descriptions[0]]
            if "Aggregated" in description_sources:
                description_sources.remove("Aggregated")
            description = descriptions[0] + " (" +  ', '.join(description_sources) + ")"
            if "enumDef" in dest_enum_obj:
                enumeration_obj = next((x for x in dest_enum_obj["enumDef"] if x["enumeration"] == enumKey), None)
                if enumeration_obj and "description" not in enumeration_obj:
                    enumeration_obj["description"] = description
                else:
                    dest_enum_obj["enumDef"].append({ "enumeration": enumKey, "description": description })
            else:
                dest_enum_obj["enumDef"] = []
                dest_enum_obj["enumDef"].append({ "enumeration": enumKey, "description": description })
