from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QTextEdit, QScrollArea, QTableWidget, QCheckBox, QComboBox, QRadioButton, QTreeWidget, \
    QTreeWidgetItem, QGridLayout, QListWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from parameters import (load_parameters, translate, read_all_objects, get_children,
                        get_all_children, get_all_data, get_objects_of_type, create_item, get_object_data, is_leaf)
from item_classes import BaseObject
from layout_classes import InputLine, LabelledComboBox, View, ScrollContainer, AbilityView, LabelledTextEdit

param_dict = load_parameters()
# damage_types = param_dict["damage"]
# armor_names = param_dict["armor"]


class BasePopup(QWidget):
    popup_cancel = pyqtSignal(bool)
    popup_ok = pyqtSignal(BaseObject)

    def __init__(self):
        QWidget.__init__(self)
        self._layout = QVBoxLayout()
        self.main_layout = QVBoxLayout()
        self._layout.addLayout(self.main_layout)
        self.button_layout = QHBoxLayout()
        self._layout.addLayout(self.button_layout)
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton(translate("ui_cancel"))
        self.ok_button.clicked.connect(self.ok_pressed)
        self.cancel_button.clicked.connect(self.cancel_pressed)
        self.button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)
        self.setLayout(self._layout)
        self.setWindowModality(Qt.ApplicationModal)
        # self.show()

    def cancel_pressed(self):
        self.popup_cancel.emit(True)
        self.close()

    def ok_pressed(self):
        self.popup_ok.emit(None)
        self.close()


class AbilityPopup(BasePopup):

    def __init__(self, kwargs):
        BasePopup.__init__(self)
        self.abilities = get_objects_of_type("ability")

        for name, data in self.abilities.items():
            self.abilities[name] = create_item(data)
        self.translate_abilities()
        self.validator = kwargs["validator"]
        self.override_checkbox = QCheckBox("override_disabled")
        self.override_checkbox.stateChanged.connect(self.update_button)
        self.button_layout.insertWidget(0, self.override_checkbox)

        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setFixedWidth(750)
        scroll.setFixedHeight(800)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        self.main_layout.addLayout(layout)
        self.selected_ability = None
        self.setWindowTitle(translate("ui_ability_add_button"))
        self.ability_layout = QVBoxLayout()
        scroll_widget.setLayout(self.ability_layout)
        self.ability_is_valid = False
        self.current_row = None
        self.current_column = None
        self.current_table = None
        self.build_table()
        self.update_button()
        self.show()

    def build_table(self):
        abilities_tier1 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name].tier == 1]
        abilities_tier2 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name].tier == 2]
        abilities_tier3 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name].tier == 3]
        for index, ability_subset in enumerate([abilities_tier1, abilities_tier2, abilities_tier3]):
            label = QLabel("Tier{}".format(index + 1))
            label.setStyleSheet("font: bold 16px;")
            self.ability_layout.addWidget(label)
            table = self.get_table(ability_subset, index)
            self.fill_table(ability_subset, table)
            table.resizeColumnsToContents()
            table.resizeRowsToContents()
            self.ability_layout.addWidget(table)
            width, height = get_true_table_size(table)
            table.setFixedWidth(width)
            table.setFixedHeight(height)

    def fill_table(self, ability_subset, table):
        for row, ability in enumerate(ability_subset):
            row_enabled = True
            already_bought = False
            ability_status = self.validator(self.abilities[ability])
            if ability_status[0]:
                already_bought = True
                row_enabled = False
            if sum(ability_status[1]) < 0:
                row_enabled = False
            for column, parameter in enumerate(["name", "display", "requirements", "description", "tier"]):
                value = self.abilities[ability].__dict__[parameter]
                if column == 2:
                    item = TableRequirementItem(value, ability_status[1])
                    table.setCellWidget(row, column, item)
                elif column == 3:
                    item = TableDescriptionItem(value, 400)
                    table.setCellWidget(row, column, item)
                else:
                    item = TableDescriptionItem(value, 150)
                    table.setCellWidget(row, column, item)
            if not row_enabled:
                for column in range(5):
                    child = table.cellWidget(row, column)
                    p = child.palette()
                    p.setColor(child.backgroundRole(), QColor(0, 0, 0, 50)
                               if not already_bought else QColor(0, 100, 0, 50))
                    child.setPalette(p)
                    child.setAutoFillBackground(True)

    def get_table(self, ability_subset, index):
        table = MyTableWidget(index)
        table.setRowCount(len(ability_subset))
        table.setColumnCount(5)
        table.setSelectionBehavior(1)
        table.setHorizontalScrollBarPolicy(1)
        table.setVerticalScrollBarPolicy(1)
        table.setColumnHidden(0, True)
        table.setColumnHidden(4, True)
        table.verticalHeader().setVisible(False)
        table.klik.connect(self.selected)
        table.currentCellChanged.connect(self.cell_changed)
        table.setHorizontalHeaderLabels([translate("ui_ability_name"), translate("ui_ability_display_name"),
                                         translate("ui_ability_requirements"), translate("ui_ability_description"),
                                         translate("ui_ability_tier")])
        return table

    def translate_abilities(self, locale="PL"):
        for name, ability in self.abilities.items():
            ability.display = translate(name)
            ability.description = translate(ability.description, locale=locale)

    def cell_changed(self, current_row, current_column, last_row, last_column):
        self.current_column = current_column
        self.current_row = current_row

    def ok_pressed(self):
        self.popup_ok.emit(self.selected_ability)
        self.close()

    def selected(self, index):
        counter = 0
        self.current_table = index
        for n in range(self.ability_layout.count()):
            item = self.ability_layout.itemAt(n).widget()
            if isinstance(item, QLabel):
                continue
            if counter == index:
                self.selected_ability = self.abilities[item.cellWidget(self.current_row, 0).text()]
                ability_status = self.validator(self.selected_ability)
                self.ability_is_valid = not ability_status[0] and sum(ability_status[1]) == 0
                self.update_button()
            if counter != index:
                item.clearSelection()
            counter += 1

    def update_button(self):
        self.ok_button.setEnabled(self.selected_ability is not None and
                                  (self.ability_is_valid + self.override_checkbox.isChecked()))


class MyTableWidget(QTableWidget):
    klik = pyqtSignal(int)

    def __init__(self, index):
        QTableWidget.__init__(self)
        self.index = index
        self.clicked.connect(lambda: self.klik.emit(self.index))


def get_true_table_size(table_widget: QTableWidget):
    width = 4
    height = table_widget.horizontalHeader().height()
    for column_index in range(table_widget.columnCount()):
        width += table_widget.columnWidth(column_index)
    for row_index in range(table_widget.rowCount()):
        height += table_widget.rowHeight(row_index)
    return width, height


class TableRequirementItem(QWidget):

    def __init__(self, data, status):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        for index, n in enumerate(data):
            if data[n] is True:
                if not n:
                    continue
                label = QLabel(translate(n)[0])
            else:
                label = QLabel("{} {}".format(translate(n), data[n]))
            label.setStyleSheet("color: green") if status[index] == 0 else label.setStyleSheet("color: red")
            layout.addWidget(label)
        self.setLayout(layout)


class TableDescriptionItem(QLabel):

    def __init__(self, data, width):
        QLabel.__init__(self)
        self.setWordWrap(True)
        self.setFixedWidth(width)
        self.setText(str(data))
        self.setContentsMargins(2, 2, 2, 2)


# class WeaponPopup(BasePopup):
#     popup_ok = pyqtSignal(Weapon)
#
#     def __init__(self, kwargs):
#         BasePopup.__init__(self)
#         self.edit = None
#         if "edit" in kwargs:
#             self.edit = kwargs["edit"]
#         self.archetype_weapons = load_weapons()
#         self.current_weapon = None
#         combo_layout = QHBoxLayout()
#         self.archetype_combobox = LabelledComboBox(label=translate("ui_item_archetype"))
#         self.archetype_names = []
#         self.fill_archetype_combobox()
#         if self.edit is not None:
#             self.archetype_combobox.setCurrentIndex(self.archetype_names.index(self.edit.arch_name))
#             self.archetype_combobox.setEnabled(False)
#         self.archetype_combobox.currentIndexChanged.connect(self.fill_parameters)
#         self.weapon_name = InputLine("weapon_name", Qt.AlignLeft, label=translate("ui_item_name"))
#         combo_layout.addWidget(self.archetype_combobox)
#         combo_layout.addWidget(self.weapon_name)
#
#         damage_layout = QHBoxLayout()
#         self.damage_value = InputLine("weapon_damage", Qt.AlignLeft, dtype="int", label=translate("ui_weapon_damage"))
#         self.ap_value = InputLine("weapon_ap", Qt.AlignLeft, dtype="int", label=translate("ui_weapon_ap"))
#         self.damage_type = LabelledComboBox(label=translate("ui_weapon_damage_type"))
#         for damage_type in damage_types:
#             self.damage_type.addItem(damage_type)
#         damage_layout.addWidget(self.damage_value)
#         damage_layout.addWidget(self.damage_type)
#         damage_layout.addWidget(self.ap_value)
#
#         shot_layout = QHBoxLayout()
#         self.max_energy = InputLine("weapon_max_energy", Qt.AlignLeft,
#                                     dtype="int", label=translate("ui_weapon_max_magazine"))
#         self.energy_per_shot = InputLine("weapon_shot_cost", Qt.AlignLeft,
#                                          dtype="int", label=translate("ui_weapon_shotcost"))
#         self.shot_type = InputLine("weapon_mode", Qt.AlignLeft, label=translate("ui_weapon_fire_mode"))
#         shot_layout.addWidget(self.max_energy)
#         shot_layout.addWidget(self.energy_per_shot)
#         shot_layout.addWidget(self.shot_type)
#
#         self.main_layout.addLayout(combo_layout)
#         self.main_layout.addLayout(damage_layout)
#         self.main_layout.addLayout(shot_layout)
#         self.fill_parameters()
#         self.show()
#
#     def fill_archetype_combobox(self):
#         for weapon in self.archetype_weapons:
#             self.archetype_combobox.addItem(translate(weapon))
#             self.archetype_names.append(weapon)
#         self.archetype_names.append("weapon_other")
#         self.archetype_combobox.addItem(translate("weapon_other"))
#
#     def fill_parameters(self, index=None):
#         if self.edit is None:
#             index = self.archetype_combobox.currentIndex()
#             weapon_name = self.archetype_names[index]
#             weapon = Weapon()
#             if weapon_name in self.archetype_weapons:
#                 weapon_line = self.archetype_weapons[weapon_name]._line
#                 weapon.load_from_line(weapon_line)
#         else:
#             weapon = self.edit
#             weapon_name = weapon.name
#         self.weapon_name.setText(translate(weapon_name))
#         if weapon_name == "weapon_other" and self.edit is None:
#             self.current_weapon = weapon
#             return
#         self.damage_value.setText(str(weapon.damage))
#         self.ap_value.setText(str(weapon.ap))
#         self.damage_type.setCurrentIndex(damage_types.index(weapon.damage_type))
#         self.max_energy.setText(str(weapon.max_magazine))
#         self.energy_per_shot.setText(str(weapon.shot_cost))
#         self.shot_type.setText("/".join(weapon.fire_modes))
#         self.current_weapon = weapon
#
#     def ok_pressed(self):
#         self.current_weapon.name = self.weapon_name.text()
#         self.current_weapon.damage = int(self.damage_value.text())
#         self.current_weapon.ap = int(self.ap_value.text())
#         self.current_weapon.damage_type = self.damage_type.currentText()
#         self.current_weapon.max_magazine = int(self.max_energy.text())
#         self.current_weapon.shot_cost = int(self.energy_per_shot.text())
#         self.current_weapon.fire_modes = self.shot_type.text().split("/")
#         self.popup_ok.emit(self.current_weapon)
#         self.close()


# class ArmorPopup(BasePopup):
#     popup_ok = pyqtSignal(Armor)
#
#     def __init__(self, kwargs):
#         BasePopup.__init__(self)
#         if "edit" in kwargs:
#             self.edit = kwargs["edit"]
#         self.archetype_armor = load_armors()
#         self.current_armor = None
#         combo_layout = QHBoxLayout()
#         self.archetype_combobox = LabelledComboBox(label=translate("ui_item_archetype"))
#         self.archetype_names = []
#         self.fill_archetype_combobox()
#         if self.edit is not None:
#             self.archetype_combobox.setCurrentIndex(self.archetype_names.index(self.edit.arch_name))
#             self.archetype_combobox.setEnabled(False)
#         self.archetype_combobox.currentIndexChanged.connect(self.fill_parameters)
#         self.armor_name = InputLine("armor_name", Qt.AlignLeft, label=translate("ui_item_name"))
#         combo_layout.addWidget(self.archetype_combobox)
#         combo_layout.addWidget(self.armor_name)
#
#         armor_layout = QHBoxLayout()
#         self.armors = {}
#         for armor in armor_names:
#             armor_widget = InputLine(armor, Qt.AlignLeft, dtype="int",
#                                      label=translate(armor))
#             self.armors[armor] = armor_widget
#             armor_layout.addWidget(armor_widget)
#
#         self.main_layout.addLayout(combo_layout)
#         self.main_layout.addLayout(armor_layout)
#         self.fill_parameters()
#         self.show()
#
#     def fill_archetype_combobox(self):
#         for armor in self.archetype_armor:
#             self.archetype_combobox.addItem(translate(armor))
#             self.archetype_names.append(armor)
#         self.archetype_names.append("armor_other")
#         self.archetype_combobox.addItem(translate("armor_other"))
#
#     def fill_parameters(self, index=None):
#         if self.edit is None:
#             index = self.archetype_combobox.currentIndex()
#             armor_name = self.archetype_names[index]
#             armor = Armor()
#             if armor_name in self.archetype_armor:
#                 armor_line = self.archetype_armor[armor_name]._line
#                 armor.load_from_line(armor_line)
#         else:
#             armor = self.edit
#             armor_name = armor.name
#         self.current_armor = armor
#         self.armor_name.setText(translate(armor_name))
#         if armor_name == "armor_other":
#             for armor_name in armor_names:
#                 self.armors[armor_name].setText(armor.armor[armor_name])
#             return
#         for armor_type in armor_names:
#             self.armors[armor_type].setText(armor.armor[armor_type])
#
#     def ok_pressed(self):
#         self.current_armor.name = self.armor_name.text()
#         for armor_type in armor_names:
#             self.current_armor.armor[armor_type] = int(self.armors[armor_type].text())
#         self.popup_ok.emit(self.current_armor)
#         self.close()


class ItemPopup(BasePopup):
    popup_ok = pyqtSignal(BaseObject)

    def __init__(self, **kwargs):
        BasePopup.__init__(self)
        layout = QVBoxLayout()
        line1 = QHBoxLayout()
        line2 = QVBoxLayout()
        layout.addLayout(line1)
        layout.addLayout(line2)
        self.edit = None
        if "edit" in kwargs:
            self.edit = kwargs["edit"]
        self.quantity = InputLine("quantity", dtype="int", label=translate("ui_item_quantity"))
        self.name = InputLine("name", dtype="str", label=translate("ui_item_name"))
        self.weight = InputLine("weight", dtype="float", label=translate("ui_item_weight"))
        line1.addWidget(self.quantity, 1)
        line1.addWidget(self.name, 4)
        line1.addWidget(self.weight, 1)
        label = QLabel(translate("ui_item_description"))
        self.description = QTextEdit()
        line2.addWidget(label)
        line2.addWidget(self.description)
        if self.edit is None:
            self.item = BaseObject()
            self.quantity.setText("1")
            self.weight.setText("0")
        else:
            self.item = self.edit
            self.quantity.setEnabled(False)
            self.name.setText(self.edit.name)
            self.weight.setText(self.edit.weight)
            self.description.setText(self.edit.description)
        self.main_layout.addLayout(layout)
        self.show()

    def ok_pressed(self):
        if not self.name.text().strip():
            return
        if self.edit is None:
            self.item.total_quantity = int(self.quantity.text())
            self.item.equipped_quantity = int(self.quantity.text())
        self.item.name = self.name.text()
        self.item.weight = float(self.weight.text())
        self.item.description = self.description.toPlainText()
        self.popup_ok.emit(self.item)
        # self.close()


class ItemMovePopup(BasePopup):
    popup_ok = pyqtSignal(BaseObject, int)

    def __init__(self, item, equipped=False):
        BasePopup.__init__(self)
        layout = QVBoxLayout()
        self.item = item
        self.equipped = equipped
        label_layout = QVBoxLayout()
        label = QLabel("{}: {}".format(translate("ui_item_transfer_dialog"), item.name))
        label_layout.addWidget(label)
        layout.addLayout(label_layout)

        values_layout = QHBoxLayout()
        self.equipment_value = InputLine("max", dtype="int", enabled=False, label=translate("ui_items_in_inventory"))
        value = item.equipped_quantity if equipped else item.total_quantity - item.equipped_quantity
        self.equipment_value.setText(value)
        self.transfer_value = InputLine("transfer", dtype="int", min_val=0, max_val=value,
                                        label=translate("ui_items_to_transfer"))
        self.transfer_value.setText(value)
        values_layout.addWidget(self.transfer_value)
        values_layout.addWidget(self.equipment_value)

        layout.addLayout(values_layout)
        self.main_layout.addLayout(layout)
        self.show()

    def ok_pressed(self):
        value = int(self.transfer_value.text())
        self.popup_ok.emit(self.item, -value if self.equipped else value)
        self.close()


class CreateCharacterPopup(BasePopup):
    popup_ok = pyqtSignal(bool)

    def __init__(self):
        BasePopup.__init__(self)
        self.alternative = False
        choice_layout = QHBoxLayout()
        normal_button = QRadioButton(translate("ui_normal_character"))
        normal_button.setChecked(True)
        alternative_button = QRadioButton(translate("ui_alternative_character"))
        normal_button.clicked.connect(lambda: self.change_selection(False))
        alternative_button.clicked.connect(lambda: self.change_selection(True))
        choice_layout.addWidget(normal_button)
        choice_layout.addWidget(alternative_button)
        self.main_layout.addLayout(choice_layout)
        self.show()

    def change_selection(self, alternative):
        self.alternative = alternative

    def ok_pressed(self):
        self.popup_ok.emit(self.alternative)
        self.close()


# class ModifierItemPopup(BasePopup):
#     popup_ok = pyqtSignal(ModifierItem)
#
#     def __init__(self, kwargs):
#         BasePopup.__init__(self)
#         self.alternative = kwargs["alternative"]
#         self.edit = None
#         if "edit" in kwargs:
#             self.edit = kwargs["edit"]
#         self.include = []
#         if "include" in kwargs:
#             self.include = kwargs["include"]
#         self.archetype_items = load_modifiers(self.alternative)
#         if self.include:
#             for item in list(self.archetype_items.keys()):
#                 if self.archetype_items[item].type not in self.include:
#                     del self.archetype_items[item]
#         self.current_item = None
#         combo_layout = QHBoxLayout()
#         self.archetype_combobox = LabelledComboBox(label=translate("ui_item_archetype"))
#         self.archetype_combobox.setEnabled(self.edit is None)
#         self.archetype_names = []
#         if self.edit is None:
#             self.fill_archetype_combobox()
#         self.archetype_combobox.currentIndexChanged.connect(self.fill_parameters)
#         self.item_name = InputLine("item_name", Qt.AlignLeft, label=translate("ui_item_name"))
#         self.item_name.value_changed.connect(self.update_parameters)
#         combo_layout.addWidget(self.archetype_combobox)
#         combo_layout.addWidget(self.item_name)
#         self.bonuses_layout = QVBoxLayout()
#
#         add_button_layout = QVBoxLayout()
#         add_button = QPushButton(translate("ui_add_property"))
#         add_button.clicked.connect(self.add_property)
#         add_button_layout.addWidget(add_button)
#
#         self.main_layout.addLayout(combo_layout)
#         self.main_layout.addLayout(self.bonuses_layout)
#         self.main_layout.addLayout(add_button_layout)
#         self.fill_parameters()
#         self.show()
#
#     def fill_archetype_combobox(self):
#         for item in self.archetype_items:
#             self.archetype_combobox.addItem(translate(item))
#             self.archetype_names.append(item)
#         self.archetype_names.append("item_other")
#         self.archetype_combobox.addItem(translate("item_other"))
#
#     def fill_parameters(self):
#         if self.edit is None:
#             index = self.archetype_combobox.currentIndex()
#             item_name = self.archetype_names[index]
#             self.item_name.setText(translate(item_name))
#             item = ModifierItem()
#             self.current_item = item
#             self.remove_property("all")
#             if item_name == "item_other":
#                 return
#             item_line = self.archetype_items[item_name]._line
#             item.load_from_line(item_line)
#         else:
#             item = self.edit
#             self.item_name.setText(item.name)
#         self.current_item = item
#         self.remove_property("all")
#         for property in item.bonuses:
#             self.add_property(property=property, value=item.bonuses[property])
#
#     def update_parameters(self, parameter, value):
#         if parameter == "item_name":
#             self.current_item.name = value
#         if parameter in self.current_item.bonuses:
#             self.current_item.bonuses[parameter] = int(value)
#
#     def add_property(self, fixed=False, property=None, value=0):
#         view = ModifierView(self.alternative, not fixed)
#         view.set_property(property, value)
#         self.bonuses_layout.addWidget(view)
#         view.delete.connect(self.remove_property)
#
#     def remove_property(self, prop_id):
#         for index in reversed(range(self.bonuses_layout.count())):
#             child = self.bonuses_layout.itemAt(index)
#             if child is None:
#                 continue
#             widget = child.widget()
#             if widget is None:
#                 continue
#             if not isinstance(widget, ModifierView):
#                 continue
#             if prop_id != "all" and widget.name != prop_id:
#                 continue
#             widget.setParent(None)
#             widget.deleteLater()
#
#     def sum_up_item(self):
#         self.current_item.bonuses = {}
#         for index in reversed(range(self.bonuses_layout.count())):
#             child = self.bonuses_layout.itemAt(index)
#             if child is None:
#                 continue
#             widget = child.widget()
#             if widget is None:
#                 continue
#             if not isinstance(widget, ModifierView):
#                 continue
#             prop_name = widget.param_names[widget.param_combo.currentIndex()]
#             if not widget.value.text():
#                 continue
#             value = int(widget.value.text())
#             if prop_name not in self.current_item.bonuses:
#                 self.current_item.bonuses[prop_name] = value
#                 continue
#             if value > self.current_item.bonuses[prop_name]:
#                 self.current_item.bonuses[prop_name] = value
#                 continue
#
#     def ok_pressed(self):
#         self.sum_up_item()
#         self.popup_ok.emit(self.current_item)
#         self.close()


class ModifierView(View):

    def __init__(self, alternative=False, enabled=True):
        View.__init__(self)
        self.alternative = alternative
        self.name = random_word(5)
        layout = QHBoxLayout()
        self.param_combo = QComboBox()
        self.param_names = []
        self.param_combo.setEnabled(enabled)
        self.value = InputLine("value", dtype="int", maxwidth=60)
        self.cost = InputLine("cost", dtype="int", maxwidth=60)
        layout.addWidget(self.param_combo)
        layout.addWidget(self.value)
        if alternative:
            layout.addWidget(self.cost)
        self.fill_combobox()
        self.setLayout(layout)

    def fill_combobox(self):
        mods = self.load_modifiable_parameters()
        self.param_names = mods
        self.param_combo.addItems([translate(mod) for mod in mods])

    def set_property(self, prop, value):
        if prop not in self.param_names:
            return
        index = self.param_names.index(prop)
        self.param_combo.setCurrentIndex(index)
        self.value.setText(value)

    def load_modifiable_parameters(self):
        params = load_parameters(self.alternative)
        mods = []
        for n in params:
            if n not in ["attrib", "skill"]:
                continue
            mods.extend(params[n])
        return mods


class ItemListPopup(BasePopup):

    def __init__(self, kwargs=None):
        BasePopup.__init__(self)
        inner_layout = QHBoxLayout()
        self.full_data_dict = {}
        self.inheritance_dict = {}
        self.read_all_items()
        button = QPushButton(translate("ui_add_item"))
        button.clicked.connect(self.add_item_field)
        self.button_layout.insertWidget(1, button)
        self.item_types = kwargs["include"]
        self.main_layout.addLayout(inner_layout)
        self.tree_view = QTreeWidget()
        self.tree_view.setColumnCount(1)
        self.tree_view.setHeaderLabels([translate("ui_item_name")])
        self.tree_view.setMinimumWidth(200)
        inner_layout.addWidget(self.tree_view, 1)
        self.grid_widget = MyGridWidget()
        self.grid_widget.multiselect_updated.connect(self.update_current_item_data)
        inner_layout.addWidget(self.grid_widget, 2)
        self.tree_view.itemClicked.connect(self.get_item)
        self.current_item_data = {}
        # self.full_dict = {}
        self.update_tree()
        self.show()

    def read_all_items(self):
        read_all_objects(False)
        self.inheritance_dict = dict(get_all_data())
        read_all_objects(True)
        self.full_data_dict = dict(get_all_data())

    def add_item_field(self):
        new_name = "new_item"
        index = 0
        while new_name in self.full_data_dict:
            index += 1
            new_name = "new_item_{}".format(index)
        self.full_data_dict[new_name] = dict(self.current_item_data)
        self.inheritance_dict[new_name] = {"name": new_name, }
        self.full_data_dict[new_name]["parent"] = self.current_item_data["name"]
        self.inheritance_dict[new_name]["parent"] = self.current_item_data["name"]
        self.full_data_dict[new_name]["name"] = new_name
        widget = MyTreeWidgetItem(self.tree_view.currentItem())
        widget.set_text(new_name)

    def update_object_fields(self, new_name):
        for field_name, field in self.grid_widget.fields.items():
            if field_name == "name" or field_name == "parent":
                continue
            values = field.get_data()
            self.full_data_dict[new_name][field_name] = values
            for child in get_all_children(new_name, self.full_data_dict):
                if field_name not in self.inheritance_dict[child]:
                    self.full_data_dict[child][field_name] = values

    def update_inheritance(self):
        name = self.current_item_data["name"]
        new_name = self.grid_widget.fields["name"].get_data()

        if new_name != name:
            self.full_data_dict[new_name] = self.full_data_dict[name]
            self.inheritance_dict[new_name] = self.inheritance_dict[name]
            self.full_data_dict[new_name]["name"] = new_name
            self.inheritance_dict[new_name]["name"] = new_name
            del self.full_data_dict[name]
            del self.inheritance_dict[name]
            for child in get_children(name, self.full_data_dict):
                self.full_data_dict[child]["parent"] = new_name
                self.inheritance_dict[child]["parent"] = new_name
            self.tree_view.currentItem().set_text(new_name)
        return new_name

    def update_tree(self, other_dict=None):
        self.tree_view.clear()
        objects_list = []
        for item_type in self.item_types:
            objects = get_all_children(item_type, self.full_data_dict)
            objects_list.extend(objects)
        for item in list(self.full_data_dict.keys()):
            if item not in objects_list:
                del self.full_data_dict[item]

        def get_tree_objects(parent, child):
            widget = MyTreeWidgetItem(parent)
            widget.set_text(child)
            children = get_children(child)
            for child in children:
                get_tree_objects(widget, child)

        for item_type in self.item_types:
            for item in get_children(item_type, other_dict):
                get_tree_objects(self.tree_view, item)

    def get_item(self, item, column):
        self.get_data(item, self.full_data_dict)
        self.ok_button.setEnabled(True)
        if not is_leaf(self.current_item_data["name"], self.full_data_dict):
            self.ok_button.setEnabled(False)
        self.update_grid()

    def get_data(self, item, other_dict=None):
        full_data = get_object_data(item.name, other_dict=other_dict)
        for key, values in full_data.items():
            if isinstance(values, list):
                for index, item in reversed(list(enumerate(values))):
                    if not isinstance(item, str):
                        continue
                    item_data = get_object_data(item)
                    item = create_item(item_data)
                    full_data[key][index] = item
        self.current_item_data = full_data

    def update_grid(self):
        self.grid_widget.clear()
        self.grid_widget.fill_grid(self.current_item_data)

    def update_current_item_data(self, name, created, item):
        item_name = item.name
        if created:
            if isinstance(self.current_item_data[name], list):
                for curr_item in self.current_item_data[name]:
                    if curr_item.name == item_name:
                        return
                self.current_item_data[name].append(item)
            else:
                self.current_item_data[name] = item
        else:
            found = False
            for curr_item in self.current_item_data[name]:
                if curr_item.name == item_name:
                    found = True
                    break
            if found:
                self.current_item_data[name].remove(curr_item)
        self.update_grid()

    def ok_pressed(self):
        new_name = self.update_inheritance()
        # Change other fields
        self.update_object_fields(new_name)

        final_item = BaseObject()
        for name, widget in self.grid_widget.fields.items():
            final_item.__dict__[name] = widget.get_data()
        self.popup_ok.emit(final_item)


class MyTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, parent):
        QTreeWidgetItem.__init__(self, parent)
        self.name = None

    def set_text(self, text):
        self.name = text
        self.setText(0, translate(text))


class MyGridWidget(QWidget):
    multiselect_updated = pyqtSignal(str, bool, BaseObject)

    def __init__(self):
        QWidget.__init__(self)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.fields = {}

    def fill_grid(self, data: dict):
        self.clear()
        self.fields = {}
        index = 0
        num_columns = 4
        immutables = ["type", "base_skill", "parent", "weapon_type"]
        combos = ["damage_type", "hands"]
        lines = ["name"]
        texts = ["display", "tooltip", "description"]
        ints = ["price", "ap", "damage", "max_magazine", "power_magazine", "shot_cost", "availability", "armor_head",
                "armor_rh", "armor_chest", "armor_lh", "armor_rl", "armor_ll", "weight"]
        multiselects = ["available_addon", "addon", "bonuses", "available_modification", "modification",
                        "trait", "fire_mode"]
        row = 0
        for key in immutables:
            if key not in data:
                continue
            field = InputLine(key, label=translate(key))
            field.setEnabled(False)
            value = data[key]
            field.setText(value)
            field.format_label(8, True)

            self.fields[key] = field
            self.grid_layout.addWidget(field, index // num_columns + row, index % num_columns)
            index += 1

        row = index // num_columns + row + 1
        index = 0
        key = "name"
        field = InputLine(key, label=translate("param_" + key))
        field.format_label(8, True)
        field.setText(data[key])
        self.fields[key] = field
        self.grid_layout.addWidget(field, index // num_columns + row, index % num_columns)
        index = 1
        for key in ints:
            if key not in data:
                continue
            field = InputLine(key, label=translate("param_"+key), dtype="int" if key != "weight" else "float")
            value = data[key]
            field.setText(value)
            field.format_label(8, True)
            self.fields[key] = field
            self.grid_layout.addWidget(field, index // num_columns + row, index % num_columns)
            index += 1

        row = index // num_columns + row + 1
        index = 0
        for key in combos:
            if key not in data:
                continue
            field = InputLine(key, label=translate("param_"+key))
            value = data[key]
            if isinstance(value, list):
                if value:
                    value = value[0]
                else:
                    value = ""
            field.setText(value)
            field.format_label(8, True)
            self.fields[key] = field
            self.grid_layout.addWidget(field, index // num_columns + row, index % num_columns)
            index += 1

        row = index // num_columns + row + 1
        index = 0
        for key in texts:
            if key not in data:
                continue
            field = LabelledTextEdit(key, label=key)
            value = data[key]
            field.set_text(translate(value))
            field.format_label(8)
            self.fields[key] = field
            self.grid_layout.addWidget(field, index // num_columns + row, index % num_columns)
            index += 1

        row = index // num_columns + row + 1
        index = 0
        for key in multiselects:
            if key not in data:
                continue
            includes = None
            if key == "addon" or key == "modifier":
                includes = [obj.name for obj in data["available_"+key]]

            item_type = [key.replace("available_", "")]
            if key == "bonuses":
                item_type = ["ability", "skill", "attribute"]
            field = ScrollContainer(key,  "ui_add_item", AbilityView, label="ui_"+key,
                                    popup=ItemSelectPopup, item_type=item_type, include_only=includes)
            field.item_created.connect(lambda x, y: self.multiselect_updated.emit(x, True, y))
            field.item_removed.connect(lambda x, y: self.multiselect_updated.emit(x, False, y))
            field.fill(data[key])
            field.format_label(8)
            self.fields[key] = field
            self.grid_layout.addWidget(field, index // num_columns + row, index % num_columns)
            index += 1

    def clear(self):
        for child_index in reversed(range(self.grid_layout.count())):
            child = self.grid_layout.itemAt(child_index)
            if child is None:
                continue
            child = child.widget()
            if child is None:
                continue
            child.deleteLater()


class ItemSelectPopup(BasePopup):

    def __init__(self, kwargs):
        item_types = kwargs["item_type"]
        local_param_dict = load_parameters()
        alternative_params = load_parameters(True)
        for key in alternative_params:
            if key == "skill":
                for skill_name in alternative_params[key]:
                    if skill_name in local_param_dict[key]:
                        continue
                    local_param_dict[key][skill_name] = alternative_params[key][skill_name]
                continue
            for item in alternative_params[key]:
                if item not in local_param_dict[key]:
                    local_param_dict[key].append(item)
        self.include = None
        self.exclude = None
        if "include_only" in kwargs:
            self.include = kwargs["include_only"]
        if "exclude" in kwargs:
            self.include = kwargs["exclude"]
        BasePopup.__init__(self)
        self.items = {}
        layout = QHBoxLayout()
        self.value_input = QLineEdit()
        # self.item_list = QListWidget()
        self.item_list = QTreeWidget()
        layout.addWidget(self.item_list)
        layout.addWidget(self.value_input)
        self.main_layout.addLayout(layout)
        for item_type in item_types:

            par_widget = MyTreeWidgetItem(self.item_list)
            par_widget.set_text(item_type)
            if item_type == "skill":
                for skill_name in local_param_dict["skill"]:
                    child_widget = MyTreeWidgetItem(par_widget)
                    child_widget.set_text(skill_name)
                    self.items[skill_name] = 0
                continue
            if item_type == "attribute":
                for attrib_name in local_param_dict["attrib"]:
                    child_widget = MyTreeWidgetItem(par_widget)
                    child_widget.set_text(attrib_name)
                    self.items[attrib_name] = 0
                continue
            items = get_children(item_type)
            if self.include is not None:
                for name, data in list(items.items()):
                    if name not in self.include:
                        del items[name]
                        continue

            elif self.exclude is not None:
                for name, data in list(items.items()):
                    if name in self.exclude:
                        del items[name]
                        continue
            for name, data in items.items():
                self.items[name] = data
                child_widget = MyTreeWidgetItem(par_widget)
                child_widget.set_text(name)

        # self.items_names = []
        # for item in self.items:
        #     self.items_names.append(item)
        # self.item_list.addItems([translate(name) for name in self.items_names])
        self.item_list.currentItemChanged.connect(self.show_selection)
        self.main_layout.addWidget(self.item_list)
        self.show()

    def show_selection(self, current, previous):

        # current_index = self.item_list.currentIndex().row()
        # if current_index == -1:
        #     return
        item_name = self.item_list.currentItem().name
        if item_name not in self.items:
            return
        if isinstance(self.items[item_name], int):
            self.value_input.setText(str(self.items[item_name]))
            self.value_input.setVisible(True)
            return
        self.value_input.setVisible(False)

    def ok_pressed(self):
        item_name = item_name = self.item_list.currentItem().name
        if isinstance(self.items[item_name], int):
            value = int(self.value_input.text())
            if not value:
                return
            item = BaseObject()
            item.name = item_name
            item.value = value
        else:
            item = create_item(self.items[item_name])
        self.popup_ok.emit(item)




