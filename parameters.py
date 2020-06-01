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


def translate(name, locale="PL"):
    if not name.strip():
        return ""
    locale_file = path.join("locales", "translations_{}.csv".format(locale))
    if not path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
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


def load_weapons():
    from item_classes import weapon_from_line
    weapons = {}
    with codecs.open(path.join("parameters", "weapons.csv"), "r",
                     encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.strip():
                continue
            if line.startswith("#") or line.startswith(";"):
                continue
            weapon = weapon_from_line(line)
            if weapon.arch_name in weapons:
                print("Weapon '{}' already defined, check the config files!".format(weapon.arch_name))
                continue
            weapons[weapon.arch_name] = weapon
    return weapons


def load_armors():
    from item_classes import armor_from_line
    armors = {}
    with codecs.open(path.join("parameters", "armors.csv"), "r",
                     encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.strip():
                continue
            if line.startswith("#") or line.startswith(";"):
                continue
            armor = armor_from_line(line)
            armors[armor.arch_name] = armor
    return armors


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
                objects[current_object] = {"parent": parent}
                continue
            parameter, value = valid_line.split("=")
            parameter = parameter.strip()
            values = value.strip().split(",")
            for index, value in enumerate([a for a in values]):
                if not value:
                    del values[index]
            objects[current_object]["name"] = current_object
            objects[current_object][parameter] = values
    return objects


def get_objects_of_type(object_type):
    global ALL_OBJECTS_DICT
    if not ALL_OBJECTS_DICT:
        read_all_objects()
    children = get_all_children(ALL_OBJECTS_DICT, object_type)
    output = {}
    for child in children:
        output[child] = ALL_OBJECTS_DICT[child]
    return output


def get_object_data(object_name):
    global ALL_OBJECTS_DICT
    if not ALL_OBJECTS_DICT:
        read_all_objects()
    if object_name not in ALL_OBJECTS_DICT:
        return
    return ALL_OBJECTS_DICT[object_name]


def get_all_children(object_dict, name):
    all_children = []

    def get_children(name):
        for child_name, item_dict in object_dict.items():
            if item_dict["parent"] != name:
                continue
            all_children.append(child_name)
            get_children(child_name)
    get_children(name)
    return all_children


def get_children(object_type):
    children = {}
    objects = get_objects_of_type(object_type)
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
    item = None
    if data["type"] == "weapon":
        item = Weapon()
    if data["type"] == "armor":
        item = Armor()
    if data["type"] == "ability":
        item = Ability()
    if data["type"] == "ranged_weapon":
        item = RangedWeapon()
    if data["type"] == "trait":
        item = Trait()
    if item is None:
        return

    for key in data:
        if key not in item.__dict__:
            continue
        if key == "requirements":
            item.set_requirements(data[key])
            continue
        item.__dict__[key] = data[key]
    return item


def read_all_objects():
    global ALL_OBJECTS_DICT
    final_dict = {}
    base_dict = read_objects("parameters/base_objects.txt")
    for key, item in base_dict.items():
        full_data = get_full_data(base_dict, key)
        final_dict[key] = full_data
    for filename in ["abilities", "modifiers", "weapons", "armors"]:
        objects = read_objects("parameters/{}.txt".format(filename))
        current_dict = dict(final_dict)
        for key, item in objects.items():
            current_dict[key] = item
        for key, item in objects.items():
            full_data = get_full_data(current_dict, key)
            final_dict[key] = full_data
    ALL_OBJECTS_DICT = final_dict


def reload_objects():
    read_all_objects()

read_all_objects()
