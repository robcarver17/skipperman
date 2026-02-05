from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, int2date

from app.data_access.sql.shared_column_names import *
from app.objects.utilities.exceptions import arg_not_passed, MissingData, MultipleMatches

EVENTS_TABLE = "list_of_events"
INDEX_EVENTS_TABLE = "index_list_of_events"

from app.objects.events import (
    ListOfEvents,
    SORT_BY_START_DSC,
    SORT_BY_START_ASC,
    SORT_BY_NAME,
    Event,
)


def get_sort_clause(sort_by: str = arg_not_passed):
    if sort_by == SORT_BY_NAME:
        return "ORDER BY %s" % EVENT_NAME
    elif sort_by == SORT_BY_START_ASC:
        return "ORDER BY %s" % EVENT_START_DATE
    elif sort_by == SORT_BY_START_DSC:
        return "ORDER BY %s DESC" % EVENT_START_DATE
    else:
        return ""

class SqlDataListOfEvents(GenericSqlData):
    def add_event(self, event: Event):
        if event.invalid:
            raise Exception("Event invalid because %s" % event.invalid_reason())

        existing_events = self.read()
        existing_events.confirm_event_does_not_already_exist(event)

        event_id = self.next_available_id()

        try:
            if self.table_does_not_exist(EVENTS_TABLE):
                self.create_table()

            event_name = event.event_name
            start_date = date2int(event.start_date)
            end_date = date2int(event.end_date)

            insertion = "INSERT INTO %s ( %s, %s, %s, %s) VALUES ( ?,?,?,?)" % (
                    EVENTS_TABLE, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_ID)

            self.cursor.execute(insertion, (event_name, start_date, end_date, event_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing events table" % str(e1))
        finally:
            self.close()


    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(EVENTS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                EVENT_ID,
                EVENTS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading events data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def get_event_from_id(self, event_id: str, default=arg_not_passed) -> Event:
        if self.table_does_not_exist(EVENTS_TABLE):
            if default is arg_not_passed:
                raise MissingData("event id %s not found" % event_id)
            else:
                return default

        try:
            cursor = self.cursor
            statement = "SELECT %s, %s, %s FROM %s WHERE %s='%s' " % (
                EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENTS_TABLE,
                EVENT_ID, int(event_id)
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading events data" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            if default is arg_not_passed:
                raise MissingData("event id %s not found" % event_id)
            else:
                return default
        elif len(raw_list)>1:
            raise MultipleMatches("more than one event with id %s" % event_id)

        raw_event = raw_list[0]
        event = Event(
                event_name=raw_event[0],
            start_date=int2date(raw_event[1]),
            end_date=int2date(raw_event[2]),
            id=event_id)

        return event

    def read(self, sort_by: str =arg_not_passed) -> ListOfEvents:
        if self.table_does_not_exist(EVENTS_TABLE):
            return ListOfEvents.create_empty()

        try:
            sort_clause = get_sort_clause(sort_by)
            cursor = self.cursor
            statement = "SELECT %s, %s, %s, %s FROM %s %s" % (
                EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_ID, EVENTS_TABLE,
                sort_clause
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
                event_id = int(event.id)

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
                %s INTEGER
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
