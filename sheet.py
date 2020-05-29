import pickle
from parameters import load_parameters


attribute_skill_dict = None
armor_names = None
attribute_names = None
character_names = None
notes_names = None
parameter_names = None


def read_parameters(alternative=False):
    global attribute_skill_dict
    global armor_names
    global attribute_names
    global character_names
    global notes_names
    global parameter_names
    param_dict = load_parameters(alternative=alternative)
    attribute_skill_dict = param_dict["skill"]
    armor_names = param_dict["armor"]
    attribute_names = param_dict["attrib"]
    character_names = param_dict["character"]
    notes_names = param_dict["notes"]
    parameter_names = param_dict["param"]


class Character:

    def __init__(self, is_robot=False, version=None):
        self.is_robot = is_robot
        self.version = version
        self.attributes = {}
        self.attribute_advancements = {}
        self.attribute_bonuses = {}
        read_parameters(alternative=self.is_robot)
        self.attribute_skill_dict = attribute_skill_dict
        self.armor_names = armor_names
        self.attribute_names = attribute_names
        self.character_names = character_names
        self.notes_names = notes_names
        self.parameter_names = parameter_names
        for attribute in self.attribute_names:
            self.attributes[attribute] = 0
            self.attribute_advancements[attribute] = 0
            self.attribute_bonuses[attribute] = 0

        self.skills = {}
        self.skill_bonuses = {}
        self.skill_bonuses2 = {}
        for skill in self.attribute_skill_dict:
            self.skills[skill] = 0
            self.skill_bonuses[skill] = 0
            self.skill_bonuses2[skill] = 0

        self.parameters = {}
        self.character = {}
        for parameter in self.parameter_names:
            self.parameters[parameter] = 0
        for name in self.character_names:
            self.character[name] = ""

        # self.armor = set()
        # self.weapons = set()
        # self.modifier_items = set()
        self.objects = set()
        self.items = set()  # TODO remove later
        self.notes = {}
        for note in self.notes_names:
            self.notes[note] = ""

        self.abilities = set()
        self.implants = []
        self.free_XP = 0
        self.spent_XP = 0

    def calculate_skill(self, skill, full=True):
        ski_value = 0
        ski_value += self.skills[skill]
        ski_bonus1, ski_bonus2 = self.get_skill_bonuses(skill)
        if self.is_robot and ski_bonus1 == 0 and ski_bonus2 == 0:
            return 0
        ski_value += ski_bonus1
        ski_value += ski_bonus2
        if full:
            attributes = self.attribute_skill_dict[skill]
            modifier = self.read_modifier_items(skill, "modifier")
            ski_value += modifier
            values = []
            for att in attributes:
                values.append(str(self.calculate_attribute(att) + ski_value))
            final_value = "/".join(values)
        else:
            final_value = [str(ski_value)]
        return final_value

    def get_skill_bonuses(self, skill):
        ski_value1 = self.skill_bonuses[skill]
        ski_value2 = self.skill_bonuses2[skill]
        ski_value1 += self.read_modifier_items(skill, "bonus")
        ski_value2 += self.read_modifier_items(skill, "bonus2")
        return ski_value1, ski_value2

    def calculate_attribute(self, attribute, full=True):
        att_value = 0
        att_value += self.attributes[attribute]
        att_value += self.attribute_advancements[attribute]
        att_value += self.attribute_bonuses[attribute]
        if full:
            att_value += self.read_modifier_items(attribute)
        return att_value

    def calculate_armor(self):
        armor_dict = {}
        for armor_slot in self.armor_names:
            armor_dict[armor_slot] = self.calculate_attribute("attrib_toughness") // 10
        for armor in self.items:
            if armor.type != "armor":
                continue
            if not armor.equipped_quantity:
                continue
            for armor_slot in self.armor_names:
                armor_dict[armor_slot] += armor.armor[armor_slot]
        for armor_slot in self.armor_names:
            modifier = self.read_modifier_items(armor_slot)
            armor_dict[armor_slot] += modifier
        return armor_dict

    def add_object(self, obj):
        self.objects.add(obj)

    def remove_object(self, obj):
        for element in self.objects:
            pass

    def add_ability(self, ability):
        if self.has_ability(ability.name):
            return
        self.abilities.add(ability)

    def remove_ability(self, ability):
        # ab = self.has_ability(ability)
        # if not ability:
        #     return
        self.abilities.remove(ability)

    def get_abilities(self):
        abilities = set()  # TODO fix later
        # for object in self.objects:
        #     if object.type == "ability":
        #         abilities.append(object)
        # return abilities
        # abilities = self.get_modifier_item_abilities()
        return self.abilities | abilities

    def add_weapon(self, weapon):
        if weapon in self.items:
            return False
        self.items.add(weapon)
        return True

    def remove_weapon(self, item):
        found = False
        for weapon in self.items:
            if item.ID == weapon.ID:
                found = True
                break
        if found:
            self.items.remove(weapon)
        return found

    def add_armor(self, armor):
        if armor in self.items:
            return False
        self.items.add(armor)
        return True

    def remove_armor(self, item):
        found = False
        for armor in self.items:
            if item.ID == armor.ID:
                found = True
                break
        if found:
            self.items.remove(armor)
        return found

    def find_item_with_id(self, _id):
        for item in self.items:
            if _id == item.ID:
                return item
        return

    def find_item_with_name(self, name):
        for item in self.items:
            if name == item.name:
                return item
        return

    def change_notes(self, name, value):
        self.notes[name] = value

    def change_parameter(self, name, value):
        if name.startswith("character_"):
            self.character[name] = value
        if name not in self.parameters:
            return
        self.parameters[name] = value
        self.update_parameters()

    def change_character(self, name, value):
        self.character[name] = value

    def change_skill(self, name, val_type, value):
        if val_type == "adv":
            self.skills[name] = int(value)
        if val_type == "bonus":
            self.skill_bonuses[name] = int(value)

    def change_attribute(self, name, val_type, value):
        if val_type == "base":
            self.attributes[name] = value
        if val_type == "adv":
            self.attribute_advancements[name] = value
        self.update_parameters()

    def get_modifier_item_abilities(self):
        abilities = set()
        for item in self.items:
            if not item.equipped_quantity:
                continue
            for bonus in item.bonuses:
                if bonus.startswith("ability_"):
                    abilities.add(bonus)
        return abilities

    def read_modifier_items(self, param, mod_type="modifier"):
        out = 0
        for item in self.items:
            if not item.equipped_quantity:
                continue
            if item.type not in ["modifier", "bionic", "implant", "part", "module"]:
                continue
            if item.bonus_type != mod_type:
                continue
            if param not in item.bonuses:
                continue
            out += item.bonuses[param]
        return out

    def add_modifier_item(self, item):
        if item in self.items:
            return
        self.items.add(item)

    def remove_modifier_item(self, item):
        found = False
        for modifier in self.items:
            if item.ID == modifier.ID:
                found = True
                break
        if found:
            self.equip_modifier_item(modifier, False)
            self.items.remove(modifier)
        return found

    def calculate_current_encumbrance(self):
        curr_weight = 0
        for item in self.items:
            curr_weight += item.equipped_quantity * item.weight
        return curr_weight

    def equip_modifier_item(self, item, equip):
        if item.equipped == equip:
            return
        item.equipped = equip
        if item.bonus_type == "modifier":
            return
        if not equip:
            return
        for other_item in self.items:
            if other_item.ID == item.ID:
                continue
            if not other_item.equipped:
                continue
            if other_item.bonus_type != item.bonus_type:
                continue
            if set(other_item.bonuses.keys()) & set(item.bonuses.keys()):
                self.equip_modifier_item(other_item, False)

    def add_item(self, item):
        if item in self.items:
            return
        self.items.add(item)

    def remove_item(self, equipped, _item):
        found = False
        for item in self.items:
            if _item.ID == item.ID:
                found = True
                break
        if not found:
            return
        if equipped:
            item.total_quantity -= item.equipped_quantity
            item.equipped_quantity = 0
        else:
            item.total_quantity -= item.total_quantity - item.equipped_quantity
        if item.total_quantity == 0:
            self.items.remove(item)

    def move_item(self, item, value):
        if item not in self.items:
            return
        item.equipped_quantity += value
        if item.equipped_quantity > item.total_quantity:
            item.equipped_quantity = item.total_quantity
        if item.equipped_quantity < 0:
            item.equipped_quantity = 0

    def update_parameters(self):
        self.update_speed()
        self.update_encumbrance()
        self.update_reputation()
        pass

    def update_speed(self):
        agi_bonus = self.calculate_attribute("attrib_agility") // 10
        self.parameters["param_speed_low"] = agi_bonus * 2
        self.parameters["param_speed_med"] = agi_bonus * 3
        self.parameters["param_speed_high"] = agi_bonus * 6
        pass

    def update_encumbrance(self):
        strength = self.calculate_attribute("attrib_strength")
        self.parameters["param_encumbrance_low"] = (strength + 1) // 2
        self.parameters["param_encumbrance_med"] = strength
        self.parameters["param_encumbrance_high"] = round((strength * 1.5) + 0.5)

    def update_reputation(self):
        self.parameters["param_reputation_total"] = int(self.parameters["param_reputation_good"]) + \
                                                    int(self.parameters["param_reputation_bad"])

    def has_ability(self, ability):

        for obj in self.abilities:
            if obj.type != "ability":
                continue
            if obj.name == ability:
                return True
        return False
        # return ability in self.abilities

