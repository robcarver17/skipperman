from typing import Dict, List

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.cadet_with_id_with_group_at_event import (
    ListOfCadetIdsWithGroups,
    CadetIdWithGroup,
)
from app.objects.cadets import ListOfCadets
from app.objects.composed.cadets_at_event_with_groups import (
    DaysAndGroups,
    DictOfCadetsWithDaysAndGroupsAtEvent,
)
from app.objects.day_selectors import Day
from app.objects.events import Event, ListOfEvents
from app.objects.groups import (
    ListOfGroups,
    Group,
    unallocated_group_id,
    unallocated_group,
)
from app.objects.utilities.utils import most_common

CADETS_WITH_GROUP_ID_TABLE = "list_of_cadet_ids_with_groups"
INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE = "event_cadet_day"


class SqlDataListOfCadetsWithGroups(GenericSqlData):
    def delete_cadet_group_on_day(self, event_id: str, cadet_id: str, day: Day):
        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d AND %s='%s'"
                % (
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                    DAY,
                    day.name,
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

    def delete_cadet_from_event_and_return_messages(
        self,
        event_id: str,
        cadet_id: str,
    ) -> List[str]:
        rows = len(
            self.days_and_group_at_event_for_cadet(event_id=event_id, cadet_id=cadet_id)
        )

        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                return ["Cadet not at event %s" % event_id]

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d"
                % (
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

        return [
            "Removed %d days of group attendance at event with ID %s" % (rows, event_id)
        ]

    def update_or_add_cadet_in_group_on_day(
        self,
        event_id: str,
        cadet_id: str,
        day: Day,
        group_id: str,
    ):
        if group_id is unallocated_group_id:
            self.set_cadet_to_unallocated_group_on_day(
                event_id=event_id, cadet_id=cadet_id, day=day
            )

        elif self.is_cadet_in_group_already_on_day(
            event_id=event_id, cadet_id=cadet_id, day=day
        ):
            self._update_existing_cadet_in_group_on_day_without_checks(
                event_id=event_id, cadet_id=cadet_id, day=day, group_id=group_id
            )
        else:
            self.add_cadet_to_group_on_day(
                event_id=event_id, cadet_id=cadet_id, day=day, group_id=group_id
            )

    def set_cadet_to_unallocated_group_on_day(
        self,
        event_id: str,
        cadet_id: str,
        day: Day,
    ):
        if self.is_cadet_in_group_already_on_day(
            event_id=event_id, cadet_id=cadet_id, day=day
        ):
            self.delete_cadet_group_on_day(
                event_id=event_id, cadet_id=cadet_id, day=day
            )
        else:
            ## nothing to do
            pass

    def _update_existing_cadet_in_group_on_day_without_checks(
        self,
        event_id: str,
        cadet_id: str,
        day: Day,
        group_id: str,
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s=%d WHERE %s=%d AND %s='%s' AND %s=%d " % (
                CADETS_WITH_GROUP_ID_TABLE,
                GROUP_ID,
                int(group_id),
                EVENT_ID,
                int(event_id),
                DAY,
                day.name,
                CADET_ID,
                int(cadet_id),
            )
            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

    def add_cadet_to_group_on_day(
        self,
        event_id: str,
        cadet_id: str,
        day: Day,
        group_id: str,
    ):
        if self.is_cadet_in_group_already_on_day(
            event_id=event_id, cadet_id=cadet_id, day=day
        ):
            raise Exception("Cadet already in group on day")

        self._add_cadet_to_group_on_day_without_checks(
            event_id=event_id, cadet_id=cadet_id, day=day, group_id=group_id
        )

    def _add_cadet_to_group_on_day_without_checks(
        self,
        event_id: str,
        cadet_id: str,
        day: Day,
        group_id: str,
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                self.create_table()
            self._add_row_without_commits_or_checks(
                event_id=event_id,
                cadet_with_group_ids=CadetIdWithGroup(
                    cadet_id=cadet_id, day=day, group_id=group_id
                ),
            )
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

    def is_cadet_in_group_already_on_day(
        self,
        event_id: str,
        cadet_id: str,
        day: Day,
    ):
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d AND %s=%d AND %s='%s' """
                % (
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                    DAY,
                    day.name,
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def get_list_of_active_cadets_in_group(
        self, event_id: str, group: Group
    ) -> ListOfCadets:
        all_group_allocations_at_event = (
            self.get_group_allocations_for_event_active_cadets_only(event_id)
        )
        cadets_in_group = all_group_allocations_at_event.cadets_in_group_during_event(
            group
        )
        cadets_in_group = cadets_in_group.sort_by_firstname()

        return cadets_in_group

    def get_dict_of_cadets_with_groups_at_event(
        self, event_id: str
    ) -> DictOfCadetsWithDaysAndGroupsAtEvent:
        list_of_cadet_ids = self.get_list_of_all_cadet_ids_with_groups_at_event(
            event_id
        )
        return DictOfCadetsWithDaysAndGroupsAtEvent(
            [
                (
                    self.list_of_cadets.cadet_with_id(cadet_id),
                    self.days_and_group_at_event_for_cadet(
                        event_id=event_id, cadet_id=cadet_id
                    ),
                )
                for cadet_id in list_of_cadet_ids
            ]
        )

    @property
    def list_of_groups(self):
        list_of_groups = self.object_store.get(
            self.object_store.data_api.data_list_of_groups.read
        )

        return list_of_groups

    def get_group_allocations_for_event_active_cadets_only(
        self, event_id: str
    ) -> DictOfCadetsWithDaysAndGroupsAtEvent:
        return DictOfCadetsWithDaysAndGroupsAtEvent(
            [
                (
                    self.list_of_cadets.cadet_with_id(cadet_id),
                    self.days_and_group_at_event_for_cadet(
                        event_id=event_id, cadet_id=cadet_id
                    ),
                )
                for cadet_id in self.list_of_active_cadet_ids_at_event(event_id)
            ]
        )

    def days_and_group_at_event_for_cadet(
        self, event_id: str, cadet_id: str
    ) -> DaysAndGroups:
        raw_dict = self.get_dict_of_days_and_group_ids_at_event_for_cadet(
            event_id=event_id, cadet_id=cadet_id
        )
        return DaysAndGroups(
            dict(
                [
                    (day, self.list_of_groups.group_with_id(group_id))
                    for day, group_id in raw_dict.items()
                ]
            )
        )

    def get_dict_of_days_and_group_ids_at_event_for_cadet(
        self, cadet_id: str, event_id: str
    ) -> Dict[Day, str]:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return dict()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s FROM %s WHERE %s=%d AND %s=%d """
                % (
                    DAY,
                    GROUP_ID,
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        return dict([(Day[raw_item[0]], str(raw_item[1])) for raw_item in raw_list])

    def list_of_active_cadet_ids_at_event(self, event_id: str) -> List[str]:
        return self.object_store.get(
            self.object_store.data_api.data_cadets_at_event.get_list_of_active_cadets_at_event,
            event_id=event_id,
        )

    @property
    def list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = self.object_store.get(
            self.object_store.data_api.data_list_of_cadets.read
        )

        return list_of_cadets

    @property
    def list_of_events(self) -> ListOfEvents:
        list_of_events = self.object_store.get(
            self.object_store.data_api.data_list_of_events.read
        )

        return list_of_events

    def get_list_of_all_groups_at_event(self, event_id: str) -> ListOfGroups:
        raw_list = self.get_list_of_all_group_ids_at_event(event_id)
        return ListOfGroups(
            [self.list_of_groups.group_with_id(group_id) for group_id in raw_list]
        )

    def get_list_of_all_group_ids_at_event(self, event_id: str) -> List[str]:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return []

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT DISTINCT %s FROM %s WHERE %s=%d  """
                % (
                    GROUP_ID,
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        return [str(item[0]) for item in raw_list]

    def get_list_of_all_cadet_ids_with_groups_at_event(
        self, event_id: str
    ) -> List[str]:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return []

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT DISTINCT %s FROM %s WHERE %s=%d  """
                % (
                    CADET_ID,
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        return [str(item[0]) for item in raw_list]

    def get_dict_of_most_common_group_allocations_for_single_cadet(
        self, cadet_id: str
    ) -> Dict[Event, Group]:
        raw_dict = self.get_dict_of_event_ids_and_most_common_group_ids_for_cadet(
            cadet_id
        )

        return dict(
            [
                (
                    self.list_of_events.event_with_id(event_id),
                    self.list_of_groups.group_with_id(group_id),
                )
                for event_id, group_id in raw_dict.items()
            ]
        )

    def get_dict_of_event_ids_and_most_common_group_ids_for_cadet(
        self, cadet_id: str
    ) -> [str, str]:
        list_of_event_ids = self.get_list_of_event_ids_where_cadet_is_allocated(
            cadet_id
        )

        return dict(
            [
                (
                    event_id,
                    self.get_most_common_group_id_at_event_for_cadet(
                        cadet_id=cadet_id, event_id=event_id
                    ),
                )
                for event_id in list_of_event_ids
            ]
        )

    def get_most_common_group_id_at_event_for_cadet(
        self, cadet_id: str, event_id: str, default=unallocated_group.id
    ) -> str:
        return most_common(
            self.get_list_of_group_ids_at_event_for_cadet(
                cadet_id=cadet_id, event_id=event_id
            ),
            default=default,
        )

    def get_list_of_group_ids_at_event_for_cadet(self, cadet_id: str, event_id: str):
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return []

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT DISTINCT %s FROM %s WHERE %s=%d AND %s=%d """
                % (
                    GROUP_ID,
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                    CADET_ID,
                    int(cadet_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        return [str(item[0]) for item in raw_list]

    def get_list_of_event_ids_where_cadet_is_allocated(self, cadet_id: str):
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return []

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT DISTINCT %s FROM %s WHERE %s=%d  """
                % (EVENT_ID, CADETS_WITH_GROUP_ID_TABLE, CADET_ID, int(cadet_id))
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        return [str(item[0]) for item in raw_list]

    def read(self, event_id: str) -> ListOfCadetIdsWithGroups:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return ListOfCadetIdsWithGroups.create_empty()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s FROM %s WHERE %s=%d """
                % (
                    CADET_ID,
                    DAY,
                    GROUP_ID,
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        new_list = [
            CadetIdWithGroup(
                cadet_id=str(raw_cadet_with_group[0]),
                day=Day[raw_cadet_with_group[1]],
                group_id=str(raw_cadet_with_group[2]),
            )
            for raw_cadet_with_group in raw_list
        ]

        return ListOfCadetIdsWithGroups(new_list)

    def write(
        self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups, event_id: str
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                self.create_table()

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d "
                % (CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, int(event_id))
            )

            for cadet_with_group_ids in list_of_cadets_with_groups:
                self._add_row_without_commits_or_checks(
                    event_id=event_id, cadet_with_group_ids=cadet_with_group_ids
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

    def _add_row_without_commits_or_checks(
        self, event_id: str, cadet_with_group_ids: CadetIdWithGroup
    ):
        cadet_id = cadet_with_group_ids.cadet_id
        group_id = cadet_with_group_ids.group_id
        day_name = cadet_with_group_ids.day.name

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?,?)" % (
            CADETS_WITH_GROUP_ID_TABLE,
            EVENT_ID,
            CADET_ID,
            DAY,
            GROUP_ID,
        )
        self.cursor.execute(
            insertion, (int(event_id), int(cadet_id), day_name, int(group_id))
        )

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s INTEGER,
                %s STR,
                %s INTEGER
            );
        """ % (
            CADETS_WITH_GROUP_ID_TABLE,
            EVENT_ID,
            CADET_ID,
            DAY,
            GROUP_ID,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (
            INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE,
            CADETS_WITH_GROUP_ID_TABLE,
            EVENT_ID,
            CADET_ID,
            DAY,
        )
        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating table" % str(e1))
