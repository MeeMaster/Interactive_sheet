class Item:

    def __init__(self):
        self.name = None
        self.price = None
        self.weight = None
        self.tooltip = None
        self.description = None


class Armor(Item):

    def __init__(self):
        Item.__init__(self)
        self.chest = 0
        self.head = 0
        self.lh = 0
        self.rh = 0
        self.ll = 0
        self.rl = 0
        self.modifications = {}
        self.addons = {}
        self.traits = {}
        self.equipped = False

    # def calculate_armor_values(self):
    #     for mod_name in self.modifications:
    #         mod = self.modifications[mod_name]


class Weapon(Item):

    def __init__(self):
        Item.__init__(self)
        self.modifications = {}
        self.addons = {}
        self.traits = {}
        self.type = None
        self.damage = None
        self.damage_type = None
        self.ap = 0
        self.power_magazine = 0
        self.gas_storage = 0
        self.shot_cost = 0
        self.uses_gas = True
        self.equipped = False
        self.can_shoot = True

    def update(self):
        if self.power_magazine < self.shot_cost:
            self.can_shoot = False
            return
        if self.uses_gas and self.gas_storage < self.shot_cost:
            self.can_shoot = False
            return
        self.can_shoot = True

    def shoot(self):
        if not self.can_shoot:
            return
        if self.uses_gas:
            self.gas_storage -= self.shot_cost
        self.power_magazine -= self.shot_cost
        self.update()

