import codecs
from os import path

#base_path = path.split(path.abspath(__file__))[0]

notes_names = ["notes", "contacts", "knowledge"]

attribute_names = ["param_strength", "param_agility", "param_intelligence", 
                   "param_toughness", "param_willpower", "param_charisma"]
damage_types = ["e", "p", "x", "el", "i", "ammo"]
character_names = ["param_name", "param_race", "param_planet", "param_age", "param_traits", "param_profession"]

parameter_names = ["param_encumbrance_low", "param_encumbrance_med", "param_encumbrance_high", "param_speed_low", 
                   "param_speed_med", "param_speed_high", "param_reputation_bad", "param_reputation_good", 
                   "param_hp_max", "param_hp_current", "param_pp_total", "param_pp_curr", "param_fatigue", 
                   "param_xp_total", "param_xp_free"]

armor_names = ["param_armor_head", "param_armor_rh", "param_armor_chest", 
               "param_armor_lh", "param_armor_rl", "param_armor_ll"]

attribute_skill_dict = {"param_athletics": ["param_strength"],
                        "param_melee_unarmed": ["param_strength", "param_agility"],
                        "param_melee_armed": ["param_strength", "param_agility"],
                        "param_ranged_light": ["param_agility"],
                        "param_ranged_heavy": ["param_strength"],
                        "param_ranged_stationary": ["param_intelligence", "param_agility"],
                        "param_dodge": ["param_agility"],
                        "param_dexterity": ["param_agility"],
                        "param_perception": ["param_intelligence", "param_agility"],
                        "param_analysis": ["param_intelligence"],
                        "param_composition": ["param_willpower"],
                        "param_persistence": ["param_willpower"],
                        "param_resistance": ["param_toughness"],
                        "param_conceal": ["param_agility"],
                        "param_influence": ["param_charisma"],
                        "param_diplomacy": ["param_charisma"],
                        "param_cheat": ["param_charisma"],
                        "param_commerce": ["param_charisma"],
                        "param_interrogation": ["param_charisma"],
                        "param_survival": ["param_intelligence", "param_agility"],
                        "param_cybernetics": ["param_intelligence"],
                        "param_mechanics": ["param_intelligence"],
                        "param_security": ["param_intelligence"],
                        "param_navigation": ["param_intelligence"],
                        "param_medicine": ["param_intelligence"],
                        "param_pilot_speeders": ["param_agility"],
                        "param_pilot_walkers": ["param_agility"],
                        "param_pilot_spaceships": ["param_agility"]
                        }


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
