from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.volunteers import *
from app.data_access.resolve_paths_and_filenames import (
    LIST_OF_VOLUNTEERS_FILE_ID,
    LIST_OF_VOLUNTEER_SKILLS_FILE_ID,
    LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID,
    LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID,
    LIST_OF_IDENTIFIED_VOLUNTEERS_AT_EVENT_FILE_ID,
    LIST_OF_VOLUNTEERS_IN_ROLES_FILE_ID,
    LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID,
    LIST_OF_SKILLS_FILE_ID,
    VOLUNTEER_ROLES_FILE_ID,
    VOLUNTEER_TEAMS_FILE_ID,
    VOLUNTEER_ROLE_AND_TEAMS_FILE_ID,
    NOTES_FILE_ID,
)
from app.objects.cadet_volunteer_connections_with_ids import (
    ListOfCadetVolunteerAssociationsWithIds,
)
from app.objects.roles_and_teams import (
    ListOfRolesWithSkillIds,
    ListOfTeams,
    ListOfTeamsAndRolesWithIds,
)
from app.objects.volunteers_with_skills_and_ids import ListOfVolunteerSkillsWithIds

from app.objects.volunteer_at_event_with_id import ListOfVolunteersAtEventWithId
from app.objects.identified_volunteer_at_event import (
    ListOfIdentifiedVolunteersAtEvent,
)
from app.objects.volunteer_role_targets import (
    ListOfTargetForRoleWithIdAtEvent,
)
from app.objects.volunteer_roles_and_groups_with_id import (
    ListOfVolunteersWithIdInRoleAtEvent,
)


class CsvDataListOfRoles(GenericCsvData, DataListOfRoles):
    def read(self) -> ListOfRolesWithSkillIds:
        return self.read_and_return_object_of_type(
            ListOfRolesWithSkillIds, file_identifier=VOLUNTEER_ROLES_FILE_ID
        )

    def write(self, list_of_roles: ListOfRolesWithSkillIds):
        self.write_object(list_of_roles, file_identifier=VOLUNTEER_ROLES_FILE_ID)


class CsvDataListOfTeams(GenericCsvData, DataListOfTeams):
    def read(self) -> ListOfTeams:
        return self.read_and_return_object_of_type(
            ListOfTeams, file_identifier=VOLUNTEER_TEAMS_FILE_ID
        )

    def write(self, list_of_teams: ListOfTeams):
        self.write_object(list_of_teams, file_identifier=VOLUNTEER_TEAMS_FILE_ID)


class CsvDataListOfTeamsAndRolesWithIds(GenericCsvData, DataListOfTeamsAndRolesWithIds):
    def read(self) -> ListOfTeamsAndRolesWithIds:
        return self.read_and_return_object_of_type(
            ListOfTeamsAndRolesWithIds, file_identifier=VOLUNTEER_ROLE_AND_TEAMS_FILE_ID
        )

    def write(self, list_of_teams_and_roles_with_ids: ListOfTeamsAndRolesWithIds):
        self.write_object(
            list_of_teams_and_roles_with_ids,
            file_identifier=VOLUNTEER_ROLE_AND_TEAMS_FILE_ID,
        )


class CsvDataListOfSkills(GenericCsvData, DataListOfSkills):
    def read(self) -> ListOfSkills:
        return self.read_and_return_object_of_type(
            ListOfSkills, file_identifier=LIST_OF_SKILLS_FILE_ID
        )

    def write(self, list_of_skills: ListOfSkills):
        self.write_object(list_of_skills, file_identifier=LIST_OF_SKILLS_FILE_ID)


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
    def read(self) -> ListOfVolunteerSkillsWithIds:
        list_of_volunteer_skills = self.read_and_return_object_of_type(
            ListOfVolunteerSkillsWithIds,
            file_identifier=LIST_OF_VOLUNTEER_SKILLS_FILE_ID,
        )

        return list_of_volunteer_skills

    def write(self, list_of_volunteer_skills: ListOfVolunteerSkillsWithIds):
        self.write_object(
            list_of_volunteer_skills, file_identifier=LIST_OF_VOLUNTEER_SKILLS_FILE_ID
        )


class CsvDataListOfCadetVolunteerAssociations(
    GenericCsvData, DataListOfCadetVolunteerAssociations
):
    def read(self) -> ListOfCadetVolunteerAssociationsWithIds:
        list_of_cadet_volunteer_associations = self.read_and_return_object_of_type(
            ListOfCadetVolunteerAssociationsWithIds,
            file_identifier=LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID,
        )

        return list_of_cadet_volunteer_associations

    def write(
        self,
        list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociationsWithIds,
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
    def read(self, event_id: str) -> ListOfTargetForRoleWithIdAtEvent:
        return self.read_and_return_object_of_type(
            ListOfTargetForRoleWithIdAtEvent,
            file_identifier=LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )

    def write(
        self,
        list_of_targets_for_roles_at_event: ListOfTargetForRoleWithIdAtEvent,
        event_id: str,
    ):
        self.write_object(
            list_of_targets_for_roles_at_event,
            file_identifier=LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfNotes(DataListOfNotes, GenericCsvData):
    def read(self) -> ListOfNotes:
        return self.read_and_return_object_of_type(
            ListOfNotes,
            file_identifier=NOTES_FILE_ID,
        )

    def write(self, list_of_notes: ListOfNotes):
        self.write_object(list_of_notes, file_identifier=NOTES_FILE_ID)
