
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import CADET_ID, DICT_OF_EVENT_IDS_AND_GROUP_NAMES
from app.objects.cadets import ListOfCadets
from app.objects.composed.dict_of_previous_cadet_groups import \
    DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds
from app.objects.events import ListOfEvents
from app.objects.previous_cadet_groups import ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds, GroupNamesForEventsAndCadetPersistentVersionWithIds
from app.objects.utilities.transform_data import dict_as_str, dict_from_str

PERSISTENT_CADETS_WITH_GROUP_ID_TABLE = "list_of_group_names_for_events_and_cadet_persistent_versions"
INDEX_NAME_PERSISTENT_CADETS_WITH_GROUP_ID_TABLE = "cadet_id_in_persistent_table_index"


class SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion(GenericSqlData):
    def get_dict_of_group_names_for_events_and_cadets_persistent_version(
            self) -> DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds:

        raw_data_as_list = self.read()
        new_dict ={}
        for raw_item in raw_data_as_list:
            cadet_id = raw_item.cadet_id
            dict_of_event_ids_and_group_names = raw_item.dict_of_event_ids_and_group_names

            cadet = self.list_of_cadets.cadet_with_id(cadet_id)
            dict_this_cadet = dict([
                (self.list_of_events.event_with_id(event_id),
                 group_name)
                for event_id, group_name in dict_of_event_ids_and_group_names.items()
            ])
            new_dict[cadet] = dict_this_cadet

        return DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds(new_dict)

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_cadets.read
        )

    @property
    def list_of_events(self) -> ListOfEvents:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_events.read
        )


    def delete_persistent_version_of_previous_groups_for_cadet(self, cadet_id: str):
        try:
            if self.table_does_not_exist(PERSISTENT_CADETS_WITH_GROUP_ID_TABLE):
                return

            self.cursor.execute("DELETE FROM %s WHERE %s=%d " % (
                PERSISTENT_CADETS_WITH_GROUP_ID_TABLE,
            CADET_ID,
            int(cadet_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to persistent groups at event table" % str(e1))
        finally:
            self.close()

    def update_dict_of_group_names_for_events_and_cadets_persistent_version(self,
                                                                            dict_of_group_names_for_events_and_cadets: DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds):

        as_list_with_ids = dict_of_group_names_for_events_and_cadets.as_list_with_ids()
        self.write(as_list_with_ids)

    def read(self) ->  ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds:
        if self.table_does_not_exist(PERSISTENT_CADETS_WITH_GROUP_ID_TABLE):
            return ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds.create_empty()

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
                self._insert_row_without_checks_or_commits(cadet_id_with_group_names_dict)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to persistent groups at event table" % str(e1))
        finally:
            self.close()

    def _insert_row_without_checks_or_commits(self, cadet_id_with_group_names_dict: GroupNamesForEventsAndCadetPersistentVersionWithIds):
        cadet_id = int(cadet_id_with_group_names_dict.cadet_id)
        group_names_dict = dict_as_str(cadet_id_with_group_names_dict.dict_of_event_ids_and_group_names)

        insertion = "INSERT INTO %s (%s, %s) VALUES (?, ?)" % (
            PERSISTENT_CADETS_WITH_GROUP_ID_TABLE,
            CADET_ID, DICT_OF_EVENT_IDS_AND_GROUP_NAMES)
        self.cursor.execute(insertion,
                            (cadet_id, group_names_dict))

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
