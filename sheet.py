import pickle


class Character:

    def __init__(self):
        self.name = None
        self.age = None
        self.planet = None
        self.race = None
        self.profession = None
        self.traits = None
        self.attributes = {"Strength": 0,
                           "Agility": 0,
                           "Intelligence": 0,
                           "Toughness": 0,
                           "Willpower": 0,
                           "Charisma": 0
                           }

        self.attribute_advancements = {"Strength": 0,
                                       "Agility": 0,
                                       "Intelligence": 0,
                                       "Toughness": 0,
                                       "Willpower": 0,
                                       "Charisma": 0
                                       }

        self.attribute_bonuses = {"Strength": 0,
                                  "Agility": 0,
                                  "Intelligence": 0,
                                  "Toughness": 0,
                                  "Willpower": 0,
                                  "Charisma": 0
                                  }

        self.skills = {"Athletics": 0,
                       "Unarmed": 0,
                       "Armed": 0,
                       "Light weapons": 0,
                       "Heavy weapons": 0,
                       "Gunnery": 0,
                       "Dodge": 0,
                       "Dexterity": 0,
                       "Perception": 0,
                       "Analysis": 0,
                       "Calmness": 0,
                       "Persistence": 0,
                       "Resistance": 0,
                       "Steal": 0,
                       "Hide": 0,
                       "Diplomacy": 0,
                       "Deceive": 0,
                       "Commerce": 0,
                       "Interrogation": 0,
                       "Intimidation": 0,
                       "Survival": 0,
                       "Cybernetics": 0,
                       "Mechanics": 0,
                       "Lockpicking": 0,
                       "Navigation": 0,
                       "Medicine": 0,
                       "Speeders": 0,
                       "Walkers": 0,
                       "Starships": 0
                       }

        self.skill_bonuses = {"Athletics": 0,
                              "Unarmed": 0,
                              "Armed": 0,
                              "Light weapons": 0,
                              "Heavy weapons": 0,
                              "Gunnery": 0,
                              "Dodge": 0,
                              "Dexterity": 0,
                              "Perception": 0,
                              "Analysis": 0,
                              "Calmness": 0,
                              "Persistence": 0,
                              "Resistance": 0,
                              "Steal": 0,
                              "Hide": 0,
                              "Diplomacy": 0,
                              "Deceive": 0,
                              "Commerce": 0,
                              "Interrogation": 0,
                              "Intimidation": 0,
                              "Survival": 0,
                              "Cybernetics": 0,
                              "Mechanics": 0,
                              "Lockpicking": 0,
                              "Navigation": 0,
                              "Medicine": 0,
                              "Speeders": 0,
                              "Walkers": 0,
                              "Starships": 0
                              }

        self.parameters = {
            "Low encumbrance": 0,
            "Medium encumbrance": 0,
            "High encumbrance": 0,
            "Low speed": 0,
            "Medium speed": 0,
            "High speed": 0,
            "Bad reputation": 0,
            "Good reputation": 0,
            "Total HP": 0,
            "Current HP": 0,
            "Total PP": 0,
            "Current PP": 0,
            "Fatigue": 0,
            "Armor head": 0,
            "Armor chest": 0,
            "Armor rh": 0,
            "Armor lh": 0,
            "Armor rl": 0,
            "Armor ll": 0
        }

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


