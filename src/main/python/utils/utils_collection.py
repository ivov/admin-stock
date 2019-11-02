import re
from PyQt5 import QtGui, QtCore, QtWidgets


def format_display_name_into_sql_name(display_name):
    separators_regex = re.compile("[-,/. ]")
    return separators_regex.sub("_", display_name)


def format_number_for_calculation(number):
    """Takes a number in a Spanish-formatted string and returns it as a float."""
    return float(number.replace(".", "").replace(",", "."))


def format_number_for_display(number):
    """Takes a number as a float and returns it as a Spanish-formatted string."""
    number = str(number).replace(".", "!").replace(",", ".").replace("!", ",")
    if number.endswith(",0"):
        return number.replace(",0", "")
    elif number.endswith(",00"):
        return number.replace(",00", "")
    else:
        return number


def populate_table_column_with_list_of_strings(table, col_num, input_list):
    """Takes a list of strings and populates a table column item with each string."""
    for row_number, data in enumerate(input_list):
        item = QtWidgets.QTableWidgetItem(data)
        table.setItem(row_number, col_num, item)
        item.setTextAlignment(QtCore.Qt.AlignCenter)


def populate_table_column_with_list_of_integers(table, col_num, input_list, **kwargs):
    """Takes a list of integers and populates a table column item with each string."""
    with_plus = kwargs.get("with_plus", False)
    with_minus = kwargs.get("with_minus", False)
    for row_number, data in enumerate(input_list):
        if with_plus:
            data = "+" + format_number_for_display(data)
        elif with_minus:
            data = "–" + format_number_for_display(data)
        else:
            data = format_number_for_display(data)
        item = QtWidgets.QTableWidgetItem(data)
        table.setItem(row_number, col_num, item)
        item.setTextAlignment(QtCore.Qt.AlignCenter)


def populate_model_column_with_list_of_items(model, col_num, input_list):
    """Takes a list of strings and populates a table view column item with each string."""
    for row_number, data in enumerate(input_list):
        item = QtGui.QStandardItem(data)
        model.setItem(row_number, col_num, item)
        item.setTextAlignment(QtCore.Qt.AlignCenter)


def give_light_blue_color_to_found_item_row(table, found_item, **kwargs):
    """Give light blue color to found item row, except if orange or yellow. The flag keep_light_blue_color=True prevents color reset, used for component deletion."""
    for i in range(table.columnCount()):
        row = table.item(found_item.row(), i)
        row_color = row.background().color()
        if not row_color == QtGui.QColor("orange"):
            if row_color == QtGui.QColor("yellow"):
                pass
            else:
                row.setForeground(QtGui.QColor("black"))
                row.setBackground(QtGui.QColor("#99ccff"))
    if kwargs.get("keep_light_blue_color", False):
        return
    QtCore.QTimer.singleShot(5000, lambda: reset_row_color(table, found_item))


def reset_row_color(table, found_item):
    """Reset color of found item row from light blue to white."""
    for i in range(table.columnCount()):
        table.item(found_item.row(), i).setForeground(QtGui.QColor("black"))
        table.item(found_item.row(), i).setBackground(QtGui.QColor("white"))


def color_criticals_in_orange_in_main_section(table, criticals):
    """Takes table as a widget and critical values as a dict and colors in orange the background of critical items in main table."""
    if criticals:
        for key in criticals.keys():
            for i in range(table.rowCount()):
                for j in range(table.columnCount()):
                    if table.item(i, j).background().color() != QtGui.QColor("yellow"):
                        if table.item(i, 0).text() == key:
                            if (
                                int(table.item(i, 1).text().replace(".", ""))
                                <= criticals[key]
                            ):
                                table.item(i, j).setForeground(QtGui.QColor("black"))
                                table.item(i, j).setBackground(QtGui.QColor("orange"))
                    elif table.item(i, 0).text() == key:
                        if (
                            int(table.item(i, 1).text().replace(".", ""))
                            > criticals[key]
                        ):
                            table.item(i, j).setForeground(QtGui.QColor("black"))
                            table.item(i, j).setBackground(QtGui.QColor("white"))
                    elif table.item(i, 0).text() not in criticals:
                        table.item(i, j).setForeground(QtGui.QColor("black"))
                        table.item(i, j).setBackground(QtGui.QColor("white"))

    elif not criticals:
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                if table.item(i, j).background().color() != QtGui.QColor("yellow"):
                    table.item(i, j).setBackground(QtGui.QColor("white"))
                    table.item(i, j).setForeground(QtGui.QColor("black"))


def color_zeros_in_grey_in_main_section(table, criticals):
    """Colors in grey the foreground of zero items in main table, unless zero item is critical."""
    for i in range(table.rowCount()):
        for j in range(table.columnCount()):
            if table.item(i, j).text() == "0":
                table.item(i, j).setForeground(QtGui.QColor("#80807f"))

    for x in range(table.rowCount()):
        for y in range(table.columnCount()):
            if table.item(x, 0).text() in criticals:
                table.item(x, y).setForeground(QtGui.QColor("black"))
                table.item(x, y).setBackground(QtGui.QColor("orange"))


def color_excluded_in_yellow_in_main_section(table, excluded_state, unused_comps):
    for comp in unused_comps:
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                if table.item(i, 0).text() == comp:
                    if excluded_state == "on":
                        table.item(i, j).setBackground(QtGui.QColor("yellow"))
                        table.item(i, j).setForeground(QtGui.QColor("black"))
                    elif excluded_state == "off":
                        if table.item(i, 0).text() == comp:
                            table.item(i, j).setBackground(QtGui.QColor("white"))


def scroll_to_row_in_table(table, text, **kwargs):
    found_item_list = table.findItems(text, QtCore.Qt.MatchExactly)
    found_item = found_item_list[0]
    table.scrollToItem(found_item, QtWidgets.QAbstractItemView.PositionAtTop)
    give_light_blue_color_to_found_item_row(
        table,
        found_item,
        keep_light_blue_color=kwargs.get("keep_light_blue_color", False),
    )


def get_month_number(month_name):
    """Takes a month name as a string and returns its number as a string."""
    month_name_and_number = {
        "Enero": "1",
        "Febrero": "2",
        "Marzo": "3",
        "Abril": "4",
        "Mayo": "5",
        "Junio": "6",
        "Julio": "7",
        "Agosto": "8",
        "Septiembre": "9",
        "Octubre": "10",
        "Noviembre": "11",
        "Diciembre": "12",
    }
    return month_name_and_number[month_name]


def get_line_items_contents(holder_layout, **kwargs):
    """Takes a layout containing at least one layout with two fields and a button, and returns the contents of those fields as a list of strings. If the 'as_dictionary' flag is set, the function returns the contents of those field as a dict of strings and floats."""
    as_dictionary = kwargs.get("as_dictionary", False)
    contents_of_all_fields = []
    for l in holder_layout.children():
        contents_of_all_fields.append(l.itemAt(0).widget().text())
        contents_of_all_fields.append(l.itemAt(1).widget().text())

    if as_dictionary:
        first_values = contents_of_all_fields[0::2]
        second_values = contents_of_all_fields[1::2]
        second_values_as_floats = [float(i) for i in second_values]
        return dict(zip(first_values, second_values_as_floats))
    else:
        return contents_of_all_fields


def remove_three_widget_layout(layout):
    """Takes a layout, deletes all its sublayouts and deletes the layout, used mainly for deleting a field-field-button line."""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    layout.setParent(None)


def delete_layout(layout):
    """Takes in a layout with children, deletes children and layout."""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    layout.setParent(None)


def remove_layout(layout):
    while 1:
        child = layout.count() and layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            remove_layout(child.layout())
