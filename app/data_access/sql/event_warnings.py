from app.data_access.sql.generic_sql_data import GenericSqlData, int2bool, bool2int
from app.objects.event_warnings import ListOfEventWarnings, EventWarningLog
from app.data_access.sql.shared_column_names import *

EVENT_WARNING_TABLE = "event_warning_table"
INDEX_EVENT_WARNING_TABLE = "index_event_warning_table"


class SqlDataListOfEventWarnings(GenericSqlData):
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

