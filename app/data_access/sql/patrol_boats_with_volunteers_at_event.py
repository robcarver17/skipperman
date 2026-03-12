from typing import List

from app.data_access.sql.shared_column_names import *
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    DictOfVolunteersAtEventWithPatrolBoatsByDay,
    PatrolBoatByDayDict,
)
from app.objects.day_selectors import Day
from app.objects.patrol_boats import ListOfPatrolBoats
from app.objects.patrol_boats_with_volunteers_with_id import (
    ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
    VolunteerWithIdAtEventWithPatrolBoatId,
    OLD_EMPTY_VOLUNTEER_ID,
    EMPTY_VOLUNTEER_ID,
)
from app.objects.utilities.exceptions import missing_data, MultipleMatches
from app.objects.volunteers import ListOfVolunteers

PATROL_BOATS_AND_VOLUNTEERS_TABLE = "patrol_boats_and_volunteers_table"
INDEX_PATROL_BOATS_AND_VOLUNTEERS_TABLE = "index_patrol_boats_and_volunteers_table"


class SqlDataListOfVolunteersAtEventWithPatrolBoats(GenericSqlData):
    def get_sorted_list_of_patrol_boats_at_event(
            self,
            event_id: str
    ) -> ListOfPatrolBoats:
        boat_ids = self.boat_ids_at_event_including_unallocated(event_id)
        list_of_all_boats = self.list_of_patrol_boats

        return list_of_all_boats.subset_from_list_of_ids_retaining_order(boat_ids)

    def delete_volunteer_from_patrol_boat_on_day_at_event(
        self, event_id: str, volunteer_id: str, day: Day
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d AND %s='%s' "
                % (
                    PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                    EVENT_ID,
                    int(event_id),
                    VOLUNTEER_ID,
                    int(volunteer_id),
                    DAY,
                    day.name,
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def remove_patrol_boat_and_all_associated_volunteers_from_event(
        self, event_id: str, patrol_boat_id: str
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d  "
                % (
                    PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                    EVENT_ID,
                    int(event_id),
                    PATROL_BOAT_ID,
                    int(patrol_boat_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def add_unallocated_boat(
        self, event_id: str, list_of_days: List[Day], patrol_boat_id: str
    ):
        try:
            for day in list_of_days:
                self.add_new_boat_day_volunteer_allocation(
                    event_id=event_id,
                    day=day,
                    patrol_boat_id=patrol_boat_id,
                    volunteer_id=EMPTY_VOLUNTEER_ID,
                )
        except:
            raise "Can't add boat as already exists"

    def add_new_boat_day_volunteer_allocation(
        self,
        event_id: str,
        patrol_boat_id: str,
        day: Day,
        volunteer_id: str,
    ):
        existing_boat_id = self.existing_boat_id_for_volunteer_on_day(
            event_id=event_id, day=day, volunteer_id=volunteer_id, default=missing_data
        )
        if existing_boat_id is missing_data:
            self._add_boat_id_for_volunteer_on_day_without_checks(
                event_id=event_id,
                day=day,
                patrol_boat_id=patrol_boat_id,
                volunteer_id=volunteer_id,
            )
        else:
            if existing_boat_id == patrol_boat_id:
                return
            raise Exception("volunteer already on boat that day")

    def is_boat_allocated_to_an_id_for_volunteer_on_day(
        self,
        event_id: str,
        day: Day,
        volunteer_id: str,
    ):
        existing = self.existing_boat_id_for_volunteer_on_day(
            event_id=event_id, day=day, volunteer_id=volunteer_id, default=missing_data
        )
        if existing is missing_data:
            return False
        else:
            return True

    def existing_boat_id_for_volunteer_on_day(
        self, event_id: str, day: Day, volunteer_id: str, default=missing_data
    ) -> str:
        if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
            return default

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s  FROM %s WHERE %s=%d AND %s=%d AND %s='%s' """
                % (
                    PATROL_BOAT_ID,
                    PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                    EVENT_ID,
                    int(event_id),
                    VOLUNTEER_ID,
                    int(volunteer_id),
                    DAY,
                    day.name,
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading patrol boats and volunteers at event" % str(e1)
            )
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list) > 1:
            raise MultipleMatches
        else:
            return str(raw_list[0][0])

    def _add_boat_id_for_volunteer_on_day_without_checks(
        self, event_id: str, day: Day, volunteer_id: str, patrol_boat_id: str
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
                self.create_table()

                volunteer_and_boat = VolunteerWithIdAtEventWithPatrolBoatId(
                    volunteer_id=volunteer_id, patrol_boat_id=patrol_boat_id, day=day
                )
                self._add_volunteer_with_boat_without_commit_or_checks(
                    event_id=event_id, volunteer_and_boat=volunteer_and_boat
                )
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def delete_boat_id_for_volunteer_on_day(
        self,
        event_id: str,
        day: Day,
        volunteer_id: str,
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
                self.create_table()

                self.cursor.execute(
                    "DELETE FROM %s WHERE %s=%d AND %s=%d AND %s='%s' "
                    % (
                        PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                        EVENT_ID,
                        int(event_id),
                        VOLUNTEER_ID,
                        int(volunteer_id),
                        DAY,
                        day.name,
                    )
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def is_boat_empty_on_day(
        self, event_id: str, day: Day, patrol_boat_id: str
    ) -> bool:
        if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
            return True

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT *  FROM %s WHERE %s=%d AND %s=%s AND %s=%d AND %s<>%d """
                % (
                    PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                    EVENT_ID,
                    int(event_id),
                    DAY,
                    day,
                    PATROL_BOAT_ID,
                    int(patrol_boat_id),
                    VOLUNTEER_ID,
                    int(EMPTY_VOLUNTEER_ID),
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading patrol boats and volunteers at event" % str(e1)
            )
        finally:
            self.close()

        any_volunteers_on_day = len(raw_list) > 0

        return not any_volunteers_on_day

    def get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        self, event_id: str
    ) -> DictOfVolunteersAtEventWithPatrolBoatsByDay:
        raw_list = self.read(event_id)
        new_dict = {}
        for raw_item in raw_list:
            if raw_item.volunteer_id == EMPTY_VOLUNTEER_ID:
                continue
            volunteer = self.list_of_volunteers.volunteer_with_id(raw_item.volunteer_id)
            dict_this_volunteer = new_dict.get(volunteer, PatrolBoatByDayDict())
            dict_this_volunteer[raw_item.day] = self.list_of_patrol_boats.boat_given_id(
                raw_item.patrol_boat_id
            )
            new_dict[volunteer] = dict_this_volunteer

        return DictOfVolunteersAtEventWithPatrolBoatsByDay(new_dict)

    @property
    def list_of_volunteers(self) -> ListOfVolunteers:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers.read
        )

    @property
    def list_of_patrol_boats(self) -> ListOfPatrolBoats:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_patrol_boats.read
        )

    def boat_ids_at_event_including_unallocated(self, event_id: str) -> List[str]:
        if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
            return ListOfVolunteersWithIdAtEventWithPatrolBoatsId.create_empty()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT DISTINCT %s FROM %s WHERE %s=%d """
                % (
                    PATROL_BOAT_ID,
                    PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading patrol boats and volunteers at event" % str(e1)
            )
        finally:
            self.close()

        return [raw_item[0] for raw_item in raw_list]

    def read(self, event_id: str) -> ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
            return ListOfVolunteersWithIdAtEventWithPatrolBoatsId.create_empty()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s  FROM %s WHERE %s=%d """
                % (
                    VOLUNTEER_ID,
                    PATROL_BOAT_ID,
                    DAY,
                    PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading patrol boats and volunteers at event" % str(e1)
            )
        finally:
            self.close()

        new_list = [
            VolunteerWithIdAtEventWithPatrolBoatId(
                volunteer_id=str(raw_item[0]),
                patrol_boat_id=str(raw_item[1]),
                day=Day[raw_item[2]],
            )
            for raw_item in raw_list
        ]

        return ListOfVolunteersWithIdAtEventWithPatrolBoatsId(new_list)

    def write(
        self,
        people_and_boats: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
                self.create_table()

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (PATROL_BOATS_AND_VOLUNTEERS_TABLE, EVENT_ID, int(event_id))
            )

            for volunteer_and_boat in people_and_boats:
                self._add_volunteer_with_boat_without_commit_or_checks(
                    event_id=event_id, volunteer_and_boat=volunteer_and_boat
                )
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def _add_volunteer_with_boat_without_commit_or_checks(
        self, event_id: str, volunteer_and_boat: VolunteerWithIdAtEventWithPatrolBoatId
    ):
        volunteer_id = volunteer_and_boat.volunteer_id

        ## FIXME TEMP CODE
        if volunteer_id == OLD_EMPTY_VOLUNTEER_ID:
            volunteer_id = int(EMPTY_VOLUNTEER_ID)
        else:
            volunteer_id = int(volunteer_id)

        day = volunteer_and_boat.day.name
        patrol_boat_id = int(volunteer_and_boat.patrol_boat_id)

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
            PATROL_BOATS_AND_VOLUNTEERS_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            PATROL_BOAT_ID,
            DAY,
        )

        self.cursor.execute(
            insertion, (int(event_id), volunteer_id, patrol_boat_id, day)
        )

    def create_table(self):
        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER, 
                    %s INTEGER,
                    %s INTEGER,
                    %s STR
                );
            """ % (
            PATROL_BOATS_AND_VOLUNTEERS_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            PATROL_BOAT_ID,
            DAY,
        )

        ## FIXME NO INDEX REMOVE ONCE ISSUE RESOLVED

        try:
            self.cursor.execute(table_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating patrol boats at event table" % str(e1)
            )
        finally:
            self.close()
