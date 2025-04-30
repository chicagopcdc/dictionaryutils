""" utility library for yaml=>json dictionary creation scripts """
# pylint: disable=too-many-arguments,line-too-long,consider-using-f-string

import requests

# pylint: disable-next=no-member
requests.packages.urllib3.util.connection.HAS_IPV6 = False


def get_info(ontology, code):
    """ *** DEPRECATED, USE get_info_evs() *** retrieve ncit concept info for specified ontology and code """
    ret = {}

    if ontology == "ncit":
        ret["termDef"] = {}
        url = "https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&ns=ncit&code=" + code

        response = None
        try:
            response = requests.get(url, timeout=30)
        except requests.exceptions.RequestException as e:
            print(e)
            print("ERROR: network error with {} url".format(url))
            return {}

        if not response or response.status_code != 200:
            print("ERROR getting NCIt page for {} !!!!!".format(url))
            response.raise_for_status()
            return {}
        page = response.text

        ret["termDef"]["source"] = ontology
        ret["termDef"]["cde_id"] = code
        ret["termDef"]["term_url"] = url

        index = page.find("<b>Preferred Name:&nbsp;</b>")
        if index == -1:
            print(f"Name not found in page {url}")
        else:
            index += len("<b>Preferred Name:&nbsp;</b>")
            end_index = page.index("</p>", index)
            ret["termDef"]["term"] = page[index:end_index].strip()

        index = page.find("<b>Definition:&nbsp;</b>")
        if index == -1:  
            index = page.find("<b>NCI-GLOSS Definition:&nbsp;</b>")
            if index == -1:
                print(f"definition not found in page {url}")
            else:
                index += len("<b>NCI-GLOSS Definition:&nbsp;</b>")
                end_index = page.index("</p>", index)
                ret["description"] = page[index:end_index].strip()
        else:
            index += len("<b>Definition:&nbsp;</b>")
            end_index = page.index("</p>", index)
            ret["description"] = page[index:end_index].strip()

        index = page.find("<span class=\"vocabularynamelong_ncit\">")
        if index == -1:
            print(f"Version not found in page {url}")
        else:
            index += len("<span class=\"vocabularynamelong_ncit\">")
            end_index = page.index("</span>", index)
            ret["termDef"]["cde_version"] = page[index:end_index].strip()

    return ret


def get_concept_info(ontology: str, code: str):
    """ Get concept info for specified ontology and code, e.g. "ncit" and "C3224" """
    concept: dict[str, any] = {}
    term_def: dict[str, str] = {}

    if ontology is None or not ontology.strip():
        print(f"Warning: invalid ontology '{ontology}'")
        return concept

    if code is None or not code.strip():
        print(f"Warning: invalid code '{code}' for ontology '{ontology}'")
        return concept

    search_ontology: str = ontology.strip().lower()
    search_code: str = code.strip().upper()

    # pylint: disable-next=invalid-name
    EVS_ONTOLOGIES: list[str] = (
        "ncit", # NCI Thesaurus
        "ncim", # NCI Metathesaurus
        "chebi", # Chemical Entities of Biological Interest
        "go", # Gene Ontology
        "hgnc", # HUGO Gene Nomenclature Committee
        "icd10cm", # ICD-10-CM: The International Classification of Diseases, Tenth Revision, Clinical Modification
        "icd9cm", # ICD-9-CM: The International Classification of Diseases, Ninth Revision, Clinical Modification
        "mdr", # MedDRA: Medical Dictionary for Regulatory Activities (**NOTE: license restricted)
        "medrt", # Medication Reference Terminology)
        "umlssemnet", # UMLS Semantic Network
    )
    if search_ontology not in EVS_ONTOLOGIES:
        print(f"Invalid ontology '{ontology}' ('{ontology}:{code}'), must be supported by NCI EVS: {EVS_ONTOLOGIES}")
        return concept

    if search_ontology != "ncit":
        raise RuntimeError(f"Retrieval of concept for ontology/terminology '{ontology}' not implemented")

    url: str = f"https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/{search_code}"
    evs_concept: dict[str, any] = {}
    try:
        response: requests.Response
        with requests.get(url, stream=True, timeout=(5, 10)) as response:
            response.raise_for_status()
            evs_concept = response.json()
    except requests.exceptions.RequestException as ex:
        print(f"Error retrieving concept from URL '{url}':")
        print(ex)

    if not evs_concept:
        print(f"Warning: unable to retrieve concept info for code '{code}'")
        return concept
    term_def["source"] = search_ontology
    term_def["code"] = search_code
    term_def["term_url"] = url
    term_def["term"] = evs_concept.get("name")
    term_def["version"] = evs_concept.get("version")

    evs_concept_definitions: list[dict[str, any]] = [
        d for d in evs_concept.get("definitions", []) if d.get("type", "").upper() == "DEFINITION"
    ]
    if not evs_concept_definitions:
        evs_concept_definitions = [
            d for d in evs_concept.get("definitions", [])
                if d.get("type", "").upper() == "ALT_DEFINITION" and d.get("source", "").upper() == 'NCI-GLOSS'
        ]
    if len(evs_concept_definitions) > 1:
        raise RuntimeError(
            f"Unexpected number ({len(evs_concept_definitions)}) of definitions found for concept '{code}': " +
            str(evs_concept_definitions)
        )
    if evs_concept_definitions:
        evs_concept_definition: dict[str, any] = evs_concept_definitions[0]
        if not evs_concept_definition.get("definition"):
            raise RuntimeError(f"'definition' property not specified in primary definition node for concept {code}")
        concept["description"] = evs_concept_definition.get("definition")
    else:
        print(f"No NCI or NCI-GLOSS definitions found for concept '{ontology}:{code}'")

    concept["termDef"] = term_def
    return concept


def add_codes(
    value: dict[str, any],
    yaml_file_dict: dict[str, any],
    category: str,
    dest_attribute_name: str=None,
    dest_attribute_obj: dict[str, any]=None,
    value_key: str=None
):
    """ add/set concept code info for specified target object """
    if "codes" not in value:
        return
    code_pair: str
    for code_pair in value["codes"]:
        if not code_pair:
            continue
        if code_pair.count(":") != 1:
            print(f"ERROR: wrong code format '{code_pair}' for variable '{category}'")
            continue
        ontology: str
        code: str
        ontology, _, code = code_pair.partition(":")
        composite_code: str = f"{ontology.strip().lower()}_{code.strip().upper()}"
        if composite_code in yaml_file_dict:
            print(f"INFO: value '{composite_code}' already present in _terms file or already added.")
            # overwrite the destination object"s "description" attribute with
            # the ontology code"s "description" if available (not null/blank)
            yaml_file_dict_desc = str(yaml_file_dict[composite_code].get("description", "")).strip()
            if dest_attribute_name == "term" and yaml_file_dict_desc != "":
                dest_attribute_obj["description"] = yaml_file_dict_desc

            if dest_attribute_name and dest_attribute_obj:
                if dest_attribute_name not in dest_attribute_obj:
                    dest_attribute_obj[dest_attribute_name] = []
                tmp_obj: dict[str, str] = {"$ref": "_terms.yaml#/" + composite_code}
                if dest_attribute_name == "enumDef":
                    if not value_key:
                        raise RuntimeError("ERROR: missing value_key for enum")
                    tmp_obj["enumeration"] = value_key
                dest_attribute_obj[dest_attribute_name].append(tmp_obj)
        else:
            print(f"composite code not in yaml_file_dict: '{composite_code}'")
            concept_info: dict[str, any] = get_concept_info(ontology, code)
            if "termDef" in concept_info:
                yaml_file_dict[composite_code] = concept_info


def add_enum_description(dest_enum_obj: dict[str, any], enum_description_source: dict[str, any], enum_key: str):
    """ set 'enumDef' property on specified target object """
    if "descriptions" not in enum_description_source:
        return

    descriptions: list[str] = list(enum_description_source["descriptions"].keys())
    if not descriptions:
        return

    description_sources: list[str] = enum_description_source["descriptions"][descriptions[0]]
    if "Aggregated" in description_sources:
        description_sources.remove("Aggregated")

    # description = descriptions[0] + " (" +  ", ".join(description_sources) + ")"
    description: str = ", ".join(description_sources)

    if "enumDef" in dest_enum_obj:
        enum_key_obj: dict[str, str] = next((x for x in dest_enum_obj["enumDef"] if x["enumeration"] == enum_key), None)
        if enum_key_obj:
            # "description" attribute may not be defined for enumeration_obj created by add_codes (tmp_obj)
            enum_key_obj["description"] = enum_key_obj.get("description", "") + description
        else:
            dest_enum_obj["enumDef"].append({ "enumeration": enum_key, "description": description })
    else:
        dest_enum_obj["enumDef"] = [{ "enumeration": enum_key, "description": description }]
