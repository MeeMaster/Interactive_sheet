from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem,\
                            QSizePolicy, QTextEdit, QScrollArea, QTableWidget, QCheckBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from parameters import load_abilities, translate_parameter, translate_ui, translate_ability


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
        self.cancel_button = QPushButton("Cancel")
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
        abilities_tier1 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name]["tier"] == "1"]
        abilities_tier2 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name]["tier"] == "2"]
        abilities_tier3 = [ability_name for ability_name in self.abilities
                           if self.abilities[ability_name]["tier"] == "3"]
        self.selected_ability = None
        self.setWindowTitle("Dodaj zdolność")
        self.ability_layout = QVBoxLayout()
        scroll_widget.setLayout(self.ability_layout)
        self.ability_is_valid = False
        self.current_row = None
        self.current_column = None
        self.current_table = None
        self.update_button()
        for index, ability_subset in enumerate([abilities_tier1, abilities_tier2, abilities_tier3]):
            label = QLabel("Tier{}".format(index+1))
            label.setStyleSheet("font: bold 16px;")
            self.ability_layout.addWidget(label)
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
            table.setHorizontalHeaderLabels([translate_ui("ability_name"), translate_ui("ability_display_name"),
                                             translate_ui("ability_requirements"), translate_ui("ability_description"),
                                             translate_ui("ability_tier")])
            for row, ability in enumerate(ability_subset):
                row_enabled = True
                for column, parameter in enumerate(["name", "display", "requirements", "description", "tier"]):
                    value = self.abilities[ability][parameter]
                    if isinstance(value, dict):
                        item = TableRequirementItem(value, self.character)
                        table.setCellWidget(row, column, item)
                        row_enabled = item.fulfilled
                    elif column == 3:
                        item = TableDescriptionItem(value, 400)
                        table.setCellWidget(row, column, item)
                    else:
                        item = TableDescriptionItem(value, 150)
                        table.setCellWidget(row, column, item)
                if not row_enabled:
                    for column, parameter in enumerate(["name", "display", "requirements", "description", "tier"]):
                        # table.cell
                        child = table.cellWidget(row, column)
                        p = child.palette()
                        p.setColor(child.backgroundRole(), QColor(0, 0, 0, 50))
                        child.setPalette(p)
                        child.setAutoFillBackground(True)

            table.resizeColumnsToContents()
            table.resizeRowsToContents()
            self.ability_layout.addWidget(table)
            width, height = get_true_table_size(table)
            table.setFixedWidth(width)
            table.setFixedHeight(height)
        scroll_widget.setLayout(self.ability_layout)
        self.main_layout.addLayout(layout)
        self.show()

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
                self.ability_is_valid = requirement.fulfilled
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



# class AbilityPopup(BasePopup):
#     popup_ok = pyqtSignal(dict)
#
#     def __init__(self, character=None):
#         self.abilities = load_abilities()
#         self.character = character
#         self.ability_names = sorted([a for a in self.abilities.keys()
#                                      if a not in self.character.abilities])
#         self.selected_ability = None
#         BasePopup.__init__(self)
#         self.setWindowTitle("Dodaj zdolność")
#         self.ability_layout = QHBoxLayout()
#         self.ability_combobox = QComboBox()
#         self.ability_requirements = QLabel()
#         self.ability_requirements.setText(" " * 30)
#         self.ability_cost = QLabel()
#         self.ability_combobox.addItems([self.abilities[a]["display"] for a in self.ability_names])
#         self.ability_combobox.currentIndexChanged.connect(self.select_item)
#         self.ability_name_layout = QVBoxLayout()
#         self.ability_requirements_layout = QVBoxLayout()
#         self.ability_cost_layout = QVBoxLayout()
#         name_label = QLabel("Nazwa zdolności")
#         req_label = QLabel("Wymagania")
#         cost_label = QLabel("Koszt")
#         self.ability_name_layout.addWidget(name_label)
#         self.ability_requirements_layout.addWidget(req_label)
#         self.ability_cost_layout.addWidget(cost_label)
#         self.ability_name_layout.addWidget(self.ability_combobox)
#         self.ability_requirements_layout.addWidget(self.ability_requirements)
#         self.ability_cost_layout.addWidget(self.ability_cost)
#         self.ability_name_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
#         self.ability_requirements_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
#         self.ability_cost_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
#         self.ability_layout.addLayout(self.ability_name_layout)
#         self.ability_layout.addLayout(self.ability_requirements_layout)
#         self.ability_layout.addLayout(self.ability_cost_layout)
#         self.ability_description = QTextEdit()
#         self.ability_description.setEnabled(False)
#         self.ability_description.setMaximumHeight(80)
#         self.ability_layout.addWidget(self.ability_description)
#         self.main_layout.addLayout(self.ability_layout)
#         self.select_item()
#         self.show()
#
#     def select_item(self):
#         index = self.ability_combobox.currentIndex()
#         item = self.ability_names[index]
#         self.ability_requirements.setText("\n".join(self.abilities[item]["requirements"]))
#         self.ability_description.setText(self.abilities[item]["description"])
#         print(self.abilities[item]["tier"])
#         self.ability_cost.setText("{} XP".format(int(self.abilities[item]["tier"])*300))
#
#     def ok_pressed(self):
#         index = self.ability_combobox.currentIndex()
#         item = self.ability_names[index]
#         self.popup_ok.emit(self.abilities[item])
#         self.close()


