from app.data_access.sql.generic_sql_data import GenericSqlData, int2bool, bool2int
from app.data_access.sql.shared_column_names import DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER
from app.objects.boat_classes import ListOfBoatClasses, BoatClass
from app.objects.utilities.exceptions import arg_not_passed, MissingData, MultipleMatches

DINGHIES_TABLE = "dinghies_table"
INDEX_NAME_DINGHIES_TABLE = "dinghies_table_index"


class SqlDataListOfDinghies(GenericSqlData):

    def modify_boat_class(
            self, existing_boat: BoatClass, ## won't have ID use name to ID
            new_boat: BoatClass ## name may have changed
    ):
        if existing_boat.name == new_boat.name:
            pass
        else:
            if self.names_are_duplicated_including_new_name(new_boat.name):
                raise Exception("Name %s already in data" % new_boat.name)

        try:

            name = new_boat.name
            hidden = bool2int(new_boat.hidden)
            existing_id = int(self.get_id_for_boat_with_name(existing_boat.name))

            insertion = "UPDATE %s SET %s =?, %s=? WHERE %s=?" % (
                DINGHIES_TABLE,
                DINGHY_NAME,
                HIDDEN,
                DINGHY_ID
            )

            self.cursor.execute(insertion, (
                name, hidden, existing_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def add_new_boat_class_given_string(
            self, name_of_entry_to_add: str
    ):
        if self.names_are_duplicated_including_new_name(name_of_entry_to_add):
            raise Exception("Name %s already in data" % name_of_entry_to_add)

        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            boat = BoatClass(name_of_entry_to_add, hidden=False)
            name = boat.name
            hidden = bool2int(boat.hidden)
            id = self.next_available_id()
            idx = self.next_available_order()

            insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                DINGHIES_TABLE,
                DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER)

            self.cursor.execute(insertion, (
                name, hidden, id, idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()



    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                DINGHY_ID,
                DINGHIES_TABLE
            )
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


    def next_available_order(self) ->int:
        return self.last_used_order()+1

    def last_used_order(self)-> int:
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                DINGHY_ORDER,
                DINGHIES_TABLE
            )
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



    def names_are_duplicated_including_new_name(self, new_name: str):
        existing_names = self.get_all_boat_names()
        existing_names.append(new_name)

        return len(set(existing_names)) < len(existing_names)

    def get_all_boat_names(self):
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                return []

            cursor = self.cursor
            cursor.execute('''SELECT %s FROM %s''' % (
                DINGHY_NAME,  DINGHIES_TABLE
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading boat classes" % str(e1))
        finally:
            self.close()

        return [str(item[0]) for item in raw_list]

    def get_id_for_boat_with_name(self, name: str, default=arg_not_passed):
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                if default is arg_not_passed:
                    raise MissingData("%s not found" % name)
                else:
                    return default

            cursor = self.cursor
            cursor.execute('''SELECT %s FROM %s WHERE %s = "%s" ''' % (
                DINGHY_ID, DINGHIES_TABLE, DINGHY_NAME, str(name)
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading boat classes" % str(e1))
        finally:
            self.close()

        if len(raw_list)>1:
            raise MultipleMatches("Multiple boats called %s" % name)
        elif len(raw_list)==0:
            if default is arg_not_passed:
                raise MissingData("%s not found" % name)
            else:
                return default

        return str(raw_list[0][0])

    def read(self) -> ListOfBoatClasses:
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                return ListOfBoatClasses.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s ORDER BY %s''' % (
                DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHIES_TABLE, DINGHY_ORDER
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading boat classes" % str(e1))
        finally:
            self.close()

        new_list = [BoatClass(name=str(raw_boat[0]),
                             hidden=int2bool(raw_boat[1]),
                             id=str(raw_boat[2])) for raw_boat in raw_list]

        return ListOfBoatClasses(new_list)


    def write(self, list_of_boats: ListOfBoatClasses):
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (DINGHIES_TABLE))

            for idx, boat in enumerate(list_of_boats):
                name = boat.name
                hidden = bool2int(boat.hidden)
                id = int(boat.id)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    DINGHIES_TABLE,
                    DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER)

                self.cursor.execute(insertion, (
                    name, hidden, id, idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def create_table(self):

        #name: str
        #hidden: bool
        #id: str = arg_not_passed

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s INTEGER,
                %s INTEGER
            );
        """ % (DINGHIES_TABLE,
                DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_NAME_DINGHIES_TABLE, DINGHIES_TABLE, DINGHY_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating dinghies table" % str(e1))
        finally:
            self.close()
