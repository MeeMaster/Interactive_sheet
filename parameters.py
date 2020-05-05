import codecs
import os
from item_classes import weapon_from_line
base_path = os.path.split(os.path.abspath(__file__))[0]


attribute_names = ["strength", "agility", "intelligence", "toughness", "willpower", "charisma"]
damage_types = ["e", "p", "x", "el", "i", "ammo"]
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
                        "security": ["intelligence"],
                        "navigation": ["intelligence"],
                        "medicine": ["intelligence"],
                        "pilot_speeders": ["agility"],
                        "pilot_walkers": ["agility"],
                        "pilot_spaceships": ["agility"]
                        }


def load_abilities():
    abilities = {}
    with codecs.open(os.path.join(base_path, "parameters", "abilities.csv"), "r", encoding="windows-1250", errors='ignore') as infile:
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
    locale_file = os.path.join(base_path, "locales", "ability_names_{}.csv".format(locale))
    if not os.path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = os.path.join(base_path, "locales", "ability_names_{}.csv".format("EN"))
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
    locale_file = os.path.join(base_path, "locales", "parameter_names_{}.csv".format(locale))
    if not os.path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = os.path.join(base_path, "locales", "parameter_names_{}.csv".format("EN"))
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
    locale_file = os.path.join(base_path, "locales", "ui_names_{}.csv".format(locale))
    if not os.path.exists(locale_file):
        print("Could not localize locale file '{}'".format(locale_file))
        locale_file = os.path.join(base_path, "locales", "ui_names_{}.csv".format("EN"))
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


def load_weapons():
    weapons = {"ranged": {},
               "melee": {}
               }
    with codecs.open(os.path.join(base_path, "parameters", "weapons.csv"), "r",
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
            if "melee" in weapon.base_skill:
                weapons["melee"][weapon.arch_name] = weapon
                continue
            weapons["ranged"][weapon.arch_name] = weapon
    return weapons
