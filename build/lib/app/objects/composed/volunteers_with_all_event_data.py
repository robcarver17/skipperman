from copy import copy
from dataclasses import dataclass
from typing import Dict

from app.objects.day_selectors import Day

from app.objects.cadets import ListOfCadets

from app.objects.composed.cadet_volunteer_associations import (
    DictOfCadetsAssociatedWithVolunteer,
)
from app.objects.events import ListOfEvents, Event
from app.objects.exceptions import missing_data, arg_not_passed, MissingData
from app.objects.food import no_food_requirements

from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.composed.volunteers_with_skills import (
    SkillsDict,
    DictOfVolunteersWithSkills,
)
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfDaysRolesAndGroupsAndTeams,
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    RoleAndGroupAndTeam,
)
from app.objects.composed.volunteers_at_event_with_registration_data import (
    RegistrationDataForVolunteerAtEvent,
    DictOfRegistrationDataForVolunteerAtEvent,
)
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    PatrolBoatByDayDict,
    DictOfVolunteersAtEventWithPatrolBoatsByDay,
)
from app.objects.composed.food_at_event import (
    DictOfVolunteersWithFoodRequirementsAtEvent,
    FoodRequirements,
)


@dataclass
class AllEventDataForVolunteer:
    registration_data: RegistrationDataForVolunteerAtEvent
    volunteer_skills: SkillsDict
    roles_and_groups: DictOfDaysRolesAndGroupsAndTeams
    patrol_boats: PatrolBoatByDayDict
    associated_cadets: ListOfCadets
    event: Event
    volunteer: Volunteer
    food_requirements: FoodRequirements

    def not_on_patrol_boat_on_given_day(self, day: Day) -> bool:
        return self.patrol_boats.not_on_patrol_boat_on_given_day(day)


class DictOfAllEventDataForVolunteers(Dict[Volunteer, AllEventDataForVolunteer]):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, AllEventDataForVolunteer],
        event: Event,
        dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
        dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
        dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
        dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
        dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer,
        dict_of_volunteers_with_food_at_event: DictOfVolunteersWithFoodRequirementsAtEvent,
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
        self._dict_of_cadets_associated_with_volunteers = (
            dict_of_cadets_associated_with_volunteers
        )
        self._dict_of_volunteers_with_food_at_event = (
            dict_of_volunteers_with_food_at_event
        )
        self._event = event

    def not_on_patrol_boat_on_given_day_and_available(
        self, day: Day
    ) -> "DictOfAllEventDataForVolunteers":
        list_of_volunteers = ListOfVolunteers(
            [
                volunteer
                for volunteer, volunteer_data in self.items()
                if volunteer_data.not_on_patrol_boat_on_given_day(day)
                and volunteer_data.registration_data.availablity.available_on_day(day)
            ]
        )
        return self.sort_by_list_of_volunteers(list_of_volunteers)

    def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        self, volunteer: Volunteer, new_role_and_group: RoleAndGroupAndTeam
    ):
        available_days = self.dict_of_registration_data_for_volunteers_at_event.get_data_for_volunteer(
            volunteer
        ).availablity.days_available()
        self.dict_of_volunteers_at_event_with_days_and_roles.update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
            list_of_days_available=available_days,
            volunteer=volunteer,
            new_role_and_group=new_role_and_group,
        )

    def delete_role_at_event_for_volunteer_on_day(
        self, volunteer: Volunteer, day: Day, delete_power_boat: bool = True
    ):
        days_and_roles_data = self.dict_of_volunteers_at_event_with_days_and_roles
        days_and_roles_data.delete_role_for_volunteer_on_day(
            day=day, volunteer=volunteer
        )

        if delete_power_boat:
            patrol_boat_data = self.dict_of_volunteers_at_event_with_patrol_boats
            patrol_boat_data.delete_patrol_boat_for_volunteer_on_day(
                day=day, volunteer=volunteer
            )

    def delete_volunteer_from_event(self, volunteer: Volunteer):
        volunteer_registration_data = (
            self.dict_of_registration_data_for_volunteers_at_event
        )
        volunteer_registration_data.drop_volunteer(volunteer)

        days_and_roles_data = self.dict_of_volunteers_at_event_with_days_and_roles
        days_and_roles_data.drop_volunteer(volunteer)

        patrol_boat_data = self.dict_of_volunteers_at_event_with_patrol_boats
        patrol_boat_data.drop_volunteer(volunteer)

        food_data = self.dict_of_volunteers_with_food_at_event
        food_data.drop_volunteer(volunteer)

    def make_volunteer_unavailable_on_day(self, volunteer: Volunteer, day: Day):

        volunteer_registration_data = (
            self.dict_of_registration_data_for_volunteers_at_event
        )
        volunteer_registration_data.make_volunteer_unavailable_on_day(
            day=day, volunteer=volunteer
        )

        days_and_roles_data = self.dict_of_volunteers_at_event_with_days_and_roles
        days_and_roles_data.delete_role_for_volunteer_on_day(
            day=day, volunteer=volunteer
        )

        patrol_boat_data = self.dict_of_volunteers_at_event_with_patrol_boats
        patrol_boat_data.delete_patrol_boat_for_volunteer_on_day(
            day=day, volunteer=volunteer
        )

    def get_data_for_volunteer(self, volunteer, default=arg_not_passed):
        try:
            return self.get(volunteer)
        except:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

    def sort_by_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        new_raw_dict = dict(
            [(volunteer, self[volunteer]) for volunteer in list_of_volunteers]
        )

        return DictOfAllEventDataForVolunteers(
            raw_dict=new_raw_dict,
            dict_of_volunteers_with_skills=self.dict_of_volunteers_with_skills,
            dict_of_registration_data_for_volunteers_at_event=self.dict_of_registration_data_for_volunteers_at_event,
            dict_of_volunteers_at_event_with_days_and_roles=self.dict_of_volunteers_at_event_with_days_and_roles,
            dict_of_volunteers_at_event_with_patrol_boats=self.dict_of_volunteers_at_event_with_patrol_boats,
            dict_of_cadets_associated_with_volunteers=self.dict_of_cadets_associated_with_volunteers,
            dict_of_volunteers_with_food_at_event=self.dict_of_volunteers_with_food_at_event,
            event=self.event,
        )

    @property
    def dict_of_registration_data_for_volunteers_at_event(
        self,
    ) -> DictOfRegistrationDataForVolunteerAtEvent:
        return self._dict_of_registration_data_for_volunteers_at_event

    @property
    def dict_of_volunteers_with_skills(self) -> DictOfVolunteersWithSkills:
        return self._dict_of_volunteers_with_skills

    @property
    def dict_of_volunteers_at_event_with_days_and_roles(
        self,
    ) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
        return self._dict_of_volunteers_at_event_with_days_and_roles

    @property
    def dict_of_volunteers_at_event_with_patrol_boats(
        self,
    ) -> DictOfVolunteersAtEventWithPatrolBoatsByDay:
        return self._dict_of_volunteers_at_event_with_patrol_boats

    @property
    def dict_of_cadets_associated_with_volunteers(
        self,
    ) -> DictOfCadetsAssociatedWithVolunteer:
        return self._dict_of_cadets_associated_with_volunteers

    @property
    def dict_of_volunteers_with_food_at_event(
        self,
    ) -> DictOfVolunteersWithFoodRequirementsAtEvent:
        return self._dict_of_volunteers_with_food_at_event

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
    dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer,
    dict_of_volunteers_with_food_at_event: DictOfVolunteersWithFoodRequirementsAtEvent,
) -> DictOfAllEventDataForVolunteers:
    event = list_of_events.event_with_id(event_id)

    raw_dict = compose_raw_dict_of_all_event_data_for_volunteers(
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
        dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers,
        dict_of_volunteers_with_food_at_event=dict_of_volunteers_with_food_at_event,
        event=event,
    )

    return DictOfAllEventDataForVolunteers(
        raw_dict=raw_dict,
        event=event,
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
        dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers,
        dict_of_volunteers_with_food_at_event=dict_of_volunteers_with_food_at_event,
    )


def compose_raw_dict_of_all_event_data_for_volunteers(
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer,
    dict_of_volunteers_with_food_at_event: DictOfVolunteersWithFoodRequirementsAtEvent,
    event: Event,
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
                        volunteer, DictOfDaysRolesAndGroupsAndTeams()
                    ),
                    patrol_boats=dict_of_volunteers_at_event_with_patrol_boats.get(
                        volunteer, PatrolBoatByDayDict()
                    ),
                    associated_cadets=dict_of_cadets_associated_with_volunteers.get(
                        volunteer, ListOfCadets([])
                    ),
                    food_requirements=dict_of_volunteers_with_food_at_event.food_for_volunteer(
                        volunteer, default=no_food_requirements
                    ),
                    event=event,
                ),
            )
            for volunteer in volunteers_at_event
        ]
    )
