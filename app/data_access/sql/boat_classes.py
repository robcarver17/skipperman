from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.utilities.transform_data import bool2int, int2bool
from app.data_access.sql.shared_column_names import (
    DINGHY_NAME,
    HIDDEN,
    DINGHY_ID,
    DINGHY_ORDER,
)
from app.objects.boat_classes import ListOfBoatClasses, BoatClass
from app.objects.utilities.exceptions import (
    arg_not_passed,
    MissingData,
    MultipleMatches,
    missing_data,
)

DINGHIES_TABLE = "dinghies_table"
INDEX_NAME_DINGHIES_TABLE = "dinghies_table_index"


class SqlDataListOfDinghies(GenericSqlData):
    def modify_boat_class(
        self,
        existing_boat: BoatClass,  ## won't have ID use name to ID
        new_boat: BoatClass,  ## name may have changed
    ):
        if existing_boat.name == new_boat.name:
            pass
        else:
            if self.boat_name_already_exists(new_boat.name):
                raise Exception("Name %s already in data" % new_boat.name)

        existing_id = self.get_id_for_boat_with_name(
            existing_boat.name, default=missing_data
        )
        if existing_id is missing_data:
            raise Exception("boat %s doesn't exist" % existing_boat)

        self._modify_boat_class_without_checks(
            existing_id=existing_id, new_boat=new_boat
        )

    def _modify_boat_class_without_checks(
        self,
        existing_id: str,  ## won't have ID use name to ID
        new_boat: BoatClass,  ## name may have changed
    ):
        try:
            name = new_boat.name
            hidden = bool2int(new_boat.hidden)

            insertion = "UPDATE %s SET %s ='%s', %s=%d WHERE %s=%d" % (
                DINGHIES_TABLE,
                DINGHY_NAME,
                name,
                HIDDEN,
                hidden,
                DINGHY_ID,
                int(existing_id),
            )

            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def add_new_boat_class_given_string(self, new_boat: BoatClass):
        name_of_entry_to_add = new_boat.name
        if self.boat_name_already_exists(name_of_entry_to_add):
            raise Exception("Name %s already in data" % name_of_entry_to_add)

        self._add_new_boat_class_without_checks(new_boat)

    def _add_new_boat_class_without_checks(self, new_boat: BoatClass):
        idx = self.next_available_id()
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            self._add_row_without_check_or_commit(idx=idx, boat=new_boat)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def next_available_id(self) -> int:
        return self.last_used_id() + 1

    def last_used_id(self) -> int:
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (DINGHY_ID, DINGHIES_TABLE)
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading boat data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def next_available_order(self) -> int:
        return self.last_used_order() + 1

    def last_used_order(self) -> int:
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (DINGHY_ORDER, DINGHIES_TABLE)
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading boat data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def boat_name_already_exists(self, new_name: str):
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s='%s' """
                % (DINGHIES_TABLE, DINGHY_NAME, str(new_name))
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading boat classes" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def get_id_for_boat_with_name(self, name: str, default=missing_data):
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                return default

            cursor = self.cursor
            cursor.execute(
                """SELECT %s FROM %s WHERE %s = "%s" """
                % (DINGHY_ID, DINGHIES_TABLE, DINGHY_NAME, str(name))
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading boat classes" % str(e1))
        finally:
            self.close()

        if len(raw_list) > 1:
            raise MultipleMatches("Multiple boats called %s" % name)
        elif len(raw_list) == 0:
            return default

        return str(raw_list[0][0])

    def read(self) -> ListOfBoatClasses:
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                return ListOfBoatClasses.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s FROM %s ORDER BY %s"""
                % (DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHIES_TABLE, DINGHY_ORDER)
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading boat classes" % str(e1))
        finally:
            self.close()

        new_list = [
            BoatClass(
                name=str(raw_boat[0]), hidden=int2bool(raw_boat[1]), id=str(raw_boat[2])
            )
            for raw_boat in raw_list
        ]

        return ListOfBoatClasses(new_list)

    def write(self, list_of_boats: ListOfBoatClasses):
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (DINGHIES_TABLE))

            for idx, boat in enumerate(list_of_boats):
                self._add_row_without_check_or_commit(idx=idx, boat=boat)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def _add_row_without_check_or_commit(self, idx: int, boat: BoatClass):
        name = boat.name
        hidden = bool2int(boat.hidden)
        id = int(boat.id)

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
            DINGHIES_TABLE,
            DINGHY_NAME,
            HIDDEN,
            DINGHY_ID,
            DINGHY_ORDER,
        )

        self.cursor.execute(insertion, (name, hidden, id, idx))

    def create_table(self):
        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s INTEGER,
                %s INTEGER
            );
        """ % (
            DINGHIES_TABLE,
            DINGHY_NAME,
            HIDDEN,
            DINGHY_ID,
            DINGHY_ORDER,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_NAME_DINGHIES_TABLE,
            DINGHIES_TABLE,
            DINGHY_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating dinghies table" % str(e1))
        finally:
            self.close()
