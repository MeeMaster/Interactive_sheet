import os, sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal

from sheet import Character
from window import MainWindow

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
                        "Calmness": ["Willpower"],
                        "Persistence": ["Willpower"],
                        "Resistance": ["Toughness"],
                        "Steal": ["Agility"],
                        "Hide": ["Agility"],
                        "Diplomacy": ["Charisma"],
                        "Deceive": ["Charisma"],
                        "Commerce": ["Charisma"],
                        "Interrogation": ["Charisma"],
                        "Intimidation": ["Strength", "Charisma"],
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


class Application:

    def __init__(self):
        self.main_window = MainWindow()
        self.main_widget = self.main_window.window_widget
        self.sheet = Character()
        self.main_window.directory_signal.connect(self.file_IO)

        # Register attributes
        for attribute in self.main_widget.attribute_dict:
            att_class = self.main_widget.attribute_dict[attribute]
            att_class.attribute_changed.connect(self.change_attribute)

        # Register skills
        for skill in self.main_widget.skills_dict:
            skill_class = self.main_widget.skills_dict[skill]
            skill_class.skill_changed.connect(self.change_skill)

        # Register params
        for parameter in self.main_widget.params_dict:
            param_class = self.main_widget.params_dict[parameter]
            param_class.value_changed.connect(self.change_parameter)

        for armor in self.main_widget.armor_dict:
            armor_class = self.main_widget.armor_dict[armor]
            armor_class.armor_changed.connect(self.change_armor)

        self.fill_form()




    def file_IO(self, *args):
        path, action = args
        if action == "open":
            self.read_character(path)
        if action == "save":
            self.save_character(path)
        pass

    def read_character(self, path):
        self.sheet.load_character(path)
        self.fill_form()

    def save_character(self, path):
        self.sheet.save_character(path)

    def change_attribute(self, name, val_type, value):
        if val_type == "base":
            self.sheet.attributes[name] = value
        if val_type == "adv":
            self.sheet.attribute_advancements[name] = value
        total = self.calculate_attribute(name)
        self.update_attribute(name, total)

    def calculate_attribute(self, attribute):
        att_value = 0
        att_value += self.sheet.attributes[attribute]
        att_value += self.sheet.attribute_advancements[attribute]
        att_value += self.sheet.attribute_bonuses[attribute]
        return att_value

    def update_attribute(self, attribute, value):
        self.main_widget.attribute_dict[attribute].set_total(value)
        for skill in attribute_skill_dict:
            if attribute in attribute_skill_dict[skill]:
                skill_val = self.calculate_skill(skill)
                self.update_skill(skill, skill_val)

    def calculate_skill(self, skill):
        ski_value = 0
        ski_value += self.sheet.skills[skill]
        ski_value += self.sheet.skill_bonuses[skill]
        attributes = attribute_skill_dict[skill]
        values = []
        for att in attributes:
            values.append(str(self.calculate_attribute(att) + ski_value))
        final_value = "/".join(values)
        return final_value

    def change_skill(self, name, val_type, value):
        if val_type == "adv":
            self.sheet.skills[name] = value
        if val_type == "bonus":
            self.sheet.skill_bonuses[name] = value
        final_value = self.calculate_skill(name)
        self.update_skill(name, final_value)

    def update_skill(self, name, value):
        self.main_widget.skills_dict[name].set_total(value)

    def change_parameter(self, name, value):
        self.sheet.parameters[name] = value

    def change_armor(self, slot, armor_dict):
        self.sheet.armor[slot] = armor_dict

    def fill_armor(self, slot):
        if slot not in self.sheet.armor:
            return
        armor_dict = self.sheet.armor[slot]
        armor_widget = self.main_widget.armor_dict[slot]
        for key in armor_dict:
            armor_widget.set_prop(key, armor_dict[key])

    def fill_form(self):
        # Attributes
        for attribute in self.sheet.attributes:
            val = self.sheet.attributes[attribute]
            self.main_widget.attribute_dict[attribute].set_base(val)
            val = self.sheet.attribute_advancements[attribute]
            self.main_widget.attribute_dict[attribute].set_advancement(val)
            val = self.calculate_attribute(attribute)
            self.update_attribute(attribute, val)
        # Skills
        for skill in self.sheet.skills:
            val = self.sheet.skills[skill]
            self.main_widget.skills_dict[skill].set_advancement(val)
            val = self.sheet.skill_bonuses[skill]
            self.main_widget.skills_dict[skill].set_bonus(val)
            val = self.calculate_skill(skill)
            self.update_skill(skill, val)
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_class = Application()
    sys.exit(app.exec_())