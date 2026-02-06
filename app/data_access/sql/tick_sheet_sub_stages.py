from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.substages import ListOfTickSubStages, TickSubStage
from app.objects.utilities.exceptions import arg_not_passed, MissingData, MultipleMatches, missing_data

TICK_SUBSTAGE_TABLE = "tick_substages"
INDEX_TICK_SUBSTAGE_TABLE = "index_tick_substages"

class SqlDataListOfTickSubStages(GenericSqlData):
    def modify_substage_name(
            self,
            existing_substage_id:str,
            new_name: str,
    ):
        existing_item = self.get_substage_with_id(substage_id=existing_substage_id, default=missing_data)
        if existing_item is missing_data:
            raise Exception("Can't modify non existent item with id %s" % existing_substage_id)

        if existing_item.name == new_name:
            return

        if self.does_substage_with_name_exist(new_name, qualification_id=existing_item.stage_id):
            raise Exception("Cannot change name from %s to %s as an item with that name already exists for this qualification" % (existing_item.name, new_name))

        self._modify_substage_name_without_checks(existing_substage_id=existing_substage_id, new_name=new_name)

    def _modify_substage_name_without_checks(
            self,
            existing_substage_id:str,
            new_name: str,
    ):
        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s='%s' WHERE %s='%s'" % (
                    TICK_SUBSTAGE_TABLE,
                    TICK_SUBSTAGE_NAME,
                    str(new_name),
                    TICK_SUBSTAGE_ID,
                    int(existing_substage_id))

            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing tick items" % str(e1))
        finally:
            self.close()

    def add_new_substage_to_qualification(
            self, qualification_id:str, new_substage_name: str
    ):
        if self.does_substage_with_name_exist(substage_name=new_substage_name, qualification_id=qualification_id):
            raise Exception("Can't add %s as already exists for this qualification" % new_substage_name)

        new_substage = TickSubStage(stage_id=qualification_id, name=new_substage_name, id=str(self.next_available_id()))

        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                self.create_table()

            self.add_substage_without_checks_or_commit(new_substage)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing substage" % str(e1))
        finally:
            self.close()


    def get_substage_with_id(self, substage_id: str, default=arg_not_passed):
        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                if default is arg_not_passed:
                    raise MissingData("%s not found" % substage_id)
                else:
                    return default

            cursor = self.cursor
            cursor.execute('''SELECT  %s, %s FROM %s WHERE %s='%s' ''' % (
                TICK_SUBSTAGE_NAME,
                QUALIFICATION_ID,
                TICK_SUBSTAGE_TABLE,
                TICK_SUBSTAGE_ID,
                int(substage_id)
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading tick items" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            if default is arg_not_passed:
                raise MissingData("%s not found" % substage_id)
            else:
                return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one %s matches" % substage_id)

        raw_item = raw_list[0]

        return TickSubStage(name=raw_item[0], id=substage_id, stage_id=str(raw_item[1]))

    def does_substage_with_name_exist(self, substage_name: str, qualification_id:str):
        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                return False
            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s='%s' AND %s='%s' ''' % (
                TICK_SUBSTAGE_TABLE,
                TICK_SUBSTAGE_NAME,
                str(substage_name),
                QUALIFICATION_ID,
                int(qualification_id)
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading substages" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                TICK_SUBSTAGE_ID,
                TICK_SUBSTAGE_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])


    def read(self) -> ListOfTickSubStages:
        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                return ListOfTickSubStages.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s ORDER BY %s''' % (
                TICK_SUBSTAGE_NAME,
                TICK_SUBSTAGE_ID,
                QUALIFICATION_ID,
                TICK_SUBSTAGE_TABLE,
                TICK_SUBSTAGE_ID
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading tick substages" % str(e1))
        finally:
            self.close()

        new_list = [
            TickSubStage(name=raw_item[0], id=str(raw_item[1]), stage_id=str(raw_item[2]))
        for raw_item in raw_list]

        return ListOfTickSubStages(new_list)

    def write(self, list_of_tick_substages: ListOfTickSubStages):
        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (TICK_SUBSTAGE_TABLE))

            for substage in list_of_tick_substages:
                self.add_substage_without_checks_or_commit(substage)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing substages" % str(e1))
        finally:
            self.close()

    def add_substage_without_checks_or_commit(self, substage: TickSubStage):
        name = substage.name
        id = int(substage.id)
        stage_id = int(substage.stage_id)

        insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?, ?)" % (
            TICK_SUBSTAGE_TABLE, TICK_SUBSTAGE_NAME, TICK_SUBSTAGE_ID, QUALIFICATION_ID)

        self.cursor.execute(insertion, (
            name, id, stage_id))

    def create_table(self):
        try:
            self.cursor.execute("DROP TABLE %s" % TICK_SUBSTAGE_TABLE)
            self.conn.commit()
        except:
            pass

        table_creation_query = """
                CREATE TABLE %s (
                    %s STR, 
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (TICK_SUBSTAGE_TABLE,
                    TICK_SUBSTAGE_NAME,
                   QUALIFICATION_ID,
                   TICK_SUBSTAGE_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
INDEX_TICK_SUBSTAGE_TABLE, TICK_SUBSTAGE_TABLE, TICK_SUBSTAGE_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating substage table" % str(e1))
        finally:
            self.close()





