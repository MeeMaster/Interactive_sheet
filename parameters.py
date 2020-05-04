import codecs
import os

attribute_names = ["strength", "agility", "intelligence", "toughness", "willpower", "charisma"]

character_names = ["name", "race", "planet", "age", "traits", "profession"]

parameter_names = ["encumbrance_low", "encumbrance_med", "encumbrance_high", "speed_low", "speed_med",
                   "speed_high", "reputation_bad", "reputation_good", "hp_max", "hp_current", "pp_total",
                   "pp_curr", "fatigue", "xp_total", "xp_free"]

armor_names = ["armor_head", "armor_rh", "armor_chest", "armor_lh", "armor_rl", "armor_ll"]

attribute_skill_dict = {"athletics": ["strength"],
                        "melee_unarmed": ["strength", "agility"],
                        "melee_armed": ["strength", "agility"],
                        "ranged_light": ["agility"],
                        "ranged_heavy": ["strength"],
                        "ranged_stationary": ["intelligence", "agility"],
                        "dodge": ["agility"],
                        "dexterity": ["agility"],
                        "perception": ["intelligence", "agility"],
                        "analysis": ["intelligence"],
                        "composition": ["willpower"],
                        "persistence": ["willpower"],
                        "resistance": ["toughness"],
                        "conceal": ["agility"],
                        "influence": ["charisma"],
                        "diplomacy": ["charisma"],
                        "cheat": ["charisma"],
                        "commerce": ["charisma"],
                        "interrogation": ["charisma"],
                        "survival": ["intelligence", "agility"],
                        "cybernetics": ["intelligence"],
                        "mechanics": ["intelligence"],
                        "security": ["agility"],
                        "navigation": ["intelligence"],
                        "medicine": ["intelligence"],
                        "pilot_speeders": ["agility"],
                        "pilot_walkers": ["agility"],
                        "pilot_spaceships": ["agility"]
                        }


def load_abilities():
    abilities = {}
    with codecs.open("abilities.csv", "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.strip():
                continue
            name, display, requirements, desc, tier = line.strip().split(";")
            if name in abilities:
                print("Ability '{}' already defined, check the config files!")
                continue
            abilities[name] = {
                "name": name,
                "display": display,
                "requirements": {},
                "description": desc,
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
    locale_file = "ability_names_{}.csv".format(locale)
    if not os.path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = "ability_names_{}.csv".format("EN")
        if not os.path.exists(locale_file):
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
    locale_file = "parameter_names_{}.csv".format(locale)
    if not os.path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = "parameter_names_{}.csv".format("EN")
        if not os.path.exists(locale_file):
            return name
    with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.startswith(name):
                continue
            name, translation = line.strip().split(";")
            return translation
        print("No translation found for parameter '{}' and locale '{}'".format(name, locale))
        return name


def translate_ui(name, locale="PL"):
    locale_file = "ui_names_{}.csv".format(locale)
    if not os.path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = "ui_names_{}.csv".format("EN")
        if not os.path.exists(locale_file):
            return name
    with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.startswith(name):
                continue
            name, translation = line.strip().split(";")
            return translation
        print("No translation found for parameter '{}' and locale '{}'".format(name, locale))
        return name
