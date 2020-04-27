from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem,\
                            QSizePolicy, QTextEdit
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt


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

    def __init__(self, character=None):
        self.abilities = load_abilities()
        self.ability_names = sorted([a for a in self.abilities.keys()])
        self.selected_ability = None
        BasePopup.__init__(self)
        self.setWindowTitle("Dodaj zdolność")
        self.ability_layout = QHBoxLayout()
        self.ability_combobox = QComboBox()
        self.ability_requirements = QLabel()
        self.ability_requirements.setText(" " * 30)
        self.ability_cost = QLabel()
        self.ability_combobox.addItems(self.ability_names)
        self.ability_combobox.currentIndexChanged.connect(self.select_item)
        self.ability_name_layout = QVBoxLayout()
        self.ability_requirements_layout = QVBoxLayout()
        self.ability_cost_layout = QVBoxLayout()
        name_label = QLabel("Nazwa zdolności")
        req_label = QLabel("Wymagania")
        cost_label = QLabel("Koszt")
        self.ability_name_layout.addWidget(name_label)
        self.ability_requirements_layout.addWidget(req_label)
        self.ability_cost_layout.addWidget(cost_label)
        self.ability_name_layout.addWidget(self.ability_combobox)
        self.ability_requirements_layout.addWidget(self.ability_requirements)
        self.ability_cost_layout.addWidget(self.ability_cost)
        self.ability_name_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.ability_requirements_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.ability_cost_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.ability_layout.addLayout(self.ability_name_layout)
        self.ability_layout.addLayout(self.ability_requirements_layout)
        self.ability_layout.addLayout(self.ability_cost_layout)
        self.ability_description = QTextEdit()
        self.ability_description.setEnabled(False)
        self.ability_description.setMaximumHeight(80)
        self.ability_layout.addWidget(self.ability_description)
        self.main_layout.addLayout(self.ability_layout)
        self.select_item()
        self.show()

    def select_item(self):
        index = self.ability_combobox.currentIndex()
        item = self.ability_names[index]
        # self.selected_ability = item
        self.ability_requirements.setText("\n".join(self.abilities[item]["requirements"]))
        self.ability_description.setText(self.abilities[item]["description"])

    def ok_pressed(self):
        index = self.ability_combobox.currentIndex()
        item = self.ability_names[index]
        self.popup_ok.emit(item if item is not None else "")
        self.close()



def load_abilities():
    abilities = {}
    with open("abilities.csv", "r") as infile:
        for line in infile:
            if not line.strip():
                continue
            name, requirements, desc = line.strip().split(";")
            abilities[name] = {
                "requirements": [a.strip() for a in requirements.split(",")],
                "description": desc
                }
    return abilities
