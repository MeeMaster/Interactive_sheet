from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QTextEdit, QScrollArea, QTableWidget, QCheckBox, QComboBox, QRadioButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from parameters import (load_parameters, load_abilities, translate_parameter, translate_ui, translate_ability,
                        load_weapons, load_armors, translate_item, load_modifiers)
from item_classes import Weapon, Armor, Item, random_word, ModifierItem
from layout_classes import InputLine, LabelledComboBox, View

param_dict = load_parameters()
damage_types = param_dict["damage"]
armor_names = param_dict["armor"]


class BasePopup(QWidget):
    popup_cancel = pyqtSignal(bool)
    popup_ok = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        self._layout = QVBoxLayout()
        self.main_layout = QVBoxLayout()
        self._layout.addLayout(self.main_layout)
        self.button_layout = QHBoxLayout()
        self._layout.addLayout(self.button_layout)
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton(translate_ui("ui_cancel"))
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
        self.popup_ok.emit("")
        self.close()


class AbilityPopup(BasePopup):
    popup_ok = pyqtSignal(str)

    def __init__(self, kwargs):
        BasePopup.__init__(self)
        self.abilities = load_abilities()
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
        self.setWindowTitle(translate_ui("ui_ability_add_button"))
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
                           if self.abilities[ability_name]["tier"] == "1"]
        abilities_tier2 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name]["tier"] == "2"]
        abilities_tier3 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name]["tier"] == "3"]
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
                value = self.abilities[ability][parameter]
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
        table.setHorizontalHeaderLabels([translate_ui("ui_ability_name"), translate_ui("ui_ability_display_name"),
                                         translate_ui("ui_ability_requirements"), translate_ui("ui_ability_description"),
                                         translate_ui("ui_ability_tier")])
        return table

    def translate_abilities(self, locale="PL"):
        for ability in self.abilities:
            display, description = translate_ability(ability, locale=locale)
            self.abilities[ability]["display"] = display
            self.abilities[ability]["description"] = description

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
                self.selected_ability = item.cellWidget(self.current_row, 0).text()
                ability_status = self.validator(self.abilities[self.selected_ability])
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
                label = QLabel(translate_ability(n)[0])
            else:
                label = QLabel("{} {}".format(translate_parameter(n), data[n]))
            label.setStyleSheet("color: green") if status[index] == 0 else label.setStyleSheet("color: red")
            layout.addWidget(label)
        self.setLayout(layout)


class TableDescriptionItem(QLabel):

    def __init__(self, data, width):
        QLabel.__init__(self)
        self.setWordWrap(True)
        self.setFixedWidth(width)
        self.setText(data)
        self.setContentsMargins(2, 2, 2, 2)


class WeaponPopup(BasePopup):
    popup_ok = pyqtSignal(Weapon)

    def __init__(self, kwargs):
        BasePopup.__init__(self)
        self.edit = None
        if "edit" in kwargs:
            self.edit = kwargs["edit"]
        self.archetype_weapons = load_weapons()
        self.current_weapon = None
        combo_layout = QHBoxLayout()
        self.archetype_combobox = LabelledComboBox(label=translate_ui("ui_item_archetype"))
        self.archetype_names = []
        self.fill_archetype_combobox()
        if self.edit is not None:
            self.archetype_combobox.setCurrentIndex(self.archetype_names.index(self.edit.arch_name))
            self.archetype_combobox.setEnabled(False)
        self.archetype_combobox.currentIndexChanged.connect(self.fill_parameters)
        self.weapon_name = InputLine("weapon_name", Qt.AlignLeft, label=translate_ui("ui_item_name"))
        combo_layout.addWidget(self.archetype_combobox)
        combo_layout.addWidget(self.weapon_name)

        damage_layout = QHBoxLayout()
        self.damage_value = InputLine("weapon_damage", Qt.AlignLeft, dtype="int", label=translate_ui("ui_weapon_damage"))
        self.ap_value = InputLine("weapon_ap", Qt.AlignLeft, dtype="int", label=translate_ui("ui_weapon_ap"))
        self.damage_type = LabelledComboBox(label=translate_ui("ui_weapon_damage_type"))
        for damage_type in damage_types:
            self.damage_type.addItem(damage_type)
        damage_layout.addWidget(self.damage_value)
        damage_layout.addWidget(self.damage_type)
        damage_layout.addWidget(self.ap_value)

        shot_layout = QHBoxLayout()
        self.max_energy = InputLine("weapon_max_energy", Qt.AlignLeft,
                                    dtype="int", label=translate_ui("ui_weapon_max_magazine"))
        self.energy_per_shot = InputLine("weapon_shot_cost", Qt.AlignLeft,
                                         dtype="int", label=translate_ui("ui_weapon_shotcost"))
        self.shot_type = InputLine("weapon_mode", Qt.AlignLeft, label=translate_ui("ui_weapon_fire_mode"))
        shot_layout.addWidget(self.max_energy)
        shot_layout.addWidget(self.energy_per_shot)
        shot_layout.addWidget(self.shot_type)

        self.main_layout.addLayout(combo_layout)
        self.main_layout.addLayout(damage_layout)
        self.main_layout.addLayout(shot_layout)
        self.fill_parameters()
        self.show()

    def fill_archetype_combobox(self):
        for weapon in self.archetype_weapons:
            self.archetype_combobox.addItem(translate_item(weapon))
            self.archetype_names.append(weapon)
        self.archetype_names.append("weapon_other")
        self.archetype_combobox.addItem(translate_item("weapon_other"))

    def fill_parameters(self, index=None):
        if self.edit is None:
            index = self.archetype_combobox.currentIndex()
            weapon_name = self.archetype_names[index]
            weapon = Weapon()
            if weapon_name in self.archetype_weapons:
                weapon_line = self.archetype_weapons[weapon_name]._line
                weapon.load_from_line(weapon_line)
        else:
            weapon = self.edit
            weapon_name = weapon.name
        self.weapon_name.setText(translate_item(weapon_name))
        if weapon_name == "weapon_other" and self.edit is None:
            self.current_weapon = weapon
            return
        self.damage_value.setText(str(weapon.damage))
        self.ap_value.setText(str(weapon.ap))
        self.damage_type.setCurrentIndex(damage_types.index(weapon.damage_type))
        self.max_energy.setText(str(weapon.max_magazine))
        self.energy_per_shot.setText(str(weapon.shot_cost))
        self.shot_type.setText("/".join(weapon.fire_modes))
        self.current_weapon = weapon

    def ok_pressed(self):
        self.current_weapon.name = self.weapon_name.text()
        self.current_weapon.damage = int(self.damage_value.text())
        self.current_weapon.ap = int(self.ap_value.text())
        self.current_weapon.damage_type = self.damage_type.currentText()
        self.current_weapon.max_magazine = int(self.max_energy.text())
        self.current_weapon.shot_cost = int(self.energy_per_shot.text())
        self.current_weapon.fire_modes = self.shot_type.text().split("/")
        self.popup_ok.emit(self.current_weapon)
        self.close()


class ArmorPopup(BasePopup):
    popup_ok = pyqtSignal(Armor)

    def __init__(self, kwargs):
        BasePopup.__init__(self)
        if "edit" in kwargs:
            self.edit = kwargs["edit"]
        self.archetype_armor = load_armors()
        self.current_armor = None
        combo_layout = QHBoxLayout()
        self.archetype_combobox = LabelledComboBox(label=translate_ui("ui_item_archetype"))
        self.archetype_names = []
        self.fill_archetype_combobox()
        if self.edit is not None:
            self.archetype_combobox.setCurrentIndex(self.archetype_names.index(self.edit.arch_name))
            self.archetype_combobox.setEnabled(False)
        self.archetype_combobox.currentIndexChanged.connect(self.fill_parameters)
        self.armor_name = InputLine("armor_name", Qt.AlignLeft, label=translate_ui("ui_item_name"))
        combo_layout.addWidget(self.archetype_combobox)
        combo_layout.addWidget(self.armor_name)

        armor_layout = QHBoxLayout()
        self.armors = {}
        for armor in armor_names:
            armor_widget = InputLine(armor, Qt.AlignLeft, dtype="int",
                                     label=translate_parameter(armor))
            self.armors[armor] = armor_widget
            armor_layout.addWidget(armor_widget)

        self.main_layout.addLayout(combo_layout)
        self.main_layout.addLayout(armor_layout)
        self.fill_parameters()
        self.show()

    def fill_archetype_combobox(self):
        for armor in self.archetype_armor:
            self.archetype_combobox.addItem(translate_item(armor))
            self.archetype_names.append(armor)
        self.archetype_names.append("armor_other")
        self.archetype_combobox.addItem(translate_item("armor_other"))

    def fill_parameters(self, index=None):
        if self.edit is None:
            index = self.archetype_combobox.currentIndex()
            armor_name = self.archetype_names[index]
            armor = Armor()
            if armor_name in self.archetype_armor:
                armor_line = self.archetype_armor[armor_name]._line
                armor.load_from_line(armor_line)
        else:
            armor = self.edit
            armor_name = armor.name
        self.current_armor = armor
        self.armor_name.setText(translate_item(armor_name))
        if armor_name == "armor_other":
            for armor_name in armor_names:
                self.armors[armor_name].setText(armor.armor[armor_name])
            return
        for armor_type in armor_names:
            self.armors[armor_type].setText(armor.armor[armor_type])

    def ok_pressed(self):
        self.current_armor.name = self.armor_name.text()
        for armor_type in armor_names:
            self.current_armor.armor[armor_type] = int(self.armors[armor_type].text())
        self.popup_ok.emit(self.current_armor)
        self.close()


class ItemPopup(BasePopup):
    popup_ok = pyqtSignal(Item)

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
        self.quantity = InputLine("quantity", dtype="int", label=translate_ui("ui_item_quantity"))
        self.name = InputLine("name", dtype="str", label=translate_ui("ui_item_name"))
        self.weight = InputLine("weight", dtype="float", label=translate_ui("ui_item_weight"))
        line1.addWidget(self.quantity, 1)
        line1.addWidget(self.name, 4)
        line1.addWidget(self.weight, 1)
        label = QLabel(translate_ui("ui_item_description"))
        self.description = QTextEdit()
        line2.addWidget(label)
        line2.addWidget(self.description)
        if self.edit is None:
            self.item = Item()
            self.quantity.setText("0")
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
    popup_ok = pyqtSignal(Item, int)

    def __init__(self, item, equipped=False):
        BasePopup.__init__(self)
        layout = QVBoxLayout()
        self.item = item
        self.equipped = equipped
        label_layout = QVBoxLayout()
        label = QLabel("{}: {}".format(translate_ui("ui_item_transfer_dialog"), item.name))
        label_layout.addWidget(label)
        layout.addLayout(label_layout)

        values_layout = QHBoxLayout()
        self.equipment_value = InputLine("max", dtype="int", enabled=False, label=translate_ui("ui_items_in_inventory"))
        value = item.equipped_quantity if equipped else item.total_quantity - item.equipped_quantity
        self.equipment_value.setText(value)
        self.transfer_value = InputLine("transfer", dtype="int", min_val=0, max_val=value,
                                        label=translate_ui("ui_items_to_transfer"))
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
        normal_button = QRadioButton(translate_ui("ui_normal_character"))
        normal_button.setChecked(True)
        alternative_button = QRadioButton(translate_ui("ui_alternative_character"))
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


class ModifierItemPopup(BasePopup):
    popup_ok = pyqtSignal(ModifierItem)

    def __init__(self, kwargs):
        BasePopup.__init__(self)
        self.alternative = kwargs["alternative"]
        self.edit = None
        if "edit" in kwargs:
            self.edit = kwargs["edit"]
        self.include = []
        if "include" in kwargs:
            self.include = kwargs["include"]
        self.archetype_items = load_modifiers(self.alternative)
        if self.include:
            for item in list(self.archetype_items.keys()):
                if self.archetype_items[item].type not in self.include:
                    del self.archetype_items[item]
        self.current_item = None
        combo_layout = QHBoxLayout()
        self.archetype_combobox = LabelledComboBox(label=translate_ui("ui_item_archetype"))
        self.archetype_combobox.setEnabled(self.edit is None)
        self.archetype_names = []
        if self.edit is None:
            self.fill_archetype_combobox()
        self.archetype_combobox.currentIndexChanged.connect(self.fill_parameters)
        self.item_name = InputLine("item_name", Qt.AlignLeft, label=translate_ui("ui_item_name"))
        self.item_name.value_changed.connect(self.update_parameters)
        combo_layout.addWidget(self.archetype_combobox)
        combo_layout.addWidget(self.item_name)
        self.bonuses_layout = QVBoxLayout()

        add_button_layout = QVBoxLayout()
        add_button = QPushButton(translate_ui("ui_add_property"))
        add_button.clicked.connect(self.add_property)
        add_button_layout.addWidget(add_button)

        self.main_layout.addLayout(combo_layout)
        self.main_layout.addLayout(self.bonuses_layout)
        self.main_layout.addLayout(add_button_layout)
        self.fill_parameters()
        self.show()

    def fill_archetype_combobox(self):
        for item in self.archetype_items:
            self.archetype_combobox.addItem(translate_item(item))
            self.archetype_names.append(item)
        self.archetype_names.append("item_other")
        self.archetype_combobox.addItem(translate_item("item_other"))

    def fill_parameters(self):
        if self.edit is None:
            index = self.archetype_combobox.currentIndex()
            item_name = self.archetype_names[index]
            self.item_name.setText(translate_item(item_name))
            item = ModifierItem()
            self.current_item = item
            self.remove_property("all")
            if item_name == "item_other":
                return
            item_line = self.archetype_items[item_name]._line
            item.load_from_line(item_line)
        else:
            item = self.edit
            self.item_name.setText(item.name)
        self.current_item = item
        self.remove_property("all")
        for property in item.bonuses:
            self.add_property(property=property, value=item.bonuses[property])

    def update_parameters(self, parameter, value):
        if parameter == "item_name":
            self.current_item.name = value
        if parameter in self.current_item.bonuses:
            self.current_item.bonuses[parameter] = int(value)

    def add_property(self, fixed=False, property=None, value=0):
        view = ModifierView(self.alternative, not fixed)
        view.set_property(property, value)
        self.bonuses_layout.addWidget(view)
        view.delete.connect(self.remove_property)

    def remove_property(self, prop_id):
        for index in reversed(range(self.bonuses_layout.count())):
            child = self.bonuses_layout.itemAt(index)
            if child is None:
                continue
            widget = child.widget()
            if widget is None:
                continue
            if not isinstance(widget, ModifierView):
                continue
            if prop_id != "all" and widget.name != prop_id:
                continue
            widget.setParent(None)
            widget.deleteLater()

    def sum_up_item(self):
        self.current_item.bonuses = {}
        for index in reversed(range(self.bonuses_layout.count())):
            child = self.bonuses_layout.itemAt(index)
            if child is None:
                continue
            widget = child.widget()
            if widget is None:
                continue
            if not isinstance(widget, ModifierView):
                continue
            prop_name = widget.param_names[widget.param_combo.currentIndex()]
            if not widget.value.text():
                continue
            value = int(widget.value.text())
            if prop_name not in self.current_item.bonuses:
                self.current_item.bonuses[prop_name] = value
                continue
            if value > self.current_item.bonuses[prop_name]:
                self.current_item.bonuses[prop_name] = value
                continue

    def ok_pressed(self):
        self.sum_up_item()
        self.popup_ok.emit(self.current_item)
        self.close()


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
        self.param_combo.addItems([translate_parameter(mod) for mod in mods])

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

