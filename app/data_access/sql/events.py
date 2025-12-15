from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, int2date

from app.objects.events import ListOfEvents
from app.objects.events import Event
from app.data_access.sql.shared_column_names import *

EVENTS_TABLE = "list_of_events"
INDEX_EVENTS_TABLE = "index_list_of_events"



class SqlDataListOfEvents(GenericSqlData):
    def read(self) -> ListOfEvents:
        if self.table_does_not_exist(EVENTS_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            statement = "SELECT %s, %s, %s, %s FROM %s" % (
                EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_ID, EVENTS_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading events data" % str(e1))
        finally:
            self.close()

        new_list = []
        for raw_event in raw_list:
            event = Event(
                event_name=raw_event[0],
            start_date=int2date(raw_event[1]),
            end_date=int2date(raw_event[2]),
            id=str(raw_event[3]))

            new_list.append(event)

        return ListOfEvents(new_list)

    def write(self, list_of_events: ListOfEvents):
        pass

        try:
            if self.table_does_not_exist(EVENTS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (EVENTS_TABLE))

            for event in list_of_events:
                event_name = event.event_name
                start_date = date2int(event.start_date)
                end_date = date2int(event.end_date)
                event_id = str(event.id)

                insertion = "INSERT INTO %s ( %s, %s, %s, %s) VALUES ( ?,?,?,?)" % (
                    EVENTS_TABLE, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_ID)

                self.cursor.execute(insertion, (event_name, start_date, end_date, event_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing events table" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s INTEGER,
                %s STR
            );
        """ % (EVENTS_TABLE,
               EVENT_NAME,
               EVENT_START_DATE, EVENT_END_DATE, EVENT_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_EVENTS_TABLE, EVENTS_TABLE, EVENT_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s creating events table" % str(e1))
        finally:
            self.close()
