from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.audit_log import AuditLogUpdateWithIds, ListOfAuditLogUpdatesWithIds, ListOfAuditLogUpdatesWithEvents, AuditLogUpdateWithEvents
from app.objects.events import ListOfEvents
from app.objects.utilities.transform_data import date2int, int2date

from app.data_access.sql.shared_column_names import *
from app.objects.utilities.exceptions import (
    arg_not_passed)

AUDIT_LOG_TABLE = "list_of_update_event_audit_logs"
INDEX_AUDIT_LOG_TABLE = "index_list_of_update_event_audit_logs"

SORT_BY_DATE_DSC = "sort_by_date_newest_first"


def get_sort_clause(sort_by: str = arg_not_passed):
    if sort_by == SORT_BY_DATE_DSC:
        return "ORDER BY %s DESC" % UPDATE_DATETIME
    else:
        return ""

def get_event_id_where_clause(event_id: str =arg_not_passed):
    if event_id is arg_not_passed:
        return ""
    else:
        return "WHERE %s=%d " % (EVENT_ID, int(event_id))

class SqlDataListOfAuditUpdates(GenericSqlData):
    def add_audit_log(self, audit_log: AuditLogUpdateWithIds):
        try:
            if self.table_does_not_exist(AUDIT_LOG_TABLE):
                self.create_table()

            self._add_row_without_commit_or_checks(audit_log)

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing events table" % str(e1))
        finally:
            self.close()

    def read_for_all_events(self, sort_by: str =SORT_BY_DATE_DSC) -> ListOfAuditLogUpdatesWithEvents:
        raw_data = self.read(sort_by=sort_by)
        return ListOfAuditLogUpdatesWithEvents(
            [
                AuditLogUpdateWithEvents.from_audit_with_id_and_list_of_events(audit_with_id=audit_with_id,
                                                                               list_of_events=self.list_of_events)
                for audit_with_id in raw_data
            ]
        )

    @property
    def list_of_events(self) -> ListOfEvents:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_events.read
        )

    def read(self, event_id: str =arg_not_passed, sort_by: str =SORT_BY_DATE_DSC) -> ListOfAuditLogUpdatesWithIds:
        if self.table_does_not_exist(AUDIT_LOG_TABLE):
            return ListOfAuditLogUpdatesWithIds()

        try:
            sort_clause = get_sort_clause(sort_by)
            where_clause = get_event_id_where_clause(event_id)
            cursor = self.cursor
            statement = "SELECT  %s, %s, %s, %s FROM %s %s %s" % (
                EVENT_ID,
                USERNAME,
                VOLUNTEER_NAME,
                UPDATE_DATETIME,
                AUDIT_LOG_TABLE,
                where_clause,
                sort_clause,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading audit log data" % str(e1))
        finally:
            self.close()

        new_list = [
            AuditLogUpdateWithIds(
                event_id=str(raw_item[0]),
                username=str(raw_item[1]),
                volunteer_name=str(raw_item[2]),
                datetime_of_update=int2date(raw_item[3],
                )
            ) for raw_item in raw_list

        ]

        return ListOfAuditLogUpdatesWithIds(new_list)

    def write(self, list_of_audit_logs: ListOfAuditLogUpdatesWithIds):
        try:
            if self.table_does_not_exist(AUDIT_LOG_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (AUDIT_LOG_TABLE))

            for audit_log in list_of_audit_logs:
                self._add_row_without_commit_or_checks(audit_log)

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing events table" % str(e1))
        finally:
            self.close()

    def _add_row_without_commit_or_checks(self, audit_log: AuditLogUpdateWithIds):
        event_id = int(audit_log.event_id)
        username = str(audit_log.username)
        volunteer = str(audit_log.volunteer_name)
        update_datetime = date2int(audit_log.datetime_of_update)

        insertion = "INSERT INTO %s ( %s, %s, %s, %s) VALUES ( ?,?,?,  ?)" % (
            AUDIT_LOG_TABLE,
            EVENT_ID,
            USERNAME,
            VOLUNTEER_NAME,
            UPDATE_DATETIME
        )

        self.cursor.execute(insertion, (event_id, username, volunteer, update_datetime))

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER,
                %s STR, 
                %s STR, 
                %s INTEGER
            );
        """ % (
            AUDIT_LOG_TABLE,
            EVENT_ID,
            USERNAME,
            VOLUNTEER_NAME,
            UPDATE_DATETIME
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (
                INDEX_AUDIT_LOG_TABLE,
            AUDIT_LOG_TABLE,
            EVENT_ID,
            USERNAME,
            UPDATE_DATETIME
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s creating audit table" % str(e1))
        finally:
            self.close()

