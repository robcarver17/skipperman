from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *
from app.objects.club_dinghies import ListOfClubDinghies, ClubDinghy
from app.objects.utilities.exceptions import arg_not_passed, missing_data, MultipleMatches

CLUB_DINGHIES_TABLE = "club_dinghies"
INDEX_CLUB_DINGHIES_TABLE = "index_club_dinghies_table"

class SqlDataListOfClubDinghies(GenericSqlData):
    def add_new_club_dinghy_with_name(self, dinghy_name: str):
        if self.does_club_dinghy_with_name_exist(dinghy_name):
            raise Exception("Can't add dinghy with name to %s as that name already exists" % dinghy_name)

        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                self.create_table()

            dinghy_id = self.next_available_id()
            dinghy_order = self.next_available_order()
            hidden_as_int = bool2int(False)

            insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                CLUB_DINGHIES_TABLE,
                DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER)

            self.cursor.execute(insertion, (
                dinghy_name,
            hidden_as_int,
            dinghy_id,
            dinghy_order))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when adding club dinghies" % str(e1))
        finally:
            self.close()

    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                DINGHY_ID,
                CLUB_DINGHIES_TABLE,
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
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                DINGHY_ORDER,
                CLUB_DINGHIES_TABLE,
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


    def modify_club_dinghy(self,
                           existing_club_dinghy_id: str,
                           new_club_dinghy: ClubDinghy
                           ):

        existing_club_dinghy = self.get_club_dinghy_from_id(existing_club_dinghy_id)
        existing_club_dinghy_name = existing_club_dinghy.name

        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                raise Exception("Can't modify dinghy as doesn't exist")

            if existing_club_dinghy_name == new_club_dinghy.name:
                pass
            else:
                if self.does_club_dinghy_with_name_exist(new_club_dinghy.name):
                    raise Exception("Can't change dinghy name to %s as that name already exists" % new_club_dinghy.name)

            print("update %s %s to %s %s" % (existing_club_dinghy, existing_club_dinghy.hidden,
                                             new_club_dinghy, new_club_dinghy.hidden))
            insertion = "UPDATE %s SET %s='%s', %s='%s' WHERE %s='%s'" % (
                    CLUB_DINGHIES_TABLE,
                    DINGHY_NAME, new_club_dinghy.name,
                    HIDDEN, bool2int(new_club_dinghy.hidden),
                    DINGHY_ID, int(existing_club_dinghy_id)

            )

            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when modifying club dinghy to %s" % (str(e1), str(new_club_dinghy)))
        finally:
            self.close()

    def get_club_dinghy_from_id(self, club_dinghy_id: str, default=arg_not_passed):
        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                return default

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ''' % (
                DINGHY_NAME, HIDDEN, CLUB_DINGHIES_TABLE,
                 DINGHY_ID, int(club_dinghy_id)
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading club dinghies" % str(e1))
        finally:
            self.close()

        if len(raw_list)>1:
            raise MultipleMatches("More than one dinghy with ID %s" % club_dinghy_id)
        if len(raw_list)==0:
            return default

        raw_boat = raw_list[0]

        return ClubDinghy(name=str(raw_boat[0]),
                             hidden=int2bool(raw_boat[1]),
                             id=club_dinghy_id)


    def does_club_dinghy_with_name_exist(self,  dinghy_name:str):
        club_dinghy = self.get_club_dinghy_with_name(dinghy_name, default=missing_data)
        if club_dinghy is missing_data:
            return False

        return True

    def get_club_dinghy_with_name(self, dinghy_name:str, default=arg_not_passed):
        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                return default

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ''' % (
                HIDDEN, DINGHY_ID, CLUB_DINGHIES_TABLE,
                DINGHY_NAME, str(dinghy_name)
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading club dinghies" % str(e1))
        finally:
            self.close()

        if len(raw_list)>1:
            raise MultipleMatches("More than one dinghy called %s" % dinghy_name)
        if len(raw_list)==0:
            return default

        raw_boat = raw_list[0]

        return ClubDinghy(name=dinghy_name,
                             hidden=int2bool(raw_boat[0]),
                             id=str(raw_boat[1]))



    def get_list_of_visible_club_dinghies(self) -> ListOfClubDinghies:
        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                return ListOfClubDinghies.create_empty()
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' ORDER BY %s''' % (
                DINGHY_NAME, HIDDEN, DINGHY_ID, CLUB_DINGHIES_TABLE,
                HIDDEN,
                bool2int(False),
                DINGHY_ORDER
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading club dinghies" % str(e1))
        finally:
            self.close()

        new_list = [ClubDinghy(name=str(raw_boat[0]),
                             hidden=int2bool(raw_boat[1]),
                             id=str(raw_boat[2])) for raw_boat in raw_list]

        return ListOfClubDinghies(new_list)


    def read(self) -> ListOfClubDinghies:
        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                return ListOfClubDinghies.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s ORDER BY %s''' % (
                DINGHY_NAME, HIDDEN, DINGHY_ID, CLUB_DINGHIES_TABLE, DINGHY_ORDER
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading club dinghies" % str(e1))
        finally:
            self.close()

        new_list = [ClubDinghy(name=str(raw_boat[0]),
                             hidden=int2bool(raw_boat[1]),
                             id=str(raw_boat[2])) for raw_boat in raw_list]

        return ListOfClubDinghies(new_list)


    def write(self, list_of_boats: ListOfClubDinghies):
        try:
            if self.table_does_not_exist(CLUB_DINGHIES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (CLUB_DINGHIES_TABLE))

            for idx, boat in enumerate(list_of_boats):
                name = boat.name
                hidden = bool2int(boat.hidden)
                id = int(boat.id)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    CLUB_DINGHIES_TABLE,
                    DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER)

                self.cursor.execute(insertion, (
                    name, hidden, id, idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing club dinghies" % str(e1))
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
            """ % (CLUB_DINGHIES_TABLE,
                   DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
        INDEX_CLUB_DINGHIES_TABLE, CLUB_DINGHIES_TABLE, DINGHY_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating club dinghies table" % str(e1))
        finally:
            self.close()
