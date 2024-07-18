from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.volunteers import *
from app.data_access.csv.resolve_csv_paths_and_filenames import (
    LIST_OF_VOLUNTEERS_FILE_ID,
    LIST_OF_VOLUNTEER_SKILLS_FILE_ID,
    LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID,
    LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID,
    LIST_OF_IDENTIFIED_VOLUNTEERS_AT_EVENT_FILE_ID,
    LIST_OF_VOLUNTEERS_IN_ROLES_FILE_ID,
    LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID,
)
from app.objects.cadet_volunteer_connections import ListOfCadetVolunteerAssociations
from app.objects.primtive_with_id.volunteer_skills import ListOfVolunteerSkills
from app.objects.primtive_with_id.volunteer_at_event import ListOfVolunteersAtEventWithId
from app.objects.primtive_with_id.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent
from app.objects.primtive_with_id.volunteer_role_targets import ListOfTargetForRoleAtEvent
from app.objects.primtive_with_id.volunteer_roles_and_groups import ListOfVolunteersWithIdInRoleAtEvent


class CsvDataListOfVolunteers(GenericCsvData, DataListOfVolunteers):
    def read(self) -> ListOfVolunteers:
        list_of_volunteers = self.read_and_return_object_of_type(
            ListOfVolunteers, file_identifier=LIST_OF_VOLUNTEERS_FILE_ID
        )

        return list_of_volunteers

    def write(self, list_of_volunteers: ListOfVolunteers):
        self.write_object(
            list_of_volunteers, file_identifier=LIST_OF_VOLUNTEERS_FILE_ID
        )


class CsvDataListOfVolunteerSkills(GenericCsvData, DataListOfVolunteerSkills):
    def read(self) -> ListOfVolunteerSkills:
        list_of_volunteer_skills = self.read_and_return_object_of_type(
            ListOfVolunteerSkills, file_identifier=LIST_OF_VOLUNTEER_SKILLS_FILE_ID
        )

        return list_of_volunteer_skills

    def write(self, list_of_volunteer_skills: ListOfVolunteerSkills):
        self.write_object(
            list_of_volunteer_skills, file_identifier=LIST_OF_VOLUNTEER_SKILLS_FILE_ID
        )


class CsvDataListOfCadetVolunteerAssociations(
    GenericCsvData, DataListOfCadetVolunteerAssociations
):
    def read(self) -> ListOfCadetVolunteerAssociations:
        list_of_cadet_volunteer_associations = self.read_and_return_object_of_type(
            ListOfCadetVolunteerAssociations,
            file_identifier=LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID,
        )

        return list_of_cadet_volunteer_associations

    def write(
        self, list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations
    ):
        self.write_object(
            list_of_cadet_volunteer_associations,
            file_identifier=LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID,
        )


class CsvDataListOfVolunteersAtEvent(GenericCsvData, DataListOfVolunteersAtEvent):
    def read(self, event_id: str) -> ListOfVolunteersAtEventWithId:
        list_of_volunteers_at_event = self.read_and_return_object_of_type(
            ListOfVolunteersAtEventWithId,
            file_identifier=LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )

        return list_of_volunteers_at_event

    def write(
        self, list_of_volunteers_at_event: ListOfVolunteersAtEventWithId, event_id: str
    ):
        self.write_object(
            list_of_volunteers_at_event,
            file_identifier=LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfIdentifiedVolunteersAtEvent(
    GenericCsvData, DataListOfIdentifiedVolunteersAtEvent
):
    def read(self, event_id: str) -> ListOfIdentifiedVolunteersAtEvent:
        return self.read_and_return_object_of_type(
            ListOfIdentifiedVolunteersAtEvent,
            file_identifier=LIST_OF_IDENTIFIED_VOLUNTEERS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )

    def write(
        self,
        list_of_identified_volunteers: ListOfIdentifiedVolunteersAtEvent,
        event_id: str,
    ):
        self.write_object(
            list_of_identified_volunteers,
            file_identifier=LIST_OF_IDENTIFIED_VOLUNTEERS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfVolunteersInRolesAtEvent(
    GenericCsvData, DataListOfVolunteersInRolesAtEvent
):
    def read(self, event_id: str) -> ListOfVolunteersWithIdInRoleAtEvent:
        list_of_volunteers_in_roles_at_event = self.read_and_return_object_of_type(
            ListOfVolunteersWithIdInRoleAtEvent,
            file_identifier=LIST_OF_VOLUNTEERS_IN_ROLES_FILE_ID,
            additional_file_identifiers=event_id,
        )

        return list_of_volunteers_in_roles_at_event

    def write(
        self,
        list_of_volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
        event_id: str,
    ):
        self.write_object(
            list_of_volunteers_in_roles_at_event,
            file_identifier=LIST_OF_VOLUNTEERS_IN_ROLES_FILE_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfTargetForRoleAtEvent(GenericCsvData, DataListOfTargetForRoleAtEvent):
    def read(self, event_id: str) -> ListOfTargetForRoleAtEvent:
        return self.read_and_return_object_of_type(
            ListOfTargetForRoleAtEvent,
            file_identifier=LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )

    def write(
        self,
        list_of_targets_for_roles_at_event: ListOfTargetForRoleAtEvent,
        event_id: str,
    ):
        self.write_object(
            list_of_targets_for_roles_at_event,
            file_identifier=LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )
