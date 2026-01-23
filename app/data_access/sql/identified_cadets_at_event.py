from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.cadets import OLD_TEMPORARY_SKIP_TEST_CADET_ID, TEMPORARY_SKIP_TEST_CADET_ID
from app.objects.identified_cadets_at_event import ListOfIdentifiedCadetsAtEvent, IdentifiedCadetAtEvent
from app.data_access.sql.shared_column_names import *

CADET_IDENTIFIED_AT_EVENT_TABLE = "identified_cadets_at_event"
INDEX_CADET_IDENTIFIED_AT_EVENT_TABLE = "index_identified_cadets_at_event"

class SqlDataListOfIdentifiedCadetsAtEvent(
    GenericSqlData
):
    def read(self, event_id: str) -> ListOfIdentifiedCadetsAtEvent:
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                return ListOfIdentifiedCadetsAtEvent.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ''' % (
                CADET_ID, ROW_ID, CADET_IDENTIFIED_AT_EVENT_TABLE, EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at event" % str(e1))
        finally:
            self.close()

        new_list = [
            IdentifiedCadetAtEvent(cadet_id=str(raw_item[0]), row_id = raw_item[1])
            for raw_item in raw_list]

        return ListOfIdentifiedCadetsAtEvent(new_list)

    def write(
        self, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent, event_id: str
    ):
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADET_IDENTIFIED_AT_EVENT_TABLE, EVENT_ID, event_id))

            for identified_cadet_at_event in list_of_cadets_at_event:
                cadet_id = int(identified_cadet_at_event.cadet_id)
                row_id = str(identified_cadet_at_event.row_id)

                ## FIXME: EVENTUALLY REMOVE
                if cadet_id==OLD_TEMPORARY_SKIP_TEST_CADET_ID:
                    cadet_id = TEMPORARY_SKIP_TEST_CADET_ID

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?, ?,?)" % (
                    CADET_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    CADET_ID,
                    ROW_ID)
                self.cursor.execute(insertion,
                                    (int(event_id), cadet_id, row_id))


            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to identified cadets at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()


    def create_table(self):

        table_creation_query = """
                    CREATE TABLE %s (
                        %s INT, 
                        %s INT, 
                        %s STR
                    );
                """ % (CADET_IDENTIFIED_AT_EVENT_TABLE,
                       EVENT_ID,
                       CADET_ID,
                       ROW_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
            INDEX_CADET_IDENTIFIED_AT_EVENT_TABLE,
            CADET_IDENTIFIED_AT_EVENT_TABLE,
            EVENT_ID,
            ROW_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating identified cadets at event table" % str(e1))
        finally:
            self.close()
