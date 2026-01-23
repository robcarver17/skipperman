from copy import copy

from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, int2date
from app.data_access.sql.shared_column_names import *
from app.data_access.configuration.field_list import (
    _ROW_ID,
    _REGISTRATION_STATUS,
REGISTRATION_DATE,
CADET_DATE_OF_BIRTH,
)

from app.objects.registration_data import RegistrationDataForEvent, RowInRegistrationData

MAPPED_REGISTRATION_DATA_TABLE = "mapped_registration_data_table"
INDEX_MAPPED_REGISTRATION_DATA_TABLE = "index_mapped_registration_data_table"


class SqlDataMappedRegistrationData(GenericSqlData):
    def read(self, event_id: str) -> RegistrationDataForEvent:
        try:
            if self.table_does_not_exist(MAPPED_REGISTRATION_DATA_TABLE):
                self.create_table()

            cursor = self.cursor
            cursor.execute("SELECT %s, %s, %s FROM %s WHERE %s='%d'" % (
                ROW_ID,
                REGISTRATION_ROW_NAME, REGISTRATION_ROW_VALUE,
                MAPPED_REGISTRATION_DATA_TABLE,
                EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading registration data" % str(e1))
        finally:
            self.close()

        new_dict_key_is_rowid = {}
        for raw_registration_data in raw_list:
            key = raw_registration_data[1]
            if key==_ROW_ID:
                continue
            row_id = str(raw_registration_data[0])
            dict_this_rowid = new_dict_key_is_rowid.get(row_id, {})

            value = raw_registration_data[2]
            if key in [REGISTRATION_DATE, CADET_DATE_OF_BIRTH]:
                value = int2date(int(value))

            dict_this_rowid[key] = value
            new_dict_key_is_rowid[row_id] = dict_this_rowid

        new_list = []
        for row_id, registration_data_as_dict in new_dict_key_is_rowid.items():
            registration_data_as_dict[_ROW_ID] = row_id
            new_list.append(RowInRegistrationData.from_dict_of_str(registration_data_as_dict))

        return RegistrationDataForEvent(new_list)

    def write(self, mapped_wa_event: RegistrationDataForEvent, event_id: str):
        try:
            if self.table_does_not_exist(MAPPED_REGISTRATION_DATA_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (MAPPED_REGISTRATION_DATA_TABLE,
                                                                              EVENT_ID,
                                                                              int(event_id)))
            for row_in_registration_data in mapped_wa_event:
                # First special field used to index
                row_id = str(row_in_registration_data.row_id)

                # Status - 2nd special field
                registration_status = row_in_registration_data.registration_status
                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    MAPPED_REGISTRATION_DATA_TABLE,
                    ROW_ID, EVENT_ID, REGISTRATION_ROW_NAME, REGISTRATION_ROW_VALUE)
                self.cursor.execute(insertion, (
                    row_id, int(event_id), _REGISTRATION_STATUS, registration_status.name))

                as_str_dict = row_in_registration_data.as_str_dict()

                for key in row_in_registration_data.list_of_keys_excluding_special_keys():
                    value = copy(as_str_dict[key])
                    if key in [REGISTRATION_DATE, CADET_DATE_OF_BIRTH]:
                        value = str(date2int(value))

                    insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                        MAPPED_REGISTRATION_DATA_TABLE,
                        ROW_ID, EVENT_ID, REGISTRATION_ROW_NAME, REGISTRATION_ROW_VALUE)
                    self.cursor.execute(insertion, (
                        str(row_id), int(event_id), key, value))

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when writing registration data at event# %s" % (str(e1), event_id))
        finally:
            self.close()


    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s STR,
                %s STR,
                %s STR
            );
        """ % (MAPPED_REGISTRATION_DATA_TABLE,
               EVENT_ID,
               ROW_ID,
               REGISTRATION_ROW_NAME,
               REGISTRATION_ROW_VALUE
               )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_MAPPED_REGISTRATION_DATA_TABLE,
                                                                      MAPPED_REGISTRATION_DATA_TABLE,
                                                                      EVENT_ID,
                                                                      ROW_ID,
                                                                      REGISTRATION_ROW_NAME)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating cadet registration row table" % str(e1))
        finally:
            self.close()
