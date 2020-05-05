import pickle
from parameters import armor_names, attribute_names, attribute_skill_dict, character_names, parameter_names


class Character:

    def __init__(self):
        self.name = None
        self.age = None
        self.planet = None
        self.race = None
        self.profession = None
        self.traits = None
        self.attributes = {}
        self.attribute_advancements = {}
        self.attribute_bonuses = {}
        for attribute in attribute_names:
            self.attributes[attribute] = 0
            self.attribute_advancements[attribute] = 0
            self.attribute_bonuses[attribute] = 0

        self.skills = {}
        self.skill_bonuses = {}
        for skill in attribute_skill_dict:
            self.skills[skill] = 0
            self.skill_bonuses[skill] = 0

        self.parameters = {}
        for parameter in parameter_names:
            self.parameters[parameter] = 0
        for name in character_names:
            self.parameters[name] = ""

        self.armor = {}
        self.weapons = {}
        self.items = {}
        self.notes = ""
        self.knowledge = ""
        self.contacts = ""

        self.abilities = []
        self.implants = []
        self.free_XP = 0
        self.spent_XP = 0

    def calculate_skill(self, skill):
        ski_value = 0
        ski_value += self.skills[skill]
        ski_value += self.skill_bonuses[skill]
        attributes = attribute_skill_dict[skill]
        values = []
        for att in attributes:
            values.append(str(self.calculate_attribute(att) + ski_value))
        final_value = "/".join(values)
        return final_value

    def calculate_attribute(self, attribute):
        att_value = 0
        att_value += self.attributes[attribute]
        att_value += self.attribute_advancements[attribute]
        att_value += self.attribute_bonuses[attribute]
        return att_value

    def calculate_armor(self):
        armor = {}
        for armor_slot in armor_names:
            armor[armor_slot] = self.attributes["param_toughness"] // 10
        for armor_name in self.armor:
            armor_item = self.armor[armor_name]
            if not armor_item["Equipped"]:
                continue
            for armor_slot in armor_names:
                armor[armor_slot] += armor_item[armor_slot]
        return armor

