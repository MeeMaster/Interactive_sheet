from PyQt5.QtWidgets import (QPushButton, QWidget, QAction, QSpacerItem, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QLineEdit, QCheckBox, QMenu, QComboBox, QTextEdit, QTableWidget, QHeaderView,
                             QToolButton)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator, QColor, QDoubleValidator
# from parameters import translate, translate
from parameters import load_parameters, translate, is_types
from item_classes import BaseObject

param_dict = load_parameters()
armor_names = param_dict["armor"]


line_edit_style = "QLineEdit { background: rgba(255, 255, 255, 100); border-width: 0px;\
 alternate-background-color: rgba(200,200,200,50); font: bold 10px; margin: 0px;}"


class ScrollContainer(QWidget):
    item_created = pyqtSignal(str, object)
    item_equipped = pyqtSignal(str, object, bool)
    item_removed = pyqtSignal(str, object)
    item_edited = pyqtSignal(str, object)

    def __init__(self, name, button_text, content_widget, popup=None, label=None, **kwargs):
        QWidget.__init__(self)
        # self.parent = parent
        self.name = name
        self.kwargs = kwargs
        self.layout = QVBoxLayout()
        self.label = QLabel(translate(name))
        if label is not None:
            self.label = QLabel(translate(label))
        self.label.setStyleSheet("font: bold 14px")
        self.layout.addWidget(self.label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        if button_text is not None:
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
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def format_label(self, size=14, bold=True, italic=False):
        self.label.setStyleSheet("font: {} {} {}px".format("bold" if bold else "", "italic" if italic else "", size))

    def open_popup(self, edit=None):
        if self.popup is not None:
            self.kwargs["edit"] = edit
            self.current_popup = self.popup(kwargs=self.kwargs)
            # if edit is None:
            self.current_popup.popup_ok.connect(self.ok_clicked)
            # else:
            #     self.current_popup.popup_ok.connect(lambda: self.item_edited.emit())
            self.current_popup.popup_cancel.connect(self.close_popup)

    def ok_clicked(self, obj):
        if self.kwargs["edit"] is None:
            self.item_created.emit(self.name, obj)
        else:
            self.item_edited.emit(self.name, obj)
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
        widget.delete.connect(lambda x: self.item_removed.emit(self.name, x))
        widget.item_equipped.connect(lambda x, y: self.item_equipped.emit(self.name, x, y))
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

    def fill(self, items):
        for item in items:
            self.add_widget(item)

    def get_data(self):
        return [child.item for child in self.get_children()]


class ConditionalScrollContainer(ScrollContainer):

    def __init__(self, name, button_text, content_widget, conditions=[], popup=None, **kwargs):
        ScrollContainer.__init__(self, name, button_text, content_widget, popup, **kwargs)
        self.conditions = conditions
        self.kwargs = kwargs
        kwargs["include"] = conditions

    def fill(self, items):
        for item in items:
            ok = False
            if is_types(item, self.conditions):
                self.add_widget(item)


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
        if self.dtype == "equation":
            self.line.setValidator(MyEquationValidator(min_val, max_val))
        self.register_field(val_dict=val_dict)
        self.layout.addWidget(self.line)
        if spacer == "lower":
            self.layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        if spacer == "upper":
            self.layout.insertSpacerItem(0, QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def format_label(self, size=14, bold=True, italic=False):
        self.label.setStyleSheet("font: {} {} {}px".format("bold" if bold else "", "italic" if italic else "", size))

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

    def get_data(self):
        text = self.text()
        if self.dtype == "int":
            return int(text)
        if self.dtype == "float":
            return float(text)
        if self.dtype == "equation":
            return text
        return text


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
        self.item = ability
        self.name = ability.name
        layout = QVBoxLayout()
        self.display_name = translate(ability.name)  # TODO
        self.description = translate(ability.description)
        self.setToolTip(translate(ability.tooltip))
        self.display = QLineEdit()
        layout.addWidget(self.display)
        self.display_name += " {}".format(ability.value) if ability.value else ""
        self.display.setText(self.display_name)
        self.display.setEnabled(False)
        self.setLayout(layout)
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
        layout = QVBoxLayout()
        line1_layout = QHBoxLayout()
        line2_layout = QHBoxLayout()
        self.equipped_checkbox = EquippedCheckbox()
        self.equipped_checkbox.setChecked(self.item.equipped_quantity > 0)
        self.equipped_checkbox.stateChanged.connect(self.equip)
        line1_layout.addWidget(self.equipped_checkbox)
        self.weapon_name = LabelledLabel(label=translate("ui_item_name"))
        # self.weapon_name.setFixedWidth(120
        self.weapon_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        line1_layout.addWidget(self.weapon_name, stretch=0)
        self.weapon_type = LabelledLabel(label=translate("ui_weapon_type"))
        line1_layout.addWidget(self.weapon_type, stretch=0)
        self.weapon_damage = LabelledLabel(label=translate("ui_weapon_damage"))
        line1_layout.addWidget(self.weapon_damage, stretch=0)
        self.weapon_pp = LabelledLabel(label=translate("ui_weapon_ap"))
        line1_layout.addWidget(self.weapon_pp, stretch=0)
        self.weapon_damage_type = LabelledLabel(label=translate("ui_weapon_damage_type"))
        line1_layout.addWidget(self.weapon_damage_type, stretch=0)
        self.weapon_ammo_cost = LabelledLabel(label=translate("ui_weapon_shotcost"))
        line1_layout.addWidget(self.weapon_ammo_cost, stretch=0)
        self.weapon_current_power = LabelledLabel(label=translate("ui_weapon_magazine"))
        line1_layout.addWidget(self.weapon_current_power, stretch=0)
        self.weapon_weight = LabelledLabel(label=translate("ui_item_weight"))
        line2_layout.addWidget(self.weapon_weight, stretch=0)
        self.weapon_value = LabelledLabel(label=translate("ui_item_price"))
        line2_layout.addWidget(self.weapon_value, stretch=0)
        self.weapon_traits = LabelledLabel(label=translate("ui_item_traits"))
        self.weapon_traits.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        line2_layout.addWidget(self.weapon_traits, stretch=0)
        layout.addLayout(line1_layout, stretch=0)
        layout.addLayout(line2_layout, stretch=0)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.setContentsMargins(0, 0, 0, 0)
        self.fill_values()
        self.add_header_option("Edit", self.edit)
        self.setLayout(layout)

    def edit(self):
        self.edit_item.emit(self.item)

    def equip(self, equip):
        self.item_equipped.emit(self.item, equip)

    def fill_values(self):
        self.weapon_name.set_text(translate(self.item.display) if self.item.display else self.item.name)
        self.weapon_damage.set_text(str(self.item.damage))
        self.weapon_damage_type.set_text(self.item.damage_type)
        self.weapon_pp.set_text(str(self.item.ap))
        self.weapon_ammo_cost.set_text(str(self.item.shot_cost))
        self.weapon_current_power.set_text(str(self.item.power_magazine))
        self.weapon_value.set_text(str(self.item.price))
        self.weapon_weight.set_text(str(self.item.weight))
        self.equipped_checkbox.setChecked(self.item.equipped_quantity > 0)
        self.weapon_type.set_text(translate(self.item.weapon_type))


class ArmorView(View):

    def __init__(self, armor):
        View.__init__(self)
        self.name = armor.ID
        self.item = armor
        layout = QVBoxLayout()
        line1_layout = QHBoxLayout()
        line1_layout.setContentsMargins(0, 0, 0, 0)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(p)
        self.setAutoFillBackground(True)
        self.equipped_checkbox = EquippedCheckbox()
        self.equipped_checkbox.setChecked(self.item.equipped_quantity > 0)
        self.equipped_checkbox.stateChanged.connect(self.equip)
        line1_layout.addWidget(self.equipped_checkbox)

        self.armor_name = LabelledLabel(label=translate("ui_item_name"))
        self.armor_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        line1_layout.addWidget(self.armor_name)
        self.armor_parts = {}
        for armor_name in armor_names:
            armor_piece = LabelledLabel(label=translate(armor_name))
            self.armor_parts[armor_name] = armor_piece
            line1_layout.addWidget(armor_piece)
        self.weight = LabelledLabel(label=translate("ui_item_weight"))
        line1_layout.addWidget(self.weight)
        self.value = LabelledLabel(label=translate("ui_item_price"))
        line1_layout.addWidget(self.value)

        layout.addLayout(line1_layout)
        self.add_header_option("Edit", self.edit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fill_values()
        self.setLayout(layout)

    def edit(self):
        self.edit_item.emit(self.item)

    def equip(self, equip):
        self.item_equipped.emit(self.item, equip)

    def fill_values(self):
        self.armor_name.set_text(self.item.display)
        for armor_name in armor_names:
            self.armor_parts[armor_name].set_text(str(self.item.__dict__[armor_name]))
        self.value.set_text(str(self.item.price))
        self.weight.set_text(str(self.item.weight))
        self.equipped_checkbox.setChecked(self.item.equipped_quantity > 0)


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
        self.label = QLabel(translate("ui_item_equipped"))
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


class MyEquationValidator(QValidator):

    def __init__(self, m, n):
        QValidator.__init__(self)

    def validate(self, a0, a1):
        if a1 == 0:
            return QValidator.Acceptable, "+0.0", 1
        if a0[0] not in ["*", "/", "+", "-"]:
            try:
                val = round(float(a0), 1)
                return QValidator.Intermediate, str(val), a1
            except:
                return QValidator.Invalid, a0, a1
        else:
            try:
                val = round(float(a0[1:]), 1)
                return QValidator.Acceptable, a0[0]+str(val), a1
            except:
                return QValidator.Invalid, a0, a1
        # return QValidator.Invalid, a0, a1
        # if a1 > 1:

    def fixup(self, a0: str) -> str:
        try:
            val = round(float(a0), 1)
            return "+"+str(val)
        except:
            return ""
        pass

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

    def currentText(self):
        return self.box.currentText()

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

    def format_label(self, size=14, bold=True, italic=False):
        self.label.setStyleSheet("font: {} {} {}px".format("bold" if bold else "", "italic" if italic else "", size))

    def get_text(self):
        return self.text_edit.toPlainText()

    def set_text(self, text):
        if not text:
            return
        if isinstance(text, list):
            text = text[0]
        self.text_edit.setText(text)

    def get_data(self):
        return self.get_text()


class LabelledLabel(QWidget):

    def __init__(self, text="", align_flag=Qt.AlignLeft, label=None, spacer=None):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        if label is not None:
            self.label = QLabel(label)
            self.label.setWordWrap(True)
            self.label.setStyleSheet("font: 8px")
            self.label.setContentsMargins(0, 0, 0, 0)
            self.label.setAlignment(align_flag)
            layout.addWidget(self.label)
        self.text = QLabel()
        self.text.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text)
        if spacer == "lower":
            layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        if spacer == "upper":
            layout.insertSpacerItem(0, QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.setContentsMargins(0, 0, 0, 0)
        self.set_text(text)
        self.setLayout(layout)

    def set_text(self, text):
        self.text.setText(text)


class EquipmentWidget(QWidget):
    item_qty_changed = pyqtSignal(bool, str, int, bool)
    item_create = pyqtSignal(str, BaseObject)
    move_item = pyqtSignal(object, int)
    delete_item = pyqtSignal(bool, BaseObject)
    edit_item = pyqtSignal(str)

    def __init__(self, popup=None, transfer_popup=None):
        QWidget.__init__(self)
        layout = QVBoxLayout()
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
        label = QLabel(translate("ui_equipped_items"))
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
        label = QLabel(translate("ui_stashed_items"))
        label.setStyleSheet("font: bold 12px")
        label.setAlignment(Qt.AlignCenter)
        stash_table_layout.addWidget(label)
        stash_table_layout.addWidget(self.stash_table)
        button_left = QToolButton()
        button_left.setArrowType(Qt.UpArrow)
        button_left.clicked.connect(lambda: self.open_transfer_popup(True))
        button_left.setFixedWidth(40)
        button_right = QToolButton()
        button_right.setArrowType(Qt.DownArrow)
        button_right.clicked.connect(lambda: self.open_transfer_popup(False))
        button_right.setFixedWidth(40)
        button_add = QPushButton(translate("ui_add_item_button"))
        button_add.clicked.connect(self.open_popup)
        button_add.setFixedWidth(60)
        buttons_layout = QHBoxLayout()
        # buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        buttons_layout.addWidget(button_left)
        buttons_layout.addWidget(button_add)
        buttons_layout.addWidget(button_right)
        # buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        layout.addLayout(equipped_table_layout, 10)
        layout.addLayout(buttons_layout, 1)
        layout.addLayout(stash_table_layout, 10)
        self.setLayout(layout)

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
            if item.ID == current_item_id:
                found = True
                break
        if not found:
            return
        self.current_popup = self.transfer_popup(item, not equip)
        self.current_popup.popup_ok.connect(self.move_item_func)
        self.current_popup.popup_cancel.connect(self.close_popup)

    def item_edit(self, item_id):
        found = False
        for item in self.items:
            if item.ID == item_id:
                found = True
                break
        if not found:
            return
        self.open_popup(edit=item)
        self.current_popup.popup_ok.connect(self.add_item)
        self.current_popup.popup_cancel.connect(self.close_popup)

    def add_item(self, item):
        self.item_create.emit(item.name, item)
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

    def signal_delete(self, equipped, item_id):
        found = False
        for item in self.items:
            if item.ID == item_id:
                found = True
                break
        if not found:
            return
        self.delete_item.emit(equipped, item)

    def signal_forward(self, *args):
        self.item_qty_changed.emit(*args)

    def update_item_tables(self):
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
        self.table.setMinimumWidth(500)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        self.edit_item.emit(current_item_id)

    def remove_item(self):
        if self.table.currentRow() == -1:
            return
        current_item_id = self.table.cellWidget(self.table.currentRow(), 0).text()
        self.delete_item.emit(self.equipped, current_item_id)

    def get_table(self):
        self.table.setColumnCount(5)
        self.table.setSelectionBehavior(1)
        self.table.setHorizontalScrollBarPolicy(1)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels([translate("ui_item_name"), translate("ui_item_quantity"),
                                              translate("ui_item_name"),
                                              translate("ui_item_weight"),
                                              translate("ui_item_total_weight")])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def fill_table(self, data):
        data = [item for item in data if item.type == "item"]
        data_len = len([item for item in data if item.equipped_quantity > 0]) if self.equipped else \
            len([item for item in data if (item.total_quantity != item.equipped_quantity) or item.total_quantity == 0])
        self.table.setRowCount(data_len)
        index = 0
        for item in data:
            value = item.equipped_quantity if self.equipped else item.total_quantity - item.equipped_quantity
            if self.equipped and value == 0:
                continue
            if not self.equipped and value == 0 and item.total_quantity != 0:
                continue
            self.table.setCellWidget(index, 0, QLabel(item.ID))
            counter_widget = ItemCounter(item.ID)
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
            index += 1
        self.table.resizeRowsToContents()
        self.table.show()

    def item_changed(self, item, value, change=True):
        self.item_qty_changed.emit(self.equipped, item, value, change)

    def clear(self):
        self.table.setRowCount(0)

    def update_values(self, data):
        self.clear()
        self.fill_table(data)


class ModifierItemView(View):

    def __init__(self, equipment_item):
        View.__init__(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 1, 1, 1)
        self.item = equipment_item
        self.name = equipment_item.ID
        name_layout = QVBoxLayout()
        name = QLabel(equipment_item.name)
        name_layout.addWidget(name)
        self.values_layout = QVBoxLayout()
        cost_layout = QVBoxLayout()
        cost = QLabel("TODO COST")  # TODO
        cost_layout.addWidget(cost)
        layout.addLayout(name_layout)
        layout.addLayout(self.values_layout)
        layout.addLayout(cost_layout)
        checkbox_layout = QVBoxLayout()
        self.equipped_checkbox = QCheckBox()
        self.equipped_checkbox.setChecked(self.item.equipped_quantity > 0)
        self.equipped_checkbox.stateChanged.connect(lambda x: self.update_parameters("equipped", x))
        checkbox_layout.addWidget(self.equipped_checkbox)
        layout.addLayout(checkbox_layout)
        self.setLayout(layout)
        view = PropertyView(self.item.bonuses)
        self.values_layout.addWidget(view)
        # for bonus in :
        #

        self.add_header_option("Edit", self.edit)
        self.setLayout(layout)

    def edit(self):
        self.edit_item.emit(self.item)

    def update_parameters(self, parameter, value):
        if parameter == "equipped":
            self.item_equipped.emit(self.item, value)


class PropertyView(QWidget):

    def __init__(self, bonuses):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        names = [name for name in bonuses]
        if names:
            self.label = QLabel(translate(names[0]))
            self.value = QLabel(str(bonuses[names[0]]))
            self.cont = QLabel("...")
            layout.addWidget(self.label)
            layout.addWidget(self.value)
        if len(bonuses) > 1:
            layout.addWidget(self.cont)
        self.setToolTip("\n".join([translate(name)+": "+str(value) for name, value in bonuses.items()]))
        self.setLayout(layout)

