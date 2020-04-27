import os, sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction, QSpacerItem, QSizePolicy, QFrame,
                             QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFileDialog, QLineEdit, QTextEdit,
                             QTabWidget, QCheckBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from layout_classes import *
from popups import *
from PyQt5.QtGui import QPixmap, QIntValidator


attribute_names = ["Strength", "Agility", "Intelligence", "Toughness", "Willpower", "Charisma"]

skill_names = ["Athletics", "Unarmed", "Armed", "Light weapons", "Heavy weapons", "Gunnery", "Dodge", "Dexterity",
               "Perception", "Analysis", "Calmness", "Persistence", "Resistance", "Steal", "Hide", "Diplomacy",
               "Deceive", "Commerce", "Interrogation", "Intimidation", "Survival", "Cybernetics", "Mechanics",
               "Lockpicking", "Navigation", "Medicine", "Speeders", "Walkers", "Starships"]

character_names = ["Name", "Race", "Planet", "Age", "Traits", "Profession"]

armor_names = ["Armor head", "Armor rh", "Armor chest", "Armor lh", "Armor rl", "Armor ll"]

colors = [Qt.white, Qt.black, Qt.red, Qt.darkRed, Qt.green, Qt.darkGreen, Qt.blue, Qt.darkBlue, Qt.cyan, Qt.darkCyan,
          Qt.magenta, Qt.darkMagenta, Qt.yellow, Qt.darkYellow, Qt.gray, Qt.darkGray, Qt.lightGray]


class MainWindow(QMainWindow):
    directory_signal = pyqtSignal(str, str)
    save_signal = pyqtSignal()
    new_sheet = pyqtSignal()
    exit = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.title = 'Karta postaci'
        # self.left = 20
        # self.top = 30
        # self.width = 1600
        # self.height = 1000
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)

        # Add menu bar
        bar = self.menuBar()
        file = bar.addMenu("Plik")
        file.addAction("Nowa")
        file.addAction("Otworz")
        save = QAction("Zapisz", self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        save_as = QAction("Zapisz jako...", self)
        save_as.setShortcut("Ctrl+Shift+S")
        file.addAction(save_as)
        exit_action = QAction("Wyjdz", self)
        file.addAction(exit_action)
        file.triggered[QAction].connect(self.process_trigger)

        # Add main widget
        self.window_widget = MyWindowWidget(self)
        self.setCentralWidget(self.window_widget)
        self.show()
        # self.statusBar().setSizeGripEnabled(False)

    def open_file_name_dialog(self, pop_type):
        file_dialog = QFileDialog()
        # file_dialog.setFileMode()
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath = ""
        if pop_type == "open":
            filepath = file_dialog.getOpenFileName(self, "Wczytaj karte", os.getcwd(),
                                                   "Character files (*.cht)", options=options)

        if pop_type == "save":
            filepath = file_dialog.getSaveFileName(self, "Zapisz karte", os.getcwd(),
                                                   "Character files (*.cht)", options=options)
        if not filepath[0]:
            return
        self.directory_signal.emit(filepath[0], pop_type)

    def process_trigger(self, q):
        if q.text() == "Otworz":
            self.open_file_name_dialog("open")
        if q.text() == "Zapisz":
            self.save_signal.emit()
        if q.text() == "Zapisz jako...":
            self.open_file_name_dialog("save")
        if q.text() == "Nowa":
            self.new_sheet.emit()
        if q.text() == "Wyjdz":
            self.exit.emit()


class MyWindowWidget(QWidget):
    attribute_changed = pyqtSignal(str, str, int)

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.setAutoFillBackground(True)
        # Create character sheet layout
        self.main_layout = QHBoxLayout(self)
        self.main_sheet_layout = QVBoxLayout()
        self.main_layout.addLayout(self.main_sheet_layout, 6)
        self.actions_panel_layout = QVBoxLayout()
        self.main_layout.addLayout(self.actions_panel_layout, 1)
        self.actions_panel_layout.setSizeConstraint(3)

        # Logo
        # self.logo_layout = QVBoxLayout()
        # self.main_sheet_layout.addLayout(self.logo_layout, 1)
        # self.logo = QLabel()
        # self.logo_pixmap = QPixmap("Logo.png")
        # self.logo.setPixmap(self.logo_pixmap)
        # self.logo_layout.addWidget(self.logo)

        self.tabs = QTabWidget()
        self.main_sheet_layout.addWidget(self.tabs, 9)

        # Define target field holders
        self.params_dict = {}
        self.weapons_dict = {}
        self.armor_dict = {}
        self.skills_dict = {}
        self.attribute_dict = {}
        self.abilities = {}

        self.tab1 = self.get_tab1()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab1, "Postać")
        self.tabs.addTab(self.tab2, "Ekwipunek")
        self.tabs.addTab(self.tab3, "Pozostałe")

        self.page2 = QHBoxLayout()
        # Equipment panel
        self.tab2.setLayout(self.page2)
        self.weapons_armor_layout = QVBoxLayout()
        self.weapons_layout = QVBoxLayout()
        self.weapons_scroll = QScrollArea()
        self.weapons_layout.addWidget(self.weapons_scroll)
        self.weapons_scroll_layout = QVBoxLayout()
        self.weapons_scroll_widget = QWidget()
        self.weapons_scroll_widget.setLayout(self.weapons_scroll_layout)

        self.weapons_armor_layout.addLayout(self.weapons_layout)
        self.armor_layout = QVBoxLayout()
        self.armor_scroll = QScrollArea()
        self.armor_layout.addWidget(self.armor_scroll)
        self.armor_scroll_widget = QWidget()
        self.armor_scroll_layout = QVBoxLayout()
        self.armor_scroll_widget.setLayout(self.armor_scroll_layout)
        self.weapons_armor_layout.addLayout(self.armor_layout)
        self.weapons_armor_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.page2.addLayout(self.weapons_armor_layout, stretch=4)

        self.misc_and_notes_layout = QVBoxLayout()
        self.miscellaneous_equipment = QVBoxLayout()
        self.misc_and_notes_layout.addLayout(self.miscellaneous_equipment)

        self.equipment_scroll_area = ScrollContainer("Equipment", "Add item", EquipmentView)
        self.miscellaneous_equipment.addWidget(self.equipment_scroll_area)
        # self.equipment_scroll_area_widget = QWidget()

        # self.equipment_scroll_area_layout = QVBoxLayout()
        # self.equipment_scroll_area_widget.setLayout(self.equipment_scroll_area_layout)

        self.page2.addLayout(self.misc_and_notes_layout, stretch=2)
        self.notes_layout = QVBoxLayout()
        self.misc_and_notes_layout.addLayout(self.notes_layout)
        self.misc_and_notes_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.wealth_and_knowledge_layout = QVBoxLayout()
        self.page2.addLayout(self.wealth_and_knowledge_layout)
        self.knowledge_layout = QVBoxLayout()
        self.wealth_layout = QVBoxLayout()
        self.contacts_layout = QVBoxLayout()
        self.wealth_and_knowledge_layout.addLayout(self.knowledge_layout)
        self.wealth_and_knowledge_layout.addLayout(self.contacts_layout)
        self.wealth_and_knowledge_layout.addLayout(self.wealth_layout)
        self.wealth_and_knowledge_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))


        self.weapons_label = QLabel("Weapons")
        self.weapons_label.setStyleSheet("font: bold 14px")
        self.weapons_scroll_layout.addWidget(self.weapons_label)
        for n in range(3):
            weapon = WeaponView("Weapon1", val_dict=self.weapons_dict)
            self.weapons_scroll_layout.addWidget(weapon)
        self.weapons_scroll.setWidget(self.weapons_scroll_widget)


        self.armor_label = QLabel("Armor")
        self.armor_label.setStyleSheet("font: bold 14px")
        self.armor_scroll_layout.addWidget(self.armor_label)
        for n in range(4):
            armor = ArmorView("Armor1", val_dict=self.armor_dict)
            self.armor_scroll_layout.addWidget(armor)
        self.armor_scroll.setWidget(self.armor_scroll_widget)

        # self.equipment_dict = {}
        # for n in range(20):
        #     eq = EquipmentView("Equipment1", val_dict=self.equipment_dict)
        #     self.equipment_scroll_area_layout.addWidget(eq)
        # self.equipment_scroll_area_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.notes_label = QLabel("Notes")
        self.notes_label.setStyleSheet("font: bold 14px")
        self.notes = QTextEdit()
        self.notes.setFixedWidth(200)
        self.notes.setFixedHeight(400)
        self.notes_layout.addWidget(self.notes_label)
        self.notes_layout.addWidget(self.notes)

        # self.equipment_scroll_area.setWidget(self.equipment_scroll_area_widget)

        # self.knowledge_label = QLabel("Knowledge")
        # self.knowledge_label.setStyleSheet("font: bold 14px")
        # self.knowledge = QTextEdit()
        # self.knowledge.setFixedWidth(200)
        # self.knowledge.setFixedHeight(400)
        # self.knowledge_layout.addWidget(self.knowledge_label)
        # self.knowledge_layout.addWidget(self.knowledge)
        #
        # self.contacts_label = QLabel("Contacts")
        # self.contacts_label.setStyleSheet("font: bold 14px")
        # self.contacts = QTextEdit()
        # self.contacts.setFixedWidth(200)
        # self.contacts.setFixedHeight(400)
        # self.contacts_layout.addWidget(self.contacts_label)
        # self.contacts_layout.addWidget(self.contacts)

    def get_tab1(self):
        tab1 = QWidget()
        page1 = QVBoxLayout()
        tab1.setLayout(page1)
        # Parameters layout
        names_layout = QHBoxLayout()
        page1.addLayout(names_layout)
        attributes_layout = QHBoxLayout()
        attributes_layout.setContentsMargins(0, 0, 0, 0)
        page1.addLayout(attributes_layout)
        character_layout = QHBoxLayout()
        page1.addLayout(character_layout)
        page1.addSpacerItem(QSpacerItem(40, 200, QSizePolicy.Minimum, QSizePolicy.Expanding))
        skills1_layout, skills2_layout = self.fill_skills()
        character_layout.addLayout(skills1_layout)
        column2_layout = QVBoxLayout()
        skills_hitbox_layout = QHBoxLayout()
        character_layout.addLayout(column2_layout)
        column2_layout.addLayout(skills_hitbox_layout)
        abilities_layout = QVBoxLayout()
        column2_layout.addLayout(abilities_layout)
        hitbox_widget = QWidget()
        hitbox_widget.setMinimumWidth(250)
        hitbox_widget.setMinimumHeight(450)
        skills_hitbox_layout.addLayout(skills2_layout)
        skills_hitbox_layout.addWidget(hitbox_widget)
        names_inner_layout = self.fill_names()
        names_layout.addLayout(names_inner_layout)
        inner_armor_layout = self.fill_armor()
        hitbox_widget.setLayout(inner_armor_layout)
        # Set Attributes
        self.fill_attributes(attributes_layout)
        # Set skills

        abilities = ScrollContainer("Abilities", "Add ability", InputLine, popup=AbilityPopup, val_dict=self.abilities)
        abilities_layout.addWidget(abilities)
        return tab1

    def fill_skills(self):
        skills1_layout = QVBoxLayout()
        skills2_layout = QVBoxLayout()
        label = QLabel("Skills")
        label.setStyleSheet("font: bold 14px")
        skills1_layout.addWidget(label)
        label = QLabel(" ")
        label.setStyleSheet("font: bold 14px")
        skills2_layout.addWidget(label)
        for index, skill in enumerate(skill_names):
            ski = SkillView(name=skill, val_dict=self.skills_dict)
            if index < 25:
                skills1_layout.addWidget(ski)
            else:
                skills2_layout.addWidget(ski, stretch=0)
        skills1_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        skills2_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return skills1_layout, skills2_layout

    def fill_attributes(self, attributes_layout):
        for attribute in attribute_names:
            att = AttributeView(name=attribute, val_dict=self.attribute_dict)
            attributes_layout.addWidget(att, stretch=0)

    def fill_names(self):
        inner_names_layout = QHBoxLayout()
        layout_1 = QVBoxLayout()
        layout_2 = QVBoxLayout()
        layout_3 = QVBoxLayout()
        inner_names_layout.addLayout(layout_1)
        inner_names_layout.addLayout(layout_2)
        inner_names_layout.addLayout(layout_3)
        for index, name in enumerate(character_names):
            na = NameView(name=name, val_dict=self.params_dict)
            if index < 3:
                layout_1.addWidget(na)
            else:
                layout_2.addWidget(na)
        total_xp = InputLine("total_xp", val_dict=self.params_dict, label="Total XP", maxwidth=60)
        free_xp = InputLine("free_xp", val_dict=self.params_dict, label="Free XP", maxwidth=60)
        layout_3.addWidget(total_xp)
        layout_3.addWidget(free_xp)
        return inner_names_layout

    def fill_armor(self):
        inner_armor_layout = QVBoxLayout()
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        arms = QHBoxLayout()
        arms.setContentsMargins(0, 0, 0, 0)
        legs = QHBoxLayout()
        legs.setContentsMargins(0, 0, 0, 0)
        life = QHBoxLayout()
        life.setContentsMargins(0, 0, 0, 0)
        label_layout = QHBoxLayout()
        label = QLabel("Armor")
        label.setStyleSheet("font: bold 14px")
        # label.setMaximumHeight(30)
        label.setContentsMargins(0, 0, 0, 0)
        label.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(label)
        label_layout.setContentsMargins(0, 0, 0, 0)
        inner_armor_layout.addLayout(label_layout)
        inner_armor_layout.addLayout(head, 2)
        inner_armor_layout.addLayout(arms, 3)
        inner_armor_layout.addLayout(legs, 2)
        inner_armor_layout.addLayout(life, 1)
        total_hp = InputLine("Total HP", val_dict=self.params_dict, label="Total HP", maxwidth=35)
        current_hp = InputLine("Current HP", val_dict=self.params_dict, label="Current HP", maxwidth=35)
        total_pp = InputLine("Total PP", val_dict=self.params_dict, label="Total PP", maxwidth=35)
        current_pp = InputLine("Current PP", val_dict=self.params_dict, label="Current PP", maxwidth=35)
        fatigue = InputLine("Fatigue", val_dict=self.params_dict, label="Fatigue", maxwidth=35)
        life.addWidget(total_hp)
        life.addWidget(current_hp)
        life.addWidget(total_pp)
        life.addWidget(current_pp)
        life.addWidget(fatigue)
        for index, name in enumerate(armor_names):
            na = InputLine(name=name, val_dict=self.params_dict, label=name, maxwidth=30)
            na.setContentsMargins(0, 0, 0, 0)
            if index < 1:
                head.addWidget(na)
            elif index < 4:
                arms.addWidget(na)
            else:
                legs.addWidget(na)
        inner_armor_layout.setContentsMargins(0, 0, 0, 0)
        return inner_armor_layout








if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())