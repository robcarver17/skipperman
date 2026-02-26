from typing import Dict

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.composed.volunteers_at_event_with_registration_data import (
    DictOfRegistrationDataForVolunteerAtEvent,
    RegistrationDataForVolunteerAtEvent,
)
from app.objects.day_selectors import DaySelector, Day
from app.objects.utilities.exceptions import missing_data, MultipleMatches
from app.objects.volunteer_at_event_with_id import (
    ListOfVolunteersAtEventWithId,
    VolunteerAtEventWithId,
)
from app.objects.volunteers import ListOfVolunteers, Volunteer

VOLUNTEERS_AT_EVENT_TABLE = "volunteers_at_event"
INDEX_VOLUNTEERS_AT_EVENT_TABLE = "index_volunteers_at_event"


class SqlDataListOfVolunteersAtEvent(GenericSqlData):
    def make_volunteer_available_on_day(
        self, volunteer_id: str, event_id: str, day: Day
    ):
        self._set_availability_on_day_for_volunteer(
            volunteer_id=volunteer_id, event_id=event_id, day=day, available=True
        )

    def make_volunteer_unavailable_on_day(
        self, volunteer_id: str, event_id: str, day: Day
    ):
        self._set_availability_on_day_for_volunteer(
            volunteer_id=volunteer_id, event_id=event_id, day=day, available=False
        )

    def _set_availability_on_day_for_volunteer(
        self, volunteer_id: str, event_id: str, day: Day, available: bool
    ):
        if not self.is_volunteer_already_at_event(
            volunteer_id=volunteer_id, event_id=event_id
        ):
            raise Exception("volunteer not at event")

        current_availability = self.read_for_volunteer(
            event_id=event_id, volunteer_id=volunteer_id
        ).availablity
        if available:
            current_availability.make_available_on_day(day)
        else:
            current_availability.make_unavailable_on_day(day)
        try:
            self.cursor.execute(
                "UPDATE %s SET %s='%s' WHERE %s=%d AND %s=%d "
                % (
                    VOLUNTEERS_AT_EVENT_TABLE,
                    VOLUNTEER_AVAILABLITY,
                    current_availability.as_str(),
                    EVENT_ID,
                    int(event_id),
                    VOLUNTEER_ID,
                    int(volunteer_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def delete_volunteer_at_event(self, volunteer_id: str, event_id: str):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d"
                % (
                    VOLUNTEERS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    VOLUNTEER_ID,
                    int(volunteer_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def add_volunteer_to_event(
        self, event_id: str, volunteer_at_event_with_id: VolunteerAtEventWithId
    ):
        if self.is_volunteer_already_at_event(
            event_id=event_id, volunteer_id=volunteer_at_event_with_id.volunteer_id
        ):
            raise Exception("Can't add as at event already")

        self._add_volunteer_to_event_without_checks(
            event_id=event_id, volunteer_at_event_with_id=volunteer_at_event_with_id
        )

    def _add_volunteer_to_event_without_checks(
        self, event_id: str, volunteer_at_event_with_id: VolunteerAtEventWithId
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                self.create_table()

            self._add_row_without_checks_or_commits(
                event_id=event_id, volunteer_at_event=volunteer_at_event_with_id
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def update_volunteer_notes_at_event(
        self, event_id: str, volunteer_id: str, new_notes: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                return
            self.cursor.execute(
                "UPDATE %s SET %s='%s' WHERE %s=%d AND %s=%d "
                % (
                    VOLUNTEERS_AT_EVENT_TABLE,
                    VOLUNTEER_NOTES,
                    new_notes,
                    EVENT_ID,
                    int(event_id),
                    VOLUNTEER_ID,
                    int(volunteer_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def get_availability_dict_for_volunteers_at_event(
        self, event_id: str
    ) -> Dict[Volunteer, DaySelector]:
        registration_data = self.get_dict_of_registration_data_for_volunteers_at_event(
            event_id=event_id
        )
        return dict(
            [
                (
                    volunteer,
                    registration_data.get_data_for_volunteer(volunteer).availablity,
                )
                for volunteer in registration_data.list_of_volunteers_at_event()
            ]
        )

    def get_dict_of_registration_data_for_volunteers_at_event(
        self, event_id: str
    ) -> DictOfRegistrationDataForVolunteerAtEvent:
        raw_data = self.read(event_id)
        new_dict = {}
        for raw_item in raw_data:
            volunteer = self.list_of_volunteeers.volunteer_with_id(
                raw_item.volunteer_id
            )
            reg_data = (
                RegistrationDataForVolunteerAtEvent.from_volunteer_at_event_with_id(
                    volunteer_at_event_with_id=raw_item
                )
            )
            new_dict[volunteer] = reg_data

        return DictOfRegistrationDataForVolunteerAtEvent(new_dict)

    @property
    def list_of_volunteeers(self) -> ListOfVolunteers:
        list_of_volunteers = self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers.read
        )

        return list_of_volunteers

    def is_volunteer_already_at_event(self, event_id: str, volunteer_id: str):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT* FROM %s WHERE %s='%d' AND %s='%d' """
                % (
                    VOLUNTEERS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    VOLUNTEER_ID,
                    int(volunteer_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers at event" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def read_for_volunteer(
        self, event_id: str, volunteer_id: str, default=missing_data
    ) -> VolunteerAtEventWithId:
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                return default

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s, %s, %s, %s FROM %s WHERE %s=%d AND %s=%d """
                % (
                    VOLUNTEER_NOTES,
                    VOLUNTEER_AVAILABLITY,
                    PREFERRED_DUTIES,
                    SAME_OR_DIFFERENT_DUTIES,
                    VOLUNTEER_ANY_OTHER_INFORMATION,
                    VOLUNTEER_STATUS,
                    VOLUNTEERS_AT_EVENT_TABLE,
                    VOLUNTEER_ID,
                    int(volunteer_id),
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers at event" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list) > 1:
            raise MultipleMatches
        raw_item = raw_list[0]

        return VolunteerAtEventWithId(
            volunteer_id=volunteer_id,
            notes=str(raw_item[0]),
            availablity=DaySelector.from_str(raw_item[1]),
            preferred_duties=str(raw_item[2]),
            same_or_different=str(raw_item[3]),
            any_other_information=str(raw_item[4]),
            self_declared_status=str(raw_item[5]),
            list_of_associated_cadet_id=[],
        )

    def read(self, event_id: str) -> ListOfVolunteersAtEventWithId:
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                return ListOfVolunteersAtEventWithId.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s, %s, %s, %s, %s FROM %s WHERE %s=%d """
                % (
                    VOLUNTEER_ID,
                    VOLUNTEER_AVAILABLITY,
                    PREFERRED_DUTIES,
                    SAME_OR_DIFFERENT_DUTIES,
                    VOLUNTEER_ANY_OTHER_INFORMATION,
                    VOLUNTEER_STATUS,
                    VOLUNTEER_NOTES,
                    VOLUNTEERS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers at event" % str(e1))
        finally:
            self.close()

        new_list = [
            VolunteerAtEventWithId(
                volunteer_id=str(raw_item[0]),
                availablity=DaySelector.from_str(raw_item[1]),
                preferred_duties=str(raw_item[2]),
                same_or_different=str(raw_item[3]),
                any_other_information=str(raw_item[4]),
                self_declared_status=str(raw_item[5]),
                notes=str(raw_item[6]),
                list_of_associated_cadet_id=[],
            )
            for raw_item in raw_list
        ]

        return ListOfVolunteersAtEventWithId(new_list)

    def write(
        self, list_of_volunteers_at_event: ListOfVolunteersAtEventWithId, event_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                self.create_table()

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (VOLUNTEERS_AT_EVENT_TABLE, EVENT_ID, int(event_id))
            )

            for volunteer_at_event in list_of_volunteers_at_event:
                self._add_row_without_checks_or_commits(
                    event_id=event_id, volunteer_at_event=volunteer_at_event
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to volunteers at event table event# %s"
                % (str(e1), event_id)
            )
        finally:
            self.close()

    def _add_row_without_checks_or_commits(
        self, event_id: str, volunteer_at_event: VolunteerAtEventWithId
    ):
        volunteer_id = int(volunteer_at_event.volunteer_id)
        availability = volunteer_at_event.availablity.as_str()
        preferred_duties = str(volunteer_at_event.preferred_duties)
        same_or_different = str(volunteer_at_event.same_or_different)
        any_other_information = str(volunteer_at_event.any_other_information)
        self_declared_status = str(volunteer_at_event.self_declared_status)
        notes = str(volunteer_at_event.notes)

        insertion = (
            "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s, %s) VALUES (?, ?,?,?, ?,?,?,?)"
            % (
                VOLUNTEERS_AT_EVENT_TABLE,
                EVENT_ID,
                VOLUNTEER_ID,
                VOLUNTEER_AVAILABLITY,
                PREFERRED_DUTIES,
                SAME_OR_DIFFERENT_DUTIES,
                VOLUNTEER_ANY_OTHER_INFORMATION,
                VOLUNTEER_STATUS,
                VOLUNTEER_NOTES,
            )
        )
        self.cursor.execute(
            insertion,
            (
                int(event_id),
                volunteer_id,
                availability,
                preferred_duties,
                same_or_different,
                any_other_information,
                self_declared_status,
                notes,
            ),
        )

    def create_table(self):
        table_creation_query = """
                        CREATE TABLE %s (
                            %s INT, 
                            %s INT, 
                            %s STR,
                            %s STR,
                            %s STR,
                            %s STR,
                            %s STR,
                            %s STR
                        );
                    """ % (
            VOLUNTEERS_AT_EVENT_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            VOLUNTEER_AVAILABLITY,
            PREFERRED_DUTIES,
            SAME_OR_DIFFERENT_DUTIES,
            VOLUNTEER_ANY_OTHER_INFORMATION,
            VOLUNTEER_STATUS,
            VOLUNTEER_NOTES,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
            INDEX_VOLUNTEERS_AT_EVENT_TABLE,
            VOLUNTEERS_AT_EVENT_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating volunteers at event table" % str(e1)
            )
        finally:
            self.close()
