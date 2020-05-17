import string
import random
from parameters import load_parameters, translate_item

param_dict = load_parameters()
armor_names = param_dict["armor"]


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class Item:

    def __init__(self):
        self.name = None
        self.price = 0
        self.weight = 0
        self.tooltip = None
        self.description = None
        self.availability = None
        self.total_quantity = 0
        self.equipped_quantity = 0
        self.ID = random_word(16)
        self.arch_name = None


class ModifierItem(Item):

    def __init__(self):
        Item.__init__(self)
        self.equipped = False
        self.bonuses = {}
        self.bonus_type = None
        self._line = None

    def load_from_line(self, line):
        name, availability, value, weight, bonuses, bonus_type = line.strip().split(";")
        bonuses = bonuses.split(",")
        self.arch_name = name
        self.name = translate_item(name)
        self.availability = availability
        self.price = int(value)
        self.weight = int(weight)
        self.bonus_type = bonus_type
        self._line = line

        for bonus in bonuses:
            bonus_name, value = bonus.split()
            self.bonuses[bonus_name] = int(value)


class Armor(Item):

    def __init__(self):
        Item.__init__(self)
        self.armor = {}
        for armor_param in armor_names:
            self.armor[armor_param] = 0
        self.modifications = {}
        self.addons = {}
        self.traits = {}
        self.equipped = False
        self._line = None

    def load_from_line(self, line):
        name, availability, value, armor, weight, other, traits = line.strip().split(";")
        self.arch_name = name
        self.name = translate_item(name)
        self.availability = availability
        self.price = value
        self.traits = traits.split(",")
        self.weight = weight
        self._line = line
        for part in armor.split(","):
            part, value = part.split()
            self.armor[part] = int(value)


class Weapon(Item):

    def __init__(self):
        Item.__init__(self)
        self.modifications = []
        self.addons = []
        self.traits = []
        self.type = None
        self.damage = 0
        self.damage_type = None
        self.ap = 0
        self.power_magazine = 0
        self.max_magazine = 0
        self.shot_cost = 0
        self.equipped = False
        self.can_shoot = True
        self.fire_modes = []
        self.base_skill = None
        self.hands = 0
        self._line = None
        self.weapon_type = None

    def update(self):
        if self.power_magazine < self.shot_cost:
            self.can_shoot = False
            return
        self.can_shoot = True

    def shoot(self):
        if not self.can_shoot:
            return
        self.power_magazine -= self.shot_cost
        self.update()

    def load_from_line(self, line):
        name, availability, value, damage, damage_type, ap, max_clip, energy_per_shot, \
        fire_mode, traits, mods, skill, hands, weight, weapon_type = line.strip().strip().split(";")
        self.arch_name = name
        self.name = translate_item(name)
        self.availability = availability
        self.price = value
        self.damage = damage
        self.damage_type = damage_type
        self.ap = ap
        self.max_magazine = max_clip
        self.shot_cost = energy_per_shot
        self.fire_modes = fire_mode.split(",")
        self.traits = traits.split(",")
        self.mods = mods.split(",")
        self.base_skill = skill
        self.hands = hands
        self.weight = weight
        self.weapon_type = weapon_type
        self._line = line


def weapon_from_line(line):
    weapon = Weapon()
    weapon.load_from_line(line)
    return weapon


def modifier_from_line(line):
    item = ModifierItem()
    item.load_from_line(line)
    return item


def armor_from_line(line):
    armor = Armor()
    armor.load_from_line(line)
    return armor

