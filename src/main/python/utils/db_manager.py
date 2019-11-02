import sqlite3
from datetime import datetime
from PyQt5 import QtCore
from pandas import DataFrame
from utils import utils_collection as utils


class DB_Manager:
    def __init__(self):
        settings = QtCore.QSettings("solutronic", "admin_stock")
        db_location = settings.value("db_location")
        self.connection = sqlite3.connect(db_location)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """Closes the connection of a DB_Manager instance."""
        self.connection.close()

    def enable_foreign_keys(self):
        """Enables foreign keys, mostly used for ON UPDATE CASCADE."""
        self.connection.execute("PRAGMA foreign_keys = ON")

    def get_total_table_count(self):
        """Returns the total number of component tables as an int."""
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type = 'table' AND NOT name LIKE '\\_%' ESCAPE '\\';
            """
        )
        return self.cursor.fetchone()[0]

    def get_excluded_state(self):
        """Returns the config state value for whether excluded should be highlighted or not."""
        self.cursor.execute("SELECT excluded_checkbox FROM _config;")
        return self.cursor.fetchone()[0]

    def get_all_SQL_names_for_components(self):
        """Returns the names of all component tables in SQL format as a list of strings."""
        self.cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND NOT name LIKE '\\_%' ESCAPE '\\'
            ORDER BY name ASC;
            """
        )
        return [i[0] for i in self.cursor.fetchall()]

    def get_all_display_names_for_components(self):
        """Returns the names of all component tables in display format as a list of strings."""
        self.cursor.execute("SELECT display_name FROM _component_names;")
        return [i[0] for i in self.cursor.fetchall()]

    def get_SQL_name_for_component(self, component_name_display):
        """Takes a component in display format as a string and returns its name in SQL format."""
        self.cursor.execute(
            """
            SELECT sql_name FROM _component_names
            WHERE display_name = '{}';
            """.format(
                component_name_display
            )
        )
        return self.cursor.fetchone()[0]

    def get_components_not_in_use(self):
        """Returns components not in use (i.e., any component not used in at least one recipe) as a list of strings."""
        components_in_use = self.get_components_in_use()
        all_components = self.get_all_display_names_for_components()
        return [i for i in all_components if i not in components_in_use]

    def get_components_in_use(self):
        """Returns components in use (i.e., every component used in at least one recipe) as a list of strings."""
        all_recipes = self.get_all_recipes_as_sql()
        components_in_recipes = {}
        for recipe in all_recipes:
            self.cursor.execute(f"SELECT * FROM '{recipe}';")
            for i in self.cursor.fetchall():
                component = i[0]
                component_qty = i[1]
                components_in_recipes[component] = component_qty

        return [k for k in components_in_recipes]

    def get_all_recipes_as_sql(self):
        """Returns the names of all recipe tables in SQL format as a list of strings."""
        self.cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name LIKE '\\_recipe\\_%' ESCAPE '\\';
            """
        )
        return [i[0] for i in self.cursor.fetchall()]

    def get_all_recipes_as_display(self):
        """Returns the names of all recipe tables in SQL format as a list of strings."""
        self.cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name LIKE '\\_recipe\\_%' ESCAPE '\\';
            """
        )
        all_recipes_sql = [i[0] for i in self.cursor.fetchall()]
        all_recipes_display = []
        for recipe_sql in all_recipes_sql:
            recipe_display = recipe_sql.replace("_recipe_", "").replace("_", "-")
            all_recipes_display.append(recipe_display)

        return all_recipes_display

    def get_recipes_containing_component(self, component):
        """Takes a component as a string, and returns a dictionary with the products where component is used as the string key, and the amounts of components used in those products as the float value)."""
        result = {}
        for table in self.get_all_recipes_as_sql():
            self.cursor.execute(
                """
                SELECT * FROM {}
                WHERE recipe_component = '{}';
                """.format(
                    table, component
                )
            )
            comp_and_amt_tup = self.cursor.fetchone()
            if comp_and_amt_tup is not None:
                table = table.replace("_recipe_", "")
                amount = comp_and_amt_tup[1]
                result[table] = amount

        return result

    def create_recipe(self, recipe_name_sql):
        """Takes a recipe being created as a string and creates a table for it."""
        self.cursor.execute(
            """
            CREATE TABLE '_recipe_{}' (
                recipe_component TEXT UNIQUE,
                recipe_component_amount REAL,
                FOREIGN KEY('recipe_component')
                REFERENCES '_component_names'('display_name') ON DELETE CASCADE ON UPDATE CASCADE
            );
            """.format(
                recipe_name_sql
            )
        )
        self.connection.commit()

    def populate_recipe(self, recipe_name_sql, recipe_contents):
        """Takes a recipe name in SQL format as a string and recipe contents as a dictionary, and populates the relevant table with the contents of the dictionary."""
        for component, amount in recipe_contents.items():
            self.cursor.execute(
                """
                INSERT INTO '_recipe_{}' VALUES (
                    :recipe_component,
                    :recipe_component_amount
                );
                """.format(
                    recipe_name_sql
                ),
                {"recipe_component": component, "recipe_component_amount": amount},
            )

        self.connection.commit()

    def get_recipe_contents(self, recipe_name_sql):
        """Takes a recipe name in SQL format as a string and returns the relevant recipe contents as a dictionary with components as strings and amounts as floats."""
        self.cursor.execute("""SELECT * FROM '_recipe_{}';""".format(recipe_name_sql))
        recipe_contents_tuples = self.cursor.fetchall()
        recipe_contents = {}
        for tup in recipe_contents_tuples:
            recipe_contents[tup[0]] = tup[1]

        return recipe_contents

    def delete_recipe(self, recipe_name_sql):
        """Takes a recipe name in SQL format as a string and drops its table."""
        self.cursor.execute("""DROP TABLE '_recipe_{}';""".format(recipe_name_sql))
        self.connection.commit()

    def edit_recipe(self, recipe_name_sql, recipe_contents):
        """Takes a recipe name in SQL format as a string and recipe contents as a dictionary   with components as strings and amounts as floats, deletes its old contents and populates it with the new contents."""
        self.cursor.execute("""DELETE FROM '_recipe_{}';""".format(recipe_name_sql))
        self.populate_recipe(recipe_name_sql, recipe_contents)

    def get_stocks_for_owner(self, stock_owner):
        """Takes a stock owner as a string and returns their component stocks as a list of floats."""
        individual_stock_list = []
        all_components_SQL_names = self.get_all_SQL_names_for_components()
        for component in all_components_SQL_names:
            try:
                self.cursor.execute(
                    """
                    SELECT {} FROM {}
                    WHERE rowid = (
                        SELECT MAX(rowid) FROM {});
                    """.format(
                        stock_owner, component, component
                    )
                )
                for result in self.cursor.fetchone():
                    individual_stock_list.append(float(result))

            except:
                individual_stock_list.append(0)

        return individual_stock_list

    def get_stock_at_valdenegro_for(self, component_sql):
        self.cursor.execute(
            """
            SELECT stock_valdenegro FROM {}
            WHERE rowid = (SELECT MAX(rowid) FROM {});
            """.format(
                component_sql, component_sql
            )
        )
        return self.cursor.fetchone()[0]

    def get_stock_at_assembler_for(self, component_sql, assembler):
        self.cursor.execute(
            """
            SELECT stock_{} FROM {}
            WHERE rowid = (SELECT MAX(rowid) FROM {});
            """.format(
                assembler, component_sql, component_sql
            )
        )
        return self.cursor.fetchone()[0]

    def apply_incoming_to_valdenegro(self, data):
        self.cursor.execute(
            """
            INSERT INTO {} VALUES (
                :fecha,
                :remito,
                :proveedor,
                :nota,
                :ingreso_valdenegro,
                :egreso_valdenegro,
                :stock_valdenegro,
                :ingreso_karina,
                :egreso_karina,
                :stock_karina,
                :ingreso_brid,
                :egreso_brid,
                :stock_brid,
                :ingreso_tercero,
                :egreso_tercero,
                :stock_tercero
            )
            """.format(
                data["comp_sql"]
            ),
            {
                "fecha": datetime.now().strftime("%d/%m/%Y"),
                "remito": data["packing_list"],
                "proveedor": data["supplier"],
                "nota": data["note"],
                "ingreso_valdenegro": data["amount"],
                "egreso_valdenegro": 0,
                "stock_valdenegro": data["stock_vald_post_application"],
                "ingreso_karina": 0,
                "egreso_karina": 0,
                "stock_karina": data["stock_karina"],
                "ingreso_brid": 0,
                "egreso_brid": 0,
                "stock_brid": data["stock_brid"],
                "ingreso_tercero": 0,
                "egreso_tercero": 0,
                "stock_tercero": data["stock_tercero"],
            },
        )
        self.connection.commit()

    def make_needs_and_stocks_df(self, needed_comps_and_amounts):
        needed_comps_display = list(needed_comps_and_amounts.keys())
        needed_comps_sql = [
            self.get_SQL_name_for_component(k) for k in needed_comps_and_amounts.keys()
        ]
        needed_amounts = list(needed_comps_and_amounts.values())
        stock_valdenegro = []
        stock_karina = []
        stock_brid = []
        stock_tercero = []
        for i in needed_comps_sql:
            try:
                self.cursor.execute(
                    """
                    SELECT {} FROM {}
                    WHERE rowid = (SELECT MAX(rowid) FROM {});
                    """.format(
                        "stock_valdenegro, stock_karina, stock_brid, stock_tercero",
                        i,
                        i,
                    )
                )
                for tup in self.cursor.fetchall():
                    stock_valdenegro.append(tup[0])
                    stock_karina.append(tup[1])
                    stock_brid.append(tup[2])
                    stock_tercero.append(tup[3])

            except:
                self.cursor.execute(
                    """
                    SELECT {} FROM {} WHERE rowid = (SELECT MAX(rowid) FROM {});
                    """.format(
                        "stock_valdenegro", i, i
                    )
                )
                for tup in self.cursor.fetchall():
                    stock_valdenegro.append(tup[0])
                    stock_karina.append(0)
                    stock_brid.append(0)
                    stock_tercero.append(0)

        return DataFrame(
            {
                "comp": needed_comps_display,
                "need": needed_amounts,
                "V": stock_valdenegro,
                "K": stock_karina,
                "B": stock_brid,
                "T": stock_tercero,
            }
        )

    def apply_outgoing_to_valdenegro_and_assembler(self, data):

        assembler_values = {
            "ingreso_karina": 0,
            "egreso_karina": 0,
            "stock_karina": data["stock_karina"],
            "ingreso_brid": 0,
            "egreso_brid": 0,
            "stock_brid": data["stock_brid"],
            "ingreso_tercero": 0,
            "egreso_tercero": 0,
            "stock_tercero": data["stock_tercero"],
        }
        assembler_incoming = "ingreso_" + data["assembler"]
        assembler_outgoing = "egreso_" + data["assembler"]
        assembler_stock = "stock_" + data["assembler"]
        assembler_values[assembler_incoming] = data["comp_outgoing_amt"]
        assembler_values[assembler_outgoing] = data["comp_outgoing_need"]
        assembler_values[assembler_stock] = data["stock_assembler_post_appl"]
        self.cursor.execute(
            """
            INSERT INTO {} VALUES (
                :fecha,
                :remito,
                :proveedor,
                :nota,
                :ingreso_valdenegro,
                :egreso_valdenegro,
                :stock_valdenegro,
                :ingreso_karina,
                :egreso_karina,
                :stock_karina,
                :ingreso_brid,
                :egreso_brid,
                :stock_brid,
                :ingreso_tercero,
                :egreso_tercero,
                :stock_tercero
            );
            """.format(
                data["comp_sql"]
            ),
            {
                "fecha": datetime.now().strftime("%d/%m/%Y"),
                "remito": "---",
                "proveedor": "---",
                "nota": "---",
                "ingreso_valdenegro": 0,
                "egreso_valdenegro": data["comp_outgoing_amt"],
                "stock_valdenegro": data["stock_vald_post_appl"],
                "ingreso_karina": assembler_values["ingreso_karina"],
                "egreso_karina": assembler_values["egreso_karina"],
                "stock_karina": assembler_values["stock_karina"],
                "ingreso_brid": assembler_values["ingreso_brid"],
                "egreso_brid": assembler_values["egreso_brid"],
                "stock_brid": assembler_values["stock_brid"],
                "ingreso_tercero": assembler_values["ingreso_tercero"],
                "egreso_tercero": assembler_values["egreso_tercero"],
                "stock_tercero": assembler_values["stock_tercero"],
            },
        )
        self.connection.commit()

    def apply_subtraction_to_valdenegro_only(self, data):
        self.cursor.execute(
            """
            INSERT INTO {} VALUES (
                :fecha,
                :remito,
                :proveedor,
                :nota,
                :ingreso_valdenegro,
                :egreso_valdenegro,
                :stock_valdenegro,
                :ingreso_karina,
                :egreso_karina,
                :stock_karina,
                :ingreso_brid,
                :egreso_brid,
                :stock_brid,
                :ingreso_tercero,
                :egreso_tercero,
                :stock_tercero
            );
            """.format(
                data["comp_sql"]
            ),
            {
                "fecha": datetime.now().strftime("%d/%m/%Y"),
                "remito": "---",
                "proveedor": "---",
                "nota": "---",
                "ingreso_valdenegro": 0,
                "egreso_valdenegro": data["subtr_amount"],
                "stock_valdenegro": data["stock_vald_post_appl"],
                "ingreso_karina": 0,
                "egreso_karina": 0,
                "stock_karina": 0,
                "ingreso_brid": 0,
                "egreso_brid": 0,
                "stock_brid": 0,
                "ingreso_tercero": 0,
                "egreso_tercero": 0,
                "stock_tercero": 0,
            },
        )
        self.connection.commit()

    def log_new_movement(self, movement, destination, component, amount, user):
        self.cursor.execute(
            """
            INSERT INTO _historical_records VALUES (
                :date,
                :time,
                :movement,
                :component,
                :quantity,
                :destination,
                :user
            );
            """,
            {
                "date": datetime.now().strftime("%d/%m/%Y"),
                "time": datetime.now().strftime("%H:%M"),
                "movement": movement,
                "component": component,
                "quantity": amount,
                "destination": destination,
                "user": user,
            },
        )
        self.connection.commit()

    def get_stored_criticals(self):
        """Returns critical values and returns them as a dict."""
        self.cursor.execute("SELECT * FROM _critical_values;")
        return dict(self.cursor.fetchall())

    def delete_all_criticals(self):
        """Deletes all rows from the criticals table."""
        self.cursor.execute("DELETE FROM _critical_values;")
        self.connection.commit()

    def save_new_criticals(self, new_criticals):
        """Takes new criticals as a dict and stores them in the criticals table."""
        for component, critical_value in new_criticals.items():
            self.cursor.execute(
                """
                INSERT INTO _critical_values VALUES (
                    :component,
                    :critical_value
                );
                """,
                {"component": component, "critical_value": critical_value},
            )

        self.connection.commit()

    def log_new_config_record(self, config, details):
        """Takes values as strings and logs new config record."""
        settings = QtCore.QSettings("solutronic", "admin_stock")
        self.cursor.execute(
            """INSERT INTO _config_records VALUES (:date, :time, :config, :details, :user);""",
            {
                "date": datetime.now().strftime("%d/%m/%Y"),
                "time": datetime.now().strftime("%H:%M"),
                "config": config,
                "details": details,
                "user": settings.value("username"),
            },
        )
        self.connection.commit()

    def get_totals_for_components_and_recipes(self):
        """Returns component and recipe totals as strings for the statusbar."""
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type = 'table' AND NOT name LIKE '\\_%' ESCAPE '\\';
            """
        )
        component_total = self.cursor.fetchone()[0]
        self.cursor.execute(
            """
            SELECT COUNT(name) FROM sqlite_master
            WHERE type = 'table' AND
            name LIKE '\\_recipe\\_%' ESCAPE '\\';
            """
        )
        recipe_total = self.cursor.fetchone()[0]
        return (str(component_total), str(recipe_total))

    def get_all_admin_users(self):
        """Returns the names of all admin users as an alphabetically sorted list of strings."""
        self.cursor.execute("SELECT user from _config_records;")
        users = [i[0] for i in self.cursor.fetchall()]
        return sorted(list(set(users)))

    def get_components_mentioned_in_movements(self):
        """Returns all components mentioned in movements as a list of unique strings."""
        self.cursor.execute("SELECT component FROM _historical_records;")
        components = [i[0] for i in self.cursor.fetchall()]
        return list(set(components))

    def get_years_from_movements(self):
        """Returns all years mentioned in the _historical_records table."""
        self.cursor.execute("SELECT date FROM _historical_records;")
        years = [i[0].split("/")[2] for i in self.cursor.fetchall()]
        return list(set(years))

    def get_years_from_configs(self):
        """Returns all years mentioned in the _config_records table."""
        self.cursor.execute("SELECT date FROM _config_records;")
        years = [i[0].split("/")[2] for i in self.cursor.fetchall()]
        return list(set(years))

    def delete_all_movements(self):
        """Deletes all movements from the _historical_records table."""
        self.cursor.execute("DELETE FROM _historical_records;")
        self.connection.commit()

    def delete_all_configs(self):
        """Deletes all configs from the _config_records table."""
        self.cursor.execute("DELETE FROM _config_records;")
        self.connection.commit()

    def get_movements_as_dataframe(self):
        """Returns all movements as dataframe, ordered from newest to oldest."""
        self.cursor.execute("SELECT * FROM _historical_records;")
        movements = [list(i) for i in self.cursor.fetchall()]
        sorted_movements = list(reversed(movements))
        column_names = [
            "Fecha",
            "Hora",
            "Movimiento",
            "Componente",
            "Cantidad",
            "Destino",
            "Usuario",
        ]
        return DataFrame(sorted_movements, columns=column_names)

    def get_configs_as_dataframe(self):
        """Returns all configs as dataframe, ordered from newest to oldest."""
        self.cursor.execute("SELECT * FROM _config_records;")
        configs = [list(i) for i in self.cursor.fetchall()]
        sorted_configs = list(reversed(configs))
        column_names = ["Fecha", "Hora", "Configuración", "Detalle", "Usuario"]
        return DataFrame(sorted_configs, columns=column_names)

    def get_comp_details(self, selected_comp_SQL):
        """Takes a component in SQL format and returns its details as a dictionary."""
        self.cursor.execute("SELECT * FROM {};".format(selected_comp_SQL))
        comp_details = {
            "fecha": [],
            "remito": [],
            "proveedor": [],
            "nota": [],
            "ingreso_valdenegro": [],
            "egreso_valdenegro": [],
            "stock_valdenegro": [],
            "ingreso_karina": [],
            "egreso_karina": [],
            "stock_karina": [],
            "ingreso_brid": [],
            "egreso_brid": [],
            "stock_brid": [],
            "ingreso_tercero": [],
            "egreso_tercero": [],
            "stock_tercero": [],
        }
        for i in self.cursor.fetchall():
            comp_details["fecha"].append(i[0])
            comp_details["remito"].append(i[1])
            comp_details["proveedor"].append(i[2])
            comp_details["nota"].append(i[3])
            comp_details["ingreso_valdenegro"].append(
                utils.format_number_for_display(i[4])
            )
            comp_details["egreso_valdenegro"].append(
                utils.format_number_for_display(i[5])
            )
            comp_details["stock_valdenegro"].append(
                utils.format_number_for_display(i[6])
            )
            comp_details["ingreso_karina"].append(utils.format_number_for_display(i[7]))
            comp_details["egreso_karina"].append(utils.format_number_for_display(i[8]))
            comp_details["stock_karina"].append(utils.format_number_for_display(i[9]))
            comp_details["ingreso_brid"].append(utils.format_number_for_display(i[10]))
            comp_details["egreso_brid"].append(utils.format_number_for_display(i[11]))
            comp_details["stock_brid"].append(utils.format_number_for_display(i[12]))
            comp_details["ingreso_tercero"].append(
                utils.format_number_for_display(i[13])
            )
            comp_details["egreso_tercero"].append(
                utils.format_number_for_display(i[14])
            )
            comp_details["stock_tercero"].append(utils.format_number_for_display(i[15]))

        self.cursor.execute(
            """
            SELECT stock_valdenegro, stock_karina, stock_brid, stock_tercero FROM {}
            WHERE rowid = (SELECT MAX(rowid) FROM {});
            """.format(
                selected_comp_SQL, selected_comp_SQL
            )
        )
        for i in self.cursor.fetchall():
            comp_details["current_stock_valdenegro"] = utils.format_number_for_display(
                i[0]
            )
            comp_details["current_stock_karina"] = utils.format_number_for_display(i[1])
            comp_details["current_stock_brid"] = utils.format_number_for_display(i[2])
            comp_details["current_stock_tercero"] = utils.format_number_for_display(
                i[3]
            )

        return comp_details

    def create_new_component(self, newcomp_name_sql, newcomp_name_display, initstock):
        """Create a new table for the component, and a new entry for the component in _component_names table."""
        self.cursor.execute(
            """CREATE TABLE {} (
                fecha TEXT,
                remito TEXT,
                proveedor TEXT,
                nota TEXT,
                ingreso_valdenegro REAL,
                egreso_valdenegro REAL,
                stock_valdenegro REAL,
                ingreso_karina REAL,
                egreso_karina REAL,
                stock_karina REAL,
                ingreso_brid REAL,
                egreso_brid REAL,
                stock_brid REAL,
                ingreso_tercero REAL,
                egreso_tercero REAL,
                stock_tercero REAL
            );
            """.format(
                newcomp_name_sql
            )
        )
        self.cursor.execute(
            """
            INSERT INTO {} VALUES (
                :fecha,
                :remito,
                :proveedor,
                :nota,
                :ingreso_valdenegro,
                :egreso_valdenegro,
                :stock_valdenegro,
                :ingreso_karina,
                :egreso_karina,
                :stock_karina,
                :ingreso_brid,
                :egreso_brid,
                :stock_brid,
                :ingreso_tercero,
                :egreso_tercero,
                :stock_tercero
            );
            """.format(
                newcomp_name_sql
            ),
            {
                "fecha": datetime.now().strftime("%d/%m/%Y"),
                "remito": "---",
                "proveedor": "---",
                "nota": "Creación",
                "ingreso_valdenegro": initstock,
                "egreso_valdenegro": 0,
                "stock_valdenegro": initstock,
                "ingreso_karina": 0,
                "egreso_karina": 0,
                "stock_karina": 0,
                "ingreso_brid": 0,
                "egreso_brid": 0,
                "stock_brid": 0,
                "ingreso_tercero": 0,
                "egreso_tercero": 0,
                "stock_tercero": 0,
            },
        )
        self.cursor.execute(
            """
            INSERT INTO _component_names VALUES (
                :sql_name,
                :display_name);
            """,
            {"sql_name": newcomp_name_sql, "display_name": newcomp_name_display},
        )
        self.connection.commit()

    def edit_comp_name_everywhere(
        self,
        comp_old_sql_name,
        comp_new_sql_name,
        comp_old_display_name,
        comp_new_display_name,
    ):
        self.cursor.execute(
            """
            ALTER TABLE {} RENAME TO {};
            """.format(
                comp_old_sql_name, comp_new_sql_name
            )
        )
        self.cursor.execute(
            """
            UPDATE _component_names
            SET sql_name = '{}' WHERE display_name = '{}';
            """.format(
                comp_new_sql_name, comp_old_display_name
            )
        )
        self.cursor.execute(
            """
            UPDATE _component_names
            SET display_name = '{}' WHERE sql_name = '{}';
            """.format(
                comp_new_display_name, comp_new_sql_name
            )
        )
        self.cursor.execute(
            """
            UPDATE _critical_values
            SET component = '{}' WHERE component = '{}';
            """.format(
                comp_new_display_name, comp_old_display_name
            )
        )
        self.connection.commit()

    def delete_comp_name_everywhere(self, comp_being_deleted_sql_name):
        self.cursor.execute(
            """
            DROP TABLE {};
            """.format(
                comp_being_deleted_sql_name
            )
        )
        self.cursor.execute(
            """
            DELETE FROM _component_names
            WHERE sql_name = '{}';
            """.format(
                comp_being_deleted_sql_name
            )
        )
        all_recipes = self.get_all_recipes_as_sql()
        recipes_left_empty = []
        for recipe in all_recipes:
            self.cursor.execute(
                """
                SELECT COUNT(*) FROM '{}'
                """.format(
                    recipe
                )
            )
            if self.cursor.fetchone()[0] == 0:
                recipes_left_empty.append(recipe)

        for empty_recipe in recipes_left_empty:
            self.cursor.execute(
                """
                DROP TABLE '{}';
                """.format(
                    empty_recipe
                )
            )

        self.connection.commit()
