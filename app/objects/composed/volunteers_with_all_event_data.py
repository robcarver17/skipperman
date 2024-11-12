from dataclasses import dataclass
from typing import Dict

from app.objects.cadets import ListOfCadets

from app.objects.composed.cadet_volunteer_associations import DictOfCadetsAssociatedWithVolunteer
from app.objects.events import ListOfEvents, Event

from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.composed.volunteers_with_skills import (
    SkillsDict,
    DictOfVolunteersWithSkills,
)
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfDaysRolesAndGroups,
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
)
from app.objects.composed.volunteers_at_event_with_registration_data import (
    RegistrationDataForVolunteerAtEvent,
    DictOfRegistrationDataForVolunteerAtEvent,
)
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    PatrolBoatByDayDict,
    DictOfVolunteersAtEventWithPatrolBoatsByDay,
)


@dataclass
class AllEventDataForVolunteer:
    registration_data: RegistrationDataForVolunteerAtEvent
    volunteer_skills: SkillsDict
    roles_and_groups: DictOfDaysRolesAndGroups
    patrol_boats: PatrolBoatByDayDict
    associated_cadets: ListOfCadets
    event: Event
    volunteer: Volunteer

class DictOfAllEventDataForVolunteers(Dict[Volunteer, AllEventDataForVolunteer]):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, AllEventDataForVolunteer],
        event: Event,
        dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
        dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
        dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
        dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
        dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer
    ):
        super().__init__(raw_dict)
        self._dict_of_registration_data_for_volunteers_at_event = (
            dict_of_registration_data_for_volunteers_at_event
        )
        self._dict_of_volunteers_with_skills = dict_of_volunteers_with_skills
        self._dict_of_volunteers_at_event_with_days_and_roles = (
            dict_of_volunteers_at_event_with_days_and_roles
        )
        self._dict_of_volunteers_at_event_with_patrol_boats = (
            dict_of_volunteers_at_event_with_patrol_boats
        )
        self._dict_of_cadets_associated_with_volunteers = dict_of_cadets_associated_with_volunteers
        self._event = event

    def sort_by_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        new_raw_dict = dict([(volunteer, self[volunteer]) for volunteer in list_of_volunteers])

        return DictOfAllEventDataForVolunteers(
            raw_dict=new_raw_dict,
            dict_of_volunteers_with_skills=self.dict_of_volunteers_with_skills,
            dict_of_registration_data_for_volunteers_at_event=self.dict_of_registration_data_for_volunteers_at_event,
            dict_of_volunteers_at_event_with_days_and_roles=self.dict_of_volunteers_at_event_with_days_and_role,
            dict_of_volunteers_at_event_with_patrol_boats=self.dict_of_volunteers_at_event_with_patrol_boats,
            dict_of_cadets_associated_with_volunteers=self.dict_of_cadets_associated_with_volunteers,
            event=self.event
        )

    def filter_out_volunteer(self, volunteer: Volunteer):
        self.pop(volunteer)

    @property
    def dict_of_registration_data_for_volunteers_at_event(
        self,
    ) -> DictOfRegistrationDataForVolunteerAtEvent:
        return self._dict_of_registration_data_for_volunteers_at_event

    @property
    def dict_of_volunteers_with_skills(self) -> DictOfVolunteersWithSkills:
        return self._dict_of_volunteers_with_skills

    @property
    def dict_of_volunteers_at_event_with_days_and_role(
        self,
    ) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
        return self._dict_of_volunteers_at_event_with_days_and_roles

    @property
    def dict_of_volunteers_at_event_with_patrol_boats(
        self,
    ) -> DictOfVolunteersAtEventWithPatrolBoatsByDay:
        return self._dict_of_volunteers_at_event_with_patrol_boats

    @property
    def dict_of_cadets_associated_with_volunteers(self)-> DictOfCadetsAssociatedWithVolunteer:
        return self._dict_of_cadets_associated_with_volunteers

    @property
    def event(self) -> Event:
        return self._event

    def list_of_volunteers(self):
        return ListOfVolunteers(list(self.keys()))

def compose_dict_of_all_event_data_for_volunteers(
    event_id: str,
    list_of_events: ListOfEvents,
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer
) -> DictOfAllEventDataForVolunteers:
    event = list_of_events.object_with_id(event_id)

    raw_dict = compose_raw_dict_of_all_event_data_for_volunteers(
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
        dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers,
        event=event
    )

    return DictOfAllEventDataForVolunteers(
        raw_dict=raw_dict,
        event=event,
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
        dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers
    )


def compose_raw_dict_of_all_event_data_for_volunteers(
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer,
        event: Event
) -> Dict[Volunteer, AllEventDataForVolunteer]:
    ## THis construction means if we delete from registration data they won't be seen elsewhere
    volunteers_at_event = (
        dict_of_registration_data_for_volunteers_at_event.list_of_volunteers_at_event()
    )

    return dict(
        [
            (
                volunteer,
                AllEventDataForVolunteer(
                    volunteer=volunteer,
                    registration_data=dict_of_registration_data_for_volunteers_at_event[
                        volunteer
                    ],
                    volunteer_skills=dict_of_volunteers_with_skills.get(
                        volunteer, SkillsDict()
                    ),
                    roles_and_groups=dict_of_volunteers_at_event_with_days_and_roles.get(
                        volunteer, DictOfDaysRolesAndGroups()
                    ),
                    patrol_boats=dict_of_volunteers_at_event_with_patrol_boats.get(
                        volunteer, PatrolBoatByDayDict()
                    ),
                    associated_cadets = dict_of_cadets_associated_with_volunteers.get(volunteer, ListOfCadets([])),
                    event=event
                ),
            )
            for volunteer in volunteers_at_event
        ]
    )
