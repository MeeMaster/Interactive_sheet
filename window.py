import os, sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction, QSpacerItem, QSizePolicy, QFrame,
                             QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFileDialog, QLineEdit, QTextEdit,
                             QTabWidget, QCheckBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from layout_classes import *
from popups import *
from PyQt5.QtGui import QPixmap, QIntValidator
from parameters import attribute_names, attribute_skill_dict, character_names, armor_names
from parameters import translate_ability, translate_parameter, translate_ui
from shooting import ShootingWidget

colors = [Qt.white, Qt.black, Qt.red, Qt.darkRed, Qt.green, Qt.darkGreen, Qt.blue, Qt.darkBlue, Qt.cyan, Qt.darkCyan,
          Qt.magenta, Qt.darkMagenta, Qt.yellow, Qt.darkYellow, Qt.gray, Qt.darkGray, Qt.lightGray]


class MainWindow(QMainWindow):
    directory_signal = pyqtSignal(str, str)
    save_signal = pyqtSignal()
    new_sheet = pyqtSignal()
    exit = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.title = translate_ui("ui_window_name")
        self.setWindowTitle(self.title)
        self.current_file_path = None
        self.popup = None

        # Add menu bar
        bar = self.menuBar()
        file = bar.addMenu(translate_ui("ui_menu_file"))
        file.addAction(translate_ui("ui_new_sheet"))
        file.addAction(translate_ui("ui_menu_load_sheet"))
        save = QAction(translate_ui("ui_menu_save_sheet"), self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        file.addSeparator()
        calc = QAction(translate_ui("ui_menu_open_calculator"), self)
        file.addAction(calc)
        file.addSeparator()
        save_as = QAction(translate_ui("ui_menu_save_sheet_as"), self)
        save_as.setShortcut("Ctrl+Shift+S")
        file.addAction(save_as)
        exit_action = QAction(translate_ui("ui_menu_quit"), self)
        file.addAction(exit_action)
        file.triggered[QAction].connect(self.process_trigger)

        # Add main widget
        self.window_widget = MyWindowWidget(self)
        self.setCentralWidget(self.window_widget)

        self.show()
        # self.statusBar().setSizeGripEnabled(False)

    def open_file_name_dialog(self, pop_type):
        file_dialog = QFileDialog()
        options = QFileDialog.Options()
        filepath = ""
        if pop_type == "open":
            filepath = file_dialog.getOpenFileName(self, translate_ui("ui_load_sheet_window_title"), os.getcwd(),
                                                   "Character files (*.cht)", options=options)

        if pop_type == "save":
            filepath = file_dialog.getSaveFileName(self, translate_ui("ui_save_sheet_window_title"), os.getcwd(),
                                                   "Character files (*.cht)", options=options)
        if not filepath[0]:
            return
        self.current_file_path = filepath[0]
        self.directory_signal.emit(filepath[0], pop_type)

    def process_trigger(self, q):
        if q.text() == translate_ui("ui_menu_load_sheet"):
            self.open_file_name_dialog("open")
        if q.text() == translate_ui("ui_menu_save_sheet"):
            if self.current_file_path is None:
                self.open_file_name_dialog("save")
            else:
                self.directory_signal.emit(self.current_file_path, "save")
        if q.text() == translate_ui("ui_menu_save_sheet_as"):
            self.open_file_name_dialog("save")
        if q.text() == translate_ui("ui_new_sheet"):
            self.new_sheet.emit()
        if q.text() == translate_ui("ui_menu_quit"):
            self.exit.emit()
        if q.text() == translate_ui("ui_menu_open_calculator"):
            self.open_calculator()

    def open_calculator(self):
        self.popup = ShootingWidget()
        self.popup.closed.connect(self.close_popup)
        self.popup.show()

    def close_popup(self):
        self.popup.close()
        self.popup = None

class MyWindowWidget(QWidget):
    attribute_changed = pyqtSignal(str, str, int)
    armor_changed = pyqtSignal(bool)

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
        self.character = None
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
        self.skills_dict = {}
        self.attribute_dict = {}
        self.scrolls = {}

        self.tab1 = self.get_tab1()
        self.tab2 = self.get_tab2()
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab1, translate_ui("ui_character_tab"))
        self.tabs.addTab(self.tab2, translate_ui("ui_equipment_tab"))
        self.tabs.addTab(self.tab3, translate_ui("ui_misc_tab"))

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

        abilities = ScrollContainer(translate_ui("ui_abilities"), translate_ui("ui_ability_add_button"), AbilityView,
                                    parent=self, popup=AbilityPopup, target_function=self.handle_ability_widget)
        self.scrolls["abilities"] = abilities
        abilities_layout.addWidget(abilities)
        return tab1

    def get_tab2(self):
        tab2 = QWidget()
        page2 = QHBoxLayout()
        # Equipment panel
        tab2.setLayout(page2)
        weapons_armor_layout = QVBoxLayout()
        weapons_layout = QVBoxLayout()
        weapons_scroll = ScrollContainer(translate_ui("ui_weapons"), translate_ui("ui_weapons_add_button"), WeaponView,
                                         popup=WeaponPopup, parent=self, target_function=self.handle_weapon_widget)
        self.scrolls["weapons"] = weapons_scroll
        weapons_layout.addWidget(weapons_scroll)
        weapons_armor_layout.addLayout(weapons_layout)
        armor_layout = QVBoxLayout()
        armor_scroll = ScrollContainer(translate_ui("ui_armors"), translate_ui("ui_armor_add_button"), ArmorView,
                                       popup=ArmorPopup, parent=self, target_function=self.handle_armor_widget)
        self.scrolls["armor"] = armor_scroll
        armor_scroll.item_equipped.connect(lambda: self.armor_changed.emit(True))
        armor_layout.addWidget(armor_scroll)
        weapons_armor_layout.addLayout(armor_layout)
        weapons_armor_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        page2.addLayout(weapons_armor_layout, stretch=4)
        wealth_and_knowledge_layout = QVBoxLayout()
        page2.addLayout(wealth_and_knowledge_layout)
        knowledge_layout = QVBoxLayout()
        wealth_layout = QVBoxLayout()
        contacts_layout = QVBoxLayout()
        wealth_and_knowledge_layout.addLayout(knowledge_layout)
        wealth_and_knowledge_layout.addLayout(contacts_layout)
        wealth_and_knowledge_layout.addLayout(wealth_layout)
        wealth_and_knowledge_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return tab2

    def handle_ability_widget(self, action, ability):
        status = False
        if action == "add":
            status = self.character.add_ability(ability)
        if action == "remove":
            status = self.character.remove_ability(ability.name)
        return status

    def handle_weapon_widget(self, action, weapon):
        if action == "add":
            status = self.character.add_weapon(weapon)
        if action == "remove":
            status = self.character.remove_weapon(weapon.weapon.ID)
        return status

    def handle_armor_widget(self, action, armor):
        if action == "add":
            status = self.character.add_armor(armor)
        if action == "remove":
            status = self.character.remove_armor(armor.armor.ID)
        return status

    def handle_equipment_widget(self, action, item):
        pass

    def fill_skills(self):
        skills1_layout = QVBoxLayout()
        skills2_layout = QVBoxLayout()
        label = QLabel(translate_ui("ui_skills"))
        label.setStyleSheet("font: bold 14px")
        skills1_layout.addWidget(label)
        label = QLabel(" ")
        label.setStyleSheet("font: bold 14px")
        skills2_layout.addWidget(label)
        for index, skill in enumerate(sorted(attribute_skill_dict.keys())):
            ski = SkillView(name=skill, display_name=translate_parameter(skill), val_dict=self.skills_dict)
            if index < 25:
                skills1_layout.addWidget(ski)
            else:
                skills2_layout.addWidget(ski, stretch=0)
        skills1_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        skills2_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return skills1_layout, skills2_layout

    def fill_attributes(self, attributes_layout):
        for attribute in attribute_names:
            att = AttributeView(name=attribute, display_name=translate_parameter(attribute), val_dict=self.attribute_dict)
            attributes_layout.addWidget(att, stretch=0)

    def fill_names(self):
        inner_names_layout = QHBoxLayout()
        layout_1 = QVBoxLayout()
        layout_2 = QVBoxLayout()
        layout_3 = QVBoxLayout()
        inner_names_layout.addLayout(layout_1, 2)
        inner_names_layout.addLayout(layout_2, 4)
        inner_names_layout.addLayout(layout_3, 1)
        for index, name in enumerate(character_names):
            na = NameView(name=name, display_name=translate_parameter(name), val_dict=self.params_dict)
            if index < 3:
                layout_1.addWidget(na)
            else:
                layout_2.addWidget(na)
        total_xp = InputLine("xp_total", dtype="int", val_dict=self.params_dict,
                             label=translate_parameter("param_xp_total"), maxwidth=60)
        free_xp = InputLine("xp_free", dtype="int", val_dict=self.params_dict,
                            label=translate_parameter("param_xp_free"), maxwidth=60)
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
        label = QLabel(translate_ui("ui_armor"))
        label.setStyleSheet("font: bold 14px")
        label.setContentsMargins(0, 0, 0, 0)
        label.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(label)
        label_layout.setContentsMargins(0, 0, 0, 0)
        inner_armor_layout.addLayout(label_layout)
        inner_armor_layout.addLayout(head, 2)
        inner_armor_layout.addLayout(arms, 3)
        inner_armor_layout.addLayout(legs, 2)
        inner_armor_layout.addLayout(life, 1)
        total_hp = InputLine("hp_max", val_dict=self.params_dict,
                             label=translate_parameter("param_hp_max"), maxwidth=35, spacer="upper")
        current_hp = InputLine("hp_current", val_dict=self.params_dict,
                               label=translate_parameter("param_hp_current"), maxwidth=35, spacer="upper")
        total_pp = InputLine("pp_total", val_dict=self.params_dict,
                             label=translate_parameter("param_pp_total"), maxwidth=35, spacer="upper")
        current_pp = InputLine("pp_curr", val_dict=self.params_dict,
                               label=translate_parameter("param_pp_curr"), maxwidth=35, spacer="upper")
        fatigue = InputLine("fatigue", val_dict=self.params_dict,
                            label=translate_parameter("param_fatigue"), maxwidth=35, spacer="upper")
        life.addWidget(total_hp)
        life.addWidget(current_hp)
        life.addWidget(total_pp)
        life.addWidget(current_pp)
        life.addWidget(fatigue)
        for index, name in enumerate(armor_names):
            na = InputLine(name=name, val_dict=self.params_dict, enabled=False,
                           label=translate_parameter(name), maxwidth=30, spacer="lower")
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