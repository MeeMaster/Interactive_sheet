from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction, QSpacerItem, QSizePolicy, QFrame,
                             QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFileDialog, QLineEdit, QTextEdit,
                             QTabWidget, QCheckBox, QMenu, QComboBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIntValidator, QValidator, QColor


line_edit_style = "QLineEdit { background: rgba(255, 255, 255, 100); border-width: 0px;\
 alternate-background-color: rgba(200,200,200,50); font: bold 10px; margin: 0px;}"


class ScrollContainer(QWidget):

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
                child.setParent(None)
                self.target_function("remove", name)  # TODO create a "handle widget" function in window

    def add_widget(self):
        if self.popup is not None:
            print(self.parent)
            self.current_popup = self.popup(self.parent.character)
            self.current_popup.popup_ok.connect(self._add_widget)
            self.current_popup.popup_cancel.connect(self.close_popup)
        else:
            self._add_widget("None")

    def close_popup(self):
        self.current_popup = None

    def _add_widget(self, widget_params):
        widget = self.content_widget(widget_params, self.parent.character)
        widget.delete.connect(self.remove_widget)
        self.scroll_widget.layout().addWidget(widget)
        self.current_popup = None


class View(QWidget):
    delete = pyqtSignal(str)

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

    def __init__(self, ability, character):
        View.__init__(self)
        self.name = ability["name"]
        layout = QVBoxLayout()
        self.display_name = ability["display"]
        self.requirements = ability["requirements"]
        self.description = ability["description"]
        self.setToolTip(self.description)
        self.display = QLineEdit()
        layout.addWidget(self.display)
        self.display.setText(self.display_name)
        self.display.setEnabled(False)
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        character.abilities.append(self.name)


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
        self.line.setText(value)

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


class WeaponView(View):

    def __init__(self, name="", display_name=None, val_dict=None):
        View.__init__(self)
        self.display_name = display_name if display_name is not None else name

        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(p)
        self.setAutoFillBackground(True)

        self.name = name
        self.val_dict = val_dict
        self.layout = QVBoxLayout()
        self.line1_layout = QHBoxLayout()
        self.line2_layout = QHBoxLayout()
        self.line3_layout = QHBoxLayout()
        self.weapon_name = InputLine("name", Qt.AlignLeft, label="Name")
        self.weapon_name.setFixedWidth(200)
        self.line1_layout.addWidget(self.weapon_name, stretch=0)
        self.weapon_type = InputLine("type", Qt.AlignLeft, label="Type")
        self.line1_layout.addWidget(self.weapon_type, stretch=0)
        self.weapon_damage = InputLine("damage", label="Damage")
        self.line1_layout.addWidget(self.weapon_damage, stretch=0)
        self.weapon_pp = InputLine("pp", dtype="int", label="AP")
        self.line1_layout.addWidget(self.weapon_pp, stretch=0)
        self.weapon_damage_type = InputLine("damage_type", Qt.AlignLeft, label="Dmg type")
        self.line1_layout.addWidget(self.weapon_damage_type, stretch=0)
        self.weapon_ammo_cost = InputLine("shoot_cost", dtype="int", label="Cost")
        self.line1_layout.addWidget(self.weapon_ammo_cost, stretch=0)
        self.weapon_current_power = InputLine("battery", dtype="int", label="Power")
        self.line1_layout.addWidget(self.weapon_current_power, stretch=0)
        self.weapon_current_gas = InputLine("gas", dtype="int", label="Gas")
        self.line1_layout.addWidget(self.weapon_current_gas, stretch=0)
        self.weapon_traits = InputLine("traits", Qt.AlignLeft, label="Traits")
        self.line2_layout.addWidget(self.weapon_traits, stretch=0)
        self.weapon_value = InputLine("value", dtype="int", label="Value", maxwidth=40)
        self.line2_layout.addWidget(self.weapon_value, stretch=0)
        self.weapon_weight = InputLine("weight", dtype="int", label="Weight")
        self.line2_layout.addWidget(self.weapon_weight, stretch=0)
        self.equipped_checkbox = EquippedCheckbox()
        self.line2_layout.addWidget(self.equipped_checkbox)
        self.layout.addLayout(self.line1_layout, stretch=0)
        self.layout.addLayout(self.line2_layout, stretch=0)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


class EquippedCheckbox(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.label = QLabel("Equipped")
        self.label.setStyleSheet("font: 8px")
        self.label.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.label)
        self.checkbox = QCheckBox()
        self.checkbox.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.checkbox)
        self.layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


class ArmorView(View):

    def __init__(self, name="", display_name=None, val_dict=None):
        View.__init__(self)
        self.display_name = display_name if display_name is not None else name
        self.name = name
        self.val_dict = val_dict

        self.setFixedWidth(400)
        self.layout = QVBoxLayout()
        self.line1_layout = QHBoxLayout()
        self.line1_layout.setContentsMargins(0, 0, 0, 0)
        self.line2_layout = QHBoxLayout()
        self.line2_layout.setContentsMargins(0, 0, 0, 0)
        self.armor_name = InputLine("name", Qt.AlignLeft, label="Name")
        self.line1_layout.addWidget(self.armor_name)
        self.armor_head = InputLine("Armor head", label="Head", maxwidth=30)
        self.line1_layout.addWidget(self.armor_head)
        self.armor_chest = InputLine("Armor chest", label="Chest", maxwidth=30)
        self.line1_layout.addWidget(self.armor_chest)
        self.armor_lh = InputLine("Armor lh", label="LH", maxwidth=30)
        self.line1_layout.addWidget(self.armor_lh)
        self.armor_rh = InputLine("Armor rh", label="RH", maxwidth=30)
        self.line1_layout.addWidget(self.armor_rh)
        self.armor_ll = InputLine("Armor ll", label="LL", maxwidth=30)
        self.line1_layout.addWidget(self.armor_ll)
        self.armor_rl = InputLine("Armor rl", label="RL", maxwidth=30)
        self.line1_layout.addWidget(self.armor_rl)
        self.weight = InputLine("weight", dtype="int", label="Weight", maxwidth=30)
        self.line2_layout.addWidget(self.weight)
        self.value = InputLine("value", dtype="int", label="Value", maxwidth=30)
        self.line2_layout.addWidget(self.value)
        self.traits = InputLine("traits", Qt.AlignLeft, label="Traits")
        self.line2_layout.addWidget(self.traits)
        self.equipped_checkbox = EquippedCheckbox()
        self.line2_layout.addWidget(self.equipped_checkbox)
        self.layout.addLayout(self.line1_layout)
        self.layout.addLayout(self.line2_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


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
