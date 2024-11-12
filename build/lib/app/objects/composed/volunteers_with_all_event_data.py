from dataclasses import dataclass
from typing import Dict

from app.objects.composed.roles_and_teams import DictOfTeamsWithRoles
from app.objects.events import ListOfEvents, Event

from app.objects.volunteers import Volunteer
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


class DictOfAllEventDataForVolunteers(Dict[Volunteer, AllEventDataForVolunteer]):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, AllEventDataForVolunteer],
        event: Event,
        dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
        dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
        dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
        dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
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
        self._event = event

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
    def event(self) -> Event:
        return self._event


def compose_dict_of_all_event_data_for_volunteers(
    event_id: str,
    list_of_events: ListOfEvents,
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
) -> DictOfAllEventDataForVolunteers:
    event = list_of_events.object_with_id(event_id)

    raw_dict = compose_raw_dict_of_all_event_data_for_volunteers(
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
    )

    return DictOfAllEventDataForVolunteers(
        raw_dict=raw_dict,
        event=event,
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
    )


def compose_raw_dict_of_all_event_data_for_volunteers(
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
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
                ),
            )
            for volunteer in volunteers_at_event
        ]
    )
