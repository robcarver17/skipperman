from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.identified_volunteer_at_event import (
    ListOfIdentifiedVolunteersAtEvent,
    IdentifiedVolunteerAtEvent,
    PERMANENT_SKIP_VOLUNTEER_ID,
    SKIP_FOR_NOW_VOLUNTEER_ID,
)

VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE = "volunteer_identified_at_event"
INDEX_VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE = "index_volunteer_identified_at_event"


class SqlDataListOfIdentifiedVolunteersAtEvent(GenericSqlData):
    def mark_volunteer_as_skipped_permanently(
        self, event_id: str, row_id: str, volunteer_index: int
    ):
        self.add_or_update_identified_volunteer(
            event_id=event_id,
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=PERMANENT_SKIP_VOLUNTEER_ID,
        )

    def mark_volunteer_as_skipped_for_now(
        self, event_id: str, row_id: str, volunteer_index: int
    ):
        self.add_or_update_identified_volunteer(
            event_id=event_id,
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=SKIP_FOR_NOW_VOLUNTEER_ID,
        )

    def _update_identification_for_volunteer(
        self, event_id: str, row_id: str, volunteer_index: int, volunteer_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                return

            self.cursor.execute(
                "UPDATE %s SET %s=%d WHERE %s=%d AND %s='%s' AND %s=%d "
                % (
                    VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
                    VOLUNTEER_ID,
                    int(volunteer_id),
                    EVENT_ID,
                    int(event_id),
                    ROW_ID,
                    str(row_id),
                    VOLUNTEER_INDEX,
                    int(volunteer_index),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def add_or_update_identified_volunteer(
        self, event_id: str, row_id: str, volunteer_index: int, volunteer_id: str
    ):
        if self.is_this_row_and_index_already_identified(
            event_id=event_id, row_id=row_id, volunteer_index=volunteer_index
        ):
            self._update_identification_for_volunteer(
                event_id=event_id,
                row_id=row_id,
                volunteer_id=volunteer_id,
                volunteer_index=volunteer_index,
            )
        else:
            self._add_identified_volunteer_without_checks(
                event_id=event_id,
                row_id=row_id,
                volunteer_id=volunteer_id,
                volunteer_index=volunteer_index,
            )

    def _add_identified_volunteer_without_checks(
        self, event_id: str, row_id: str, volunteer_index: int, volunteer_id: str
    ):
        identified_volunteer_at_event = IdentifiedVolunteerAtEvent(
            volunteer_index=volunteer_index,
            row_id=row_id,
            volunteer_id=volunteer_id,
        )
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                self.create_table()

            self._add_identified_volunteer_without_checks_or_commits(
                event_id=event_id,
                identified_volunteer_at_event=identified_volunteer_at_event,
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def delete_volunteer_from_identified_data(self, event_id: str, volunteer_id: str):
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d "
                % (
                    VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    VOLUNTEER_ID,
                    int(volunteer_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def is_this_row_and_index_already_identified(
        self, event_id: str, row_id: str, volunteer_index: int
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d AND %s='%s' AND %s=%d """
                % (
                    VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    ROW_ID,
                    str(row_id),
                    VOLUNTEER_INDEX,
                    int(volunteer_index),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers at event" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def read(self, event_id: str) -> ListOfIdentifiedVolunteersAtEvent:
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                return ListOfIdentifiedVolunteersAtEvent.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s FROM %s WHERE %s=%d """
                % (
                    VOLUNTEER_ID,
                    VOLUNTEER_INDEX,
                    ROW_ID,
                    VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers at event" % str(e1))
        finally:
            self.close()

        new_list = [
            IdentifiedVolunteerAtEvent(
                volunteer_id=str(raw_item[0]),
                volunteer_index=int(raw_item[1]),
                row_id=raw_item[2],
            )
            for raw_item in raw_list
        ]

        return ListOfIdentifiedVolunteersAtEvent(new_list)

    def delete_volunteers_at_event(self, event_id: str):
        if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
            return

        self.cursor.execute(
            "DELETE FROM %s WHERE %s=%d"
            % (VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE, EVENT_ID, int(event_id))
        )

        self.conn.commit()


    def write(
        self,
        list_of_identified_volunteers: ListOfIdentifiedVolunteersAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE):
                self.create_table()

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE, EVENT_ID, int(event_id))
            )

            for identified_volunteer_at_event in list_of_identified_volunteers:
                self._add_identified_volunteer_without_checks_or_commits(
                    event_id=event_id,
                    identified_volunteer_at_event=identified_volunteer_at_event,
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to identified volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def _add_identified_volunteer_without_checks_or_commits(
        self, event_id: str, identified_volunteer_at_event: IdentifiedVolunteerAtEvent
    ):
        volunteer_id = identified_volunteer_at_event.volunteer_id
        row_id = str(identified_volunteer_at_event.row_id)
        volunteer_index = int(identified_volunteer_at_event.volunteer_index)

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?, ?)" % (
            VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            VOLUNTEER_INDEX,
            ROW_ID,
        )
        self.cursor.execute(
            insertion, (int(event_id), int(volunteer_id), volunteer_index, row_id)
        )

    def create_table(self):
        table_creation_query = """
                        CREATE TABLE %s (
                            %s INT, 
                            %s INT,
                            %s INT, 
                            %s STR
                        );
                    """ % (
            VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            VOLUNTEER_INDEX,
            ROW_ID,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s, %s)" % (
            INDEX_VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
            VOLUNTEER_IDENTIFIED_AT_EVENT_TABLE,
            EVENT_ID,
            ROW_ID,
            VOLUNTEER_INDEX,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating identified volunteers at event table" % str(e1)
            )
        finally:
            self.close()
