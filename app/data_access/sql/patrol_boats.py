
from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat
from app.data_access.sql.shared_column_names import *


PATROL_BOATS_TABLE = "patrol_boats"
INDEX_PATROL_BOATS_TABLE = "index_patrol_boats_table"

class SqlDataListOfPatrolBoats(GenericSqlData):
    def read(self) -> ListOfPatrolBoats:
        try:
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                return ListOfPatrolBoats.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s ORDER BY %s''' % (
                PATROL_BOAT_NAME, HIDDEN, PATROL_BOAT_ID, PATROL_BOATS_TABLE, PATROL_BOAT_ORDER
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading club dinghies" % str(e1))
        finally:
            self.close()

        new_list = [PatrolBoat(name=str(raw_boat[0]),
                             hidden=int2bool(raw_boat[1]),
                             id=str(raw_boat[2])) for raw_boat in raw_list]

        return ListOfPatrolBoats(new_list)


    def write(self, list_of_boats: ListOfPatrolBoats):
        try:
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (PATROL_BOATS_TABLE))

            for idx, boat in enumerate(list_of_boats):
                name = boat.name
                hidden = bool2int(boat.hidden)
                id = int(boat.id)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    PATROL_BOATS_TABLE,
                PATROL_BOAT_NAME, HIDDEN, PATROL_BOAT_ID, PATROL_BOAT_ORDER)

                self.cursor.execute(insertion, (
                    name, hidden, id, idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing patrol boats" % str(e1))
        finally:
            self.close()

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
            """ % (PATROL_BOATS_TABLE,
                   PATROL_BOAT_NAME, HIDDEN, PATROL_BOAT_ID, PATROL_BOAT_ORDER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
        INDEX_PATROL_BOATS_TABLE, PATROL_BOATS_TABLE, PATROL_BOAT_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating patrol boats table" % str(e1))
        finally:
            self.close()
