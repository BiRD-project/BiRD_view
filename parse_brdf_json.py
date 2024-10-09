import json
import jsonschema
from jsonschema import validate, FormatChecker
import numpy as np
import copy
# import colour as clr
json_schema = open('BRDF_JSON_schema/brdf_json_schema_v1.0.json')
dict_from_json_schema = json.loads(json_schema.read())

def validate_brdf_json(dict_from_brdf_json, dict_from_brdf_json_schema):
    try:
        validate(instance=dict_from_brdf_json, schema=dict_from_brdf_json_schema, format_checker=FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
        return err
    # variables_array = dict_from_brdf_json["data"]["variables"]
    # values_array = dict_from_brdf_json["data"]["values"]
    # line_n = 1
    # for line in values_array:
    #     if len(line) != len(variables_array):
    #         err = "Data line length does not match number of variables. Line number: " + str(line_n) + "."
    #         return err
    #     line_n += 1
    return "File valid!"

def simple_validate_brdf_json(dict_from_brdf_json, dict_from_brdf_json_schema):
    try:
        validate(instance=dict_from_brdf_json, schema=dict_from_brdf_json_schema, format_checker=FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
        return False
    # variables_array = dict_from_brdf_json["data"]["variables"]
    # values_array = dict_from_brdf_json["data"]["values"]
    # line_n = 1
    # for line in values_array:
    #     if len(line) != len(variables_array):
    #         # err = "Data line length does not match number of variables. Line number: " + str(line_n) + "."
    #         return False
    #     line_n += 1
    return True

def parse_brdf_json_legacy(dict_from_brdf_json):
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


def parse_brdf_json_legacy_2(dict_from_brdf_json):
    validity = simple_validate_brdf_json(dict_from_brdf_json, dict_from_json_schema)
    # parsed_brdf_dict = copy.deepcopy(dict_from_brdf_json)
    parsed_brdf_dict = {}
    parsed_brdf_dict["metadata"] = dict_from_brdf_json["metadata"]
    parsed_brdf_dict["validity"] = validity
    parsed_brdf_dict["data"] = {}
    parsed_brdf_dict["data"]["values"] = {}
    parsed_brdf_dict["data"]["variables"] = []
    for i in enumerate(dict_from_brdf_json["data"].keys()):
        if i[1] != 'adhoc_variables':
            parsed_brdf_dict["data"]["variables"].append(dict_from_brdf_json["data"][i[1]])
            parsed_brdf_dict["data"]["variables"][i[0]]["name"] = i[1]
            if i[1] != 'BRDF' and i[1] != "uBRDF":
                if i[1] == 'polarization_i' or i[1] == "polarization_r":
                    if "notation" in parsed_brdf_dict["data"]["variables"][i[0]]:
                        if parsed_brdf_dict["data"]["variables"][i[0]]["notation"] == "sp":
                            parsed_brdf_dict["data"]["variables"][i[0]]["uvals"] = np.unique(dict_from_brdf_json["data"][i[1]]["values"])
                            parsed_brdf_dict["data"]["variables"][i[0]]["sval"] = parsed_brdf_dict["data"]["variables"][i[0]]["uvals"][0]
                        elif parsed_brdf_dict["data"]["variables"][i[0]]["notation"] == "inStokes":
                            parsed_brdf_dict["data"]["variables"][i[0]]["uvals"] = np.unique(dict_from_brdf_json["data"][i[1]]["values"], axis=0)
                            dummy = []
                            for k in range(len(parsed_brdf_dict["data"]["variables"][i[0]]["uvals"])):
                                dummy.append(str(parsed_brdf_dict["data"]["variables"][i[0]]["uvals"][k]))
                            parsed_brdf_dict["data"]["variables"][i[0]]["uvals"] = dummy
                            parsed_brdf_dict["data"]["variables"][i[0]]["sval"] = parsed_brdf_dict["data"]["variables"][i[0]]["uvals"][0]
                else:
                    parsed_brdf_dict["data"]["variables"][i[0]]["uvals"] = np.unique(dict_from_brdf_json["data"][i[1]]["values"])
                    parsed_brdf_dict["data"]["variables"][i[0]]["sval"] = parsed_brdf_dict["data"]["variables"][i[0]]["uvals"][0]
                # print(parsed_brdf_dict["data"]["variables"])
            if i[1] != 'polarization_i' and i[1] != "polarization_r":
                parsed_brdf_dict["data"]["values"][i[1]] = np.array(parsed_brdf_dict["data"]["variables"][i[0]]["values"]).astype(np.float64)
                del parsed_brdf_dict["data"]["variables"][i[0]]["values"]
                print(parsed_brdf_dict["data"]["values"][i[1]])
            else:
                if "notation" in parsed_brdf_dict["data"]["variables"][i[0]]:
                    if parsed_brdf_dict["data"]["variables"][i[0]]["notation"] == "sp":
                        parsed_brdf_dict["data"]["values"][i[1]] = np.array(parsed_brdf_dict["data"]["variables"][i[0]]["values"]).astype(str)
                        del parsed_brdf_dict["data"]["variables"][i[0]]["values"]
                        print(parsed_brdf_dict["data"]["values"][i[1]])
                    elif parsed_brdf_dict["data"]["variables"][i[0]]["notation"] == "inStokes":
                        parsed_brdf_dict["data"]["values"][i[1]] = np.array(parsed_brdf_dict["data"]["variables"][i[0]]["values"]).astype(int)
                        del parsed_brdf_dict["data"]["variables"][i[0]]["values"]
                        dummy = []
                        for k in range(len(parsed_brdf_dict["data"]["values"][i[1]])):
                            dummy.append(str(parsed_brdf_dict["data"]["values"][i[1]][k]))
                        parsed_brdf_dict["data"]["values"][i[1]] = np.array(dummy)
                        print(parsed_brdf_dict["data"]["values"][i[1]])
    return parsed_brdf_dict

def parse_brdf_json(dict_from_brdf_json):
    validity = simple_validate_brdf_json(dict_from_brdf_json, dict_from_json_schema)
    if "values" in dict_from_brdf_json["data"] and "variables" in dict_from_brdf_json["data"]:
        parsed_brdf_dict = copy.deepcopy(dict_from_brdf_json)
        parsed_brdf_dict["validity"] = validity
        values_array = np.array(dict_from_brdf_json["data"]["values"])
        values_array = np.transpose(values_array)
        for i in range(len(values_array)):
            variable_name = parsed_brdf_dict["data"]["variables"][i]["name"]
            variable_type = parsed_brdf_dict["data"]["variables"][i]["type"]
            parsed_brdf_dict["data"][variable_name] = parsed_brdf_dict["data"]["variables"][i]
            if variable_type == "number":
                parsed_brdf_dict["data"][variable_name]["values"] = values_array[i, :].astype(np.float64)
            elif variable_type == "string":
                parsed_brdf_dict["data"][variable_name]["values"] = values_array[i, :].astype(str)
            if variable_name != 'BRDF' and variable_name != "uBRDF":
                parsed_brdf_dict["data"][variable_name]["uvals"] = np.unique(parsed_brdf_dict["data"][variable_name]["values"])
                parsed_brdf_dict["data"][variable_name]["sval"] = parsed_brdf_dict["data"]["variables"][i]["uvals"][0]
        del parsed_brdf_dict["data"]["variables"]
        del parsed_brdf_dict["data"]["values"]
    else:
        parsed_brdf_dict = copy.deepcopy(dict_from_brdf_json)
        parsed_brdf_dict["validity"] = validity
        for variable in dict_from_brdf_json["data"]:
            if variable != "adhoc_variables":
                if variable != "BRDF" and variable != "uBRDF":
                    if variable != 'polarization_i' and variable != 'polarization_r':
                        parsed_brdf_dict["data"][variable]["uvals"] = np.unique(parsed_brdf_dict["data"][variable]["values"])
                        parsed_brdf_dict["data"][variable]["sval"] = parsed_brdf_dict["data"][variable]["uvals"][0]
                    else:
                        if parsed_brdf_dict["data"][variable]["notation"] == "sp":
                            parsed_brdf_dict["data"][variable]["uvals"] = np.unique(parsed_brdf_dict["data"][variable]["values"])
                            parsed_brdf_dict["data"][variable]["sval"] = parsed_brdf_dict["data"][variable]["uvals"][0]
                        elif parsed_brdf_dict["data"][variable]["notation"] == "inStokes":
                            dummy = []
                            for k in range(len(parsed_brdf_dict["data"][variable]["values"])):
                                dummy.append(str(parsed_brdf_dict["data"][variable]["values"][k]))
                            parsed_brdf_dict["data"][variable]["values"] = dummy
                            parsed_brdf_dict["data"][variable]["uvals"] = np.unique(parsed_brdf_dict["data"][variable]["values"])
                            parsed_brdf_dict["data"][variable]["sval"] = str(parsed_brdf_dict["data"][variable]["uvals"][0])
            else:
                for adhoc_variable in parsed_brdf_dict["data"]["adhoc_variables"]:
                    parsed_brdf_dict["data"][adhoc_variable+'_adhoc'] = parsed_brdf_dict["data"]["adhoc_variables"][adhoc_variable]
                    parsed_brdf_dict["data"][adhoc_variable+'_adhoc']["uvals"] = np.unique(parsed_brdf_dict["data"][adhoc_variable+'_adhoc']["values"])
                    parsed_brdf_dict["data"][adhoc_variable+'_adhoc']["sval"] = parsed_brdf_dict["data"][adhoc_variable+'_adhoc']["uvals"][0]
                del parsed_brdf_dict["data"]["adhoc_variables"]
    return parsed_brdf_dict


# json_file = open('C:\\Users\\lanevsd1\\PycharmProjects\\BiRD_view_v5\\Test BRDF data files\\example.brdf')
# json_schema = open('brdf_json_schema_v1.0.json')
# dict_from_json = json.loads(json_file.read())
# test = parse_brdf_json(dict_from_json)
# dict_from_json_schema = json.loads(json_schema.read())
# valid = validate_brdf_json(dict_from_json, dict_from_json_schema)
# print(valid)
#
# parsed_brdf_json = parse_brdf_json(dict_from_json)
# print(dict_from_json["data"]["values"])
# print(parsed_brdf_json["data"]["values"])






