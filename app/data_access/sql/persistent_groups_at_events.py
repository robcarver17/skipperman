import pandas as pd

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import CADET_ID, DICT_OF_EVENT_IDS_AND_GROUP_NAMES
from app.objects.previous_cadet_groups import ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds, GroupNamesForEventsAndCadetPersistentVersionWithIds
from app.objects.utilities.transform_data import dict_as_str, dict_from_str

PERSISTENT_CADETS_WITH_GROUP_ID_TABLE = "list_of_group_names_for_events_and_cadet_persistent_versions"
INDEX_NAME_PERSISTENT_CADETS_WITH_GROUP_ID_TABLE = "cadet_id_in_persistent_table_index"


class SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion(GenericSqlData):
    def read(self) ->  ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds:
        if self.table_does_not_exist(PERSISTENT_CADETS_WITH_GROUP_ID_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s''' % (
                CADET_ID, DICT_OF_EVENT_IDS_AND_GROUP_NAMES, PERSISTENT_CADETS_WITH_GROUP_ID_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading persistent groups at events" % str(e1))
        finally:
            self.close()

        new_list = [
            GroupNamesForEventsAndCadetPersistentVersionWithIds(
                cadet_id=str(raw_groups[0]),
                dict_of_event_ids_and_group_names = dict_from_str(raw_groups[1])
            )
            for raw_groups in raw_list
        ]

        return ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds(new_list)


    def write(self, list_of_cadet_ids_with_group_names:  ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds):
        try:
            if self.table_does_not_exist(PERSISTENT_CADETS_WITH_GROUP_ID_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % PERSISTENT_CADETS_WITH_GROUP_ID_TABLE)

            for cadet_id_with_group_names_dict in list_of_cadet_ids_with_group_names:
                cadet_id = int(cadet_id_with_group_names_dict.cadet_id)
                group_names_dict =  dict_as_str(cadet_id_with_group_names_dict.dict_of_event_ids_and_group_names)

                insertion = "INSERT INTO %s (%s, %s) VALUES (?, ?)" % (
                    PERSISTENT_CADETS_WITH_GROUP_ID_TABLE,
                    CADET_ID, DICT_OF_EVENT_IDS_AND_GROUP_NAMES)
                self.cursor.execute(insertion,
                                    (cadet_id, group_names_dict))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to persistent groups at event table" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s STR
            );
        """ % (PERSISTENT_CADETS_WITH_GROUP_ID_TABLE, CADET_ID, DICT_OF_EVENT_IDS_AND_GROUP_NAMES)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_NAME_PERSISTENT_CADETS_WITH_GROUP_ID_TABLE,
                                                                              PERSISTENT_CADETS_WITH_GROUP_ID_TABLE,
                                                                              CADET_ID)
        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating table" % str(e1))
