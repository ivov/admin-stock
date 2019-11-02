main_column_menu_style = """
    QMenu {
        width: 139px;
        background-color: rgb(221, 221, 221);
        border: 1px solid rgb(171, 171, 171);
    } QMenu::item {
        padding-left: 10px;
        height:23px;
        width: 139px;
    } QMenu::item:selected {
        background-color:rgb(50, 50, 50);
        color: white;
    }
"""

main_section_title_style = """
    QLabel {
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 10px;
    }
"""

main_section_menu_style = """
    QMenu {
        width: 125px;
        background-color: rgb(221, 221, 221);
        border: 1px solid rgb(171, 171, 171);
    } QMenu::item:selected {
        background-color: rgb(50, 50, 50);
    }
"""

main_section_table_style = """
    QTableWidget {
        border: 1px solid #acacac;
    }
"""

criticals_title_style = """
    QLabel {
        font-weight: bold;
        margin-bottom: 5px;
    }"
"""

criticals_subtitle_style = """
    QLabel {
        margin-bottom: 15px;
    }
"""

statusbar_style = """
    QStatusBar {
        min-height: 20px;
        padding-bottom: 10px;
        background-color: white;
        border-top: 1px solid #acacac;
    } QStatusBar::item {
        border: 0;
    }
"""

statusbar_first_label_style = """
    QLabel {
        font-weight: bold;
        padding-left: 12px;
        margin-right: 4px;
    }
"""

statusbar_bold_label_style = """
    QLabel {
        font-weight: bold;
        margin-left: 12px;
    }
"""

statusbar_last_label_style = """
    QLabel {
        padding-right: 12px;
    }
"""

statusbar_during_quick_message_style = """
    QStatusBar {
        min-height: 20px;
        padding-bottom: 10px;
        background-color: #88c0d0;
        border-top: 1px solid #acacac;
    } QStatusBar::item {
        border: 0;
    }
"""

statusbar_quick_message_label_style = """
    QLabel {
        font-weight: bold;
        padding-left: 12px;
        margin-right: 4px;
        padding-bottom: 2px;
    }
"""

excluded_dialog_title_style = """
    QLabel {
        font-weight: bold;
        margin-bottom: 5px;
    }
"""

excluded_dialog_subtitle_style = """
    QLabel {
        margin-bottom: 5px;
    }
"""

initdb_dialog_title_style = """
    QLabel {
        font-weight: bold;
        margin-bottom: 10px;
    }
"""

rename_user_dialog_title_style = """
    QLabel {
        font-weight: bold;
        margin-bottom: 10px;
    }
"""

movements_dialog_title_style = """
    QLabel {
        font-weight: bold;
    }
"""

movements_dialog_groupbox_filter_selected_style = """
    QGroupBox {
        font-weight: bold;
        border: 1px solid black;
        margin: 10px 0px;
    } QGroupBox::Title {
        subcontrol-position: top center;
        subcontrol-origin: margin;
        bottom: -3px;
        padding: 0px 10px;
    }
"""

movements_dialog_table_view_style = """
    QTableView {
        gridline-color: white;
    }
"""

movements_dialog_date_selection_subdialog_style = """
    QGroupBox {
        border: 0.5px solid gray;
        margin-top: 10px;
        margin-bottom: 5px;
        margin-left: 30px;
        margin-right: 30px;
    } QGroupBox::Title {
        subcontrol-position: top center;
        subcontrol-origin: margin;
        bottom: -3px;
        padding: 0px 10px;
    }
"""

movements_dialog_stats_subdialog_title_style = """
    QLabel {
        font-weight: bold;
        margin-bottom: 5px;
    }
"""

movements_dialog_stats_subdialog_averages_button_style = """
    QPushButton {
        margin-bottom: 20px;
        min-height: 22px;
    }
"""

comp_details_dialog_title_style = """
    QLabel {
        margin-bottom: 7px;
        font-weight: bold
    }
"""

generic_title_style = """
    QLabel {
        font-weight: bold;
        margin-bottom: 10px;
    }
"""

generic_groupbox_normal_style = """
    QGroupBox {
        font-weight: normal;
        border: 0.5px solid gray;
        margin: 10px 0px;
    } QGroupBox::Title {
        subcontrol-position: top center;
        subcontrol-origin: margin;
        bottom: -3px;
        padding: 0px 10px;
    }
"""

generic_messagebox_style = """
    QMessageBox {
        background-color: #f0f0f0;
    }
"""

edit_input_dialog_subtitle_style = """
    QLabel {
        margin-bottom: 5px;
        font-weight: bold;
    }
"""

edit_confirmation_box_label_bold_style = """
    QLabel {
        margin-bottom: 10px;
        font-weight: bold;
    }
"""

edit_confirmation_box_label_normal_style = """
    QLabel {
        margin-bottom: 5px;
    }
"""

delete_component_dialog_label_normal_style = """
    QLabel {
        margin-bottom: 5px;
    }
"""

delete_component_dialog_label_bold_style = """
    QLabel {
        margin-bottom: 5px;
        font-weight: bold;
    }
"""

outgoing_dialog_table_left_title_style = """
    QLabel {
        margin: 10px 10px 10px 0;
    }
"""

outgoing_dialog_table_right_title_style = """
    QLabel {
        margin: 10px 0;
    }
"""

outgoing_applied_msgbox_title_1_style = """
    QLabel {
        font-weight: bold;
        margin-bottom: 5px;
    }
"""

outgoing_applied_msgbox_title_2_style = """
    QLabel {
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
    }
"""
