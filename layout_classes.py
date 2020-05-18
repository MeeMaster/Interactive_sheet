from PyQt5.QtWidgets import (QPushButton, QWidget, QAction, QSpacerItem, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QLineEdit, QCheckBox, QMenu, QComboBox, QTextEdit, QTableWidget)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator, QColor, QDoubleValidator
from parameters import translate_ability, translate_ui, translate_parameter
from parameters import load_parameters
from item_classes import Item

param_dict = load_parameters()
armor_names = param_dict["armor"]


line_edit_style = "QLineEdit { background: rgba(255, 255, 255, 100); border-width: 0px;\
 alternate-background-color: rgba(200,200,200,50); font: bold 10px; margin: 0px;}"


class ScrollContainer(QWidget):
    item_created = pyqtSignal(object)
    item_equipped = pyqtSignal(object, bool)
    item_removed = pyqtSignal(object)
    item_edited = pyqtSignal()

    def __init__(self, name, button_text, content_widget, popup=None, **kwargs):
        QWidget.__init__(self)
        # self.parent = parent
        self.kwargs = kwargs
        self.layout = QVBoxLayout()
        self.label = QLabel(name)
        self.label.setStyleSheet("font: bold 14px")
        self.layout.addWidget(self.label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        self.button = QPushButton(button_text)
        self.button.clicked.connect(lambda: self.open_popup())
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

    def open_popup(self, edit=None):
        if self.popup is not None:
            # print(self.kwargs)
            print(self.kwargs)
            self.kwargs["edit"] = edit
            print(self.kwargs)
            self.current_popup = self.popup(self.kwargs)
            if edit is None:
                self.current_popup.popup_ok.connect(self.ok_clicked)
            else:
                self.current_popup.popup_ok.connect(lambda: self.item_edited.emit())
            self.current_popup.popup_cancel.connect(self.close_popup)

    def ok_clicked(self, obj):
        self.item_created.emit(obj)
        self.close_popup()

    def close_popup(self):
        self.current_popup.close()
        self.current_popup = None

    def edit_item(self, item):
        self.open_popup(edit=item)

    def get_children(self):
        children = []
        for child_index in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(child_index)
            if child is None:
                continue
            child = child.widget()
            if child is None:
                continue
            if not isinstance(child, self.content_widget):
                continue
            children.append(child)
        return children

    def find_child_index(self, name):
        for child_index in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(child_index)
            if child is None:
                continue
            child = child.widget()
            if child is None:
                continue
            if child.name == name:
                return child_index
        return None

    def find_child(self, name):
        child_index = self.find_child_index(name)
        if child_index is None:
            return None
        return self.scroll_layout.itemAt(child_index).widget()

    def add_widget(self, widget_params):
        widget = self.content_widget(widget_params)
        child_index = self.find_child_index(widget)
        if child_index is not None:
            return
        widget.delete.connect(lambda x: self.item_removed.emit(x))
        widget.item_equipped.connect(lambda x, y: self.item_equipped.emit(x, y))
        widget.edit_item.connect(self.edit_item)
        self.scroll_layout.insertWidget(-2, widget)

    def remove_widget(self, name):
        child = self.find_child(name)
        child.deleteLater()
        child.setParent(None)

    def clear(self):
        children = self.get_children()
        for child in children:
            child.deleteLater()
            child.setParent(None)


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
        if self.dtype == "float":
            self.line.setValidator(MyFloatValidator(min_val, max_val))
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

    def set_enabled(self, enabled):
        self.line.setEnabled(enabled)


class AttributeView(QWidget):
    attribute_changed = pyqtSignal(str, str, int)

    def __init__(self, name="", display_name=None, val_dict=None, alternative=False):
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

        self.advancement = InputLine("adv", dtype="int")
        self.advancement.value_changed.connect(self.emit_changed)
        if not alternative:
            self.input_layout.addWidget(self.base)
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

    def __init__(self, name="", display_name=None, val_dict=None, alternative=False):
        super(QWidget, self).__init__()
        self.setFixedWidth(220)
        # color_widget(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.name = name
        self.display_name = display_name if display_name is not None else name
        self.layout = QHBoxLayout()
        label_layout = QVBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.display_name)
        self.label.setContentsMargins(0, 0, 0, 0)
        self.label.setFixedWidth(120)
        label_layout.addWidget(self.label)
        self.layout.addLayout(label_layout)

        advancement_layout = QVBoxLayout()
        advancement_layout.setContentsMargins(0, 0, 0, 0)
        self.advancement = InputLine("adv", dtype="int")
        self.advancement.value_changed.connect(self.emit_changed)
        self.advancement.setFixedWidth(30)
        self.advancement.setContentsMargins(0, 0, 0, 0)
        advancement_layout.addWidget(self.advancement)
        self.layout.addLayout(advancement_layout)
        bonuses_layout = QVBoxLayout()
        self.bonus = InputLine("bonus", dtype="int", enabled=not alternative)
        self.bonus.value_changed.connect(self.emit_changed)
        self.bonus.setFixedWidth(30)
        self.bonus.setContentsMargins(0, 0, 0, 0)
        bonuses_layout.addWidget(self.bonus)
        self.bonus2 = InputLine("bonus2", dtype="int", enabled=not alternative)
        self.bonus2.value_changed.connect(self.emit_changed)
        self.bonus2.setFixedWidth(30)
        self.bonus2.setContentsMargins(0, 0, 0, 0)
        if alternative:
            bonuses_layout.addWidget(self.bonus2)
        self.layout.addLayout(bonuses_layout)

        totals_layout = QVBoxLayout()
        totals_layout.setContentsMargins(0, 0, 0, 0)
        self.total = InputLine("total", dtype="str", enabled=False)
        self.total.setFixedWidth(40)
        self.total.setContentsMargins(0, 0, 0, 0)
        totals_layout.addWidget(self.total)
        self.layout.addLayout(totals_layout)
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

    def set_bonus(self, value, value2=0):
        self.bonus.setText(str(value))
        self.bonus2.setText(str(value2))

    def set_advancement(self, value):
        self.advancement.setText(str(value))

    def set_enabled(self, enabled):
        self.advancement.set_enabled(enabled)


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
    delete = pyqtSignal(object)
    item_equipped = pyqtSignal(object, bool)
    edit_item = pyqtSignal(object)

    def __init__(self):
        QWidget.__init__(self)
        self.menu = QMenu(self)
        self.menu_actions = {"Usun": self.remove}
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu.addAction(QAction("Usun", self))
        self.customContextMenuRequested.connect(self.show_header_menu)
        self.item = None

    def show_header_menu(self, point):
        self.menu.triggered[QAction].connect(self.resolve_action)
        self.menu.exec_(self.mapToGlobal(point))

    def add_header_option(self, option, target):
        self.menu.addAction(QAction(option, self))
        self.menu_actions[option] = target

    def resolve_action(self, action):
        if action.text() not in self.menu_actions:
            return
        self.menu_actions[action.text()]()

    def remove(self):
        self.delete.emit(self.item)


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
        self.item = self.name
        self.layout().setContentsMargins(0, 0, 0, 0)


class WeaponView(View):

    def __init__(self, weapon):
        View.__init__(self)
        self.item = weapon
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
        self.equipped_checkbox.setChecked(self.item.equipped)
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
            self.item.name = value
        if parameter == "weapon_damage":
            self.item.damage = value
        if parameter == "weapon_ap":
            self.item.ap = value
        if parameter == "damage_type":
            self.item.damage_type = value
        if parameter == "current_battery":
            self.item.power_magazine = value
        if parameter == "weapon_shot_cost":
            self.item.shot_cost = value
        if parameter == "weapon_mode":
            self.item.fire_modes = value.split("/")
        # if parameter == "weapon_traits":
        #     self.current_weapon.traits = value
        if parameter == "weapon_value":
            self.item.price = value
        if parameter == "weapon_weight":
            self.item.weight = value
        if parameter == "equipped":
            self.item.equipped = value
        # if parameter == "weapon_shot_cost":
        #     self.current_weapon.shot_cost = value

    def fill_values(self):
        self.weapon_name.setText(self.item.name)
        self.weapon_damage.setText(self.item.damage)
        self.weapon_damage_type.setText(self.item.damage_type)
        self.weapon_pp.setText(self.item.ap)
        self.weapon_ammo_cost.setText(self.item.shot_cost)
        self.weapon_current_power.setText(self.item.power_magazine)
        self.weapon_value.setText(self.item.price)
        self.weapon_weight.setText(self.item.weight)
        self.equipped_checkbox.setChecked(self.item.equipped)
        self.weapon_type.setText(translate_parameter(self.item.weapon_type))


class ArmorView(View):

    def __init__(self, armor):
        View.__init__(self)
        self.name = armor.ID
        self.item = armor
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
        self.equipped_checkbox.setChecked(self.item.equipped)
        self.equipped_checkbox.stateChanged.connect(lambda x: self.update_parameters("equipped", x))
        self.line2_layout.addWidget(self.equipped_checkbox)
        self.layout.addLayout(self.line1_layout)
        self.layout.addLayout(self.line2_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.fill_values()
        self.setLayout(self.layout)

    def update_parameters(self, parameter, value):
        if parameter in armor_names:
            self.item.armor[parameter] = int(value)
        if parameter == "armor_name":
            self.item.name = value
        if parameter == "equipped":
            self.item.equipped = value
        if parameter == "armor_value":
            self.item.price = value
        if parameter == "armor_weight":
            self.item.weight = value
        self.item_equipped.emit(self.item, self.item.equipped)

    def fill_values(self):
        self.armor_name.setText(self.item.name)
        for armor_name in armor_names:
            self.armor_parts[armor_name].setText(self.item.armor[armor_name])
        self.value.setText(self.item.price)
        self.weight.setText(self.item.weight)
        self.equipped_checkbox.setChecked(self.item.equipped)


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


class MyFloatValidator(QValidator):

    def __init__(self, minimum=None, maximum=None):
        QValidator.__init__(self)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, a0, a1):
        if a1 == 0:
            return QValidator.Acceptable, "0", 1
        try:
            val = round(float(a0), 1)
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
    move_item = pyqtSignal(object, int)
    delete_item = pyqtSignal(bool, Item)
    edit_item = pyqtSignal(str)

    def __init__(self, popup=None, transfer_popup=None):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.popup = popup
        self.items = None
        self.current_popup = None
        self.transfer_popup = transfer_popup
        self.equipped_table = ItemTable(equipped=True)
        self.equipped_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.equipped_table.item_qty_changed.connect(self.signal_forward)
        self.equipped_table.delete_item.connect(self.signal_delete)
        self.equipped_table.edit_item.connect(self.item_edit)
        equipped_table_layout = QVBoxLayout()
        label = QLabel(translate_ui("ui_equipped_items"))
        label.setStyleSheet("font: bold 12px")
        label.setAlignment(Qt.AlignCenter)
        equipped_table_layout.addWidget(label)
        equipped_table_layout.addWidget(self.equipped_table)
        self.stash_table = ItemTable(equipped=False)
        self.stash_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stash_table.item_qty_changed.connect(self.signal_forward)
        self.stash_table.delete_item.connect(self.signal_delete)
        self.stash_table.edit_item.connect(self.item_edit)
        stash_table_layout = QVBoxLayout()
        label = QLabel(translate_ui("ui_stashed_items"))
        label.setStyleSheet("font: bold 12px")
        label.setAlignment(Qt.AlignCenter)
        stash_table_layout.addWidget(label)
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
        self.setLayout(layout)

    def set_items(self, items):
        self.items = items

    def open_popup(self, **kwargs):
        if self.current_popup is not None:
            return
        self.current_popup = self.popup(**kwargs)
        self.current_popup.popup_ok.connect(self.add_item)
        self.current_popup.popup_cancel.connect(self.close_popup)

    def open_transfer_popup(self, equip=True):
        if self.current_popup is not None:
            return
        source_table = self.stash_table if equip else self.equipped_table
        current_row = source_table.table.currentRow()
        if current_row == -1:
            return
        current_item_id = source_table.table.cellWidget(current_row, 0).text()
        found = False
        for item in self.items:
            if item.name == current_item_id:
                found = True
                break
        if not found:
            return
        # current_item = source_table.items[current_item_id]
        self.current_popup = self.transfer_popup(item, not equip)
        self.current_popup.popup_ok.connect(self.move_item_func)
        self.current_popup.popup_cancel.connect(self.close_popup)

    def item_edit(self, item_id):
        found = False
        for item in self.items:
            if item.name == item_id:
                found = True
                break
        if not found:
            return
        self.open_popup(edit=item)
        self.current_popup.popup_ok.connect(self.add_item)
        self.current_popup.popup_cancel.connect(self.close_popup)

    def add_item(self, item):
        self.item_create.emit(item)
        self.close_popup()

    def move_item_func(self, item, value):
        if value:
            self.move_item.emit(item, value)
        self.close_popup()

    def close_popup(self):
        if self.current_popup is None:
            return  # TODO WTF fix that?
        self.current_popup.close()
        self.current_popup = None

    def set_items(self, items):
        self.items = items
        self.update_item_tables()

    def signal_delete(self, equipped, item_name):
        found = False
        for item in self.items:
            if item.name == item_name:
                found = True
                break
        if not found:
            return
        print("here")
        self.delete_item.emit(equipped, item)

    def signal_forward(self, *args):
        self.item_qty_changed.emit(*args)

    def update_item_tables(self):  # TODO change table data handling; make tables not hold data, just display
        self.equipped_table.update_values(self.items)
        self.stash_table.update_values(self.items)


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
        self.value_changed.emit(self.name, 1, True)

    def decrease(self):
        self.value_changed.emit(self.name, -1, True)

    def value_set(self):
        self.value_changed.emit(self.name, int(self.edit.text()), False)

    def set_value(self, value):
        self.edit.setText(value)

    def get_value(self, value):
        return int(self.edit.text())


class ItemTable(QWidget):
    item_qty_changed = pyqtSignal(bool, str, int, bool)
    delete_item = pyqtSignal(bool, str)
    edit_item = pyqtSignal(str)

    def __init__(self, equipped=True):
        QWidget.__init__(self)
        self.equipped = equipped
        self.table = QTableWidget(self)
        self.get_table()
        self.menu = QMenu(self)
        self.menu_actions = {"Usun": self.remove_item}
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu.addAction(QAction("Usun", self))
        self.customContextMenuRequested.connect(self.show_header_menu)
        self.item = None
        self.add_header_option("Edit", self.item_edit)

    def show_header_menu(self, point):
        if not self.table.selectedIndexes():
            return

        self.menu.triggered[QAction].connect(self.resolve_action)
        self.menu.exec_(self.mapToGlobal(point))

    def add_header_option(self, option, target):
        self.menu.addAction(QAction(option, self))
        self.menu_actions[option] = target

    def resolve_action(self, action):
        if action.text() not in self.menu_actions:
            return
        self.menu_actions[action.text()]()

    def item_edit(self):
        current_item_id = self.table.cellWidget(self.table.currentRow(), 0).text()
        self.edit_item.emit(current_item_id)  # TODO fix to item id later

    def remove_item(self):
        current_item_id = self.table.cellWidget(self.table.currentRow(), 0).text()
        self.delete_item.emit(self.equipped, current_item_id)

    def get_table(self):
        self.table.setColumnCount(5)
        self.table.setFixedWidth(300)
        self.table.setSelectionBehavior(1)
        self.table.setHorizontalScrollBarPolicy(1)
        # self.table.currentCellChanged.connect(lambda w, x, y, z: print(w, x, y, z, self.table.currentIndex()))
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels([translate_ui("ui_item_name"), translate_ui("ui_item_quantity"),
                                              translate_ui("ui_item_name"),
                                              translate_ui("ui_item_weight"),
                                              translate_ui("ui_item_total_weight")])

    def fill_table(self, data):  # TODO fix this shit
        self.table.setRowCount(len(data))
        for index, item in enumerate(data):
            value = item.equipped_quantity if self.equipped else item.total_quantity - item.equipped_quantity

            if self.equipped and value == 0:
                continue
            if not self.equipped and value == 0 and item.total_quantity != 0:
                continue
            # item_class = self.items[item]
            self.table.setCellWidget(index, 0, QLabel(item.name))
            counter_widget = ItemCounter(item.name)
            counter_widget.set_value(str(value))
            counter_widget.value_changed.connect(self.item_changed)
            self.table.setCellWidget(index, 1, counter_widget)
            name_label = QLabel(item.name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setToolTip(item.description)
            self.table.setCellWidget(index, 2, name_label)
            weight_label = QLabel(str(item.weight))
            weight_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(index, 3, weight_label)
            total_weight_label = QLabel("{:.1f}".format(item.weight * value))
            total_weight_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(index, 4, total_weight_label)
        for n in range(5):
            self.table.setColumnWidth(n, 60)
        self.table.setColumnWidth(2, 120)
        self.table.resizeRowsToContents()
        self.table.show()

    def item_changed(self, item, value, change=True):

        self.item_qty_changed.emit(self.equipped, item, value, change)
        # self.update_values(_id)

    def clear(self):
        self.table.setRowCount(0)

    def update_values(self, data):
        self.clear()
        self.fill_table(data)


class ModifierItemView(View):

    def __init__(self, equipment_item):
        View.__init__(self)
        layout = QHBoxLayout()
        self.item = equipment_item
        self.name = equipment_item.ID
        name_layout = QVBoxLayout()
        name = QLabel(equipment_item.name)
        name_layout.addWidget(name)
        self.values_layout = QVBoxLayout()
        cost_layout = QVBoxLayout()
        cost = QLabel("TODO COST")
        cost_layout.addWidget(cost)
        layout.addLayout(name_layout)
        layout.addLayout(self.values_layout)
        layout.addLayout(cost_layout)
        checkbox_layout = QVBoxLayout()
        self.equipped_checkbox = QCheckBox()
        self.equipped_checkbox.setChecked(self.item.equipped)
        self.equipped_checkbox.stateChanged.connect(lambda x: self.update_parameters("equipped", x))
        checkbox_layout.addWidget(self.equipped_checkbox)
        layout.addLayout(checkbox_layout)
        self.setLayout(layout)
        for bonus in self.item.bonuses:
            view = PropertyView(bonus, self.item.bonuses[bonus])
            self.values_layout.addWidget(view)
        self.add_header_option("Edit", self.edit)
        self.setLayout(layout)

    def edit(self):
        self.edit_item.emit(self.item)

    def update_parameters(self, parameter, value):
        if parameter == "equipped":
            self.item_equipped.emit(self.item, value)


class PropertyView(QWidget):

    def __init__(self, name="", value=0):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(translate_parameter(name))
        self.value = QLabel(str(value))
        layout.addWidget(self.label)
        layout.addWidget(self.value)
        self.setLayout(layout)

