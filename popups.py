from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QTextEdit, QScrollArea, QTableWidget, QCheckBox, QComboBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from parameters import load_abilities, translate_parameter, translate_ui, translate_ability, load_weapons, damage_types
from item_classes import Weapon
from layout_classes import InputLine, LabelledComboBox

class BasePopup(QWidget):
    popup_cancel = pyqtSignal(bool)
    popup_ok = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
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
        # self.show()

    def cancel_pressed(self):
        self.popup_cancel.emit(True)
        self.close()

    def ok_pressed(self):
        self.popup_ok.emit("")
        self.close()


class AbilityPopup(BasePopup):
    popup_ok = pyqtSignal(dict)

    def __init__(self, character=None):
        BasePopup.__init__(self)

        self.abilities = load_abilities()
        self.translate_abilities()
        self.character = character
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
        self.setWindowTitle("Dodaj zdolność")
        self.ability_layout = QVBoxLayout()
        scroll_widget.setLayout(self.ability_layout)
        # scroll_widget.setLayout(self.ability_layout)
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
            for column, parameter in enumerate(["name", "display", "requirements", "description", "tier"]):
                value = self.abilities[ability][parameter]
                if isinstance(value, dict):
                    item = TableRequirementItem(value, self.character)
                    table.setCellWidget(row, column, item)
                    row_enabled *= item.fulfilled
                elif column == 3:
                    item = TableDescriptionItem(value, 400)
                    table.setCellWidget(row, column, item)
                else:
                    if column == 0:
                        if value in self.character.abilities:
                            already_bought = True
                            row_enabled = False
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
        self.popup_ok.emit(self.abilities[self.selected_ability])
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
                requirement = item.cellWidget(self.current_row, 2)
                self.ability_is_valid = requirement.fulfilled \
                    if self.selected_ability not in self.character.abilities else False
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

    def __init__(self, data, character):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.fulfilled = True
        for n in data:
            if data[n] is True:
                label = QLabel(translate_ability(n)[0])
                label.setStyleSheet("color: green")
                if n not in character.abilities:
                    self.fulfilled = False
                    label.setStyleSheet("color: red")
            else:
                label = QLabel("{} {}".format(translate_parameter(n), data[n]))
                label.setStyleSheet("color: green")
                value = 0
                if n in character.skills:
                    value = int(character.skills[n]) + int(character.skill_bonuses[n])
                elif n in character.attributes:
                    value = int(character.attributes[n]) + \
                            int(character.attribute_advancements[n]) + \
                            int(character.attribute_bonuses[n])
                if int(data[n]) > value:
                    self.fulfilled = False
                    label.setStyleSheet("color: red")
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

    def __init__(self, character=None):
        BasePopup.__init__(self)
        self.archetype_weapons = load_weapons()
        self.current_weapon = None
        self.combo_layout = QHBoxLayout()
        self.archetype_combobox = LabelledComboBox(label="weapon_archetype")
        self.archetype_names = []
        self.fill_archetype_combobox()
        self.archetype_combobox.currentIndexChanged.connect(self.fill_parameters)
        self.weapon_name = InputLine("weapon_name", Qt.AlignLeft, label="weapon_name")
        self.weapon_name.value_changed.connect(self.update_parameters)
        self.combo_layout.addWidget(self.archetype_combobox)
        self.combo_layout.addWidget(self.weapon_name)

        self.damage_layout = QHBoxLayout()
        self.damage_value = InputLine("weapon_damage", Qt.AlignLeft, dtype="int", label="weapon_damage")
        self.damage_value.value_changed.connect(self.update_parameters)
        self.ap_value = InputLine("weapon_ap", Qt.AlignLeft, dtype="int", label="ap_value")
        self.ap_value.value_changed.connect(self.update_parameters)
        self.damage_type = LabelledComboBox(label="damage_type")
        for damage_type in damage_types:
            self.damage_type.addItem(damage_type)
        self.damage_type.currentIndexChanged.connect(lambda x: self.update_parameters("damage_type", damage_types[x]))
        self.damage_layout.addWidget(self.damage_value)
        self.damage_layout.addWidget(self.damage_type)
        self.damage_layout.addWidget(self.ap_value)

        self.shot_layout = QHBoxLayout()
        self.max_energy = InputLine("weapon_max_energy", Qt.AlignLeft, dtype="int", label="max_energy")
        self.max_energy.value_changed.connect(self.update_parameters)
        self.energy_per_shot = InputLine("weapon_shot_cost", Qt.AlignLeft, dtype="int", label="shot_cost")
        self.energy_per_shot.value_changed.connect(self.update_parameters)
        self.shot_type = InputLine("weapon_mode", Qt.AlignLeft, label="weapon_fire_modes")
        self.shot_type.value_changed.connect(self.update_parameters)
        self.shot_layout.addWidget(self.max_energy)
        self.shot_layout.addWidget(self.energy_per_shot)
        self.shot_layout.addWidget(self.shot_type)

        self.main_layout.addLayout(self.combo_layout)
        self.main_layout.addLayout(self.damage_layout)
        self.main_layout.addLayout(self.shot_layout)
        self.fill_parameters()
        self.show()

    def fill_archetype_combobox(self):
        for weapon_type in self.archetype_weapons:
            for weapon in self.archetype_weapons[weapon_type]:
                self.archetype_combobox.addItem(weapon)
                self.archetype_names.append(weapon)
        self.archetype_names.append("other")
        self.archetype_combobox.addItem("other")

    def fill_parameters(self, index=None):
        index = self.archetype_combobox.currentIndex()
        weapon_name = self.archetype_names[index]
        if weapon_name == "other":
            return
        weapon_line = self.archetype_weapons["melee"][weapon_name]._line \
            if weapon_name in self.archetype_weapons["melee"] \
            else self.archetype_weapons["ranged"][weapon_name]._line
        weapon = Weapon()
        weapon.load_from_line(weapon_line)

        self.damage_value.setText(str(weapon.damage))
        self.ap_value.setText(str(weapon.ap))
        self.damage_type.setCurrentIndex(damage_types.index(weapon.damage_type))
        self.max_energy.setText(str(weapon.max_magazine))
        self.energy_per_shot.setText(str(weapon.shot_cost))
        self.shot_type.setText("/".join(weapon.fire_modes))
        self.current_weapon = weapon

    def update_parameters(self, parameter, value):
        if parameter == "weapon_name":
            self.current_weapon.name = value
        if parameter == "weapon_damage":
            self.current_weapon.damage = value
        if parameter == "weapon_ap":
            self.current_weapon.ap = value
        if parameter == "damage_type":
            self.current_weapon.damage_type = value
        if parameter == "weapon_max_energy":
            self.current_weapon.max_magazine = value
        if parameter == "weapon_shot_cost":
            self.current_weapon.shot_cost = value
        if parameter == "weapon_mode":
            self.current_weapon.fire_modes = value.split("/")
