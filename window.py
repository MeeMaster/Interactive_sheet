import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, QTabWidget)
from layout_classes import *
from popups import *
from parameters import translate
from shooting import ShootingWidget

colors = [Qt.white, Qt.black, Qt.red, Qt.darkRed, Qt.green, Qt.darkGreen, Qt.blue, Qt.darkBlue, Qt.cyan, Qt.darkCyan,
          Qt.magenta, Qt.darkMagenta, Qt.yellow, Qt.darkYellow, Qt.gray, Qt.darkGray, Qt.lightGray]


class MainWindow(QMainWindow):
    directory_signal = pyqtSignal(str, str)
    save_signal = pyqtSignal()
    new_sheet = pyqtSignal(bool)
    exit = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.title = translate("ui_window_name")
        self.setWindowTitle(self.title)
        self.current_file_path = None
        self.popup = None

        # Add menu bar
        bar = self.menuBar()
        file = bar.addMenu(translate("ui_menu_file"))
        new_sheet = QAction(translate("ui_new_sheet"), self)
        new_sheet.setShortcut("Ctrl+N")
        file.addAction(new_sheet)
        open_file = QAction(translate("ui_menu_load_sheet"), self)
        open_file.setShortcut("Ctrl+O")
        file.addAction(open_file)
        save = QAction(translate("ui_menu_save_sheet"), self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        file.addSeparator()
        calc = QAction(translate("ui_menu_open_calculator"), self)
        calc.setShortcut("Ctrl+K")
        file.addAction(calc)
        file.addSeparator()
        save_as = QAction(translate("ui_menu_save_sheet_as"), self)
        save_as.setShortcut("Ctrl+Shift+S")
        file.addAction(save_as)
        exit_action = QAction(translate("ui_menu_quit"), self)
        file.addAction(exit_action)
        file.triggered[QAction].connect(self.process_trigger)
        # Add main widget
        self.window_widget = None
        self.show()

    def create(self):
        self.window_widget = MyWindowWidget(self)
        self.setCentralWidget(self.window_widget)

    def clear(self):
        if self.window_widget is None:
            return
        self.window_widget.close()
        self.window_widget.deleteLater()
        self.window_widget = None

    def open_file_name_dialog(self, pop_type):

        self.popup = QFileDialog()
        options = QFileDialog.Options()
        filepath = ""
        if pop_type == "open":
            filepath = self.popup.getOpenFileName(self, translate("ui_load_sheet_window_title"), os.getcwd(),
                                                   "Character files (*.cht)", options=options)

        if pop_type == "save":
            filepath = self.popup.getSaveFileName(self, translate("ui_save_sheet_window_title"), os.getcwd(),
                                                   "Character files (*.cht)", options=options)
        self.popup = None
        if not filepath[0]:
            return
        self.current_file_path = filepath[0]
        self.directory_signal.emit(filepath[0], pop_type)

    def process_trigger(self, q):
        if q.text() == translate("ui_menu_load_sheet"):
            self.open_file_name_dialog("open")
        if q.text() == translate("ui_menu_save_sheet"):
            if self.current_file_path is None:
                self.open_file_name_dialog("save")
            else:
                self.directory_signal.emit(self.current_file_path, "save")
        if q.text() == translate("ui_menu_save_sheet_as"):
            self.open_file_name_dialog("save")
        if q.text() == translate("ui_new_sheet"):
            self.open_new_sheet_popup()
        if q.text() == translate("ui_menu_quit"):
            self.exit.emit()
        if q.text() == translate("ui_menu_open_calculator"):
            self.open_calculator()

    def open_new_sheet_popup(self):
        self.popup = CreateCharacterPopup()
        self.popup.popup_ok.connect(self.create_sheet)
        self.popup.popup_cancel.connect(self.close_popup)

    def create_sheet(self, alternative):
        self.new_sheet.emit(alternative)
        self.current_file_path = None
        self.close_popup()

    def open_calculator(self):
        self.popup = ShootingWidget()
        self.popup.closed.connect(self.close_popup)
        self.popup.show()

    def close_popup(self):
        self.popup.close()
        self.popup = None


class MyWindowWidget(QWidget):
    # parameter_changed = pyqtSignal(str, str, int)

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
        # self.character = None
        self.tabs = QTabWidget()
        self.main_sheet_layout.addWidget(self.tabs, 9)

        # Define target field holders
        self.params_dict = {}
        self.skills_dict = {}
        self.attribute_dict = {}
        self.scrolls = {}
        self.notes_dict = {}
        self.equipment_tables = None

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab1, translate("ui_character_tab"))
        self.tabs.addTab(self.tab2, translate("ui_equipment_tab"))
        self.tabs.addTab(self.tab3, translate("ui_misc_tab"))

    def fill_tab1(self, character_names, attribute_names, skill_names, armor_names, validator, alternative=False):
        page1 = QVBoxLayout()
        self.tab1.setLayout(page1)
        # Parameters layout
        names_layout = QHBoxLayout()
        page1.addLayout(names_layout)
        attributes_layout = QHBoxLayout()
        attributes_layout.setContentsMargins(0, 0, 0, 0)
        page1.addLayout(attributes_layout)
        parameters_layout = self.fill_parameters()
        page1.addLayout(parameters_layout)
        character_layout = QHBoxLayout()
        page1.addLayout(character_layout)
        page1.addSpacerItem(QSpacerItem(40, 200, QSizePolicy.Minimum, QSizePolicy.Expanding))
        column2_layout = QVBoxLayout()
        skills_hitbox_layout = QHBoxLayout()
        skills1_layout, skills2_layout = self.fill_skills(skill_names, alternative=alternative)
        character_layout.addLayout(skills1_layout)
        skills_hitbox_layout.addLayout(skills2_layout)
        character_layout.addLayout(column2_layout)
        column2_layout.addLayout(skills_hitbox_layout)
        abilities_layout = QVBoxLayout()
        column2_layout.addLayout(abilities_layout)
        names_inner_layout = self.fill_names(character_names)
        inner_armor_layout = self.fill_armor(armor_names, alternative)
        names_layout.addLayout(names_inner_layout)
        hitbox_widget = QWidget()
        hitbox_widget.setMinimumWidth(250)
        hitbox_widget.setMinimumHeight(450)
        skills_hitbox_layout.addWidget(hitbox_widget)
        hitbox_widget.setLayout(inner_armor_layout)
        # Set Attributes
        self.fill_attributes(attributes_layout, attribute_names, alternative)
        # Set skills
        abilities = ScrollContainer("ui_abilities", translate("ui_ability_add_button"), AbilityView,
                                    validator=validator, alternative=alternative, popup=AbilityPopup)
        self.scrolls["abilities"] = abilities
        abilities_layout.addWidget(abilities)

    def fill_parameters(self):
        parameters_layout = QHBoxLayout()
        encumbrance_layout = QVBoxLayout()
        label = QLabel(translate("ui_encumbrance"))
        label.setStyleSheet("font: bold 12px")
        label.setAlignment(Qt.AlignCenter)
        encumbrance_layout.addWidget(label)
        encumbrance_values_layout = QHBoxLayout()
        encumbrance_current = InputLine("param_encumbrance_current", enabled=False, val_dict=self.params_dict,
                                        dtype="float", label=translate("param_encumbrance_current"), maxwidth=50)
        encumbrance_low = InputLine("param_encumbrance_low", enabled=False, val_dict=self.params_dict, dtype="int",
                                    label=translate("param_encumbrance_low"), maxwidth=50)
        encumbrance_med = InputLine("param_encumbrance_med", enabled=False, val_dict=self.params_dict, dtype="int",
                                    label=translate("param_encumbrance_med"), maxwidth=50)
        encumbrance_high = InputLine("param_encumbrance_high", enabled=False, val_dict=self.params_dict, dtype="int",
                                     label=translate("param_encumbrance_high"), maxwidth=50)
        encumbrance_values_layout.addWidget(encumbrance_current)
        encumbrance_values_layout.addWidget(encumbrance_low)
        encumbrance_values_layout.addWidget(encumbrance_med)
        encumbrance_values_layout.addWidget(encumbrance_high)
        encumbrance_layout.addLayout(encumbrance_values_layout)

        reputation_layout = QVBoxLayout()
        label = QLabel(translate("ui_reputation"))
        label.setStyleSheet("font: bold 12px")
        label.setAlignment(Qt.AlignCenter)
        reputation_layout.addWidget(label)
        reputation_values_layout = QHBoxLayout()
        reputation_bad = InputLine("param_reputation_bad", val_dict=self.params_dict, dtype="int",
                                   label=translate("param_reputation_bad"), maxwidth=50)
        reputation_good = InputLine("param_reputation_good", val_dict=self.params_dict, dtype="int",
                                    label=translate("param_reputation_good"), maxwidth=50)
        reputation_total = InputLine("param_reputation_total", val_dict=self.params_dict, dtype="int", enabled=False,
                                     label=translate("param_reputation_total"), maxwidth=50)
        reputation_values_layout.addWidget(reputation_bad)
        reputation_values_layout.addWidget(reputation_total)
        reputation_values_layout.addWidget(reputation_good)
        reputation_layout.addLayout(reputation_values_layout)

        speed_layout = QVBoxLayout()
        label = QLabel(translate("ui_speed"))
        label.setStyleSheet("font: bold 12px")
        label.setAlignment(Qt.AlignCenter)
        speed_layout.addWidget(label)
        speed_values_layout = QHBoxLayout()
        speed_low = InputLine("param_speed_low", enabled=False, val_dict=self.params_dict, dtype="int",
                              label=translate("param_speed_low"), maxwidth=50)
        speed_med = InputLine("param_speed_med", enabled=False, val_dict=self.params_dict, dtype="int",
                              label=translate("param_speed_med"), maxwidth=50)
        speed_high = InputLine("param_speed_high", enabled=False, val_dict=self.params_dict, dtype="int",
                               label=translate("param_speed_high"), maxwidth=50)
        speed_values_layout.addWidget(speed_low)
        speed_values_layout.addWidget(speed_med)
        speed_values_layout.addWidget(speed_high)
        speed_layout.addLayout(speed_values_layout)

        parameters_layout.addLayout(encumbrance_layout)
        parameters_layout.addLayout(reputation_layout)
        parameters_layout.addLayout(speed_layout)
        return parameters_layout

    def fill_skills(self, skill_names, alternative):
        skills1_layout = QVBoxLayout()
        skills2_layout = QVBoxLayout()
        label = QLabel(translate("ui_skills"))
        label.setStyleSheet("font: bold 14px")
        skills1_layout.addWidget(label)
        label = QLabel(" ")
        label.setStyleSheet("font: bold 14px")
        skills2_layout.addWidget(label)
        max_per_column = 15 if alternative else 25
        skill_names = sorted(skill_names, key=lambda x: translate(x))
        for index, skill in enumerate(skill_names):
            ski = SkillView(name=skill, display_name=translate(skill),
                            val_dict=self.skills_dict, alternative=alternative)
            if index < max_per_column:
                skills1_layout.addWidget(ski)
            else:
                skills2_layout.addWidget(ski, stretch=0)
        skills1_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        skills2_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return skills1_layout, skills2_layout

    def fill_attributes(self, attributes_layout, attribute_names, alternative):
        for attribute in attribute_names:
            att = AttributeView(name=attribute, display_name=translate(attribute),
                                val_dict=self.attribute_dict, alternative=alternative)
            attributes_layout.addWidget(att, stretch=0)

    def fill_names(self, character_names):
        inner_names_layout = QHBoxLayout()
        layout_1 = QVBoxLayout()
        layout_2 = QVBoxLayout()
        layout_3 = QVBoxLayout()
        inner_names_layout.addLayout(layout_1, 2)
        inner_names_layout.addLayout(layout_2, 4)
        inner_names_layout.addLayout(layout_3, 1)
        for index, name in enumerate(character_names):
            na = NameView(name=name, display_name=translate(name), val_dict=self.params_dict)
            if index < 3:
                layout_1.addWidget(na)
            else:
                layout_2.addWidget(na)
        total_xp = InputLine("param_xp_total", dtype="int", val_dict=self.params_dict,
                             label=translate("param_xp_total"), maxwidth=60)
        free_xp = InputLine("param_xp_free", dtype="int", val_dict=self.params_dict,
                            label=translate("param_xp_free"), maxwidth=60)
        layout_3.addWidget(total_xp)
        layout_3.addWidget(free_xp)
        return inner_names_layout

    def fill_armor(self, armor_names, alternative=False):
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
        label = QLabel(translate("ui_armor"))
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
        total_hp = InputLine("param_hp_max", val_dict=self.params_dict,
                             label=translate("param_hp_max"), maxwidth=35, spacer="upper")
        current_hp = InputLine("param_hp_current", val_dict=self.params_dict,
                               label=translate("param_hp_current"), maxwidth=35, spacer="upper")
        total_pp = InputLine("param_pp_total", val_dict=self.params_dict,
                             label=translate("param_pp_total"), maxwidth=35, spacer="upper")
        current_pp = InputLine("param_pp_curr", val_dict=self.params_dict,
                               label=translate("param_pp_curr"), maxwidth=35, spacer="upper")
        fatigue = InputLine("param_fatigue", val_dict=self.params_dict,
                            label=translate("param_fatigue") if not alternative else translate("param_battery"),
                            maxwidth=35, spacer="upper")
        life.addWidget(total_hp)
        life.addWidget(current_hp)
        life.addWidget(total_pp)
        life.addWidget(current_pp)
        life.addWidget(fatigue)
        for index, name in enumerate(armor_names):
            na = InputLine(name=name, val_dict=self.params_dict, enabled=False,
                           label=translate(name), maxwidth=30, spacer="lower")
            na.setContentsMargins(0, 0, 0, 0)
            if index < 1:
                head.addWidget(na)
            elif index < 4:
                arms.addWidget(na)
            else:
                legs.addWidget(na)
        inner_armor_layout.setContentsMargins(0, 0, 0, 0)
        return inner_armor_layout

    def fill_tab2(self, alternative=False):
        page2 = QVBoxLayout()
        # Equipment panel
        equipment_tabs = QTabWidget()
        page2.addWidget(equipment_tabs, 1)
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        equipment_tabs.addTab(tab1, translate("ui_weapons"))
        equipment_tabs.addTab(tab2, translate("ui_armors"))
        equipment_tabs.addTab(tab3, translate("ui_modifiers"))
        tab1_layout = QVBoxLayout()
        tab2_layout = QVBoxLayout()
        tab3_layout = QVBoxLayout()
        tab1.setLayout(tab1_layout)
        tab2.setLayout(tab2_layout)
        tab3.setLayout(tab3_layout)

        weapons_scroll = ConditionalScrollContainer("ui_weapons", translate("ui_weapons_add_button"), WeaponView,
                                                    popup=ItemListPopup, conditions=["weapon"])
        self.scrolls["weapons"] = weapons_scroll
        tab1_layout.addWidget(weapons_scroll)
        armor_scroll = ConditionalScrollContainer("ui_armors", translate("ui_armor_add_button"), ArmorView,
                                                  popup=ItemListPopup, conditions=["armor"])
        self.scrolls["armor"] = armor_scroll
        tab2_layout.addWidget(armor_scroll)

        modifier_scroll = ConditionalScrollContainer("ui_modifiers", translate("ui_modifier_add_button"),
                                                     ModifierItemView, conditions=["implant", "modifier", "bionic"],
                                                     popup=ItemListPopup, alternative=alternative)
        self.scrolls["modifiers"] = modifier_scroll
        tab3_layout.addWidget(modifier_scroll)

        if alternative:
            tab4 = QWidget()
            tab5 = QWidget()
            equipment_tabs.addTab(tab4, translate("ui_modules"))
            equipment_tabs.addTab(tab5, translate("ui_parts"))
            tab4_layout = QVBoxLayout()
            tab5_layout = QVBoxLayout()
            tab4.setLayout(tab4_layout)
            tab5.setLayout(tab5_layout)

            modules_scroll = ConditionalScrollContainer("ui_modules", translate("ui_module_add_button"),
                                                        ModifierItemView, conditions=["droid_module"],
                                                        popup=ItemListPopup, alternative=alternative)
            self.scrolls["modules"] = modules_scroll
            tab4_layout.addWidget(modules_scroll)

            parts_scroll = ConditionalScrollContainer("ui_parts", translate("ui_part_add_button"),
                                                      ModifierItemView, conditions=["droid_part"],
                                                      popup=ItemListPopup, alternative=alternative)
            self.scrolls["parts"] = parts_scroll
            tab5_layout.addWidget(parts_scroll)

        # items
        equipment_and_money = QHBoxLayout()
        name = "notes_money"
        money = LabelledTextEdit(name, label=translate("ui_{}".format(name)))
        self.notes_dict[name] = money
        self.equipment_tables = EquipmentWidget(ItemPopup, ItemMovePopup)
        equipment_and_money.addWidget(self.equipment_tables, 3)
        equipment_and_money.addWidget(money, 1)
        page2.addLayout(equipment_and_money, 2)
        self.tab2.setLayout(page2)

    def fill_tab3(self, notes_names):
        page3 = QVBoxLayout()
        for name in notes_names:
            field = LabelledTextEdit(name, label=translate("ui_{}".format(name)))
            self.notes_dict[name] = field
            page3.addWidget(field)
        self.tab3.setLayout(page3)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())