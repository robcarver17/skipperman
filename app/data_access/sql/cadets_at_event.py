from typing import List

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.cadet_with_id_at_event import ListOfCadetsWithIDAtEvent, CadetWithIdAtEvent
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import RegistrationStatus, ACTIVE_STATUS_NAMES

CADETS_AT_EVENT_TABLE = "cadets_at_event"
INDEX_CADETS_AT_EVENT_TABLE = "index_cadets_at_event"
REGISTRATION_ROW_FOR_CADETS_TABLE = "registration_row_data_for_cadets_at_event"
INDEX_REGISTRATION_ROW_FOR_CADETS_TABLE = "index_registration_row_data_for_cadets_at_event"

ACTIVE_STATUS_NAMES_AS_STR="('%s')" % ("','".join(ACTIVE_STATUS_NAMES))

class SqlDataListOfCadetsAtEvent(GenericSqlData):
    def get_list_of_active_cadet_ids_at_event(self, event: Event) -> List[str]:
        if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
            return []

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s  FROM %s WHERE %s=%d AND %s IN %s''' % (
                CADET_ID,
                CADETS_AT_EVENT_TABLE,
                EVENT_ID, int(event.id),
                CADET_MEMBERSHIP_STATUS, ACTIVE_STATUS_NAMES_AS_STR
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at events" % str(e1))
        finally:
            self.close()

        return [str(ans[0]) for ans in raw_list]

    def read(self, event_id: str) -> ListOfCadetsWithIDAtEvent:
        if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s FROM %s WHERE %s=%d ''' % (
                CADET_ID, CADET_AVAILABLITY, CADET_REGISTRATION_STATUS, CADET_REGISTRATION_NOTES, CADET_HEALTH,
                CADETS_AT_EVENT_TABLE, EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets at events" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return ListOfCadetsWithIDAtEvent.create_empty()

        list_of_cadet_ids_at_event = []
        for raw_data in raw_list:
            cadet_id = str(raw_data[0])
            availability = DaySelector.from_str(raw_data[1])
            status = RegistrationStatus(raw_data[2])
            notes = str(raw_data[3])
            health = str(raw_data[4])

            row_of_registration_data = self._read_registration_data(event_id=event_id, cadet_id=cadet_id)

            cadet_at_event = CadetWithIdAtEvent(
                cadet_id=cadet_id,
                availability=availability,
                status=status,
                notes=notes,
                health=health,
                data_in_row=row_of_registration_data
            )

            list_of_cadet_ids_at_event.append(cadet_at_event)

        return ListOfCadetsWithIDAtEvent(list_of_cadet_ids_at_event)

    def write(self, list_of_cadets_at_event: ListOfCadetsWithIDAtEvent, event_id: str):
        try:
            if self.table_does_not_exist(CADETS_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADETS_AT_EVENT_TABLE, EVENT_ID, event_id))

            for cadet_at_event in list_of_cadets_at_event:
                cadet_id = str(cadet_at_event.cadet_id)
                availability = cadet_at_event.availability.as_str()
                status = cadet_at_event.status.name
                data_in_row = cadet_at_event.data_in_row
                notes = str(cadet_at_event.notes)
                health = str(cadet_at_event.health)

                insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s) VALUES (?, ?,?,?, ?, ?)" % (
                    CADETS_AT_EVENT_TABLE,
                    EVENT_ID, CADET_ID, CADET_AVAILABLITY, CADET_REGISTRATION_STATUS, CADET_REGISTRATION_NOTES, CADET_HEALTH)
                self.cursor.execute(insertion,
                                    (int(event_id), int(cadet_id), availability, status, notes, health))

                self._write_row_of_registration_data_for_cadet_at_event(cadet_id=cadet_id,
                                                                        event_id=event_id,
                                                                        row_in_registration_data=data_in_row)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()


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
        """ % (CADETS_AT_EVENT_TABLE,
               EVENT_ID,
               CADET_ID,
                CADET_AVAILABLITY,
               CADET_REGISTRATION_STATUS,
               CADET_REGISTRATION_NOTES,
               CADET_HEALTH
               )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (INDEX_CADETS_AT_EVENT_TABLE,
                                                                      CADETS_AT_EVENT_TABLE,
                                                                      EVENT_ID,
                                                                      CADET_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating cadet registration row table" % str(e1))
        finally:
            self.close()


    def _read_registration_data(self, event_id: str, cadet_id: str) -> RowInRegistrationData:
        try:
            if self.table_does_not_exist(REGISTRATION_ROW_FOR_CADETS_TABLE):
                self._create_registration_row_data_table()

            cursor = self.cursor
            cursor.execute("SELECT %s, %s FROM %s WHERE %s='%s' AND %s='%s'" % (
                REGISTRATION_ROW_NAME, REGISTRATION_ROW_VALUE,
                REGISTRATION_ROW_FOR_CADETS_TABLE,
                CADET_ID, int(cadet_id),
                EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading registration data" % str(e1))

        ## DO NOT CLOSE AS CALLED AS PART OF ABOVE

        dict_of_str = dict([
            (str(item[0]), str(item[1]))
            for item in raw_list
        ])

        return RowInRegistrationData.from_dict_of_str(dict_of_str)

    def _write_row_of_registration_data_for_cadet_at_event(self, event_id: str, cadet_id: str, row_in_registration_data: RowInRegistrationData):
        try:
            if self.table_does_not_exist(REGISTRATION_ROW_FOR_CADETS_TABLE):
                self._create_registration_row_data_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s' AND %s='%s'" % (REGISTRATION_ROW_FOR_CADETS_TABLE,
                                                                              CADET_ID,
                                                                              int(cadet_id),
                                                                              EVENT_ID,
                                                                              int(event_id)))
            as_str_dict = row_in_registration_data.as_str_dict()

            for key, value in as_str_dict.items():

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    REGISTRATION_ROW_FOR_CADETS_TABLE,
                    CADET_ID, EVENT_ID, REGISTRATION_ROW_NAME, REGISTRATION_ROW_VALUE)

                self.cursor.execute(insertion, (
                    int(cadet_id), int(event_id), str(key), str(value)))


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
        """ % (REGISTRATION_ROW_FOR_CADETS_TABLE,
               EVENT_ID,
               CADET_ID,
               REGISTRATION_ROW_NAME,
               REGISTRATION_ROW_VALUE
               )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_REGISTRATION_ROW_FOR_CADETS_TABLE,
                                                                      REGISTRATION_ROW_FOR_CADETS_TABLE,
                                                                      EVENT_ID,
                                                                      CADET_ID,
                                                                      REGISTRATION_ROW_NAME)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
        except Exception as e1:
            raise Exception("Error %s when creating cadet registration row table" % str(e1))

        ## DO NOT CLOSE OR COMMIT
