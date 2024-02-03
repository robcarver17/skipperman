from app.objects.volunteers import Volunteer, VolunteerSkill, ListOfVolunteers, ListOfVolunteerSkills, \
    CadetVolunteerAssociation, ListOfCadetVolunteerAssociations
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfVolunteersAtEvent, ListOfCadetsWithoutVolunteersAtEvent
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent

class DataListOfVolunteers(object):
    def add(self, volunteer: Volunteer):
        list_of_volunteers = self.read()
        if volunteer in list_of_volunteers:
            raise Exception("Volunteer %s already in list of existing volunteers" % str(volunteer))

        volunteer_id = list_of_volunteers.next_id()
        volunteer.id = volunteer_id
        list_of_volunteers.append(volunteer)
        self.write(list_of_volunteers)

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

    def write(self, list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations):
        raise NotImplemented


class DataListOfVolunteersAtEvent(object):
    def read(self, event_id: str) -> ListOfVolunteersAtEvent:
        raise NotImplemented

    def write(self, list_of_volunteers_at_event: ListOfVolunteersAtEvent, event_id: str):
        raise NotImplemented


class DataListOfCadetsWithoutVolunteersAtEvent(object):
    def read(self) -> ListOfCadetsWithoutVolunteersAtEvent:
        raise NotImplemented

    def write(self, list_of_cadets_without_volunteers_at_event: ListOfCadetsWithoutVolunteersAtEvent):
        raise NotImplemented


class DataListOfVolunteersInRolesAtEvent(object):
    def read(self, event_id: str) -> ListOfVolunteersInRoleAtEvent:
        raise NotImplemented

    def write(self, list_of_volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent, event_id: str):
        raise NotImplemented
