import string
import random


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
