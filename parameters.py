import codecs

attribute_names = ["Strength", "Agility", "Intelligence", "Toughness", "Willpower", "Charisma"]

skill_names = ["Athletics", "Unarmed", "Armed", "Light weapons", "Heavy weapons", "Gunnery", "Dodge", "Dexterity",
               "Perception", "Analysis", "Composition", "Persistence", "Resistance", "Steal", "Hide", "Diplomacy",
               "Cheat", "Commerce", "Interrogation", "Survival", "Cybernetics", "Mechanics",
               "Lockpicking", "Navigation", "Medicine", "Speeders", "Walkers", "Starships"]

character_names = ["Name", "Race", "Planet", "Age", "Traits", "Profession"]

parameter_names = ["Low encumbrance", "Medium encumbrance", "High encumbrance", "Low speed", "Medium speed",
                   "High speed", "Bad reputation", "Good reputation", "Total HP", "Current HP", "Total PP",
                   "Current PP", "Fatigue", "Total XP", "Free XP"]

armor_names = ["Armor head", "Armor rh", "Armor chest", "Armor lh", "Armor rl", "Armor ll"]

attribute_skill_dict = {"Athletics": ["Strength"],
                        "Unarmed": ["Strength", "Agility"],
                        "Armed": ["Strength", "Agility"],
                        "Light weapons": ["Agility"],
                        "Heavy weapons": ["Strength"],
                        "Gunnery": ["Intelligence", "Agility"],
                        "Dodge": ["Agility"],
                        "Dexterity": ["Agility"],
                        "Perception": ["Intelligence", "Agility"],
                        "Analysis": ["Intelligence"],
                        "Composition": ["Willpower"],
                        "Persistence": ["Willpower"],
                        "Resistance": ["Toughness"],
                        "Steal": ["Agility"],
                        "Hide": ["Agility"],
                        "Influence": ["Charisma"],
                        "Diplomacy": ["Charisma"],
                        "Cheat": ["Charisma"],
                        "Commerce": ["Charisma"],
                        "Interrogation": ["Charisma"],
                        "Survival": ["Intelligence", "Agility"],
                        "Cybernetics": ["Intelligence"],
                        "Mechanics": ["Intelligence"],
                        "Lockpicking": ["Agility"],
                        "Navigation": ["Intelligence"],
                        "Medicine": ["Intelligence"],
                        "Speeders": ["Agility"],
                        "Walkers": ["Agility"],
                        "Starships": ["Agility"]
                        }


def load_abilities():
    abilities = {}
    with codecs.open("abilities.csv", "r", encoding="windows-1250", errors='ignore') as infile:
        for line in infile:
            if not line.strip():
                continue
            name, display, requirements, desc, tier = line.strip().split(";")
            abilities[name] = {
                "name": name,
                "display": display,
                "requirements": [a.strip() for a in requirements.split(",")],
                "description": desc,
                "tier": tier
                }
    return abilities
