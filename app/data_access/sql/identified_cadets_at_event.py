from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.cadets import (
    OLD_TEMPORARY_SKIP_TEST_CADET_ID,
    TEMPORARY_SKIP_TEST_CADET_ID,
    permanent_skip_cadet_id,
    temporary_skip_cadet_id,
)
from app.objects.identified_cadets_at_event import (
    ListOfIdentifiedCadetsAtEvent,
    IdentifiedCadetAtEvent,
)
from app.data_access.sql.shared_column_names import *

CADET_IDENTIFIED_AT_EVENT_TABLE = "identified_cadets_at_event"
INDEX_CADET_IDENTIFIED_AT_EVENT_TABLE = "index_identified_cadets_at_event"


class SqlDataListOfIdentifiedCadetsAtEvent(GenericSqlData):
    def delete_cadet_from_identified_data_and_return_messages(
        self, event_id: str, cadet_id: str
    ):
        if not self.is_cadet_identified_at_event(event_id=event_id, cadet_id=cadet_id):
            return []

        self.delete_cadet_from_identified_data(event_id=event_id, cadet_id=cadet_id)

        return [
            "Removed cadet identification data, for cadet %s from event %s"
            % (cadet_id, event_id)
        ]

    def is_cadet_identified_at_event(self, event_id: str, cadet_id: str):
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d AND %s=%d """
                % (
                    CADET_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at event" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def delete_cadet_from_identified_data(self, event_id: str, cadet_id: str):
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                return

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d"
                % (
                    CADET_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def mark_row_as_permanently_skip_cadet(self, event_id: str, row_id: str):
        self.update_or_add_identified_cadet_and_row(
            event_id=event_id, row_id=row_id, cadet_id=permanent_skip_cadet_id
        )

    def mark_row_as_temporarily_skip_cadet(self, event_id: str, row_id: str):
        self.update_or_add_identified_cadet_and_row(
            event_id=event_id, row_id=row_id, cadet_id=temporary_skip_cadet_id
        )

    def update_or_add_identified_cadet_and_row(
        self, event_id: str, row_id: str, cadet_id: str
    ):
        if self.is_row_already_used(event_id=event_id, row_id=row_id):
            self._update_row_without_checks(
                event_id=event_id, row_id=row_id, cadet_id=cadet_id
            )
        else:
            self._add_row_without_checks(
                event_id=event_id, row_id=row_id, cadet_id=cadet_id
            )

    def is_row_already_used(self, row_id: str, event_id: str):
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d  AND %s=%s"""
                % (
                    CADET_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    ROW_ID,
                    str(row_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at event" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def _update_row_without_checks(self, event_id: str, row_id: str, cadet_id: str):
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                self.create_table()

            self.cursor.execute(
                "UPDATE %s SET %s=%d WHERE %s=%d AND %s='%s'"
                % (
                    CADET_IDENTIFIED_AT_EVENT_TABLE,
                    CADET_ID,
                    int(cadet_id),
                    EVENT_ID,
                    int(event_id),
                    ROW_ID,
                    str(row_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def _add_row_without_checks(self, event_id: str, row_id: str, cadet_id: str):
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                self.create_table()

            identified_cadet_at_event = IdentifiedCadetAtEvent(
                cadet_id=cadet_id, row_id=row_id
            )
            self._insert_row_without_commit_or_checks(
                event_id=event_id, identified_cadet_at_event=identified_cadet_at_event
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def read(self, event_id: str) -> ListOfIdentifiedCadetsAtEvent:
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                return ListOfIdentifiedCadetsAtEvent.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s FROM %s WHERE %s=%d """
                % (
                    CADET_ID,
                    ROW_ID,
                    CADET_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at event" % str(e1))
        finally:
            self.close()

        new_list = [
            IdentifiedCadetAtEvent(cadet_id=str(raw_item[0]), row_id=str(raw_item[1]))
            for raw_item in raw_list
        ]

        return ListOfIdentifiedCadetsAtEvent(new_list)

    def write(
        self, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent, event_id: str
    ):
        try:
            if self.table_does_not_exist(CADET_IDENTIFIED_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (CADET_IDENTIFIED_AT_EVENT_TABLE, EVENT_ID, int(event_id))
            )

            for identified_cadet_at_event in list_of_cadets_at_event:
                self._insert_row_without_commit_or_checks(
                    event_id=event_id,
                    identified_cadet_at_event=identified_cadet_at_event,
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def _insert_row_without_commit_or_checks(
        self, event_id: str, identified_cadet_at_event: IdentifiedCadetAtEvent
    ):
        cadet_id = int(identified_cadet_at_event.cadet_id)
        row_id = str(identified_cadet_at_event.row_id)

        ## FIXME: EVENTUALLY REMOVE
        if cadet_id == OLD_TEMPORARY_SKIP_TEST_CADET_ID:
            cadet_id = TEMPORARY_SKIP_TEST_CADET_ID

        insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?, ?,?)" % (
            CADET_IDENTIFIED_AT_EVENT_TABLE,
            EVENT_ID,
            CADET_ID,
            ROW_ID,
        )
        self.cursor.execute(insertion, (int(event_id), cadet_id, row_id))

    def create_table(self):
        table_creation_query = """
                    CREATE TABLE %s (
                        %s INT, 
                        %s INT, 
                        %s STR
                    );
                """ % (
            CADET_IDENTIFIED_AT_EVENT_TABLE,
            EVENT_ID,
            CADET_ID,
            ROW_ID,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
            INDEX_CADET_IDENTIFIED_AT_EVENT_TABLE,
            CADET_IDENTIFIED_AT_EVENT_TABLE,
            EVENT_ID,
            ROW_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating identified cadets at event table" % str(e1)
            )
        finally:
            self.close()
