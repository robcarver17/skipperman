from app.objects.volunteers import (
    ListOfVolunteers,
)
from app.objects.composed.volunteers_with_skills import DictOfVolunteersWithSkills
from app.objects.cadet_volunteer_connections_with_ids import ListOfCadetVolunteerAssociationsWithIds
from app.objects.volunteer_at_event_with_id import ListOfVolunteersAtEventWithId
from app.objects_OLD.primtive_with_id.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent
from app.objects_OLD.primtive_with_id.volunteer_role_targets import ListOfTargetForRoleAtEvent
from app.objects.volunteer_roles_and_groups_with_id import ListOfVolunteersWithIdInRoleAtEvent
from app.objects.volunteer_skills import ListOfSkills
from app.objects.roles_and_teams import ListOfRolesWithSkillIds, ListOfTeams, ListOfTeamsAndRolesWithIds

class DataListOfRoles(object):
    def read(self) -> ListOfRolesWithSkillIds:
        raise NotImplemented

    def write(self, list_of_roles: ListOfRolesWithSkillIds):
        raise NotImplemented


class DataListOfTeams(object):
    def read(self) -> ListOfTeams:
        raise NotImplemented

    def write(self, list_of_teams: ListOfTeams):
        raise NotImplemented

class DataListOfTeamsAndRolesWithIds(object):
    def read(self) -> ListOfTeamsAndRolesWithIds:
        raise NotImplemented

    def write(self, list_of_teams_and_roles_with_ids: ListOfTeamsAndRolesWithIds):
        raise NotImplemented


class DataListOfSkills(object):
    def read(self) -> ListOfSkills:
        raise NotImplemented

    def write(self, list_of_skills: ListOfSkills):
        raise NotImplemented

class DataListOfVolunteers(object):
    def read(self) -> ListOfVolunteers:
        raise NotImplemented

    def write(self, list_of_volunteers: ListOfVolunteers):
        raise NotImplemented


class DataListOfVolunteerSkills(object):
    def read(self) -> DictOfVolunteersWithSkills:
        raise NotImplemented

    def write(self, list_of_volunteer_skills: DictOfVolunteersWithSkills):
        raise NotImplemented


class DataListOfCadetVolunteerAssociations(object):
    def read(self) -> ListOfCadetVolunteerAssociationsWithIds:
        raise NotImplemented

    def write(
        self, list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociationsWithIds
    ):
        raise NotImplemented


class DataListOfVolunteersAtEvent(object):
    def read(self, event_id: str) -> ListOfVolunteersAtEventWithId:
        raise NotImplemented

    def write(
        self, list_of_volunteers_at_event: ListOfVolunteersAtEventWithId, event_id: str
    ):
        raise NotImplemented


class DataListOfIdentifiedVolunteersAtEvent(object):
    def read(self, event_id: str) -> ListOfIdentifiedVolunteersAtEvent:
        raise NotImplemented

    def write(
        self,
        event_id: str,
        list_of_identified_volunteers: ListOfIdentifiedVolunteersAtEvent,
    ):
        raise NotImplemented


class DataListOfVolunteersInRolesAtEvent(object):
    def read(self, event_id: str) -> ListOfVolunteersWithIdInRoleAtEvent:
        raise NotImplemented

    def write(
        self,
        list_of_volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
        event_id: str,
    ):
        raise NotImplemented


class DataListOfTargetForRoleAtEvent(object):
    def read(self, event_id: str) -> ListOfTargetForRoleAtEvent:
        raise NotImplemented

    def write(
        self,
        list_of_targets_for_roles_at_event: ListOfTargetForRoleAtEvent,
        event_id: str,
    ):
        raise NotImplemented
