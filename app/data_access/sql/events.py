from copy import copy

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.utilities.transform_data import date2int, int2date

from app.data_access.sql.shared_column_names import *
from app.objects.utilities.exceptions import (
    arg_not_passed,
    MultipleMatches,
    missing_data,
)

EVENTS_TABLE = "list_of_events"
INDEX_EVENTS_TABLE = "index_list_of_events"
REGISTRATION_DATES_APPLIED_FOR_EVENTS_TABLE = "registration_dates_applied_for_events"

from app.objects.events import (
    ListOfEvents,
    SORT_BY_START_DSC,
    SORT_BY_START_ASC,
    SORT_BY_NAME,
    Event,
     remove_event_and_possibly_past_events_and_sort, get_N_most_recent_events_newest_last,
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

        event.id = self.next_available_id()
        try:
            if self.table_does_not_exist(EVENTS_TABLE):
                self.create_table()
            self._add_row_without_commit_or_checks(event)
            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing events table" % str(e1))
        finally:
            self.close()

    def next_available_id(self) -> int:
        return self.last_used_id() + 1

    def last_used_id(self) -> int:
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

    def get_event_from_id(self, event_id: str, default=missing_data) -> Event:
        if self.table_does_not_exist(EVENTS_TABLE):
            return default

        try:
            cursor = self.cursor
            statement = "SELECT %s, %s, %s, %s FROM %s WHERE %s=%d " % (
                EVENT_NAME,
                EVENT_START_DATE,
                EVENT_END_DATE,
                EVENT_REG_DATE,
                EVENTS_TABLE,
                EVENT_ID,
                int(event_id),
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading events data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list) > 1:
            raise MultipleMatches("more than one event with id %s" % event_id)

        raw_event = raw_list[0]
        event = Event(
            event_name=raw_event[0],
            start_date=int2date(raw_event[1]),
            end_date=int2date(raw_event[2]),
            registration_date=int2date(raw_event[3]),
            id=event_id,
        )

        return event

    def read(self, sort_by: str = arg_not_passed) -> ListOfEvents:
        if self.table_does_not_exist(EVENTS_TABLE):
            return ListOfEvents.create_empty()

        """
        ## FIXME CAN DELETE ONCE ALL PAST DATA CLEARED FROM SNAPSHOTS
        try:
            self.cursor.execute("ALTER TABLE %s ADD %s INTEGER DEFAULT %d" % (EVENTS_TABLE, EVENT_REG_DATE,
                                                                                      date2int(NO_REGISTRATION_DATE )))
            self.conn.commit()
        except:
            pass
        """

        try:
            sort_clause = get_sort_clause(sort_by)
            cursor = self.cursor
            statement = "SELECT %s, %s, %s, %s, %s FROM %s %s" % (
                EVENT_NAME,
                EVENT_START_DATE,
                EVENT_END_DATE,
                EVENT_REG_DATE,
                EVENT_ID,
                EVENTS_TABLE,
                sort_clause,
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
                registration_date=int2date(raw_event[3]),
                id=str(raw_event[4]),
            )

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
                self._add_row_without_commit_or_checks(event)

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing events table" % str(e1))
        finally:
            self.close()

    def _add_row_without_commit_or_checks(self, event: Event):
        event_name = event.event_name
        start_date = date2int(event.start_date)
        end_date = date2int(event.end_date)
        event_id = int(event.id)
        registration_date = date2int(event.registration_date)

        insertion = "INSERT INTO %s ( %s, %s, %s, %s, %s) VALUES ( ?,?,?,?, ?)" % (
            EVENTS_TABLE,
            EVENT_NAME,
            EVENT_START_DATE,
            EVENT_END_DATE,
            EVENT_REG_DATE,
            EVENT_ID,
        )

        self.cursor.execute(
            insertion, (event_name, start_date, end_date, registration_date, event_id)
        )

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s INTEGER,
                %s INTEGER
            );
        """ % (
            EVENTS_TABLE,
            EVENT_NAME,
            EVENT_START_DATE,
            EVENT_END_DATE,
            EVENT_ID,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_EVENTS_TABLE,
            EVENTS_TABLE,
            EVENT_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s creating events table" % str(e1))
        finally:
            self.close()
