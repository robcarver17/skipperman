from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import (
    VOLUNTEER_ID,
    DAY,
    DINGHY_ID,
    EVENT_ID,
)
from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
    DictOfDaysAndClubDinghiesAtEventForPerson,
)
from app.objects.day_selectors import Day
from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import (
    VolunteerAtEventWithClubDinghyWithId,
    ListOfVolunteerAtEventWithIdAndClubDinghies,
)

VOLUNTEERS_AND_CLUB_DINGHIES_TABLE = "volunteers_and_club_dinghies_table"
INDEX_NAME_VOLUNTEERS_AND_CLUB_DINGHIES_TABLE = (
    "volunteers_and_club_dinghies_table_index"
)


class SqlDataListOfVolunteersAtEventWithClubDinghies(GenericSqlData):
    def remove_club_dinghy_from_volunteer_on_day(
        self, event_id: str, day: Day, volunteer_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d AND %s='%s' "
                % (
                    VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
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
                "Error %s when writing club dinghies and volunteers at event" % str(e1)
            )
        finally:
            self.close()

    def allocate_club_dinghy_to_volunteer_on_day(
        self,
        event_id: str,
        day: Day,
        volunteer_id: str,
        club_dinghy_id: str,
        allow_overwrite: bool = False,
    ):
        if self.is_volunteer_already_allocated_on_day(
            event_id=event_id, day=day, volunteer_id=volunteer_id
        ):
            if allow_overwrite:
                self._update_club_dinghy_for_volunteer_on_day_no_checks(
                    event_id=event_id,
                    day=day,
                    volunteer_id=volunteer_id,
                    club_dinghy_id=club_dinghy_id,
                )
            else:
                raise Exception(
                    "Can't allocate club dinghy for that day as already allocated and overwrite not permitted"
                )
        else:
            self._allocate_club_dinghy_to_volunteer_on_day_no_checks(
                event_id=event_id,
                day=day,
                volunteer_id=volunteer_id,
                club_dinghy_id=club_dinghy_id,
            )

    def is_volunteer_already_allocated_on_day(
        self,
        event_id: str,
        day: Day,
        volunteer_id: str,
    ):
        if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d AND %s=%d AND %s='%s' """
                % (
                    VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                    VOLUNTEER_ID,
                    int(volunteer_id),
                    EVENT_ID,
                    int(event_id),
                    DAY,
                    day.name,
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading volunteers and dinghies at event" % str(e1)
            )
        finally:
            self.close()

        return len(raw_list) > 0

    def _allocate_club_dinghy_to_volunteer_on_day_no_checks(
        self, event_id: str, day: Day, volunteer_id: str, club_dinghy_id: str
    ):
        volunteer_and_boat = VolunteerAtEventWithClubDinghyWithId(
            volunteer_id=volunteer_id, club_dinghy_id=club_dinghy_id, day=day
        )
        try:
            if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
                self.create_table()

            self._add_row_no_checks_or_commits(
                event_id=event_id, volunteer_and_boat=volunteer_and_boat
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing club dinghies and volunteers at event" % str(e1)
            )
        finally:
            self.close()

    def _update_club_dinghy_for_volunteer_on_day_no_checks(
        self, event_id: str, day: Day, volunteer_id: str, club_dinghy_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
                raise Exception("Can't update as existing record not present")

            self.cursor.execute(
                "UPDATE %s SET %s=%d WHERE %s=%d AND %s=%d AND %s='%s' "
                % (
                    VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                    DINGHY_ID,
                    int(club_dinghy_id),
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
                "Error %s when writing club dinghies and volunteers at event" % str(e1)
            )
        finally:
            self.close()

    def read_dict_of_volunteers_and_club_dinghies_at_event(
        self, event_id: str
    ) -> DictOfPeopleAndClubDinghiesAtEvent:
        list_of_volunteers_at_event_with_dinghies = self.read(event_id)
        new_dict = {}
        for volunteer_with_id_and_dinghy in list_of_volunteers_at_event_with_dinghies:
            volunteer = self.list_of_volunteers.volunteer_with_id(
                volunteer_with_id_and_dinghy.volunteer_id
            )
            day = volunteer_with_id_and_dinghy.day
            dinghy = self.list_of_club_dinghies.club_dinghy_with_id(
                volunteer_with_id_and_dinghy.club_dinghy_id
            )
            existing_dict_of_days = new_dict.get(
                volunteer, DictOfDaysAndClubDinghiesAtEventForPerson()
            )
            existing_dict_of_days[day] = dinghy
            new_dict[volunteer] = existing_dict_of_days

        return DictOfPeopleAndClubDinghiesAtEvent(new_dict)

    @property
    def list_of_volunteers(self):
        list_of_volunteers = self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers.read
        )

        return list_of_volunteers

    @property
    def list_of_club_dinghies(self):
        list_of_club_dinghies = self.object_store.get(
            self.object_store.data_api.data_List_of_club_dinghies.read
        )

        return list_of_club_dinghies

    def read(self, event_id: str) -> ListOfVolunteerAtEventWithIdAndClubDinghies:
        if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s  FROM %s WHERE %s=%d """
                % (
                    VOLUNTEER_ID,
                    DAY,
                    DINGHY_ID,
                    VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading volunteers and dinghies at event" % str(e1)
            )
        finally:
            self.close()

        new_list = []
        for raw_volunteer_with_id_at_event in raw_list:
            volunteer_with_id_at_event = VolunteerAtEventWithClubDinghyWithId(
                volunteer_id=str(
                    raw_volunteer_with_id_at_event[0],
                ),
                day=Day[raw_volunteer_with_id_at_event[1]],
                club_dinghy_id=str(raw_volunteer_with_id_at_event[2]),
            )
            new_list.append(volunteer_with_id_at_event)

        return ListOfVolunteerAtEventWithIdAndClubDinghies(new_list)  ## ignore warning

    def write(
        self,
        people_and_boats: ListOfVolunteerAtEventWithIdAndClubDinghies,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d "
                % (VOLUNTEERS_AND_CLUB_DINGHIES_TABLE, EVENT_ID, int(event_id))
            )

            for volunteer_and_boat in people_and_boats:
                self._add_row_no_checks_or_commits(
                    event_id=event_id, volunteer_and_boat=volunteer_and_boat
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing club dinghies and volunteers at event" % str(e1)
            )
        finally:
            self.close()

    def _add_row_no_checks_or_commits(
        self, event_id: str, volunteer_and_boat: VolunteerAtEventWithClubDinghyWithId
    ):
        volunteer_id = volunteer_and_boat.volunteer_id
        day = volunteer_and_boat.day.name
        club_dinghy_id = volunteer_and_boat.club_dinghy_id

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
            VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            DAY,
            DINGHY_ID,
        )

        self.cursor.execute(
            insertion, (int(event_id), int(volunteer_id), day, int(club_dinghy_id))
        )

    def create_table(self):
        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s INTEGER,
                %s STR,
                %s INTEGER
            );
        """ % (
            VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            DAY,
            DINGHY_ID,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (
            INDEX_NAME_VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
            VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            DAY,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating club dinghies and volunteers table" % str(e1)
            )
        finally:
            self.close()
