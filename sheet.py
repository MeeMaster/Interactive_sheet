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
        # for armor in armor_names:
        #     self.armor[armor] = 0

        self.weapons = {}
        self.items = {}
        self.notes = ""
        self.knowledge = ""
        self.contacts = ""

        self.abilities = []
        self.implants = []
        self.free_XP = 0
        self.spent_XP = 0

    def load_character(self, path):
        character_stats = pickle.load(open(path, "rb"))
        self.name, self.age, self.planet, self.race, self.profession, self.traits, \
            self.attributes, self.attribute_advancements, self.attribute_bonuses, self.skills, self.skill_bonuses, \
            self.parameters, self.abilities, self.implants, self.free_XP, self.spent_XP = character_stats

    def save_character(self, path):
        character_stats = [self.name, self.age, self.planet, self.race, self.profession, self.traits,
                           self.attributes, self.attribute_advancements, self.attribute_bonuses, self.skills,
                           self.skill_bonuses,
                           self.parameters, self.abilities, self.implants, self.free_XP, self.spent_XP]
        pickle.dump(character_stats, open(path, "wb"))


