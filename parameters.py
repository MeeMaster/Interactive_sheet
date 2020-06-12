import codecs
from os import path
from item_classes import *


ALL_OBJECTS_DICT = {}


def load_parameters(alternative=False):
    parameters = {"param": [],
                  "armor": [],
                  "notes": [],
                  "attrib": [],
                  "damage": [],
                  "character": [],
                  "skill": {}
                  }
    filepath = path.join("parameters", "parameters.csv")
    if alternative:
        filepath = path.join("parameters", "parameters_alternative.csv")
    with codecs.open(filepath, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.strip():
                continue
            if line.startswith("#"):
                continue
            field_type = line.split("_")[0]
            if field_type == "skill":
                skill, attribs = line.strip().split(";")
                attribs = attribs.split(",")
                parameters[field_type][skill] = attribs
                continue
            line = line.strip().replace(";", "")
            parameters[field_type].append(line)
    return parameters


def get_all_data():
    global ALL_OBJECTS_DICT
    if not ALL_OBJECTS_DICT:
        read_all_objects()
    return ALL_OBJECTS_DICT


def translate(name, locale="PL", supp_dict=None):
    if not name.strip():
        return ""
    if supp_dict is None:
        locale_file = path.join("locales", "translations_{}.csv".format(locale))
        if not path.exists(locale_file):
            # print("Could not localize locale file '{}'".format(locale_file))
            locale_file = path.join("locales", "translations_{}.csv".format("EN"))
            if not path.exists(locale_file):
                return name
        with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
            for line in infile:
                if not line.startswith(name):
                    continue
                read_name, translation = line.strip().split(";")
                if read_name == name:
                    return translation
            print("No translation found for value '{}' and locale '{}'".format(name, locale))
            return name
    else:
        return supp_dict[name]


def read_objects(filepath):
    objects = {}
    with open(filepath, "r") as infile:
        current_object = None
        for line in infile:
            valid_line = line.split("#")[0].strip()
            if not valid_line.strip():
                continue
            if "////" in valid_line:
                current_object = None
                continue
            if current_object is None:
                if ":" not in valid_line:
                    continue
                current_object, parent = valid_line.split(":")
                objects[current_object] = {"parent": parent, "name": current_object}
                continue
            parameter, value = valid_line.split("=")
            parameter_type = parameter.split("_")[0]
            parameter = "_".join(parameter.split("_")[1:])
            parameter = parameter.strip()
            value = value.strip()

            if parameter_type == "i":
                try:
                    value = int(value)
                except:
                    value = 0
            elif parameter_type == "f":
                try:
                    value = float(value)
                except:
                    value = 0.0
            if parameter_type == "l":
                value = value.split(",")
                for index in reversed(range(len(value))):
                    value[index] = value[index].strip()
                    if not value[index]:
                        del value[index]
            objects[current_object][parameter] = value
    return objects


def is_leaf(object_name, other_dict=None):
    global ALL_OBJECTS_DICT
    if not ALL_OBJECTS_DICT:
        read_all_objects()
    children = get_all_children(object_name, ALL_OBJECTS_DICT if other_dict is None else other_dict)
    return not len(children) > 0


def get_objects_of_type(object_type, other_dict=None):
    global ALL_OBJECTS_DICT
    if not ALL_OBJECTS_DICT:
        read_all_objects()
    children = get_all_children(object_type, ALL_OBJECTS_DICT if other_dict is None else other_dict)
    output = {}
    for child in children:
        output[child] = ALL_OBJECTS_DICT[child]
    return output


def is_type(item, item_type):
    result = False

    def get_data(item):
        if not item:
            return
        if isinstance(item, BaseObject):
            parent_dict = {"type": item.type, "parent": item.parent}
        else:
            parent_dict = ALL_OBJECTS_DICT[item]
        parent_type = parent_dict["type"]
        if parent_type == item_type:
            return True
        return get_data(parent_dict["parent"])
    result = get_data(item)
    return result


def get_object_data(object_name, other_dict=None):
    if other_dict is None:
        global ALL_OBJECTS_DICT
        if not ALL_OBJECTS_DICT:
            read_all_objects()
        if object_name not in ALL_OBJECTS_DICT:
            return
        return ALL_OBJECTS_DICT[object_name]
    return other_dict[object_name]


def get_all_children(name, object_dict):
    all_children = []

    def get_this_children(name):
        for child_name, item_dict in object_dict.items():
            if item_dict["parent"] != name:
                continue
            all_children.append(child_name)
            get_this_children(child_name)
    get_this_children(name)
    return all_children


def get_children(object_type, other_dict=None):
    children = {}
    objects = get_objects_of_type(object_type, other_dict)
    for object_name, object_data in objects.items():
        if object_data["parent"] != object_type:
            continue
        children[object_name] = object_data
    return children


def get_full_data(object_dict, item):
    item_dict = {}

    def get_data(item):
        if not item:
            return
        parent_dict = object_dict[item]
        for key in parent_dict:
            if key in item_dict:
                continue
            item_dict[key] = parent_dict[key]
        get_data(parent_dict["parent"])
    get_data(item)
    return item_dict


def get_parent(object_data):
    global ALL_OBJECTS_DICT
    if not ALL_OBJECTS_DICT:
        read_all_objects()
    parent_object_name = object_data["parent"]
    if parent_object_name not in ALL_OBJECTS_DICT:
        return
    return ALL_OBJECTS_DICT[parent_object_name]


def create_item(data):
    item = BaseObject()
    if data is None:
        return item
    for key in data:
        if key == "requirements":
            item.set_requirements(data[key])
            continue
        if isinstance(data[key], list):
            for index, obj in enumerate(data[key]):
                if not isinstance(obj, str):
                    continue
                item_data = get_object_data(obj, ALL_OBJECTS_DICT)
                obj_item = create_item(item_data)
                data[key][index] = obj_item
        item.__dict__[key] = data[key]
    return item


def read_all_objects(full_data=True):
    global ALL_OBJECTS_DICT
    final_dict = {}
    base_dict = read_objects("parameters/base_objects.txt")
    for key, data in base_dict.items():
        if full_data:
            data = get_full_data(base_dict, key)
        data["source"] = "base_objects.txt"
        final_dict[key] = data
    for filename in ["abilities", "modifiers", "items"]:
        objects = read_objects("parameters/{}.txt".format(filename))
        current_dict = dict(final_dict)
        for key, item in objects.items():
            current_dict[key] = item
        for key, data in objects.items():
            if full_data:
                data = get_full_data(current_dict, key)
            data["source"] = "{}.txt".format(filename)
            final_dict[key] = data
    ALL_OBJECTS_DICT = final_dict


def reload_objects():
    read_all_objects()

read_all_objects()
