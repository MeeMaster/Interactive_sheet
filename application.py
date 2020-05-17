# import os
import sys
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import pyqtSignal

import pickle
from sheet import Character
from window import MainWindow
from popups import ItemPopup
from item_classes import Item, Weapon, Armor, ModifierItem

# from layout_classes import ArmorView, ModifierItemView, WeaponView, AbilityView
version = 0.91


class Application:

    def __init__(self):
        self.main_window = MainWindow()
        self.main_widget = None
        self.main_window.directory_signal.connect(self.file_IO)
        self.main_window.new_sheet.connect(self.new_sheet)
        self.sheet = None

    def reset_window(self):
        self.main_window.clear()
        self.main_window.create()
        self.main_widget = self.main_window.window_widget

    def new_sheet(self, robot=False):
        self.sheet = Character(robot, version)
        self.reset_window()
        self.load_sheet()

    def load_sheet(self):
        self.reset_window()
        alt = self.sheet.is_robot
        self.main_widget.fill_tab1(self.sheet.character, self.sheet.attributes,
                                   self.sheet.skills, self.sheet.armor_names, self.ability_validator, alternative=alt)
        self.main_widget.fill_tab2()
        self.main_widget.fill_tab3([a for a in self.sheet.notes if a != "notes_money"])

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

        # Register notes
        for notebook in self.main_widget.notes_dict:
            note_class = self.main_widget.notes_dict[notebook]
            note_class.text_changed.connect(self.sheet.change_notes)

        # Register equipment
        for scroll in self.main_widget.scrolls:
            self.main_widget.scrolls[scroll].item_equipped.connect(self.equip_item)
            self.main_widget.scrolls[scroll].item_created.connect(self.create_item)
            self.main_widget.scrolls[scroll].item_removed.connect(self.remove_item)
        self.main_widget.equipment_tables.set_items(self.sheet.items)
        self.main_widget.equipment_tables.item_create.connect(self.create_item)
        self.main_widget.equipment_tables.item_qty_changed.connect(self.change_item_quantity)
        self.main_widget.equipment_tables.move_item.connect(self.move_item)
        self.main_widget.equipment_tables.delete_item.connect(self.remove_item)
        # self.main_widget.equipment_tables.edit_item.connect(self.edit_item)
        # self.main_widget.equipment_tables.delete_item.connect(self.delete_item)

        self.update_form()

    def file_IO(self, *args):
        path, action = args
        if action == "open":
            self.read_character(path)
        if action == "save":
            self.save_character(path)

    def read_character(self, path):
        self.sheet = pickle.load(open(path, "rb"))
        self.sheet = sheet_compatibility_check(self.sheet)
        self.load_sheet()

    def save_character(self, path):
        if self.sheet is None:
            return
        pickle.dump(self.sheet, open(path, "wb"))

    # Attribute Handling
    def update_attribute(self, attribute):
        val = self.sheet.attributes[attribute]
        self.main_widget.attribute_dict[attribute].set_base(val)
        val = self.sheet.attribute_advancements[attribute]
        self.main_widget.attribute_dict[attribute].set_advancement(val)
        val = self.sheet.calculate_attribute(attribute)
        self.main_widget.attribute_dict[attribute].set_total(val)
        self.update_skills()
        self.update_armor_values()
        self.update_parameters()

    def update_attributes(self):
        for attribute in self.sheet.attributes:
            self.update_attribute(attribute)

    def change_attribute(self, name, val_type, value):
        self.sheet.change_attribute(name, val_type, value)
        self.update_attribute(name)

    # Skill Handling
    def update_skill(self, skill):
        val = self.sheet.skills[skill]
        self.main_widget.skills_dict[skill].set_advancement(val)
        self.main_widget.skills_dict[skill].set_enabled(True)
        bonus_val = self.sheet.skill_bonuses[skill]
        bonus_val2 = self.sheet.skill_bonuses2[skill]
        self.main_widget.skills_dict[skill].set_bonus(bonus_val, bonus_val2)
        total_val = self.sheet.calculate_skill(skill)
        if self.sheet.is_robot:
            if bonus_val == 0 and bonus_val2 == 0:
                self.main_widget.skills_dict[skill].set_enabled(False)
                total_val = 0
        self.main_widget.skills_dict[skill].set_total(total_val)

    def update_skills(self):
        for skill in self.sheet.skills:
            self.update_skill(skill)

    def change_skill(self, name, val_type, value):
        self.sheet.change_skill(name, val_type, value)
        self.update_skill(name)

    # Parameter Handling
    def update_parameters(self):
        for parameter in self.sheet.parameters:
            self.update_parameter(parameter)

    def update_parameter(self, name):
        value = self.sheet.parameters[name]
        if name not in self.main_widget.params_dict:
            return  # TODO use all of params in the sheet
        self.main_widget.params_dict[name].setText(value)

    def change_parameter(self, name, value):
        self.sheet.change_parameter(name, value)
        self.update_parameters()

    # Character Handling
    def update_character_fields(self):
        for parameter in self.sheet.character:
            self.update_character_field(parameter)

    def update_character_field(self, name):
        value = self.sheet.character[name]
        self.main_widget.params_dict[name].setText(value)

    def change_character(self, name, value):
        self.sheet.change_character(name, value)
        self.update_character_field(name)

    # Handle all scrolls items
    def equip_item(self, item, equip):
        # Weapon
        if isinstance(item, Weapon):
            item.equipped = equip
            self.update_weapons()
        # Armor
        elif isinstance(item, Armor):
            item.equipped = equip
            self.update_armor()
            pass
        # Modifier
        elif isinstance(item, ModifierItem):
            self.sheet.equip_modifier_item(item, equip)
            self.update_modifiers()
            self.update_attributes()
            self.update_parameters()
            self.update_abilities()

    def create_item(self, item):
        # Ability
        if isinstance(item, str):
            self.add_ability(item)
            self.update_abilities()
        # Weapon
        elif isinstance(item, Weapon):
            self.sheet.add_weapon(item)
            self.update_weapons()
        # Armor
        elif isinstance(item, Armor):
            self.sheet.add_armor(item)
            self.update_armor()
        # Modifier
        elif isinstance(item, ModifierItem):
            self.sheet.add_modifier_item(item)
            self.update_modifiers()
        elif isinstance(item, Item):
            self.sheet.add_item(item)
            self.update_items()


    def remove_item(self, item):
        # Ability
        if isinstance(item, str):
            self.remove_ability(item)
            self.update_abilities()
        # Weapon
        elif isinstance(item, Weapon):
            self.sheet.remove_weapon(item)
            self.update_weapons()
        # Armor
        elif isinstance(item, Armor):
            self.sheet.remove_armor(item)
            self.update_armor()
            pass
        # Modifier
        elif isinstance(item, ModifierItem):
            self.sheet.remove_modifier_item(item)
            self.update_modifiers()
            self.update_form()
            pass
        elif isinstance(item, Item):
            self.sheet.remove_item(item)
            self.update_items()

    def delete_item(self, equipped, _id):
        source = self.sheet.items_stashed if not equipped else self.sheet.items_equipped
        if _id not in source:
            return
        del source[_id]
        self.main_widget.equipment_tables.update_item_tables()

    # Ability Handling
    def update_abilities(self):
        self.main_widget.scrolls["abilities"].clear()
        for ability in self.sheet.abilities:
            self.main_widget.scrolls["abilities"].add_widget(ability)

    def add_ability(self, ability):
        self.sheet.add_ability(ability)
        self.update_abilities()

    def remove_ability(self, ability):
        self.sheet.remove_ability(ability)
        self.update_abilities()
    # Weapon Handling

    def update_weapons(self):
        self.main_widget.scrolls["weapons"].clear()
        for weapon in self.sheet.weapons:
            self.main_widget.scrolls["weapons"].add_widget(weapon)

    def update_armor(self):
        self.main_widget.scrolls["armor"].clear()
        for armor in self.sheet.armor:
            self.main_widget.scrolls["armor"].add_widget(armor)
        self.update_armor_values()

    def update_armor_values(self):
        armor_dict = self.sheet.calculate_armor()
        for armor_slot in armor_dict:
            self.main_widget.params_dict[armor_slot].setText(str(armor_dict[armor_slot]))

    def update_modifiers(self):
        self.main_widget.scrolls["modifiers"].clear()
        for modifier in self.sheet.modifier_items:
            self.main_widget.scrolls["modifiers"].add_widget(modifier)

    def update_notes(self):
        for note_name in self.sheet.notes:
            text = self.sheet.notes[note_name]
            self.main_widget.notes_dict[note_name].set_text(text)

    def change_notes(self, name, value):
        self.main_widget.notes_dict[name].set_text(str(value))

    def update_items(self):
        self.main_widget.equipment_tables.update_item_tables()

    def change_item_quantity(self, equipped, name, value, change):
        item = self.sheet.find_item_with_name(name)
        if item is None:
            print("No such item!")
        item.total_quantity += value
        if equipped:
            item.equipped_quantity += value
        self.update_items()

    def move_item(self, item, value):
        self.sheet.move_item(item, value)
        self.main_widget.equipment_tables.update_item_tables()

    def ability_validator(self, ability):
        already_bought = self.sheet.has_ability(ability["name"])
        requires = []
        requirements = ability["requirements"]
        for requirement in requirements:
            if "ability_" in requirement:
                requires.append(int(self.sheet.has_ability(requirement)) - 1)
                continue
            if "skill_" in requirement:
                ski_val = int(self.sheet.calculate_skill(requirement, full=False)[0])
                requires.append(int(ski_val >= ability["requirements"][requirement]) -1)
                continue
            if "attrib_" in requirement:
                att_val = self.sheet.calculate_attribute(requirement, full=False)
                requires.append(int(att_val >= ability["requirements"][requirement]) - 1)
                continue
        return already_bought, requires

    def update_form(self):
        self.main_widget.character = self.sheet
        # Attributes
        self.update_attributes()
        # Skills
        self.update_skills()
        # Armor
        self.update_armor()
        # Abilities
        self.update_abilities()
        # Weapons
        self.update_weapons()
        # Modifiers
        self.update_modifiers()
        # Items
        self.update_items()
        # Armor
        self.update_armor_values()
        # Parameters
        self.update_parameters()
        # Character
        self.update_character_fields()
        # Notes
        self.update_notes()


def sheet_compatibility_check(sheet):
    sheet_dict = sheet.__dict__
    if "version" in sheet_dict:
        if sheet_dict["version"] == version:
            return sheet

    if "is_robot" not in sheet_dict:
        sheet_dict["is_robot"] = False
    reference_sheet = Character(sheet.is_robot)
    reference_dict = reference_sheet.__dict__
    for name in reference_dict:
        if name in sheet_dict:
            continue
        sheet_dict[name] = reference_dict[name]

    if not isinstance(sheet_dict["notes"], dict):
        new_notes = {}
        for item in ["notes", "knowledge", "contacts"]:
            new_notes["notes_" + item] = ""
            if item in sheet_dict:
                new_notes["notes_" + item] = sheet_dict[item]
                del sheet_dict[item]
        sheet_dict["notes"] = new_notes

    for attrib_dict in ["attributes", "attribute_advancements", "attribute_bonuses"]:
        new_dict = {}
        for attrib, value in sheet_dict[attrib_dict].items():
            new_dict[attrib.replace("param_", "attrib_")] = value
        sheet_dict[attrib_dict] = new_dict

    for skill_dict in ["skills", "skill_bonuses"]:
        new_dict = {}
        for skill, value in sheet_dict[skill_dict].items():
            new_dict[skill.replace("param_", "skill_")] = value
        sheet_dict[skill_dict] = new_dict

    if "character" not in sheet_dict:
        sheet_dict["character"] = {}
    for param in list(sheet_dict["parameters"].keys()):
        if param in ['param_name', 'param_race', 'param_planet', 'param_age', 'param_traits', 'param_profession']:
            sheet_dict["character"][param.replace("param_", "character_")] = sheet_dict["parameters"][param]
            del sheet_dict["parameters"][param]
        if "param_" not in param:
            sheet_dict["parameters"]["param_" + param] = sheet_dict["parameters"][param]
            del sheet_dict["parameters"][param]

    # Fix items
    for armor in sheet_dict["armor"]:
        armor_names = {}
        for armor_name in armor.armor:
            armor_names[armor_name.replace("param_", "")] = armor.armor[armor_name]
        armor.armor = armor_names

    sheet.version = version
    return sheet


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_class = Application()
    sys.exit(app.exec_())


