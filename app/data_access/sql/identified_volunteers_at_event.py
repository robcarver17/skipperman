from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent, IdentifiedVolunteerAtEvent, \
    PERMANENT_SKIP_VOLUNTEER_ID, SKIP_FOR_NOW_VOLUNTEER_ID, OLD_SKIP_FOR_NOW_VOLUNTEER_ID, \
    OLD_PERMANENT_SKIP_VOLUNTEER_ID

VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE = "volunteer_identified_at_event"
INDEX_VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE = "index_volunteer_identified_at_event"


class SqlDataListOfIdentifiedVolunteersAtEvent(
    GenericSqlData
):
    def read(self, event_id: str) -> ListOfIdentifiedVolunteersAtEvent:
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                return ListOfIdentifiedVolunteersAtEvent.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                VOLUNTEER_ID,
                VOLUNTEER_INDEX,
                ROW_ID,
                VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
                 EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers at event" % str(e1))
        finally:
            self.close()

        new_list = [
            IdentifiedVolunteerAtEvent(volunteer_id=str(raw_item[0]),
                                       volunteer_index = int(raw_item[1]),
                                       row_id = raw_item[2])
            for raw_item in raw_list]

        return ListOfIdentifiedVolunteersAtEvent(new_list)

    def write(
        self,
        list_of_identified_volunteers: ListOfIdentifiedVolunteersAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE, EVENT_ID, event_id))

            for identified_volunteer_at_event in list_of_identified_volunteers:
                volunteer_id = identified_volunteer_at_event.volunteer_id
                row_id = str(identified_volunteer_at_event.row_id)
                volunteer_index = int(identified_volunteer_at_event.volunteer_index)

                # FIXME TEMP CODE
                if volunteer_id == OLD_SKIP_FOR_NOW_VOLUNTEER_ID:
                    volunteer_id = SKIP_FOR_NOW_VOLUNTEER_ID
                elif volunteer_id == OLD_PERMANENT_SKIP_VOLUNTEER_ID:
                    volunteer_id = PERMANENT_SKIP_VOLUNTEER_ID

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?, ?)" % (
                    VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    VOLUNTEER_ID,
                    VOLUNTEER_INDEX,
                    ROW_ID)
                self.cursor.execute(insertion,
                                    (int(event_id), int(volunteer_id),
                                     volunteer_index, row_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to identified volunteers at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                        CREATE TABLE %s (
                            %s INT, 
                            %s INT,
                            %s INT, 
                            %s STR
                        );
                    """ % (VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
                           EVENT_ID,
                           VOLUNTEER_ID,
                           VOLUNTEER_INDEX,
                           ROW_ID
                           )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s, %s)" % (
            INDEX_VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
        VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
        EVENT_ID,
        ROW_ID,
        VOLUNTEER_INDEX)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating identified volunteers at event table" % str(e1))
        finally:
            self.close()
