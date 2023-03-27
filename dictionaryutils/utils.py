
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
            print("ERROR: Missing " + variable + " in data dictionary - - Returning not coded value: " + value)
            return_value.append((variable,value))
            continue
        if "enumDef" not in data_dictionary_node["properties"][variable]:
            print("ERROR: Missing enumDef in data dictionary for value: " + value + "in variable: " + variable + " - - Returning not coded value")
            return_value.append((variable,value))
            continue
        values = [ definition for definition in data_dictionary_node["properties"][variable]["enumDef"] if definition["enumeration"] == value and "termDef" in definition and "source" in definition["termDef"] and definition["termDef"]["source"] == ontology and  definition["termDef"]["cde_id"] ]

        if len(values) > 1 or len(values) == 0:
            print("ERROR: Expected only one value per ontology per value - - Returning not coded value")
            return_value.append((variable,value))
            continue

        return_value.append((variable,values[0]["termDef"]["cde_id"]))

    return return_value