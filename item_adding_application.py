from popups import ItemListPopup, MyTreeWidgetItem
from parameters import *
import popups
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QAction)
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(translate("ui_item_adding_app"))
        bar = self.menuBar()
        file = bar.addMenu(translate("ui_menu_file"))
        save = QAction(translate("ui_menu_save_sheet"), self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        # Add main widget
        self.window_widget = ItemList(kwargs={"include": ["base_object"], "edit": None})
        self.setCentralWidget(self.window_widget)
        self.setWindowTitle(translate("ui_item_creation_app"))
        file.triggered[QAction].connect(self.process_trigger)
        self.show()
        self.window_widget.popup_cancel.connect(lambda: self.close())

    def process_trigger(self, q):
        if q.text() == translate("ui_menu_save_sheet"):
            self.window_widget.save()
            self.statusBar().showMessage("Saved", 5000)


class ItemList(ItemListPopup):

    def __init__(self, kwargs):
        ItemListPopup.__init__(self, kwargs)
        self.translations = {}
        self.read_translations()
        global translate
        translate = self.translate
        popups.translate = self.translate
        button = QPushButton(self.translate("ui_remove_item"))
        button.clicked.connect(self.remove_item)
        self.button_layout.insertWidget(1, button)
        self.read_all_items()

    def read_translations(self, locale="PL"):
        locale_file = path.join("locales", "translations_{}.csv".format(locale))
        if not path.exists(locale_file):
            # print("Could not localize locale file '{}'".format(locale_file))
            locale_file = path.join("locales", "translations_{}.csv".format("EN"))
        with codecs.open(locale_file, "r", encoding="windows-1250", errors='ignore') as infile:
            for line in infile:
                if not line.strip():
                    continue
                if line.strip().startswith("#"):
                    continue
                read_name, translation = line.strip().split(";")
                self.translations[read_name] = translation

    def remove_item(self):
        pass

    def translate(self, name):
        if name in self.translations:
            if self.translations[name].strip():
                return self.translations[name]
        return name

    def get_item(self, item, column):
        self.get_data(item, self.full_data_dict)
        self.update_grid()

    def ok_pressed(self):
        # Verify proper inheritance
        new_name = self.update_inheritance()
        # Change other fields
        self.update_object_fields(new_name)
        curr_item = self.tree_view.currentItem()
        curr_item.set_text(curr_item.name)
        # print(sel)

    def update_object_fields(self, new_name):
        for field_name, field in self.grid_widget.fields.items():
            if field_name == "name" or field_name == "parent":
                continue
            if field_name == "tooltip" or field_name == "description" or field_name == "display":
                if field_name == "tooltip":
                    prefix = "tooltip_"
                elif field_name == "description":
                    prefix = "desc_"
                elif field_name == "display":
                    prefix = ""
                translation_name = prefix+new_name
                self.full_data_dict[new_name][field_name] = translation_name
                self.translations[translation_name] = field.get_data()
                continue
            values = field.get_data()
            self.full_data_dict[new_name][field_name] = values
            for child in get_all_children(new_name, self.full_data_dict):
                if field_name not in self.inheritance_dict[child]:
                    self.full_data_dict[child][field_name] = values

    def save(self):
        already_saved = []
        file_handles = {}
        for item_name, full_data in self.full_data_dict.items():

            def write_parent_data(name):
                data = self.full_data_dict[name]
                parent_name = data["parent"]
                if parent_name and parent_name not in already_saved:
                    write_parent_data(parent_name)
                parent_data = self.full_data_dict[parent_name] if parent_name else {}
                writer_object = ClassWriterObject()
                writer_object.name = name
                writer_object.parent = parent_name
                writer_object.source = data["source"]
                for key, value in data.items():
                    # if isinstance(value,)
                    if key not in parent_data or parent_data[key] != value:
                        writer_object.values[key] = value
                already_saved.append(name)
                if writer_object.source not in file_handles:
                    file_handles[str(writer_object.source)] = []
                file_handles[str(writer_object.source)].append(writer_object)

            write_parent_data(item_name)

        for filename, item_list in file_handles.items():
            with open("parameters/{}".format(filename), "w") as outfile:
                for item in item_list:
                    string_block = item.to_string_block()
                    outfile.write(string_block)

        with codecs.open("locales/translations_{}.csv".format("PL"),
                         "w", encoding="windows-1250", errors='ignore') as outfile:
            for key in sorted(self.translations.keys()):
                outfile.write(key+";"+self.translations[key]+"\n")


class ClassWriterObject:

    def __init__(self):
        self.name = None
        self.parent = None
        self.values = {}
        self.source = None

    def to_string_block(self):
        string_block = "{}:{}\n".format(self.name, self.parent)
        for key, value in self.values.items():
            if key == "parent" or key == "source":
                continue
            if isinstance(value, int):
                string_block += "i_{} = {}\n".format(key, value)
            if isinstance(value, float):
                string_block += "f_{} = {}\n".format(key, value)
            if isinstance(value, str):
                string_block += "t_{} = {}\n".format(key, value)
            if isinstance(value, list):
                output_list = []
                for item in value:
                    if isinstance(item, str):
                        output_list.append(item)
                    elif isinstance(item, BaseObject):
                        output_list.append(item.name + " {}".format(item.value) if item.value else item.name)
                string_block += "l_{} = {}\n".format(key, ", ".join(output_list))
        string_block += "////\n\n"
        return string_block


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())