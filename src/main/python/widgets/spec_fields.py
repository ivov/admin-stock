from PyQt5 import QtWidgets, QtCore, QtGui
from utils import db_manager


class AutocapField(QtWidgets.QLineEdit):
    """A QLineEdit that autocapitalizes input and has completers."""

    def __init__(self, placeholder_text):
        super(AutocapField, self).__init__(placeholder_text)
        self.setText("")
        self.setPlaceholderText(placeholder_text)
        self.textChanged.connect(self.autocapitalize)

    def autocapitalize(self):
        uppercase_text = self.text().upper()
        self.setText(uppercase_text)

    def set_completer(self, **kwargs):
        source = kwargs.get("source")
        db = db_manager.DB_Manager()
        if source == "comps in stock":
            string_list = db.get_all_display_names_for_components()
        elif source == "comps in movements":
            string_list = db.get_components_mentioned_in_movements()
        elif source == "recipes":
            string_list = db.get_all_recipes_as_display()
        db.close_connection()
        model = QtCore.QStringListModel()
        model.setStringList(string_list)
        completer = QtWidgets.QCompleter()
        completer.setModel(model)
        self.setCompleter(completer)


class StockNumberField(QtWidgets.QLineEdit):
    """A QLineEdit with a validator for admissible stock numbers."""

    def __init__(self, placeholder_text):
        super(StockNumberField, self).__init__(placeholder_text)
        self.setText("")
        self.setPlaceholderText(placeholder_text)
        numeric_validator = QtGui.QRegExpValidator(
            QtCore.QRegExp("[0-9]{1,6}([,][0-9]{1,2})?"), self
        )
        self.setValidator(numeric_validator)
