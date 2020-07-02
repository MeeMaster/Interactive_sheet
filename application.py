import sys
from PyQt5.QtWidgets import QApplication

import pickle
from sheet import Character
from window import MainWindow

version = 0.98


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
        self.main_widget.fill_tab2(self.sheet.is_robot)
        self.main_widget.fill_tab3([a for a in self.sheet.notes if a != "notes_money"])

        # Register attributes
        for attribute in self.main_widget.attribute_dict:
            att_class = self.main_widget.attribute_dict[attribute]
            att_class.attribute_changed.connect(self.change_attribute)

        # Register skills
        for skill in self.main_widget.skills_dict:
            skill_class = self.main_widget.skills_dict[skill]
            if not self.sheet.is_robot and skill in self.sheet.naturals:
                skill_class.set_natural(True)
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
            self.main_widget.scrolls[scroll].item_edited.connect(self.update_form)
        self.main_widget.equipment_tables.set_items(self.sheet.items)
        self.main_widget.equipment_tables.item_create.connect(self.create_item)
        self.main_widget.equipment_tables.item_qty_changed.connect(self.change_item_quantity)
        self.main_widget.equipment_tables.move_item.connect(self.move_item)
        self.main_widget.equipment_tables.delete_item.connect(self.remove_item)
        self.main_widget.current_weapon_widget.shoot_weapon.connect(self.shoot_weapon)
        self.main_widget.current_weapon_widget.swap_weapon.connect(self.swap_weapon)
        self.update_form()

    def shoot_weapon(self, weapon):
        self.main_window.open_calculator(sheet=self.sheet, weapon=weapon)

    def swap_weapon(self, direction):
        weapons = self.sheet.get_equipped_weapons()
        weapons = sorted(weapons, key=lambda x: x.name)
        current_weapon = self.main_widget.current_weapon_widget.weapon
        if current_weapon not in weapons:
            self.main_widget.current_weapon_widget.set_weapon(weapons[0])
            return


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
        bonus_val = self.sheet.get_skill_bonuses(skill)
        self.main_widget.skills_dict[skill].set_bonus(bonus_val[0], bonus_val[1])
        total_val = self.sheet.calculate_skill(skill)
        if self.sheet.is_robot:
            if bonus_val[0] == 0 and bonus_val[1] == 0:
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
        self.update_parameter("param_encumbrance_current")

    def update_parameter(self, name):
        if name == "param_encumbrance_current":
            value = self.sheet.calculate_current_encumbrance()
            self.main_widget.params_dict[name].setText(value)
            return
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
    def equip_item(self, name, item, equip):
        self.sheet.move_item(item, 1 if equip else -1)
        # item.equipped_quantity = int(equip)
        self.update_form()

    def create_item(self, name, item):
        # Ability
        if item.type == "ability":
            self.sheet.add_ability(item)
            self.update_form()
            return
        self.sheet.add_item(item)
        self.update_form()

    def remove_item(self, name, item):
        if item.type == "ability":
            self.sheet.remove_ability(item)
            self.update_form()
            return
        self.sheet.remove_item(item.equipped_quantity > 0, item)
        self.update_form()

    def delete_item(self, equipped, item):
        self.sheet.remove_item(equipped, item)
        self.update_items()

    # Ability Handling
    def update_abilities(self):
        self.main_widget.scrolls["abilities"].clear()
        self.main_widget.scrolls["abilities"].fill(self.sheet.get_abilities())

    def add_ability(self, ability):
        self.sheet.add_ability(ability)
        self.update_abilities()

    def remove_ability(self, ability):
        self.sheet.remove_ability(ability)
        self.update_abilities()
    # Weapon Handling

    def update_weapons(self):
        self.main_widget.scrolls["weapons"].clear()
        self.main_widget.scrolls["weapons"].fill(self.sheet.items)

    def update_armor(self):
        self.main_widget.scrolls["armor"].clear()
        self.main_widget.scrolls["armor"].fill(self.sheet.items)
        self.update_armor_values()

    def update_armor_values(self):
        armor_dict = self.sheet.calculate_armor()
        for armor_slot in armor_dict:
            self.main_widget.params_dict[armor_slot].setText(str(armor_dict[armor_slot]))

    def update_modifiers(self):
        self.main_widget.scrolls["modifiers"].clear()
        self.main_widget.scrolls["modifiers"].fill(self.sheet.items)
        if self.sheet.is_robot:
            self.main_widget.scrolls["modules"].clear()
            self.main_widget.scrolls["modules"].fill(self.sheet.items)
            self.main_widget.scrolls["parts"].clear()
            self.main_widget.scrolls["parts"].fill(self.sheet.items)

    def update_notes(self):
        for note_name in self.sheet.notes:
            text = self.sheet.notes[note_name]
            self.main_widget.notes_dict[note_name].set_text(text)

    def change_notes(self, name, value):
        self.main_widget.notes_dict[name].set_text(str(value))

    def update_items(self):
        self.main_widget.equipment_tables.update_item_tables()

    def change_item_quantity(self, equipped, _id, value, change):
        item = self.sheet.find_item_with_id(_id)
        if item is None:
            print("No such item!")
        item.total_quantity += value
        if item.total_quantity < 0:
            item.total_quantity = 0
        if equipped:
            item.equipped_quantity += value
        if item.equipped_quantity < 0:
            item.equipped_quantity = 0
        self.update_items()

    def move_item(self, item, value):
        self.sheet.move_item(item, value)
        self.main_widget.equipment_tables.update_item_tables()

    def ability_validator(self, ability):
        already_bought = self.sheet.has_ability(ability.name)
        requires = []
        for requirement in ability.requirements:
            if "ability_" in requirement:
                requires.append(int(self.sheet.has_ability(requirement)) - 1)
                continue
            if "skill_" in requirement:
                ski_val = int(self.sheet.calculate_skill(requirement, full=False)[0])
                requires.append(int(ski_val >= ability.requirements[requirement]) - 1)
                continue
            if "attrib_" in requirement:
                att_val = self.sheet.calculate_attribute(requirement, full=False)
                requires.append(int(att_val >= ability.requirements[requirement]) - 1)
                continue
        return already_bought, requires

    def update_form(self):
        self.main_widget.character = self.sheet
        # Modifiers
        self.update_modifiers()
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
    if isinstance(sheet_dict["items"], dict):
        items = set()
        for item in sheet_dict["items"]:
            items.add(sheet_dict["items"][item])
        sheet_dict["items"] = items
    for item in sheet_dict["items"]:
        item.weight = float(item.weight)
        item.type = "item"
    for item in sheet_dict["weapons"]:
        item.total_quantity = 1
        item.equipped_quantity = 0
        if not item.weight:
            item.weight = 0
        item.weight = float(item.weight)
        if not "damage" in item.damage_type:
            item.damage_type = "damage_" + item.damage_type
        item.type = "weapon"
    for item in sheet_dict["armor"]:
        item.total_quantity = 1
        item.equipped_quantity = 0
        item.type = "armor"
        armor_names = {}
        if not item.weight:
            item.weight = 0
        item.weight = float(item.weight)
        for armor_name in item.armor:
            armor_names[armor_name.replace("param_", "")] = item.armor[armor_name]
        item.armor = armor_names
    for item in sheet_dict["modifier_items"]:
        item.total_quantity = 1
        item.equipped_quantity = 0
        if "ability" in item.arch_name:
            item.type = "module"
        else:
            item.type = "part"

    sheet_dict["items"] = sheet_dict["items"] | sheet_dict["weapons"]
    sheet_dict["items"] = sheet_dict["items"] | sheet_dict["armor"]
    sheet_dict["items"] = sheet_dict["items"] | sheet_dict["modifier_items"]
    del sheet_dict["weapons"]
    del sheet_dict["armor"]
    del sheet_dict["modifier_items"]
    for item in sheet_dict["items"]:
        if "bonuses" not in item.__dict__:
            item.bonuses = {}

    sheet.version = version
    return sheet


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_class = Application()
    sys.exit(app.exec_())


