from typing import List

from app.data_access.sql.generic_sql_data import GenericSqlData, int2bool, bool2int
from app.objects.event_warnings import ListOfEventWarnings, EventWarningLog
from app.data_access.sql.shared_column_names import *
from app.objects.utilities.exceptions import MissingData

EVENT_WARNING_TABLE = "event_warning_table"
INDEX_EVENT_WARNING_TABLE = "index_event_warning_table"


class SqlDataListOfEventWarnings(GenericSqlData):
    def mark_event_warning_with_id_with_ignore_flag(
            self, event_id: str,  warning_id: str, ignore_flag: bool
    ):
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s= '%s' WHERE %s='%s' AND %s='%s'" % (
                EVENT_WARNING_TABLE,
                WARNING_IGNORE,
                bool2int(ignore_flag),
                WARNING_ID,
                int(warning_id),
                EVENT_ID,
                int(event_id)
            )
            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event warnings" % str(e1))
        finally:
            self.close()

    def reverse_ignore_on_active_event_warnings_with_priority_and_category(
            self, event_id: str, category: str, priority: str,
            set_active_to_ignored: bool ## False to set ignored to active
    ):
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                self.create_table()

            original_ignore_flag = not set_active_to_ignored
            new_ignore_flag = not original_ignore_flag

            insertion = "UPDATE %s SET %s='%s' WHERE %s='%s' AND %s='%s' AND %s='%s'" % (
                EVENT_WARNING_TABLE,
                WARNING_IGNORE,
                bool2int(new_ignore_flag),
                EVENT_ID,
                int(event_id),
                CATEGORY,
                str(category),
                PRIORITY,
                str(priority)
            )
            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event warnings" % str(e1))
        finally:
            self.close()


    def add_or_update_list_of_autorefreshed_event_warnings_clearing_any_missing(
            self,
            event_id: str,
            new_list_of_warnings: List[str],
            category: str,
            priority: str,
    ):

        self.delete_any_warnings_missing_from_list(
            event_id=event_id,category=category,priority=priority,
            new_list_of_warnings=new_list_of_warnings
        )
        for warning in new_list_of_warnings:
            self.add_new_event_warning_checking_for_duplicate(
                event_id=event_id,
                warning_log=EventWarningLog(
                    warning=warning,
                    priority=priority,
                    category=category,
                    ignored=False,
                    auto_refreshed=True
                )
            )

    def delete_any_warnings_missing_from_list(self,
                                              event_id: str,
                                              new_list_of_warnings: List[str],
                                              category: str,
                                              priority: str

                                              ):
        existing_warnings = self.all_existing_warnings_of_this_category_and_priority_at_event(
            event_id=event_id,
            category=category,
            priority=priority
        )
        for warning in existing_warnings:
            if warning.auto_refreshed:
                if warning.warning not in new_list_of_warnings:
                    self.delete_warning(warning_id=warning.id, event_id=event_id)

    def delete_warning(self, event_id: str, warning_id: str):
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                raise MissingData("Can't delete non existent warning")

            self.cursor.execute("DELETE FROM %s WHERE %s='%s' AND %s='%s'" % (EVENT_WARNING_TABLE,
                                                                  WARNING_ID,
                                                                  int(warning_id),
                                                                  EVENT_ID,
                                                                  int(event_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event warnings" % str(e1))
        finally:
            self.close()

    def add_new_event_warning_checking_for_duplicate(
            self,
            event_id: str,
            warning_log: EventWarningLog
    ):
        if self.duplicate_warning_exists_in_data(event_id=event_id, warning_log=warning_log):
            return

        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                self.create_table()

            event_id_as_int = int(event_id)
            next_id = self.next_available_id()

            insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s) VALUES (?,?, ?,?,?,?,?)" % (
                EVENT_WARNING_TABLE,
                EVENT_ID,
                PRIORITY,
                CATEGORY,
                WARNING_TEXT,
                WARNING_AUTO_REFRESH,
                WARNING_IGNORE,
                WARNING_ID
            )
            self.cursor.execute(insertion, (
                event_id_as_int,
            warning_log.priority,
            warning_log.category,
            warning_log.warning,
            bool2int(warning_log.auto_refreshed),
            bool2int(warning_log.ignored),
            int(next_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event warnings" % str(e1))
        finally:
            self.close()

    def duplicate_warning_exists_in_data(
            self,
            event_id: str,
            warning_log: EventWarningLog
    ):
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                return False

            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s='%s' AND %s='%s' AND %s='%s' AND %s='%s' ''' % (

                EVENT_WARNING_TABLE,
                EVENT_ID,
                int(event_id),
                CATEGORY,
                str(warning_log.category),
                PRIORITY,
                str(warning_log.priority),
                WARNING_TEXT,
                str(warning_log.warning)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading event warnings" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0


    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                WARNING_ID,
                EVENT_WARNING_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading warnings data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def all_existing_warnings_of_this_category_and_priority_at_event(self, event_id: str,
                                                                     category: str,
                                                                     priority: str) ->ListOfEventWarnings:
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                return ListOfEventWarnings.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s WHERE %s='%s' AND %s='%s' AND %s='%s' ''' % (
                WARNING_TEXT,
                WARNING_AUTO_REFRESH,
                WARNING_IGNORE,
                WARNING_ID,
                EVENT_WARNING_TABLE,
                EVENT_ID,
                int(event_id),
                CATEGORY,
                str(category),
                PRIORITY,
                str(priority)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading event warnings" % str(e1))
        finally:
            self.close()

        new_list = [
        EventWarningLog(
            priority=str(priority),
            category=str(category),
            warning=str(raw_warning[0]),
            auto_refreshed=int2bool(raw_warning[1]),
            ignored=int2bool(raw_warning[2]),
            id=str(raw_warning[3])

        )
        for raw_warning in raw_list]

        return ListOfEventWarnings(new_list)

    def read(self, event_id: str) ->ListOfEventWarnings:
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                return ListOfEventWarnings.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                PRIORITY,
                CATEGORY,
                WARNING_TEXT,
                WARNING_AUTO_REFRESH,
                WARNING_IGNORE,
                WARNING_ID,
                EVENT_WARNING_TABLE,
                EVENT_ID,
                int(event_id)

            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading event warnings" % str(e1))
        finally:
            self.close()

        new_list = [
        EventWarningLog(
            priority=str(raw_warning[0]),
            category=str(raw_warning[1]),
            warning=str(raw_warning[2]),
            auto_refreshed=int2bool(raw_warning[3]),
            ignored=int2bool(raw_warning[4]),
            id=str(raw_warning[5])

        )
        for raw_warning in raw_list]

        return ListOfEventWarnings(new_list)

    def write(self, event_warnings: ListOfEventWarnings, event_id: str):
        try:
            if self.table_does_not_exist(EVENT_WARNING_TABLE):
                self.create_table()

            event_id_as_int = int(event_id)
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (EVENT_WARNING_TABLE,
                                                                  EVENT_ID,
                                                                  event_id_as_int))

            for warning in event_warnings:

                insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s) VALUES (?,?, ?,?,?,?,?)" % (
                    EVENT_WARNING_TABLE,
                    EVENT_ID,
                    PRIORITY,
                    CATEGORY,
                    WARNING_TEXT,
                    WARNING_AUTO_REFRESH,
                    WARNING_IGNORE,
                    WARNING_ID
                )
                self.cursor.execute(insertion, (
                    event_id_as_int,
                warning.priority,
                warning.category,
                warning.warning,
                bool2int(warning.auto_refreshed),
                bool2int(warning.ignored),
                int(warning.id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event warnings" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                        CREATE TABLE %s (
                        %s INT,
                            %s STR,
                            %s STR,
                            %s STR,
                            %s INT, 
                            %s INT, 
                            %s INT
                        );
                    """ % (EVENT_WARNING_TABLE,
                           EVENT_ID,
                           PRIORITY,
                           CATEGORY,
                           WARNING_TEXT,
                           WARNING_AUTO_REFRESH,
                           WARNING_IGNORE,
                           WARNING_ID
                           )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (
            INDEX_EVENT_WARNING_TABLE,
            EVENT_WARNING_TABLE,
            EVENT_ID,
            WARNING_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating warnings table" % str(e1))
        finally:
            self.close()

