from PyQt5 import QtWidgets, QtCore
from widgets.message_boxes import WarningBox, QuestionBox
from widgets.spec_fields import AutocapField, StockNumberField
from utils.styling import criticals_title_style, criticals_subtitle_style
from utils import utils_collection as utils
from utils import db_manager
from utils import tests


class CriticalCompsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CriticalCompsDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedWidth(300)

        header_layout = QtWidgets.QVBoxLayout()

        title = QtWidgets.QLabel("Componentes críticos")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(criticals_title_style)

        subtitle = QtWidgets.QLabel(
            "Resalta en naranja los componentes con stock total\nigual o menor al valor crítico."
        )
        subtitle.setStyleSheet(criticals_subtitle_style)
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        self.criticals_holder_layout = QtWidgets.QVBoxLayout()
        criticals_button_layout = QtWidgets.QHBoxLayout()

        add_critical_button = QtWidgets.QPushButton("+ Agregar")
        add_critical_button.setShortcut("Alt+a")
        save_criticals_button = QtWidgets.QPushButton("≡ Guardar")
        save_criticals_button.setShortcut("Alt+g")
        save_criticals_button.setDefault(True)
        criticals_button_layout.addWidget(add_critical_button)
        criticals_button_layout.addWidget(save_criticals_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addLayout(self.criticals_holder_layout)
        layout.addLayout(criticals_button_layout)

        self.setLayout(layout)

        add_critical_button.clicked.connect(self.add_critical_holder)
        save_criticals_button.clicked.connect(self.save_criticals_step_1)

        db = db_manager.DB_Manager()
        self.stored_criticals = db.get_stored_criticals()
        self.existing_comps = db.get_all_display_names_for_components()
        db.close_connection()

        if self.stored_criticals:
            for i in self.stored_criticals.items():
                self.add_critical_holder()

            for i, l in enumerate(self.criticals_holder_layout.children()):
                l.itemAt(0).widget().setText(list(self.stored_criticals.keys())[i])
                l.itemAt(1).widget().setText(
                    str(list(self.stored_criticals.values())[i]).replace(".0", "")
                )

    def save_criticals_step_1(self):
        if not self.criticals_holder_layout.children():
            db = db_manager.DB_Manager()
            db.delete_all_criticals()
            self.stored_criticals = {}
            db.close_connection()
            utils.color_criticals_in_orange_in_main_section(
                self.parent().table, self.stored_criticals
            )
            self.close()
        elif self.criticals_holder_layout.children():
            contents_of_all_line_edits = []
            for l in self.criticals_holder_layout.children():
                contents_of_all_line_edits.append(l.itemAt(0).widget().text())
                contents_of_all_line_edits.append(l.itemAt(1).widget().text())

            if tests.test_if_duplicated_first_value_in_line_items_contents(
                contents_of_all_line_edits
            ):
                WarningBox(
                    "Componentes duplicados",
                    "Borrar uno de los\ncomponentes duplicados.",
                ).exec_()
            elif all(contents_of_all_line_edits):
                self.save_criticals_step_2()
            else:
                self.fix_empty_field_mid_save()

    def save_criticals_step_2(self):
        unrecognized_comp_alert = WarningBox(
            "Componente no reconocido", "Cargar el componente\ndesde el autocompletado."
        )
        new_criticals = {}
        for l in self.criticals_holder_layout.children():
            component = l.itemAt(0).widget().text()
            amount = float(l.itemAt(1).widget().text().replace(",", "."))
            new_criticals[component] = amount

        if not set(new_criticals).issubset(self.existing_comps):
            unrecognized_comp_alert.exec_()
        if set(new_criticals).issubset(self.existing_comps):
            if self.stored_criticals == new_criticals:
                self.close()
        if self.stored_criticals != new_criticals:
            db = db_manager.DB_Manager()
            db.delete_all_criticals()
            number_of_criticals = len(new_criticals)
            endstring = (
                "valor crítico" if number_of_criticals == 1 else "valores críticos"
            )
            config_record_details = str(number_of_criticals) + " " + endstring
            db.save_new_criticals(new_criticals)
            self.stored_criticals = new_criticals
            db.log_new_config_record(
                config="Edición de críticos", details=config_record_details
            )
            db.close_connection()
            utils.color_criticals_in_orange_in_main_section(
                self.parent().table, self.stored_criticals
            )
            self.close()

    def fix_empty_field_mid_save(self):
        empty_field_alert = WarningBox(
            "Campo vacío", "Completar o borrar campos\nvacíos antes de guardar."
        )
        for layout in self.criticals_holder_layout.layout().children():
            layout_1_text = layout.itemAt(0).widget().text()
            layout_2_text = layout.itemAt(1).widget().text()
            if layout_1_text == "":
                if layout_2_text == "":
                    utils.delete_layout(layout)
                    self.adjustSize()
                    self.adjustSize()
                    self.save_criticals_step_2()
            elif layout_1_text == "" or layout_2_text == "":
                empty_field_alert.exec()
                break

    def add_critical_holder(self):
        single_holder_layout = QtWidgets.QHBoxLayout()

        component_field = AutocapField("Componente...")
        component_field.setFixedWidth(175)
        component_field.setFocus()

        single_holder_layout.addWidget(component_field)

        value_field = StockNumberField("Valor...")
        value_field.setFixedWidth(65)

        single_holder_layout.addWidget(value_field)

        close_button = QtWidgets.QPushButton("×")
        close_button.setFixedWidth(20)

        single_holder_layout.addWidget(close_button)

        close_button.clicked.connect(self.remove_critical_holder)

        self.criticals_holder_layout.addLayout(single_holder_layout)

        for l in self.criticals_holder_layout.children():
            each_component_field = l.itemAt(0).widget()
            each_component_field.set_completer(source="comps in stock")

    def remove_critical_holder(self):
        selected_comp = ""
        selected_amount = ""

        for l in self.criticals_holder_layout.layout().children():
            if l.itemAt(2).widget() == self.sender():
                selected_comp = l.itemAt(0).widget().text()

        for l in self.criticals_holder_layout.layout().children():
            if l.itemAt(2).widget() == self.sender():
                selected_amount = l.itemAt(1).widget().text()

        clicked_button = self.sender()

        if selected_comp != "":
            pass
        if selected_amount != "":
            box = QuestionBox(
                "Confirmación",
                f"¿Borrar...?\nComponente: {selected_comp}\nValor crítico: {selected_amount}",
            )
            box.exec_()
            if box.clickedButton() == box.button(QtWidgets.QMessageBox.Yes):
                for layout in self.criticals_holder_layout.layout().children():
                    if layout.itemAt(2).widget() == clicked_button:
                        utils.delete_layout(layout)
                        self.adjustSize()
                        self.adjustSize()

            elif box.clickedButton() == box.button(QtWidgets.QMessageBox.No):
                pass
        else:
            for layout in self.criticals_holder_layout.layout().children():
                if layout.itemAt(2).widget() == clicked_button:
                    utils.delete_layout(layout)
                    self.adjustSize()
                    self.adjustSize()
