from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.substages import ListOfTickSubStages, TickSubStage

TICK_SUBSTAGE_TABLE = "tick_substages"
INDEX_TICK_SUBSTAGE_TABLE = "index_tick_substages"

class SqlDataListOfTickSubStages(GenericSqlData):
    def read(self) -> ListOfTickSubStages:
        try:
            if self.table_does_not_exist(TICK_SUBSTAGE_TABLE):
                return ListOfTickSubStages.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s ORDER BY %s''' % (
                TICK_SUBSTAGE_NAME,
                TICK_SUBSTAGE_ID,
                TICK_SUBSTAGE_TABLE,
                TICK_SUBSTAGE_ID
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading tick substages" % str(e1))
        finally:
            self.close()

        new_list = [
            TickSubStage(name=raw_item[0], id=str(raw_item[1]))
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
                name = substage.name
                id = int(substage.id)

                insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
TICK_SUBSTAGE_TABLE, TICK_SUBSTAGE_NAME, TICK_SUBSTAGE_ID)

                self.cursor.execute(insertion, (
                    name, id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing substages" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                CREATE TABLE %s (
                    %s STR, 
                    %s INTEGER
                );
            """ % (TICK_SUBSTAGE_TABLE,
                    TICK_SUBSTAGE_NAME,
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





