
from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat
from app.data_access.sql.shared_column_names import *
from app.objects.utilities.exceptions import arg_not_passed, MultipleMatches

PATROL_BOATS_TABLE = "patrol_boats"
INDEX_PATROL_BOATS_TABLE = "index_patrol_boats_table"

class SqlDataListOfPatrolBoats(GenericSqlData):
    def add_new_patrol_boat(self, patrol_boat_name: str):
        if self.does_patrol_boat_with_name_exist(patrol_boat_name):
            raise Exception("Boat called %s already exists" % patrol_boat_name)

        try:
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                self.create_table()

            id = self.next_available_id()
            idx = self.next_available_order()
            boat = PatrolBoat(
                patrol_boat_name,
                hidden=False
            )
            self.write_boat_without_committing(
                boat=boat,
                idx=idx,
                id=str(id)
            )
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing patrol boats" % str(e1))
        finally:
            self.close()

    def modify_patrol_boat(
            self, existing_patrol_boat_id: str, new_patrol_boat: PatrolBoat
    ):
        existing_boat = self.patrol_boat_with_id(existing_patrol_boat_id, default=None)
        if existing_boat is None:
            raise Exception("Can't modify non existent boat")
        if existing_boat.name == new_patrol_boat.name:
            pass
        else:
            if self.does_patrol_boat_with_name_exist(new_patrol_boat.name):
                raise Exception("Can't change name from %s to %s as boat called %s already exists" %
                                (existing_boat.name, new_patrol_boat.name, new_patrol_boat.name))

        try:
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s='%s', %s='%s' WHERE %s='%s' " % (
                PATROL_BOATS_TABLE,
                PATROL_BOAT_NAME,
                str(new_patrol_boat.name),
                HIDDEN,
                bool2int(new_patrol_boat.hidden),
                PATROL_BOAT_ID,
                int(existing_patrol_boat_id))

            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing patrol boats" % str(e1))
        finally:
            self.close()


    def does_patrol_boat_with_name_exist(self, patrol_boat_name: str):
        boat = self.patrol_boat_with_name(patrol_boat_name, default=None)
        if boat is None:
            return False
        else:
            return True

    def patrol_boat_with_name(self, patrol_boat_name: str, default) -> PatrolBoat:
        try:
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                return default

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ''' % (
                 HIDDEN, PATROL_BOAT_ID, PATROL_BOATS_TABLE, PATROL_BOAT_NAME, str(patrol_boat_name)
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading patrol boats" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one patrol boat with name %s" % patrol_boat_name)

        raw_boat = raw_list[0]
        return PatrolBoat(name=patrol_boat_name,
                             hidden=int2bool(raw_boat[0]),
                             id=str(raw_boat[1]))

    def patrol_boat_with_id(self, patrol_boat_id: str, default) -> PatrolBoat:
        try:
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                return default

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ''' % (
                 HIDDEN, PATROL_BOAT_NAME, PATROL_BOATS_TABLE, PATROL_BOAT_ID, int(patrol_boat_id)
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading patrol boats" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one patrol boat with id %s" % patrol_boat_id)

        raw_boat = raw_list[0]
        return PatrolBoat(name=raw_boat[1],
                             hidden=int2bool(raw_boat[0]),
                             id=patrol_boat_id)



    def next_available_id(self) ->int:
        return self.last_used_id()+1


    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                PATROL_BOAT_ID,
                PATROL_BOATS_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading dinghy data" % str(e1))
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
            if self.table_does_not_exist(PATROL_BOATS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                PATROL_BOAT_ORDER,
                PATROL_BOATS_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading dinghy data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

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
                self.write_boat_without_committing(
                    boat=boat,
                    idx=idx,
                    id=boat.id
                )
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing patrol boats" % str(e1))
        finally:
            self.close()

    def write_boat_without_committing(self, boat: PatrolBoat, id: str, idx: int):
        name = boat.name
        hidden = bool2int(boat.hidden)
        id = int(id)

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
            PATROL_BOATS_TABLE,
            PATROL_BOAT_NAME, HIDDEN, PATROL_BOAT_ID, PATROL_BOAT_ORDER)

        self.cursor.execute(insertion, (
            name, hidden, id, idx))

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
