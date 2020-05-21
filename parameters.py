import codecs
from os import path


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


def load_modifiers(alternative=False):
    from item_classes import modifier_from_line
    modifiers = {}
    filepath = path.join("parameters", "modifiers.csv")
    if alternative:
        filepath = path.join("parameters", "modifiers_alternative.csv")

    with codecs.open(filepath, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.strip():
                continue
            if line.strip().startswith("#"):
                continue
            modifier = modifier_from_line(line)
            modifiers[modifier.arch_name] = modifier
    return modifiers


def load_abilities():
    abilities = {}
    with codecs.open(path.join("parameters", "abilities.csv"), "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.strip():
                continue
            name, requirements, tier = line.strip().split(";")
            if name in abilities:
                print("Ability '{}' already defined, check the config files!".format(name))
                continue
            abilities[name] = {
                "name": name,
                "requirements": {},
                "tier": tier
                }
            if not requirements:
                continue
            for requirement in requirements.split(","):
                requirement = requirement.strip()
                if len(requirement.split()) == 1:
                    abilities[name]["requirements"][requirement] = True
                else:
                    requirement, value = requirement.split()
                    abilities[name]["requirements"][requirement] = int(value)
    return abilities


def translate_ability(name, locale="PL"):
    if not name.strip():
        return ""
    locale_file = path.join("locales", "ability_names_{}.csv".format(locale))
    if not path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = path.join("locales", "ability_names_{}.csv".format("EN"))
        if not path.exists(locale_file):
            return name, ""
    with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.startswith(name):
                continue
            name, display_name, description = line.strip().split(";")
            return display_name, description
        print("No translation found for ability '{}' and locale '{}'".format(name, locale))
        return name, ""


def translate_parameter(name, locale="PL"):
    if not name.strip():
        return ""
    locale_file = path.join("locales", "parameter_names_{}.csv".format(locale))
    if not path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = path.join("locales", "parameter_names_{}.csv".format("EN"))
        if not path.exists(locale_file):
            return name
    with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.startswith(name):
                continue
            read_name, translation = line.strip().split(";")
            if read_name == name:
                return translation
        print("No translation found for parameter '{}' and locale '{}'".format(name, locale))
        return name


def translate_ui(name, locale="PL"):
    if not name.strip():
        return ""
    locale_file = path.join("locales", "ui_names_{}.csv".format(locale))
    if not path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = path.join("locales", "ui_names_{}.csv".format("EN"))
        if not path.exists(locale_file):
            return name
    with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.startswith(name):
                continue
            read_name, translation = line.strip().split(";")
            if read_name == name:
                return translation
        print("No translation found for parameter '{}' and locale '{}'".format(name, locale))
        return name


def translate_item(name, locale="PL"):
    if not name.strip():
        return ""
    locale_file = path.join("locales", "item_names_{}.csv".format(locale))
    if not path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = path.join("locales", "item_names_{}.csv".format("EN"))
        if not path.exists(locale_file):
            return name
    with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.startswith(name):
                continue
            read_name, translation = line.strip().split(";")
            if read_name == name:
                return translation
        print("No translation found for parameter '{}' and locale '{}'".format(name, locale))
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
