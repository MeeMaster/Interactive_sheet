from PyQt5.QtWidgets import (QPushButton, QWidget, QAction, QSpacerItem, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QLineEdit, QCheckBox, QMenu, QComboBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator, QColor
from parameters import translate_ability, translate_ui, armor_names, translate_parameter


line_edit_style = "QLineEdit { background: rgba(255, 255, 255, 100); border-width: 0px;\
 alternate-background-color: rgba(200,200,200,50); font: bold 10px; margin: 0px;}"


class ScrollContainer(QWidget):
    item_equipped = pyqtSignal(bool)

    def __init__(self, name, button_text, content_widget, parent=None, popup=None, target_function=None, **kwargs):
        QWidget.__init__(self)
        self.parent=parent
        self.kwargs = kwargs
        self.layout = QVBoxLayout()
        self.label = QLabel(name)
        self.label.setStyleSheet("font: bold 14px")
        self.layout.addWidget(self.label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        self.button = QPushButton(button_text)
        self.button.clicked.connect(self.add_widget)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.popup = popup
        self.current_popup = None
        self.content_widget = content_widget
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_widget.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.target_function = target_function

    def remove_widget(self, name):
        for child_index in range(self.scroll_layout.count()):
            child = self.scroll_layout.itemAt(child_index)
            if child is None:
                continue
            child = child.widget()
            if child is None:
                continue
            if child.name == name:
                status = self.target_function("remove", child)
                child.setParent(None)

    def add_widget(self):
        if self.popup is not None:
            self.current_popup = self.popup(self.parent.character)
            self.current_popup.popup_ok.connect(self._add_widget)
            self.current_popup.popup_cancel.connect(self.close_popup)
        else:
            self._add_widget("None")

    def close_popup(self):
        self.current_popup = None

    def _add_widget(self, widget_params, filling=False):
        widget = self.content_widget(widget_params)
        widget.delete.connect(self.remove_widget)
        widget.item_equipped.connect(lambda x: self.item_equipped.emit(x))
        status = self.target_function("add", widget_params)
        if status or filling:
            self.scroll_layout.insertWidget(-2, widget)
        self.current_popup = None


class InputLine(QWidget):
    value_changed = pyqtSignal(str, str)

    def __init__(self, name, align_flag=Qt.AlignCenter, enabled=True, val_dict=None,
                 dtype="str", maxwidth=None, label=None, spacer=None):
        QWidget.__init__(self)
        self.dtype = dtype
        self.layout = QVBoxLayout()
        if label is not None:
            self.label = QLabel(label)
            self.label.setWordWrap(True)
            self.label.setStyleSheet("font: 8px")
            self.label.setContentsMargins(0, 0, 0, 0)
            self.layout.addWidget(self.label)
        self.line = QLineEdit()
        self.line.editingFinished.connect(self.emit_changed)
        self.line.setContentsMargins(0, 0, 0, 0)
        self.line.setEnabled(enabled)
        self.line.setStyleSheet(line_edit_style)
        self.line.setAlignment(align_flag)
        self.name = name
        if maxwidth is not None:
            self.setMaximumWidth(maxwidth)
        if self.dtype == "int":
            self.line.setValidator(MyIntValidator(-100, 10000))
        self.register_field(val_dict=val_dict)
        self.layout.addWidget(self.line)
        if spacer == "lower":
            self.layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        if spacer == "upper":
            self.layout.insertSpacerItem(0, QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def emit_changed(self):
        self.value_changed.emit(self.name, self.text())

    def text(self):
        return self.line.text()

    def setText(self, value):
        self.line.setText(str(value))

    def register_field(self, val_dict):
        if val_dict is None:
            return
        val_dict[self.name] = self


class AttributeView(QWidget):
    attribute_changed = pyqtSignal(str, str, int)

    def __init__(self, name="", display_name=None, val_dict=None):
        QWidget.__init__(self, parent=None)
        self.name = name
        self.setFixedWidth(80)
        self.layout = QVBoxLayout()
        self.display_name = display_name if display_name is not None else name
        self.input_layout = QHBoxLayout()
        self.total_layout = QVBoxLayout()
        self.name_layout = QVBoxLayout()
        self.layout.addLayout(self.name_layout)
        self.layout.addLayout(self.input_layout)
        self.layout.addLayout(self.total_layout)

        self.label = QLabel(self.display_name)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font: bold 12px")

        self.name_layout.addWidget(self.label)
        self.base = InputLine("base", dtype="int")
        self.base.value_changed.connect(self.emit_changed)
        self.input_layout.addWidget(self.base)
        self.advancement = InputLine("adv", dtype="int")
        self.advancement.value_changed.connect(self.emit_changed)
        self.input_layout.addWidget(self.advancement)
        self.total_value = InputLine("total", dtype="int", enabled=False)
        self.total_layout.addWidget(self.total_value)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.register_field(val_dict)

    def emit_changed(self, field_type, value):
        self.attribute_changed.emit(self.name, field_type, int(value))

    def register_field(self, val_dict):
        if val_dict is None:
            return
        val_dict[self.name] = self

    def set_total(self, value):
        self.total_value.setText(str(value))

    def set_base(self, value):
        self.base.setText(str(value))

    def set_advancement(self, value):
        self.advancement.setText(str(value))


class SkillView(QWidget):
    skill_changed = pyqtSignal(str, str, int)

    def __init__(self, name="", display_name=None, val_dict=None):
        super(QWidget, self).__init__()
        self.setFixedWidth(220)
        # color_widget(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.name = name
        self.display_name = display_name if display_name is not None else name
        self.layout = QHBoxLayout()
        self.label = QLabel(self.display_name)
        self.label.setContentsMargins(0, 0, 0, 0)
        self.label.setFixedWidth(120)
        self.layout.addWidget(self.label)
        self.advancement = InputLine("adv", dtype="int")
        self.advancement.value_changed.connect(self.emit_changed)
        self.advancement.setFixedWidth(30)
        self.advancement.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.advancement)
        self.bonus = InputLine("bonus", dtype="int")
        self.bonus.value_changed.connect(self.emit_changed)
        self.bonus.setFixedWidth(30)
        self.bonus.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.bonus)
        self.total = InputLine("total", dtype="str", enabled=False)
        self.total.setFixedWidth(40)
        self.total.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.total)
        self.register_field(val_dict)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def print_sizehints(self):
        print(self.display_name, self.sizeHint(), self.label.sizeHint(),
              self.advancement.sizeHint(), self.bonus.sizeHint(), self.total.sizeHint())

    def emit_changed(self, field_type, value):
        self.skill_changed.emit(self.name, field_type, int(value))

    def register_field(self, val_dict):
        if val_dict is None:
            return
        val_dict[self.name] = self

    def set_total(self, value):
        self.total.setText(str(value))

    def set_bonus(self, value):
        self.bonus.setText(str(value))

    def set_advancement(self, value):
        self.advancement.setText(str(value))


class NameView(QWidget):
    value_changed = pyqtSignal(str, str)

    def __init__(self, name="", display_name=None, val_dict=None):
        QWidget.__init__(self)
        self.display_name = display_name if display_name is not None else name
        self.setMinimumWidth(200)
        self.name = name
        self.val_dict = val_dict
        self.layout = QHBoxLayout()
        self.label = QLabel(self.display_name)
        self.value = InputLine(name, dtype="str", enabled=True)
        self.value.value_changed.connect(self.emit_changed)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.register_field(val_dict=val_dict)

    def setText(self, value):
        self.value.setText(value)

    def emit_changed(self, field_type, value):
        self.value_changed.emit(self.name, value)

    def register_field(self, val_dict):
        if val_dict is None:
            return
        val_dict[self.name] = self


class View(QWidget):
    delete = pyqtSignal(str)
    item_equipped = pyqtSignal(bool)

    def __init__(self):
        QWidget.__init__(self)
        self.menu = QMenu(self)
        self.menu_actions = {"Usun": self.remove}
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu.addAction(QAction("Usun", self))
        self.customContextMenuRequested.connect(self.show_header_menu)

    def add_header_option(self, option, target):
        self.menu.addAction(QAction(option, self))
        self.menu_actions[option] = target

    def show_header_menu(self, point):
        self.menu.triggered[QAction].connect(self.resolve_action)
        self.menu.exec_(self.mapToGlobal(point))

    def resolve_action(self, action):
        if action.text() not in self.menu_actions:
            return
        self.menu_actions[action.text()]()

    def remove(self):
        self.delete.emit(self.name)


class AbilityView(View):

    def __init__(self, ability):
        View.__init__(self)
        # abilities = load_abilities()
        # self.name = ability["name"]
        self.name = ability
        layout = QVBoxLayout()
        display, desc = translate_ability(ability)
        self.display_name = display
        # self.requirements = ability["requirements"]
        self.description = desc
        self.setToolTip(self.description)
        self.display = QLineEdit()
        layout.addWidget(self.display)
        self.display.setText(self.display_name)
        self.display.setEnabled(False)
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)


class WeaponView(View):

    def __init__(self, weapon):
        View.__init__(self)
        self.weapon = weapon
        self.name = weapon.ID
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(p)
        self.setAutoFillBackground(True)
        self.layout = QVBoxLayout()
        self.line1_layout = QHBoxLayout()
        self.line2_layout = QHBoxLayout()
        self.line3_layout = QHBoxLayout()
        self.weapon_name = InputLine("weapon_name", Qt.AlignLeft, label=translate_ui("ui_item_name"))
        self.weapon_name.value_changed.connect(self.update_parameters)
        self.weapon_name.setFixedWidth(200)
        self.line1_layout.addWidget(self.weapon_name, stretch=0)
        self.weapon_type = InputLine("type", Qt.AlignLeft, label=translate_ui("ui_weapon_type"))
        self.weapon_type.value_changed.connect(self.update_parameters)
        self.line1_layout.addWidget(self.weapon_type, stretch=0)
        self.weapon_damage = InputLine("weapon_damage", label=translate_ui("ui_weapon_damage"))
        self.weapon_damage.value_changed.connect(self.update_parameters)
        self.line1_layout.addWidget(self.weapon_damage, stretch=0)
        self.weapon_pp = InputLine("weapon_ap", dtype="int", label=translate_ui("ui_weapon_ap"))
        self.weapon_pp.value_changed.connect(self.update_parameters)
        self.line1_layout.addWidget(self.weapon_pp, stretch=0)
        self.weapon_damage_type = InputLine("damage_type", Qt.AlignLeft, label=translate_ui("ui_weapon_damage_type"))
        self.weapon_damage_type.value_changed.connect(self.update_parameters)
        self.line1_layout.addWidget(self.weapon_damage_type, stretch=0)
        self.weapon_ammo_cost = InputLine("weapon_shot_cost", dtype="int", label=translate_ui("ui_weapon_shotcost"))
        self.weapon_ammo_cost.value_changed.connect(self.update_parameters)
        self.line1_layout.addWidget(self.weapon_ammo_cost, stretch=0)
        self.weapon_current_power = InputLine("current_battery", dtype="int", label=translate_ui("ui_weapon_magazine"))
        self.weapon_current_power.value_changed.connect(self.update_parameters)
        self.line1_layout.addWidget(self.weapon_current_power, stretch=0)
        # self.weapon_current_gas = InputLine("gas", dtype="int", label="Gas")
        # self.line1_layout.addWidget(self.weapon_current_gas, stretch=0)
        self.weapon_traits = InputLine("weapon_traits", Qt.AlignLeft, label=translate_ui("ui_item_traits"))
        self.weapon_traits.value_changed.connect(self.update_parameters)
        self.line2_layout.addWidget(self.weapon_traits, stretch=0)
        self.weapon_value = InputLine("weapon_value", dtype="int", label=translate_ui("ui_item_price"), maxwidth=40)
        self.weapon_value.value_changed.connect(self.update_parameters)
        self.line2_layout.addWidget(self.weapon_value, stretch=0)
        self.weapon_weight = InputLine("weapon_weight", dtype="int", label=translate_ui("ui_item_weight"))
        self.weapon_weight.value_changed.connect(self.update_parameters)
        self.line2_layout.addWidget(self.weapon_weight, stretch=0)
        self.equipped_checkbox = EquippedCheckbox()
        self.equipped_checkbox.stateChanged.connect(lambda x: self.update_parameters("equipped", x))
        self.line2_layout.addWidget(self.equipped_checkbox)
        self.layout.addLayout(self.line1_layout, stretch=0)
        self.layout.addLayout(self.line2_layout, stretch=0)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.fill_values()
        self.setLayout(self.layout)

    def update_parameters(self, parameter, value):
        if parameter == "weapon_name":
            self.weapon.name = value
        if parameter == "weapon_damage":
            self.weapon.damage = value
        if parameter == "weapon_ap":
            self.weapon.ap = value
        if parameter == "damage_type":
            self.weapon.damage_type = value
        if parameter == "current_battery":
            self.weapon.power_magazine = value
        if parameter == "weapon_shot_cost":
            self.weapon.shot_cost = value
        if parameter == "weapon_mode":
            self.weapon.fire_modes = value.split("/")
        # if parameter == "weapon_traits":
        #     self.current_weapon.traits = value
        if parameter == "weapon_value":
            self.weapon.price = value
        if parameter == "weapon_weight":
            self.weapon.weight = value
        if parameter == "equipped":
            self.weapon.equipped = value
        # if parameter == "weapon_shot_cost":
        #     self.current_weapon.shot_cost = value

    def fill_values(self):
        self.weapon_name.setText(self.weapon.name)
        self.weapon_damage.setText(self.weapon.damage)
        self.weapon_damage_type.setText(self.weapon.damage_type)
        self.weapon_pp.setText(self.weapon.ap)
        self.weapon_ammo_cost.setText(self.weapon.shot_cost)
        self.weapon_current_power.setText(self.weapon.power_magazine)
        self.weapon_value.setText(self.weapon.price)
        self.weapon_weight.setText(self.weapon.weight)
        self.equipped_checkbox.setChecked(self.weapon.equipped)


class ArmorView(View):

    def __init__(self, armor):
        View.__init__(self)
        self.name = armor.ID
        self.armor = armor
        self.setFixedWidth(400)
        self.layout = QVBoxLayout()
        self.line1_layout = QHBoxLayout()
        self.line1_layout.setContentsMargins(0, 0, 0, 0)
        self.line2_layout = QHBoxLayout()
        self.line2_layout.setContentsMargins(0, 0, 0, 0)
        self.armor_name = InputLine("armor_name", Qt.AlignLeft, label="Name")
        self.armor_name.value_changed.connect(self.update_parameters)
        self.line1_layout.addWidget(self.armor_name)
        self.armor_parts = {}
        for armor_name in armor_names:
            armor_piece = InputLine(armor_name, label=translate_parameter(armor_name), maxwidth=30)
            armor_piece.value_changed.connect(self.update_parameters)
            self.armor_parts[armor_name] = armor_piece
            self.line1_layout.addWidget(armor_piece)
        self.weight = InputLine("armor_weight", dtype="int", label=translate_ui("ui_item_weight"), maxwidth=30)
        self.weight.value_changed.connect(self.update_parameters)
        self.line2_layout.addWidget(self.weight)
        self.value = InputLine("armor_value", dtype="int", label=translate_ui("ui_item_price"), maxwidth=30)
        self.value.value_changed.connect(self.update_parameters)
        self.line2_layout.addWidget(self.value)
        self.traits = InputLine("armor_traits", Qt.AlignLeft, label=translate_ui("ui_item_traits"))
        self.traits.value_changed.connect(self.update_parameters)
        self.line2_layout.addWidget(self.traits)
        self.equipped_checkbox = EquippedCheckbox()
        self.equipped_checkbox.stateChanged.connect(lambda x: self.update_parameters("equipped", x))
        self.line2_layout.addWidget(self.equipped_checkbox)
        self.layout.addLayout(self.line1_layout)
        self.layout.addLayout(self.line2_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.fill_values()
        self.setLayout(self.layout)

    def update_parameters(self, parameter, value):
        if parameter in armor_names:
            self.armor.armor[parameter] = value
        if parameter == "armor_name":
            self.armor.name = value
        if parameter == "equipped":
            self.armor.equipped = value
            self.item_equipped.emit(value)
        if parameter == "armor_value":
            self.armor.price = value
        if parameter == "armor_weight":
            self.armor.weight = value

    def fill_values(self):
        self.armor_name.setText(self.armor.name)
        for armor_name in armor_names:
            self.armor_parts[armor_name].setText(self.armor.armor[armor_name])
        self.value.setText(self.armor.price)
        self.weight.setText(self.armor.weight)
        self.equipped_checkbox.setChecked(self.armor.equipped)


class EquipmentView(QWidget):
    def __init__(self, name="", display_name=None, val_dict=None):
        QWidget.__init__(self)
        self.display_name = display_name if display_name is not None else name
        self.name = name
        self.val_dict = val_dict
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.eq_name = InputLine("name", Qt.AlignLeft, maxwidth=120)
        self.qty = InputLine("quantity", Qt.AlignLeft, maxwidth=20)
        self.weight = InputLine("weight", Qt.AlignLeft, maxwidth=20)
        self.price = InputLine("price", Qt.AlignLeft, maxwidth=20)
        self.layout.addWidget(self.eq_name)
        self.layout.addWidget(self.qty)
        self.layout.addWidget(self.weight)
        self.layout.addWidget(self.price)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


class EquippedCheckbox(QWidget):
    stateChanged = pyqtSignal(bool)

    def __init__(self):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.label = QLabel(translate_ui("ui_item_equipped"))
        self.label.setStyleSheet("font: 8px")
        self.label.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.label)
        self.checkbox = QCheckBox()
        self.checkbox.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.checkbox)
        self.layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox.stateChanged.connect(lambda: self.stateChanged.emit(self.checkbox.isChecked()))
        self.setLayout(self.layout)

    def setChecked(self, value):
        self.checkbox.setChecked(value)


class MyIntValidator(QValidator):

    def __init__(self, minimum, maximum):
        QValidator.__init__(self)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, a0, a1):
        if a1 == 0:
            return QValidator.Acceptable, "0", 1
        try:
            int(a0)
            return QValidator.Acceptable, str(int(a0)), a1
        except:
            return QValidator.Invalid, a0, a1

# def color_widget(widget):
#     import random
#     color = random.choice(colors)
#     p = widget.palette()
#     p.setColor(widget.backgroundRole(), color)
#     widget.setPalette(p)
#     widget.setAutoFillBackground(True)


class LabelledComboBox(QWidget):
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, align_flag=Qt.AlignLeft, label=None, spacer=None):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        if label is not None:
            self.label = QLabel(label)
            self.label.setWordWrap(True)
            self.label.setStyleSheet("font: 8px")
            self.label.setContentsMargins(0, 0, 0, 0)
            self.label.setAlignment(align_flag)
            self.layout.addWidget(self.label)
        self.box = QComboBox()
        self.box.currentIndexChanged.connect(lambda x: self.currentIndexChanged.emit(x))
        self.layout.addWidget(self.box)
        if spacer == "lower":
            self.layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        if spacer == "upper":
            self.layout.insertSpacerItem(0, QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def currentIndex(self):
        return self.box.currentIndex()

    def setCurrentIndex(self, index):
        self.box.setCurrentIndex(index)

    def addItem(self, item):
        self.box.addItem(item)
