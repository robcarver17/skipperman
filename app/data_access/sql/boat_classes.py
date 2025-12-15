from app.data_access.sql.generic_sql_data import GenericSqlData, int2bool, bool2int
from app.data_access.sql.shared_column_names import DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER
from app.objects.boat_classes import ListOfBoatClasses, BoatClass

DINGHIES_TABLE = "dinghies_table"
INDEX_NAME_DINGHIES_TABLE = "dinghies_table_index"


class SqlDataListOfDinghies(GenericSqlData):


    def read(self) -> ListOfBoatClasses:
        try:
            if self.table_does_not_exist(DINGHIES_TABLE):
                self.create_table()

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
