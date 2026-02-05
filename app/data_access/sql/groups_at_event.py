from typing import Dict, List

from app.data_access.sql.generic_sql_data import GenericSqlData, int2date, int2bool
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.events import EVENTS_TABLE
from app.data_access.sql.groups import GROUPS_TABLE, SqlDataListOfGroups
from app.data_access.sql.cadets_at_event import SqlDataListOfCadetsAtEvent
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups, CadetIdWithGroup
from app.objects.cadets import ListOfCadets
from app.objects.composed.cadets_at_event_with_groups import DaysAndGroupNames,  \
    DaysAndGroups, DictOfCadetsWithDaysAndGroupsAtEvent
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import ListOfGroups, Group, GroupLocation
from app.objects.utilities.exceptions import missing_data

CADETS_WITH_GROUP_ID_TABLE = "list_of_cadet_ids_with_groups"
INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE = "event_cadet_day"


class SqlDataListOfCadetsWithGroups(GenericSqlData):
    def add_cadet_to_group_on_day(self,
    event_id:str,
    cadet_id:str,
    day:Day,
    group_id:str,

):
        if self.is_cadet_in_group_already_on_day(
            event_id=event_id,
            cadet_id=cadet_id,
            day=day
        ):
            raise Exception("Cadet already in group on day")

        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                self.create_table()

            insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?,?)" % (
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID, CADET_ID, DAY, GROUP_ID)
            self.cursor.execute(insertion,
                                    (int(event_id), int(cadet_id), day.name, int(group_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

    def is_cadet_in_group_already_on_day(self,  event_id:str,
    cadet_id:str,
    day:Day,

):

        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s='%s' AND %s='%s' AND %s='%s' ''' % (

                CADETS_WITH_GROUP_ID_TABLE,
                EVENT_ID, int(event_id),
                CADET_ID, int(cadet_id),
                DAY, day.name
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def get_list_of_cadets_in_group(self, event: Event, group: Group) -> ListOfCadets:
        all_group_allocations_at_event = self.get_group_allocations_for_event_active_cadets_only(
            event=event
        )
        cadets_in_group = all_group_allocations_at_event.cadets_in_group_during_event(group)
        cadets_in_group = cadets_in_group.sort_by_firstname()

        return cadets_in_group

    def get_dict_of_cadets_with_groups_at_event(self, event_id: str) -> DictOfCadetsWithDaysAndGroupsAtEvent:
        raw_list = self.read(event_id)
        new_dict = {}
        for cadet_ids_with_groups in raw_list:
            cadet_id = cadet_ids_with_groups.cadet_id
            day = cadet_ids_with_groups.day
            group_id = cadet_ids_with_groups.group_id
            group = self.list_of_groups.group_with_id(group_id)
            cadet = self.list_of_cadets.cadet_with_id(cadet_id)
            existing_for_cadet = new_dict.get(cadet, DaysAndGroups())
            existing_for_cadet[day] = group
            new_dict[cadet] = existing_for_cadet

        return DictOfCadetsWithDaysAndGroupsAtEvent(new_dict)

    @property
    def list_of_groups(self) -> ListOfGroups:
        list_of_groups = getattr(self, "_list_of_groups", None)
        if list_of_groups is None:
            self._list_of_groups = list_of_groups = SqlDataListOfGroups(self.db_connection).read()

        return list_of_groups

    def get_group_allocations_for_event_active_cadets_only(
    self, event: Event
) -> DictOfCadetsWithDaysAndGroupsAtEvent:
        return DictOfCadetsWithDaysAndGroupsAtEvent(
            [
                (self.list_of_cadets.cadet_with_id(cadet_id),
                 self.days_and_group_at_event_for_cadet(event_id=event.id, cadet_id=cadet_id))
                for cadet_id in self.list_of_active_cadet_ids_at_event(event)
            ]
        )

    def days_and_group_at_event_for_cadet(self, event_id: str, cadet_id: str) -> DaysAndGroups:
        try:
            cursor = self.cursor

            query = ("SELECT %s.%s, %s.%s, %s.%s, %s.%s, %s.%s, %s.%s, %s.%s FROM %s JOIN %s ON %s.%s=%s.%s  WHERE %s.%s=%d AND %s.%s=%d") % (
                GROUPS_TABLE, GROUP_NAME,
                GROUPS_TABLE, LOCATION,
                GROUPS_TABLE, HIDDEN,
                GROUPS_TABLE, PROTECTED,
                GROUPS_TABLE, STREAMER,
                GROUPS_TABLE, GROUP_ID,
                CADETS_WITH_GROUP_ID_TABLE, DAY,

                CADETS_WITH_GROUP_ID_TABLE,

                GROUPS_TABLE,
                CADETS_WITH_GROUP_ID_TABLE, GROUP_ID,
                GROUPS_TABLE, GROUP_ID,

                CADETS_WITH_GROUP_ID_TABLE, EVENT_ID,
                int(event_id),

                CADETS_WITH_GROUP_ID_TABLE, CADET_ID,
                int(cadet_id)

            )

            cursor.execute(query)

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadet groups" % str(e1))
        finally:
            self.close()

        new_dict = dict(
            [
                (Day[str(raw_item[6])],
                 Group(name=str(raw_item[0]),
                       location=GroupLocation[raw_item[1]],
                       hidden=int2bool(raw_item[2]),
                       protected=int2bool(raw_item[3]),
                       streamer=str(raw_item[4]),
                       id=str(raw_item[5]))

                )
                for raw_item in raw_list
            ]
        )

        return DaysAndGroups(new_dict)

    def list_of_active_cadet_ids_at_event(self, event: Event) -> List[str]:
        list_of_active_ids = getattr(self, "_list_of_active_ids_%s" % event.id, None)
        if list_of_active_ids is None:
            list_of_active_ids = SqlDataListOfCadetsAtEvent(db_connection=self.db_connection).get_list_of_active_cadet_ids_at_event(event)
            setattr(self, "_list_of_active_ids_%s" % event.id, list_of_active_ids)

        return list_of_active_ids

    @property
    def list_of_cadets(self):
        list_of_cadets = getattr(self, "_list_of_cadets", None)
        if list_of_cadets is None:
            list_of_cadets = self._list_of_cadets = SqlDataListOfCadets(self.db_connection).read()

        return list_of_cadets

    def get_list_of_all_groups_at_event(
            self, event: Event
    ) -> ListOfGroups:

        try:
            cursor = self.cursor

            query = ("SELECT DISTINCT %s.%s, %s.%s, %s.%s, %s.%s, %s.%s, %s.%s FROM %s JOIN %s ON %s.%s=%s.%s  WHERE %s.%s=%d ") % (
                GROUPS_TABLE, GROUP_NAME,
                GROUPS_TABLE, LOCATION,
                GROUPS_TABLE, HIDDEN,
                GROUPS_TABLE, PROTECTED,
                GROUPS_TABLE, STREAMER,
                GROUPS_TABLE, GROUP_ID,

                CADETS_WITH_GROUP_ID_TABLE,

                GROUPS_TABLE,
                CADETS_WITH_GROUP_ID_TABLE, GROUP_ID,
                GROUPS_TABLE, GROUP_ID,

                CADETS_WITH_GROUP_ID_TABLE, EVENT_ID,
                int(event.id)

            )

            cursor.execute(query)

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets with qualifications" % str(e1))
        finally:
            self.close()

        new_list=[
            Group(name=str(raw_item[0]),
                  location=GroupLocation[raw_item[1]],
                  hidden=int2bool(raw_item[2]),
                  protected=int2bool(raw_item[3]),
                  streamer=str(raw_item[4]),
                  id=str(raw_item[5]))         for raw_item in raw_list]

        return ListOfGroups(new_list)

    def get_dict_of_all_event_allocations_for_single_cadet(
           self,cadet_id:str
    ) -> Dict[Event, str]:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            return dict()

        try:
            cursor = self.cursor

            query = "SELECT %s.%s, %s.%s, %s.%s, %s.%s, %s.%s FROM %s JOIN %s ON %s.%s=%s.%s JOIN %s on %s.%s = %s.%s WHERE %s.%s=%d ORDER BY %s.%s " % (
                CADETS_WITH_GROUP_ID_TABLE, DAY,
                GROUPS_TABLE, GROUP_NAME,
                EVENTS_TABLE, EVENT_NAME,
                EVENTS_TABLE, EVENT_START_DATE,
                EVENTS_TABLE, EVENT_END_DATE,
                CADETS_WITH_GROUP_ID_TABLE,
                GROUPS_TABLE,
                CADETS_WITH_GROUP_ID_TABLE, GROUP_ID,
                GROUPS_TABLE, GROUP_ID,
                EVENTS_TABLE,
                CADETS_WITH_GROUP_ID_TABLE, EVENT_ID,
                EVENTS_TABLE, EVENT_ID,
                CADETS_WITH_GROUP_ID_TABLE, CADET_ID,
                int(cadet_id),
                EVENTS_TABLE, EVENT_START_DATE




            )

            cursor.execute(query)

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets with qualifications" % str(e1))
        finally:
            self.close()

        new_dict = {}
        for raw_item in raw_list:
            day = Day[raw_item[0]]
            group_name = raw_item[1]
            event_name = raw_item[2]
            event_start_date = int2date(raw_item[3])
            event_end_date = int2date(raw_item[4])

            event = Event(event_name=event_name, start_date=event_start_date, end_date=event_end_date)

            current_entry = new_dict.get(event_name, missing_data)
            if current_entry is missing_data:
                current_entry=DaysAndGroupNames()

            current_entry[day] = group_name
            new_dict[event] = current_entry

        most_common = dict([
            (event, days_and_groups.most_common().name)
            for event, days_and_groups in new_dict.items()
        ])

        return most_common


    def read(self, event_id: str) -> ListOfCadetIdsWithGroups:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                CADET_ID, DAY, GROUP_ID,
                CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        new_list = [
            CadetIdWithGroup(
                cadet_id=str(raw_cadet_with_group[0]),
                day=Day[raw_cadet_with_group[1]],
                group_id=str(raw_cadet_with_group[2])
            ) for raw_cadet_with_group in raw_list
        ]

        return ListOfCadetIdsWithGroups(new_list)

    def write(
        self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups, event_id: str
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, int(event_id)))

            for cadet_with_group_ids in list_of_cadets_with_groups:
                cadet_id = cadet_with_group_ids.cadet_id
                group_id =cadet_with_group_ids.group_id
                day_name =cadet_with_group_ids.day.name

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?,?)" % (
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID, CADET_ID, DAY, GROUP_ID)
                self.cursor.execute(insertion,
                                    (int(event_id), int(cadet_id), day_name, int(group_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s INTEGER,
                %s STR,
                %s INTEGER
            );
        """ % (CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, CADET_ID, DAY, GROUP_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE,
                                                                              CADETS_WITH_GROUP_ID_TABLE,
                                                                              EVENT_ID,
                                                                              CADET_ID,
                                                                              DAY)
        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating table" % str(e1))
