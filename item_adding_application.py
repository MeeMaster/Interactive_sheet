from popups import ItemListPopup, MyTreeWidgetItem
from parameters import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton)
from PyQt5.Qt import QAction
import sys
import parameters
from parameters import translate


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
        self.window_widget = ItemList(kwargs={"include": ["item"]})
        self.setCentralWidget(self.window_widget)
        self.setWindowTitle(translate("ui_item_creation_app"))
        file.triggered[QAction].connect(self.process_trigger)
        self.show()
        self.window_widget.popup_cancel.connect(lambda: self.close())

    def process_trigger(self, q):
        if q.text() == translate("ui_menu_save_sheet"):
            self.window_widget.save()


class ItemList(ItemListPopup):

    def __init__(self, kwargs):
        ItemListPopup.__init__(self, kwargs)
        parameters.read_all_objects(False)
        self.inheritance_dict = dict(parameters.ALL_OBJECTS_DICT)
        parameters.read_all_objects(True)
        self.full_data_dict = parameters.ALL_OBJECTS_DICT
        button = QPushButton(translate("ui_add_item"))
        button.clicked.connect(self.add_item_field)
        self.button_layout.insertWidget(1, button)

    def get_item(self, item, column):
        self.get_data(item, self.full_data_dict)
        self.update_grid()

    def add_item_field(self):
        new_name = "new_item"
        index = 0
        while new_name in self.full_data_dict:
            index += 1
            new_name = "new_item_{}".format(index)
        self.full_data_dict[new_name] = dict(self.current_item_data)
        self.full_data_dict[new_name]["parent"] = self.current_item_data["name"]
        self.full_data_dict[new_name]["name"] = new_name
        widget = MyTreeWidgetItem(self.tree_view.currentItem())
        widget.set_text(new_name)

    def ok_pressed(self):
        # Verify proper inheritance
        name = self.current_item_data["name"]
        new_name = self.grid_widget.fields["name"].get_data()
        if new_name != name:
            self.full_data_dict[new_name] = self.full_data_dict[name]
            self.inheritance_dict[new_name] = self.inheritance_dict[name]
            self.full_data_dict[new_name]["name"] = new_name
            self.inheritance_dict[new_name]["name"] = new_name
            del self.full_data_dict[name]
            del self.inheritance_dict[name]
            for child in get_children(name, self.full_data_dict):
                self.full_data_dict[child]["parent"] = new_name
                self.inheritance_dict[child]["parent"] = new_name
            self.tree_view.currentItem().set_text(new_name)

        # Change other fields
        for field_name, field in self.grid_widget.fields.items():
            if field_name == "name" or field_name == "parent":
                continue
            values = field.get_data()
            self.full_data_dict[new_name][field_name] = values
            for child in get_all_children(self.full_data_dict, new_name):
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
            with open("parameters/{}".format(filename.replace(".txt", "_saved.txt")), "w") as outfile:
                for item in item_list:
                    string_block = item.to_string_block()
                    outfile.write(string_block)


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
                string_block += "l_{} = {}\n".format(key, ", ".join([item for item in value]))
        string_block += "////\n\n"
        return string_block


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())