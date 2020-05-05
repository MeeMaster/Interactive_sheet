from PyQt5.QtWidgets import (QPushButton, QWidget, QSpacerItem, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel, QSlider)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from parameters import translate_ui, translate_parameter
from layout_classes import InputLine
import random
from os import path
base_path = path.split(path.abspath(__file__))[0]


modifier_ranges = list(range(-50, 50, 10))
distances = [">600", "300-600", "200-300", "100-200", "80-100", "50-80", "30-50", "20-30", "10-20", "0-10"]
distance_types = {"param_distance_extreme": [">600"],
                  "param_distance_far": ["300-600", "200-300", "100-200", "80-100"],
                  "param_distance_mid": ["50-80", "30-50", "20-30"],
                  "param_distance_close": ["10-20", "0-10"]}


class ShootingWidget(QWidget):
    closed = pyqtSignal(bool)

    def __init__(self, parent=None, character=None, weapon=None):
        QWidget.__init__(self)
        self.setWindowTitle(translate_ui("ui_shooting_app"))
        if parent is not None:
            self.setParent(parent)
        self.popup = None
        window_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        window_layout.addLayout(main_layout)
        window_layout.addLayout(buttons_layout)
        shoot_layout = QVBoxLayout()
        cover_layout = QVBoxLayout()
        main_layout.addLayout(shoot_layout)
        main_layout.addLayout(cover_layout)
        self.setLayout(window_layout)

        parameters_layout = QHBoxLayout()
        distance_view_layout = QVBoxLayout()
        distance_slider_layout = QVBoxLayout()
        shoot_layout.addLayout(parameters_layout)
        shoot_layout.addLayout(distance_view_layout)
        shoot_layout.addLayout(distance_slider_layout)

        # Left side
        # Params
        self.skill_value = InputLine("skill", enabled=True, maxwidth=80, dtype="int", spacer="upper",
                                     label=translate_ui("ui_ranged_skill_value"))
        self.skill_value.setText("0")
        self.skill_value.value_changed.connect(lambda: self.update_distances())
        self.gm_modifier = InputLine("gm_mod", enabled=True, dtype="int", maxwidth=80, spacer="upper",
                                     label=translate_ui("ui_gm_modifier"))
        self.gm_modifier.setText("0")
        self.gm_modifier.value_changed.connect(lambda: self.update_distances())
        self.break_chance = InputLine("break_chance", enabled=True, dtype="int", maxwidth=80, spacer="upper",
                                      label=translate_ui("ui_break_chance"))
        self.break_chance.setText("0")
        self.break_increment = InputLine("break_increment", enabled=True, dtype="int", spacer="upper",
                                         maxwidth=80, label=translate_ui("ui_break_increment"))
        self.break_increment.setText("0")
        if weapon is not None:
            skill = weapon.base_skill
            if character is not None:
                skill_value = character.calculate_skill(skill)
                self.skill_value.setText(skill_value)
        parameters_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        parameters_layout.addWidget(self.skill_value)
        parameters_layout.addWidget(self.gm_modifier)
        parameters_layout.addWidget(self.break_chance)
        parameters_layout.addWidget(self.break_increment)
        parameters_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Icon
        internal_widget = QWidget()
        internal_widget.setFixedHeight(300)
        distance_view_internal_layout = QHBoxLayout()
        internal_widget.setLayout(distance_view_internal_layout)
        distance_view_internal_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.icon = IconWidget(QPixmap(path.join(base_path, "Images", "Silhouette.png")))
        distance_view_internal_layout.addWidget(self.icon)
        distance_view_internal_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        distance_view_layout.addWidget(internal_widget)

        # Slider
        distance_values_layout = QHBoxLayout()
        slider_layout = QVBoxLayout()
        distance_slider_layout.addLayout(distance_values_layout)
        distance_slider_layout.addLayout(slider_layout)
        distance_values_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.current_distance = InputLine("distance", enabled=False,
                                          label=translate_ui("ui_distance_value"))
        distance_values_layout.addWidget(self.current_distance)
        self.current_distance_type = InputLine("distance_type", enabled=False,
                                               label=translate_ui("ui_distance_type"))
        distance_values_layout.addWidget(self.current_distance_type)
        self.current_distance_mod = InputLine("distance_modifier", enabled=False,
                                              label=translate_ui("ui_distance_modifier"))
        distance_values_layout.addWidget(self.current_distance_mod)
        distance_values_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.distance_slider = QSlider(Qt.Horizontal)
        self.distance_slider.setMinimum(-50)
        self.distance_slider.setMaximum(40)
        self.distance_slider.setTickPosition(QSlider.TicksBelow)
        self.distance_slider.setTickInterval(10)
        self.distance_slider.setSingleStep(10)
        self.distance_slider.setValue(0)
        self.distance_slider.valueChanged.connect(lambda: self.update_distances())
        slider_layout.addWidget(self.distance_slider)

        # Right side
        target_layout = QVBoxLayout()
        size_slider_layout = QVBoxLayout()
        target_layout.addLayout(size_slider_layout)
        icon_layout = QVBoxLayout()
        target_layout.addLayout(icon_layout)
        cover_slider_layout = QVBoxLayout()
        target_layout.addLayout(cover_slider_layout)
        main_layout.addLayout(target_layout)

        # Size slider
        size_slider_values_layout = QHBoxLayout()
        size_slider_slider_layout = QVBoxLayout()
        size_slider_layout.addLayout(size_slider_values_layout)
        size_slider_values_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.size_name = InputLine("size_name", label=translate_ui("ui_size_name"), enabled=False)
        size_slider_values_layout.addWidget(self.size_name)
        self.size_modifier = InputLine("size_modifier", label=translate_ui("ui_size_mod"), enabled=False)
        size_slider_values_layout.addWidget(self.size_modifier)
        size_slider_values_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        size_slider_layout.addLayout(size_slider_slider_layout)
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(0)
        self.size_slider.setMaximum(5)
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        self.size_slider.setTickInterval(1)
        self.size_slider.setSingleStep(1)
        self.size_slider.setValue(2)
        self.size_slider.valueChanged.connect(lambda: self.update_size())
        size_slider_slider_layout.addWidget(self.size_slider)
        # Icon
        cover_internal_widget = QWidget()
        cover_internal_widget.setFixedHeight(300)
        cover_view_internal_layout = QHBoxLayout()
        cover_internal_widget.setLayout(cover_view_internal_layout)
        cover_view_internal_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.trooper_icon = CoverIconWidget(QPixmap(path.join(base_path, "Images", "Stormtrooper.png")))
        cover_view_internal_layout.addWidget(self.trooper_icon)
        cover_view_internal_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        icon_layout.addWidget(cover_internal_widget)

        # Cover slider
        cover_slider_values_layout = QHBoxLayout()
        cover_slider_slider_layout = QVBoxLayout()
        cover_slider_layout.addLayout(cover_slider_values_layout)
        cover_slider_values_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.cover_name = InputLine("cover_name", label=translate_ui("ui_cover_name"), enabled=False)
        cover_slider_values_layout.addWidget(self.cover_name)
        self.cover_modifier = InputLine("cover_modifier", label=translate_ui("ui_cover_mod"), enabled=False)
        cover_slider_values_layout.addWidget(self.cover_modifier)
        cover_slider_values_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        cover_slider_layout.addLayout(cover_slider_slider_layout)
        self.cover_slider = QSlider(Qt.Horizontal)
        self.cover_slider.setMinimum(0)
        self.cover_slider.setMaximum(75)
        self.cover_slider.setTickPosition(QSlider.TicksBelow)
        self.cover_slider.setTickInterval(25)
        self.cover_slider.setSingleStep(25)
        self.cover_slider.setValue(0)
        self.cover_slider.valueChanged.connect(lambda: self.update_cover())
        cover_slider_slider_layout.addWidget(self.cover_slider)

        # Buttons
        self.current_hit_chance = InputLine("hit_chance", enabled=False, dtype="int",
                                            label=translate_ui("ui_hit_chance"))
        shoot_one_button = QPushButton(translate_ui("ui_shoot_once"))
        shoot_one_button.clicked.connect(self.shoot_one)
        shoot_series_button = QPushButton(translate_ui("ui_shoot_series"))
        shoot_series_button.clicked.connect(self.shoot_series)
        cancel_button = QPushButton(translate_ui("ui_cancel"))
        cancel_button.clicked.connect(self.close_self)
        buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        buttons_layout.addWidget(self.current_hit_chance)
        buttons_layout.addWidget(shoot_one_button)
        buttons_layout.addWidget(shoot_series_button)
        buttons_layout.addWidget(cancel_button)

        self.update_distances(True)
        self.update_size(True)
        self.update_cover(True)
        self.update_chance()

    def update_distances(self, warmup=False):
        slider_value = self.distance_slider.value()
        if slider_value % 10 != 0:
            slider_value = round(slider_value/10) * 10
            self.distance_slider.setValue(slider_value)
        index = modifier_ranges.index(slider_value)
        self.current_distance.setText(distances[index])
        self.current_distance_mod.setText((str(slider_value) if slider_value <= 0 else "+"+str(slider_value)))
        distance_type = [key for key in distance_types if distances[index] in distance_types[key]][0]
        self.current_distance_type.setText(translate_parameter(distance_type))
        self.icon.update_to_size(int(150/(len(distances)-index)))
        if not warmup:
            self.update_chance()

    def update_size(self, warmup=False):
        sizes = [-20, -10, 0, 10, 30, 50]
        size_names = [translate_parameter(a) for a in ["param_size_tiny", "param_size_small", "param_size_normal",
                      "param_size_large", "param_size_giant", "param_size_enormous"]]
        slider_value = self.size_slider.value()
        self.size_name.setText(size_names[slider_value])
        self.size_modifier.setText((str(sizes[slider_value]) if sizes[slider_value] <= 0
                                    else "+" + str(sizes[slider_value])))
        if not warmup:
            self.update_chance()

    def update_cover(self, warmup=False):
        cover_ranges = [0, 25, 50, 75]
        cover_modifiers = [0, -10, -20, -30]
        slider_value = self.cover_slider.value()
        if slider_value % 25 != 0:
            slider_value = round(slider_value / 25) * 25
            self.cover_slider.setValue(slider_value)
        index = cover_ranges.index(slider_value)
        self.cover_name.setText(str(cover_ranges[index])+"%")
        self.cover_modifier.setText(str(cover_modifiers[index]))
        if not warmup:
            self.update_chance()

    def sum_modifiers(self):
        chance = 0
        chance += int(self.skill_value.text())
        chance += int(self.gm_modifier.text())
        chance += int(self.current_distance_mod.text())
        chance += int(self.size_modifier.text())
        chance += int(self.cover_modifier.text())
        return chance

    def update_chance(self):
        chance = self.sum_modifiers()
        self.current_hit_chance.setText(str(chance)+"%")

    def shoot_one(self):
        chance = self.sum_modifiers()
        break_chance = 100 - int(self.break_chance.text())
        hit, hits, broken = get_shots(chance, 1, weapon_base_damage_threshold=break_chance)
        self.popup = OutcomeWidget(1, hit, hits, broken)
        self.popup.closed.connect(self.close_popup)

    def shoot_series(self):
        chance = self.sum_modifiers()
        break_chance = 100 - int(self.break_chance.text())
        heat_increment = int(self.break_increment.text())
        hit, hits, broken = get_shots(chance, 10,
                                      weapon_base_damage_threshold=break_chance, weapon_heat_rate=heat_increment)
        self.popup = OutcomeWidget(10, hit, hits, broken)
        self.popup.closed.connect(self.close_popup)

    def close_popup(self, val):
        self.popup = None

    def close_self(self):
        self.closed.emit(True)
        # self.close()


class IconWidget(QWidget):

    def __init__(self, pixmap: QPixmap):
        QWidget.__init__(self)
        self.pixmap = pixmap
        layout = QVBoxLayout()
        self.icon = QLabel()
        layout.addWidget(self.icon)
        self.setLayout(layout)

    def update_to_size(self, size: int):
        p = self.pixmap.scaledToHeight(size)
        self.icon.setPixmap(p)


class CoverIconWidget(QWidget):

    def __init__(self, pixmap: QPixmap):
        QWidget.__init__(self)
        self.pixmap = pixmap
        layout = QVBoxLayout()
        self.icon = QLabel()
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.icon)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        p = self.pixmap.scaledToHeight(250)
        self.icon.setPixmap(p)
        self.setLayout(layout)


class OutcomeWidget(QWidget):
    closed = pyqtSignal(bool)

    def __init__(self, num_shots, success_first, success_remain, overheat):
        QWidget.__init__(self)
        self.setWindowTitle(translate_ui("ui_outcome_widget_name"))
        layout = QVBoxLayout()
        values_layout = QHBoxLayout()
        ok_button_layout = QVBoxLayout()
        layout.addLayout(values_layout)
        layout.addLayout(ok_button_layout)

        shots = "{}: {}".format(translate_ui("ui_num_shots_fired"), num_shots)
        label = QLabel(shots)
        values_layout.addWidget(label)

        success_first_shot = "{}: {}".format(translate_ui("ui_num_successes_first"), success_first)
        label_hit_1 = QLabel(success_first_shot)
        values_layout.addWidget(label_hit_1)

        if num_shots > 1:
            success_remaining_shots = "{}: {}".format(translate_ui("ui_num_successes_remaining"), success_remain)
            label_hit_rem = QLabel(success_remaining_shots)
            values_layout.addWidget(label_hit_rem)

        if overheat:
            overheat = "{}: {}".format(translate_ui("ui_overheated_on"), overheat)
            label_overheat = QLabel(overheat)
            values_layout.addWidget(label_overheat)

        ok_button = QPushButton("OK")
        ok_button_layout.addWidget(ok_button)
        ok_button.clicked.connect(self.close_popup)

        self.setLayout(layout)
        self.show()

    def close_popup(self):
        self.closed.emit(True)
        self.close()


def get_shots(chance, num_shots, per_shot_modifier=-40, weapon_base_damage_threshold=98, weapon_heat_rate=0):
    roll = random.randint(1, 101)
    hit_1 = (chance - roll) // 10 + 1 if roll <= chance or roll <= 5 else 0
    hits = 0
    overheated = 0
    if roll > weapon_base_damage_threshold:
        overheated = 1
    for n in range(num_shots-1):
        heat_roll = random.randint(1, 101)
        roll = random.randint(1, 101)
        if heat_roll > (weapon_base_damage_threshold - (n+2) * weapon_heat_rate):
            overheated = n+2
            break
        hits += 1 if roll <= chance - per_shot_modifier or roll <= 5 else 0
    return hit_1, hits, overheated
