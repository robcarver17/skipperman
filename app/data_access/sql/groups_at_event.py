from typing import Dict


from app.data_access.sql.generic_sql_data import GenericSqlData, int2date
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.events import EVENTS_TABLE
from app.data_access.sql.groups import GROUPS_TABLE
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups, CadetIdWithGroup
from app.objects.composed.cadets_at_event_with_groups import  DaysAndGroupNames
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.exceptions import missing_data

CADETS_WITH_GROUP_ID_TABLE = "list_of_cadet_ids_with_groups"
INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE = "event_cadet_day"


class SqlDataListOfCadetsWithGroups(GenericSqlData):
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
            (event, days_and_groups.most_common())
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
