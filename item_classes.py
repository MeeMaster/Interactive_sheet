import string
import random
# from parameters import load_parameters, translate_item
#
# param_dict = load_parameters()
# armor_names = param_dict["armor"]


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class BaseObject:

    def __init__(self):
        self.ID = random_word(16)
        self.parent = None
        self.display = ""
        self.name = ""
        self.tooltip = ""
        self.description = ""
        self.total_quantity = 0
        self.equipped_quantity = 0
        self.bonuses = {}
        self.type = "base"
        self.image = ""
        self.requirements = {}

    def set_requirements(self, requirements: list):
        for requirement in requirements:
            fields = requirement.strip().split()
            if len(fields) > 1:
                name, value = fields
                self.requirements[name] = int(value)
                continue
            self.requirements[requirement] = True


# class Ability(BaseObject):
#
#     def __init__(self):
#         BaseObject.__init__(self)
#         self.type = "ability"
#         self.requirements = {}
#         self.tier = 1
#
#     def set_requirements(self, requirements: list):
#         for requirement in requirements:
#             fields = requirement.strip().split()
#             if len(fields) > 1:
#                 name, value = fields
#                 self.requirements[name] = int(value)
#                 continue
#             self.requirements[requirement] = True
#
#
# class Trait(BaseObject):
#
#     def __init__(self):
#         BaseObject.__init__(self)
#
#
# class Item(BaseObject):
#
#     def __init__(self):
#         BaseObject.__init__(self)
#         self.price = 0
#         self.weight = 0
#         self.availability = ""
#         self.type = "item"
#
#
# class ModifierItem(Item):
#
#     def __init__(self):
#         Item.__init__(self)
#         self._line = None
#         self.type = "modifier"
#
#     # def load_from_line(self, line):
#     #     name, availability, value, weight, bonuses, bonus_type, modifier_type = line.strip().split(";")
#     #     bonuses = bonuses.split(",")
#     #     self.arch_name = name
#     #     self.name = translate_item(name)
#     #     self.availability = availability
#     #     self.price = 0 if not value else int(value)
#     #     self.weight = 0 if not weight else int(weight)
#     #     self.bonus_type = bonus_type
#     #     self._line = line
#     #     self.type = modifier_type
#     #
#     #     for bonus in bonuses:
#     #         bonus_name, value = bonus.split()
#     #         self.bonuses[bonus_name] = int(value)
#
#
# class EquipmentItem(Item):
#
#     def __init__(self):
#         Item.__init__(self)
#         self.modifications = {}
#         self.addons = {}
#         self.traits = {}
#         self.available_modifications = []
#
#
# class Armor(EquipmentItem):
#
#     def __init__(self):
#         EquipmentItem.__init__(self)
#         self.armor = {}
#         # for armor_param in armor_names:
#         #     self.armor[armor_param] = 0
#         self.type = "armor"
#
#
# class Weapon(EquipmentItem):
#
#     def __init__(self):
#         EquipmentItem.__init__(self)
#         self.type = ""
#         self.damage = 0
#         self.damage_type = ""
#         self.ap = 0
#         self.base_skill = None
#         self.hands = 0
#         self.weapon_type = ""
#         self.type = "weapon"
#
#
# class RangedWeapon(Weapon):
#
#     def __init__(self):
#         Weapon.__init__(self)
#         self.power_magazine = 0
#         self.max_magazine = 0
#         self.shot_cost = 0
#         self.can_shoot = True
#         self.fire_modes = []
#
#     def update(self):
#         if self.power_magazine < self.shot_cost:
#             self.can_shoot = False
#             return
#         self.can_shoot = True
#
#     def shoot(self):
#         if not self.can_shoot:
#             return
#         self.power_magazine -= self.shot_cost
#         self.update()
#
#     def load_from_line(self, line):
#         name, availability, value, damage, damage_type, ap, max_clip, energy_per_shot, \
#         fire_mode, traits, mods, skill, hands, weight, weapon_type, item_type = line.strip().strip().split(";")
#         self.arch_name = name
#         # self.type = "weapon"
#         self.name = translate(name)
#         self.availability = availability
#         self.price = 0 if not value else int(value)
#         self.weight = 0 if not weight else int(weight)
#         self.damage = damage
#         self.damage_type = damage_type
#         self.ap = ap
#         self.max_magazine = max_clip
#         self.shot_cost = energy_per_shot
#         self.fire_modes = fire_mode.split(",")
#         self.traits = traits.split(",")
#         self.mods = mods.split(",")
#         self.base_skill = skill
#         self.hands = hands
#         self.weapon_type = weapon_type
#         self._line = line
#
#
# def weapon_from_line(line):
#     weapon = Weapon()
#     weapon.load_from_line(line)
#     return weapon
#
#
# def modifier_from_line(line):
#     item = ModifierItem()
#     item.load_from_line(line)
#     return item
#
#
# def armor_from_line(line):
#     armor = Armor()
#     armor.load_from_line(line)
#     return armor





# def get_children()


