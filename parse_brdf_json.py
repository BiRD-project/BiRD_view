import json
import jsonschema
from jsonschema import validate, FormatChecker
import numpy as np
import copy
# import colour as clr
json_schema = open('BRDF JSON schema/brdf_json_schema_v1.0.json')
dict_from_json_schema = json.loads(json_schema.read())

def validate_brdf_json(dict_from_brdf_json, dict_from_brdf_json_schema):
    try:
        validate(instance=dict_from_brdf_json, schema=dict_from_brdf_json_schema, format_checker=FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
        return err
    variables_array = dict_from_brdf_json["data"]["variables"]
    values_array = dict_from_brdf_json["data"]["values"]
    line_n = 1
    for line in values_array:
        if len(line) != len(variables_array):
            err = "Data line length does not match number of variables. Line number: " + str(line_n) + "."
            return err
        line_n += 1
    return "File valid!"

def simple_validate_brdf_json(dict_from_brdf_json, dict_from_brdf_json_schema):
    try:
        validate(instance=dict_from_brdf_json, schema=dict_from_brdf_json_schema, format_checker=FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
        return False
    variables_array = dict_from_brdf_json["data"]["variables"]
    values_array = dict_from_brdf_json["data"]["values"]
    line_n = 1
    for line in values_array:
        if len(line) != len(variables_array):
            # err = "Data line length does not match number of variables. Line number: " + str(line_n) + "."
            return False
        line_n += 1
    return True

def parse_brdf_json(dict_from_brdf_json):
    validity = simple_validate_brdf_json(dict_from_brdf_json, dict_from_json_schema)
    parsed_brdf_dict = copy.deepcopy(dict_from_brdf_json)
    parsed_brdf_dict["validity"] = validity
    parsed_brdf_dict["data"]["values"] = {}
    values_array = np.array(dict_from_brdf_json["data"]["values"])
    values_array = np.transpose(values_array)
    for i in range(len(values_array)):
        variable_name = parsed_brdf_dict["data"]["variables"][i]["name"]
        variable_type = parsed_brdf_dict["data"]["variables"][i]["type"]
        if variable_type == "number":
            parsed_brdf_dict["data"]["values"][variable_name] = values_array[i, :].astype(np.float64)
        elif variable_type == "string":
            parsed_brdf_dict["data"]["values"][variable_name] = values_array[i, :].astype(str)
        if variable_name != 'BRDF' and variable_name != "uBRDF":
            parsed_brdf_dict["data"]["variables"][i]["uvals"] = np.unique(parsed_brdf_dict["data"]["values"][variable_name])
            parsed_brdf_dict["data"]["variables"][i]["sval"] = parsed_brdf_dict["data"]["variables"][i]["uvals"][0]
    return parsed_brdf_dict

# json_file = open('test_brdf_json2.json')
# json_schema = open('brdf_json_schema_v1.html.0.json')
# dict_from_json = json.loads(json_file.read())
# dict_from_json_schema = json.loads(json_schema.read())
# valid = validate_brdf_json(dict_from_json, dict_from_json_schema)
# print(valid)
#
# parsed_brdf_json = parse_brdf_json(dict_from_json)
# print(dict_from_json["data"]["values"])
# print(parsed_brdf_json["data"]["values"])






