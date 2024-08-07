from app.objects.primtive_with_id.volunteers import (
    ListOfVolunteers,
)
from app.objects.primtive_with_id.volunteer_skills import ListOfVolunteerSkills
from app.objects.cadet_volunteer_connections import ListOfCadetVolunteerAssociations
from app.objects.primtive_with_id.volunteer_at_event import ListOfVolunteersAtEventWithId
from app.objects.primtive_with_id.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent
from app.objects.primtive_with_id.volunteer_role_targets import ListOfTargetForRoleAtEvent
from app.objects.primtive_with_id.volunteer_roles_and_groups import ListOfVolunteersWithIdInRoleAtEvent


class DataListOfVolunteers(object):
    def read(self) -> ListOfVolunteers:
        raise NotImplemented

    def write(self, list_of_volunteers: ListOfVolunteers):
        raise NotImplemented


class DataListOfVolunteerSkills(object):
    def read(self) -> ListOfVolunteerSkills:
        raise NotImplemented

    def write(self, list_of_volunteer_skills: ListOfVolunteerSkills):
        raise NotImplemented


class DataListOfCadetVolunteerAssociations(object):
    def read(self) -> ListOfCadetVolunteerAssociations:
        raise NotImplemented

    def write(
        self, list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations
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
