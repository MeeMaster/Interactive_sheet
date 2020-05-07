# import os
import sys
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import pyqtSignal

import pickle
from sheet import Character
from window import MainWindow
from parameters import attribute_skill_dict, armor_names


class Application:

    def __init__(self):
        self.main_window = MainWindow()
        self.main_widget = self.main_window.window_widget
        self.sheet = Character()
        self.main_window.directory_signal.connect(self.file_IO)
        self.main_widget.armor_changed.connect(lambda: self.update_armor())

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

        self.fill_form()

    def file_IO(self, *args):
        path, action = args
        if action == "open":
            self.read_character(path)
        if action == "save":
            self.save_character(path)
        pass

    def read_character(self, path):
        self.sheet = pickle.load(open(path, "rb"))
        self.fill_form()

    def save_character(self, path):
        pickle.dump(self.sheet, open(path, "wb"))

    def change_attribute(self, name, val_type, value):
        if val_type == "base":
            self.sheet.attributes[name] = value
        if val_type == "adv":
            self.sheet.attribute_advancements[name] = value
        total = self.sheet.calculate_attribute(name)
        self.update_attribute(name, total)
        self.update_armor()

    def update_attribute(self, attribute, value):
        self.main_widget.attribute_dict[attribute].set_total(value)
        for skill in attribute_skill_dict:
            if attribute in attribute_skill_dict[skill]:
                skill_val = self.sheet.calculate_skill(skill)
                self.update_skill(skill, skill_val)

    def change_skill(self, name, val_type, value):
        if val_type == "adv":
            self.sheet.skills[name] = int(value)
        if val_type == "bonus":
            self.sheet.skill_bonuses[name] = int(value)
        final_value = self.sheet.calculate_skill(name)
        self.update_skill(name, final_value)

    def update_skill(self, name, value):
        self.main_widget.skills_dict[name].set_total(value)

    def change_parameter(self, name, value):
        self.sheet.parameters[name] = value

    def update_parameter(self, name, value):
        self.main_widget.params_dict[name].setText(str(value))

    def change_armor(self, slot, armor_dict):
        self.sheet.armor[slot] = armor_dict

    def fill_attributes(self):
        for attribute in self.sheet.attributes:
            val = self.sheet.attributes[attribute]
            self.main_widget.attribute_dict[attribute].set_base(val)
            val = self.sheet.attribute_advancements[attribute]
            self.main_widget.attribute_dict[attribute].set_advancement(val)
            val = self.sheet.calculate_attribute(attribute)
            self.update_attribute(attribute, val)

    def fill_skills(self):
        for skill in self.sheet.skills:
            val = self.sheet.skills[skill]
            self.main_widget.skills_dict[skill].set_advancement(val)
            val = self.sheet.skill_bonuses[skill]
            self.main_widget.skills_dict[skill].set_bonus(val)
            val = self.sheet.calculate_skill(skill)
            self.update_skill(skill, val)

    def fill_parameters(self):
        for parameter in self.sheet.parameters:
            val = self.sheet.parameters[parameter]
            if parameter not in self.main_widget.params_dict:
                continue
            self.main_widget.params_dict[parameter].setText(str(val))
            self.update_parameter(parameter, val)

    def fill_abilities(self):
        self.main_widget.scrolls["abilities"].clear()
        for ability in self.sheet.abilities:
            self.main_widget.scrolls["abilities"]._add_widget(ability, filling=True)

    def fill_weapons(self):
        self.main_widget.scrolls["weapons"].clear()
        for weapon in self.sheet.weapons:
            self.main_widget.scrolls["weapons"]._add_widget(weapon, filling=True)

    def fill_armor(self):
        self.main_widget.scrolls["armor"].clear()
        for armor in self.sheet.armor:
            self.main_widget.scrolls["armor"]._add_widget(armor, filling=True)

    def update_armor(self):
        armor_dict = self.sheet.calculate_armor()
        for armor_slot in armor_dict:
            self.main_widget.params_dict[armor_slot].setText(str(armor_dict[armor_slot]))

    def fill_form(self):
        self.main_widget.character = self.sheet
        # Attributes
        self.fill_attributes()
        # Skills
        self.fill_skills()
        # Parameters
        self.fill_parameters()
        # Armor
        self.update_armor()
        # Abilities
        self.fill_abilities()
        # Weapons
        self.fill_weapons()
        # Armor
        self.fill_armor()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_class = Application()
    sys.exit(app.exec_())
