from PyQt5.QtWidgets import (QPushButton, QWidget, QAction, QSpacerItem, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QLineEdit, QCheckBox, QMenu, QComboBox, QTextEdit, QTableWidget, QTableView)
from PyQt5.QtCore import pyqtSignal, QAbstractTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator, QColor
from parameters import translate_ability, translate_ui, armor_names, translate_parameter
from item_classes import Item

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

    def clear(self):
        for child_index in reversed(list(range(self.scroll_layout.count()))):
            child = self.scroll_layout.itemAt(child_index)
            if child is None:
                continue
            child = child.widget()
            if child is None:
                continue
            child.deleteLater()
            child.setParent(None)

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

    def __init__(self, name, align_flag=Qt.AlignCenter, enabled=True, val_dict=None, min_val=None, max_val=None,
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
            self.line.setValidator(MyIntValidator(min_val, max_val))
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
        self.name = ability
        layout = QVBoxLayout()
        display, desc = translate_ability(ability)
        self.display_name = display
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
        self.weapon_type.setText(translate_parameter(self.weapon.weapon_type))


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
            armor_piece = InputLine(armor_name, dtype="int", label=translate_parameter(armor_name), maxwidth=30)
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
            self.armor.armor[parameter] = int(value)
        if parameter == "armor_name":
            self.armor.name = value
        if parameter == "equipped":
            self.armor.equipped = value
            self.item_equipped.emit(value)
        if parameter == "armor_value":
            self.armor.price = value
        if parameter == "armor_weight":
            self.armor.weight = value
        self.item_equipped.emit(True)

    def fill_values(self):
        print(self.armor.name)
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

    def __init__(self, minimum=None, maximum=None):
        QValidator.__init__(self)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, a0, a1):
        if a1 == 0:
            return QValidator.Acceptable, "0", 1
        try:
            val = int(a0)
            if self.minimum is not None:
                if val < self.minimum:
                    return QValidator.Intermediate, str(val), a1
            if self.maximum is not None:
                if val > self.maximum:
                    return QValidator.Acceptable, str(self.maximum), a1
            return QValidator.Acceptable, str(val), a1
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


class LabelledTextEdit(QWidget):
    text_changed = pyqtSignal(str, str)

    def __init__(self, name, align_flag=Qt.AlignLeft, label=None, spacer=None):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.name = name
        if label is not None:
            self.label = QLabel(label)
            self.label.setWordWrap(True)
            self.label.setStyleSheet("font: bold 14px")
            self.label.setContentsMargins(0, 0, 0, 0)
            self.label.setAlignment(align_flag)
            self.layout.addWidget(self.label)
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(lambda: self.text_changed.emit(self.name, self.get_text()))
        self.layout.addWidget(self.text_edit)
        if spacer == "lower":
            self.layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        if spacer == "upper":
            self.layout.insertSpacerItem(0, QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def get_text(self):
        return self.text_edit.toPlainText()

    def set_text(self, text):
        self.text_edit.setText(text)


class EquipmentWidget(QWidget):
    item_qty_changed = pyqtSignal(bool, str, int, bool)
    item_create = pyqtSignal(Item)
    move_item = pyqtSignal(str, int, bool)

    def __init__(self, popup=None, transfer_popup=None):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.popup = popup
        self.current_popup = None
        self.transfer_popup = transfer_popup
        self.equipped_table = ItemTable(equipped=True)
        self.equipped_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.equipped_table.item_qty_changed.connect(self.signal_forward)
        equipped_table_layout = QVBoxLayout()
        # equipped_table_layout.setContentsMargins(0, 0, 0, 0)
        equipped_table_layout.addWidget(self.equipped_table)
        self.stash_table = ItemTable(equipped=False)
        self.stash_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stash_table.item_qty_changed.connect(self.signal_forward)
        stash_table_layout = QVBoxLayout()
        # stash_table_layout.setContentsMargins(0, 0, 0, 0)
        stash_table_layout.addWidget(self.stash_table)
        button_left = QPushButton("<<<")
        button_left.clicked.connect(lambda: self.open_transfer_popup(True))
        button_left.setFixedWidth(40)
        button_right = QPushButton(">>>")
        button_right.clicked.connect(lambda: self.open_transfer_popup(False))
        button_right.setFixedWidth(40)
        button_add = QPushButton(translate_ui("ui_add_item_button"))
        button_add.clicked.connect(self.open_popup)
        button_add.setFixedWidth(60)
        buttons_layout = QVBoxLayout()
        buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        buttons_layout.addWidget(button_left)
        buttons_layout.addWidget(button_right)
        buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        buttons_layout.addWidget(button_add)
        layout.addLayout(equipped_table_layout, 10)
        layout.addLayout(buttons_layout, 1)
        layout.addLayout(stash_table_layout, 10)
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def open_popup(self):
        if self.current_popup is not None:
            return
        self.current_popup = self.popup()
        self.current_popup.popup_ok.connect(self.add_item)
        self.current_popup.popup_cancel.connect(self.close_popup)

    def open_transfer_popup(self, equip=True):
        if self.current_popup is not None:
            return
        source_table = self.stash_table if equip else self.equipped_table
        current_row = source_table.table.currentRow()
        if current_row == -1:
            return
        print(current_row)
        current_item_id = source_table.table.cellWidget(current_row, 0).text()
        current_item = source_table.items[current_item_id]
        self.current_popup = self.transfer_popup(current_item)
        self.current_popup.popup_ok.connect(lambda _id, value: self.move_item_func(_id, value, equip))
        self.current_popup.popup_cancel.connect(self.close_popup)

    def add_item(self, item):
        self.item_create.emit(item)
        self.close_popup()

    def move_item_func(self, _id, value, equip):
        if value:
            self.move_item.emit(_id, value, equip)
        self.close_popup()

    def close_popup(self):
        self.current_popup.close()
        self.current_popup = None

    def set_item_tables(self, stashed_items, equipped_items):
        self.stash_table.items = stashed_items
        self.equipped_table.items = equipped_items
        self.update_item_tables()

    def signal_forward(self, *args):
        self.item_qty_changed.emit(*args)

    def update_item_tables(self):
        self.equipped_table.fill_table()
        self.stash_table.fill_table()


class ItemCounter(QWidget):
    value_changed = pyqtSignal(str, int, bool)

    def __init__(self, name):
        QWidget.__init__(self)
        self.name = name
        self.current_count = 0
        edit_layout = QVBoxLayout()
        layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(button_layout)
        layout.addLayout(edit_layout)
        button_add = QPushButton("+")
        button_add.setContentsMargins(0, 0, 0, 0)
        button_add.setFixedWidth(16)
        button_add.setFixedHeight(16)
        button_remove = QPushButton("-")
        button_remove.setFixedWidth(16)
        button_remove.setFixedHeight(16)
        button_remove.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(button_add)
        button_layout.addWidget(button_remove)
        button_add.clicked.connect(self.increase)
        button_remove.clicked.connect(self.decrease)
        self.edit = InputLine("ui_item_count", enabled=True, maxwidth=30, dtype="int")
        self.edit.value_changed.connect(self.value_set)
        edit_layout.addWidget(self.edit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def increase(self):
        print("increase")
        self.value_changed.emit(self.name, 1, True)

    def decrease(self):
        self.value_changed.emit(self.name, -1, True)

    def value_set(self):
        print("setting")
        self.value_changed.emit(self.name, int(self.edit.text()), False)

    def set_value(self, value):
        self.edit.setText(value)

    def get_value(self, value):
        return int(self.edit.text())


class ItemTable(QWidget):
    item_qty_changed = pyqtSignal(bool, str, int, bool)

    def __init__(self, equipped=True, current_items={}):
        QWidget.__init__(self)
        self.equipped = equipped
        self.table = None
        self.items = current_items
        self.get_table()

    def get_table(self):
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setFixedWidth(300)
        self.table.setSelectionBehavior(1)
        self.table.setHorizontalScrollBarPolicy(1)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        # self.table.currentCellChanged.connect(self.cell_changed)
        self.table.setHorizontalHeaderLabels([translate_ui("ui_item_name"), translate_ui("ui_item_quantity"),
                                              translate_ui("ui_item_name"),
                                              translate_ui("ui_item_weight"),
                                              translate_ui("ui_item_total_weight")])

    def fill_table(self):
        self.table.setRowCount(len(self.items))
        print("here")
        for index, item in enumerate(self.items):
            item_class = self.items[item]
            self.table.setCellWidget(index, 0, QLabel(item))
            counter_widget = ItemCounter(item)
            counter_widget.set_value(str(item_class.quantity))
            counter_widget.value_changed.connect(self.item_changed)
            self.table.setCellWidget(index, 1, counter_widget)
            name_label = QLabel(item_class.name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setToolTip(item_class.description)
            self.table.setCellWidget(index, 2, name_label)
            weight_label = QLabel(str(item_class.weight))
            weight_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(index, 3, weight_label)
            total_weight_label = QLabel(str(item_class.weight * item_class.quantity))
            total_weight_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(index, 4, total_weight_label)
        for n in range(5):
            self.table.setColumnWidth(n, 60)
        self.table.setColumnWidth(2, 120)
        self.table.resizeRowsToContents()
        self.table.show()

    def item_changed(self, _id, value, change=True):
        self.item_qty_changed.emit(self.equipped, _id, value, change)
        self.update_values(_id)

    def update_values(self, item_id):
        for row in range(self.table.rowCount()):
            id_cell = self.table.cellWidget(row, 0)
            if id_cell.text() != item_id:
                continue
            item = self.items[item_id]
            self.table.cellWidget(row, 1).set_value(item.quantity)
            self.table.cellWidget(row, 2).setText(item.name)
            self.table.cellWidget(row, 3).setText(str(item.weight))
            self.table.cellWidget(row, 4).setText(str(item.weight * item.quantity))




