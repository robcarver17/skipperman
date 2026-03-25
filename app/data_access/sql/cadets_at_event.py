from typing import List


from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.cadet_with_id_at_event import (
    ListOfCadetsWithIDAtEvent,
    CadetWithIdAtEvent,
)
from app.objects.cadets import ListOfCadets
from app.objects.composed.cadets_at_event_with_registration_data import (
    CadetRegistrationData,
    DictOfCadetsWithRegistrationData,
)
from app.objects.day_selectors import DaySelector, Day
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import RegistrationStatus, ACTIVE_STATUS_NAMES
from app.objects.utilities.exceptions import missing_data, MultipleMatches

CADETS_AT_EVENT_TABLE = "cadets_at_event"
INDEX_CADETS_AT_EVENT_TABLE = "index_cadets_at_event"
REGISTRATION_ROW_FOR_CADETS_TABLE = "registration_row_data_for_cadets_at_event"
INDEX_REGISTRATION_ROW_FOR_CADETS_TABLE = (
    "index_registration_row_data_for_cadets_at_event"
)

ACTIVE_STATUS_NAMES_AS_STR = "('%s')" % ("','".join(ACTIVE_STATUS_NAMES))


class SqlDataListOfCadetsAtEvent(GenericSqlData):
    def update_registration_details_for_existing_cadet_at_event_who_was_manual(
        self,
        event_id: str,
        cadet_id: str,
        row_in_registration_data: RowInRegistrationData,
    ):
        try:
            if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
                raise Exception("cadet not found in data")

            self._write_row_of_registration_data_for_cadet_at_event_without_commit(
                cadet_id=cadet_id,
                event_id=event_id,
                row_in_registration_data=row_in_registration_data,
            )
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to groups at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def update_status_of_existing_cadet_at_event(
        self, event_id: str, cadet_id: str, new_status: RegistrationStatus
    ):
        if not self.is_cadet_at_event(event_id=event_id, cadet_id=cadet_id):
            raise Exception("cadet not at event")

        status = new_status.name

        try:
            insertion = " UPDATE %s SET %s='%s' WHERE %s=%d AND %s=%d " % (
                CADETS_AT_EVENT_TABLE,
                CADET_REGISTRATION_STATUS,
                status,
                EVENT_ID,
                int(event_id),
                CADET_ID,
                int(cadet_id),
            )
            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def make_cadet_unavailable_on_day(self, event_id: str, cadet_id: str, day: Day):
        self.change_cadet_availability_on_day(
            event_id=event_id, cadet_id=cadet_id, day=day, available=False
        )

    def make_cadet_available_on_day(self, event_id: str, cadet_id: str, day: Day):
        self.change_cadet_availability_on_day(
            event_id=event_id, cadet_id=cadet_id, day=day, available=True
        )

    def change_cadet_availability_on_day(
        self, event_id: str, cadet_id: str, day: Day, available: bool
    ):
        cadet_at_event = self.get_existing_cadet_at_event(
            event_id=event_id, cadet_id=cadet_id, default=missing_data
        )
        if cadet_at_event is missing_data:
            raise Exception("cadet not at event")

        if available:
            cadet_at_event.availability.make_available_on_day(day)
        else:
            cadet_at_event.availability.make_unavailable_on_day(day)

        availability = cadet_at_event.availability.as_str()

        try:
            insertion = " UPDATE %s SET %s='%s' WHERE %s=%d AND %s=%d " % (
                CADETS_AT_EVENT_TABLE,
                CADET_AVAILABLITY,
                availability,
                EVENT_ID,
                int(event_id),
                CADET_ID,
                int(cadet_id),
            )
            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def get_existing_cadet_at_event(
        self, event_id: str, cadet_id: str, default=missing_data
    ) -> CadetWithIdAtEvent:
        if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
            return default

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s, %s, %s FROM %s WHERE %s=%d AND %s=%d """
                % (
                    CADET_ID,
                    CADET_AVAILABLITY,
                    CADET_REGISTRATION_STATUS,
                    CADET_REGISTRATION_NOTES,
                    CADET_HEALTH,
                    CADETS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at events" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list) > 1:
            raise MultipleMatches

        raw_data = raw_list[0]
        availability = DaySelector.from_str(raw_data[1])
        status = RegistrationStatus(raw_data[2])
        notes = str(raw_data[3])
        health = str(raw_data[4])

        row_of_registration_data = self._read_registration_data(
            event_id=event_id, cadet_id=cadet_id
        )

        cadet_at_event = CadetWithIdAtEvent(
            cadet_id=cadet_id,
            availability=availability,
            status=status,
            notes=notes,
            health=health,
            data_in_row=row_of_registration_data,
        )

        return cadet_at_event

    def replace_existing_cadet_at_event_where_original_cadet_was_inactive(
        self, event_id: str, new_cadet_at_event: CadetWithIdAtEvent
    ):
        self.delete_cadet_from_event_and_return_messages(
            event_id=event_id, cadet_id=new_cadet_at_event.cadet_id
        )
        self.add_new_cadet_to_event(
            event_id=event_id, cadet_at_event=new_cadet_at_event
        )

    def update_notes_for_existing_cadet_at_event(
        self, event_id: str, cadet_id: str, new_notes: str
    ):
        try:
            if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
                raise Exception("No cadet at event data")

            insertion = "UPDATE %s SET %s=? WHERE %s=%d AND %s=%d" % (
                CADETS_AT_EVENT_TABLE,
                CADET_REGISTRATION_NOTES,
                EVENT_ID,
                int(event_id),
                CADET_ID,
                int(cadet_id),
            )
            self.cursor.execute(insertion, (str(new_notes),))

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def update_health_for_existing_cadet_at_event(
        self, event_id: str, cadet_id: str, new_health: str
    ):
        try:
            if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
                raise Exception("No cadet at event data")

            insertion = "UPDATE %s SET %s=? WHERE %s=%d AND %s=%d" % (
                CADETS_AT_EVENT_TABLE,
                CADET_HEALTH,
                EVENT_ID,
                int(event_id),
                CADET_ID,
                int(cadet_id),
            )
            self.cursor.execute(insertion, (str(new_health),))

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def update_row_in_registration_data_for_existing_cadet_at_event(
        self, event_id: str, cadet_id: str, column_name: str, new_value_for_column
    ):
        try:
            if self.table_does_not_exist(REGISTRATION_ROW_FOR_CADETS_TABLE):
                self._create_registration_row_data_table()

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d AND %s='%s'"
                % (
                    REGISTRATION_ROW_FOR_CADETS_TABLE,
                    CADET_ID,
                    int(cadet_id),
                    EVENT_ID,
                    int(event_id),
                    REGISTRATION_ROW_NAME,
                    str(column_name),
                )
            )
            value_as_str = str(new_value_for_column)

            insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                REGISTRATION_ROW_FOR_CADETS_TABLE,
                CADET_ID,
                EVENT_ID,
                REGISTRATION_ROW_NAME,
                REGISTRATION_ROW_VALUE,
            )

            self.cursor.execute(
                insertion,
                (int(cadet_id), int(event_id), str(column_name), str(value_as_str)),
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to cadets at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def delete_cadet_from_event_and_return_messages(self, event_id: str, cadet_id: str):
        if not self.is_cadet_at_event(event_id=event_id, cadet_id=cadet_id):
            return []

        self.delete_cadet_from_event(event_id=event_id, cadet_id=cadet_id)

        return [
            "Removed cadet at event data, for cadet %s from event %s"
            % (cadet_id, event_id)
        ]

    def is_cadet_at_event(self, event_id: str, cadet_id: str):
        if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT *  FROM %s WHERE %s=%d AND %s=%d """
                % (
                    CADETS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at events" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def delete_cadet_from_event(self, event_id: str, cadet_id: str):
        try:
            if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
                self.create_table()

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d"
                % (
                    CADETS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to groups at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def add_new_cadet_to_event(
        self,
        event_id: str,
        cadet_at_event: CadetWithIdAtEvent,
    ):
        if self.is_cadet_at_event(event_id=event_id, cadet_id=cadet_at_event.cadet_id):
            raise Exception(
                "Can't add cadet with id %s to event with id %s as already at event"
                % (event_id, cadet_at_event)
            )

        try:
            if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
                self.create_table()

            self.write_cadet_at_event_without_commit(
                event_id=event_id, cadet_at_event=cadet_at_event
            )
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to groups at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def get_list_of_active_cadets_at_event(self, event_id: str) -> ListOfCadets:
        list_of_cadets = self.list_of_cadets
        list_of_cadet_ids = self.get_list_of_active_cadet_ids_at_event(event_id)

        return ListOfCadets(
            [list_of_cadets.cadet_with_id(id) for id in list_of_cadet_ids]
        )

    def get_list_of_active_cadet_ids_at_event(self, event_id: str) -> List[str]:
        if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
            return []

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s  FROM %s WHERE %s=%d AND %s IN %s"""
                % (
                    CADET_ID,
                    CADETS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_REGISTRATION_STATUS,
                    ACTIVE_STATUS_NAMES_AS_STR,
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at events" % str(e1))
        finally:
            self.close()

        return [str(ans[0]) for ans in raw_list]

    def read_dict_of_cadets_with_registration_data_at_event(
        self, event_id: str
    ) -> DictOfCadetsWithRegistrationData:
        list_of_cadets_with_id_at_event = self.read(event_id)

        new_dict = {}
        for cadet_with_id_at_event in list_of_cadets_with_id_at_event:
            cadet = self.list_of_cadets.cadet_with_id(cadet_with_id_at_event.cadet_id)
            registration_data = CadetRegistrationData(
                availability=cadet_with_id_at_event.availability,
                status=cadet_with_id_at_event.status,
                data_in_row=cadet_with_id_at_event.data_in_row,
                notes=cadet_with_id_at_event.notes,
                health=cadet_with_id_at_event.health,
            )
            new_dict[cadet] = registration_data

        return DictOfCadetsWithRegistrationData(new_dict)

    @property
    def list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = self.object_store.get(
            self.object_store.data_api.data_list_of_cadets.read
        )

        return list_of_cadets

    def read(self, event_id: str) -> ListOfCadetsWithIDAtEvent:
        if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s, %s, %s FROM %s WHERE %s=%d """
                % (
                    CADET_ID,
                    CADET_AVAILABLITY,
                    CADET_REGISTRATION_STATUS,
                    CADET_REGISTRATION_NOTES,
                    CADET_HEALTH,
                    CADETS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at events" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return ListOfCadetsWithIDAtEvent.create_empty()

        list_of_cadet_ids_at_event = []
        for raw_data in raw_list:
            cadet_id = str(raw_data[0])
            availability = DaySelector.from_str(raw_data[1])
            status = RegistrationStatus(raw_data[2])
            notes = str(raw_data[3])
            health = str(raw_data[4])

            row_of_registration_data = self._read_registration_data(
                event_id=event_id, cadet_id=cadet_id
            )

            cadet_at_event = CadetWithIdAtEvent(
                cadet_id=cadet_id,
                availability=availability,
                status=status,
                notes=notes,
                health=health,
                data_in_row=row_of_registration_data,
            )

            list_of_cadet_ids_at_event.append(cadet_at_event)

        return ListOfCadetsWithIDAtEvent(list_of_cadet_ids_at_event)

    def write(self, list_of_cadets_at_event: ListOfCadetsWithIDAtEvent, event_id: str):
        try:
            if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d "
                % (CADETS_AT_EVENT_TABLE, EVENT_ID, int(event_id))
            )

            for cadet_at_event in list_of_cadets_at_event:
                self.write_cadet_at_event_without_commit(
                    event_id=event_id, cadet_at_event=cadet_at_event
                )
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to groups at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def write_cadet_at_event_without_commit(
        self, event_id: str, cadet_at_event: CadetWithIdAtEvent
    ):
        cadet_id = str(cadet_at_event.cadet_id)
        availability = cadet_at_event.availability.as_str()
        status = cadet_at_event.status.name
        data_in_row = cadet_at_event.data_in_row
        notes = str(cadet_at_event.notes)
        health = str(cadet_at_event.health)

        insertion = (
            "INSERT INTO %s (%s, %s, %s, %s, %s, %s) VALUES (?, ?,?,?, ?, ?)"
            % (
                CADETS_AT_EVENT_TABLE,
                EVENT_ID,
                CADET_ID,
                CADET_AVAILABLITY,
                CADET_REGISTRATION_STATUS,
                CADET_REGISTRATION_NOTES,
                CADET_HEALTH,
            )
        )
        self.cursor.execute(
            insertion,
            (int(event_id), int(cadet_id), availability, status, notes, health),
        )

        self._write_row_of_registration_data_for_cadet_at_event_without_commit(
            cadet_id=cadet_id, event_id=event_id, row_in_registration_data=data_in_row
        )

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s INTEGER,
                %s STR,
                %s STR,
                %s STR,
                %s STR

            );
        """ % (
            CADETS_AT_EVENT_TABLE,
            EVENT_ID,
            CADET_ID,
            CADET_AVAILABLITY,
            CADET_REGISTRATION_STATUS,
            CADET_REGISTRATION_NOTES,
            CADET_HEALTH,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (
            INDEX_CADETS_AT_EVENT_TABLE,
            CADETS_AT_EVENT_TABLE,
            EVENT_ID,
            CADET_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating cadet registration row table" % str(e1)
            )
        finally:
            self.close()

    def _read_registration_data(
        self, event_id: str, cadet_id: str
    ) -> RowInRegistrationData:
        try:
            if self.table_does_not_exist(REGISTRATION_ROW_FOR_CADETS_TABLE):
                self._create_registration_row_data_table()

            cursor = self.cursor
            cursor.execute(
                "SELECT %s, %s FROM %s WHERE %s=%d AND %s=%d "
                % (
                    REGISTRATION_ROW_NAME,
                    REGISTRATION_ROW_VALUE,
                    REGISTRATION_ROW_FOR_CADETS_TABLE,
                    CADET_ID,
                    int(cadet_id),
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading registration data" % str(e1))

        ## DO NOT CLOSE AS CALLED AS PART OF ABOVE

        dict_of_str = dict([(str(item[0]), str(item[1])) for item in raw_list])

        return RowInRegistrationData.from_dict_of_str(dict_of_str)

    def _write_row_of_registration_data_for_cadet_at_event_without_commit(
        self,
        event_id: str,
        cadet_id: str,
        row_in_registration_data: RowInRegistrationData,
    ):
        try:
            if self.table_does_not_exist(REGISTRATION_ROW_FOR_CADETS_TABLE):
                self._create_registration_row_data_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d "
                % (
                    REGISTRATION_ROW_FOR_CADETS_TABLE,
                    CADET_ID,
                    int(cadet_id),
                    EVENT_ID,
                    int(event_id),
                )
            )
            as_str_dict = row_in_registration_data.as_str_dict()

            for key, value in as_str_dict.items():
                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    REGISTRATION_ROW_FOR_CADETS_TABLE,
                    CADET_ID,
                    EVENT_ID,
                    REGISTRATION_ROW_NAME,
                    REGISTRATION_ROW_VALUE,
                )

                self.cursor.execute(
                    insertion, (int(cadet_id), int(event_id), str(key), str(value))
                )

        except Exception as e1:
            raise Exception("Error %s when writing registration rows for " % str(e1))

        ### DO NOT COMMIT OR CLOSE

    def _create_registration_row_data_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s INTEGER,
                %s STR,
                %s STR
            );
        """ % (
            REGISTRATION_ROW_FOR_CADETS_TABLE,
            EVENT_ID,
            CADET_ID,
            REGISTRATION_ROW_NAME,
            REGISTRATION_ROW_VALUE,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (
            INDEX_REGISTRATION_ROW_FOR_CADETS_TABLE,
            REGISTRATION_ROW_FOR_CADETS_TABLE,
            EVENT_ID,
            CADET_ID,
            REGISTRATION_ROW_NAME,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
        except Exception as e1:
            raise Exception(
                "Error %s when creating cadet registration row table" % str(e1)
            )

        ## DO NOT CLOSE OR COMMIT
