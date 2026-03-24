from dataclasses import dataclass
from typing import Dict, List

from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.composed.roles_and_teams import DictOfTeamsWithRoles
from app.objects.composed.volunteer_roles import  ListOfRolesWithSkills
from app.objects.composed.volunteers_last_role_across_events import (
    DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents,
)
from app.objects.day_selectors import Day

from app.objects.cadets import ListOfCadets

from app.objects.composed.cadet_volunteer_associations import (
    DictOfCadetsAssociatedWithVolunteer,
)
from app.objects.events import Event
from app.objects.utilities.exceptions import arg_not_passed, MissingData
from app.objects.groups import  ListOfGroups

from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.composed.volunteers_with_skills import (
    SkillsDict,
    DictOfVolunteersWithSkills,
)
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfDaysRolesAndGroupsAndTeams,
    RoleAndGroupAndTeam,
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
)
from app.objects.composed.volunteers_at_event_with_registration_data import (
    RegistrationDataForVolunteerAtEvent,
    DictOfRegistrationDataForVolunteerAtEvent,
)
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    PatrolBoatByDayDict,
    DictOfVolunteersAtEventWithPatrolBoatsByDay, DictOfLabelsForEvent,
)

from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfDaysAndClubDinghiesAtEventForPerson,
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
    club_boats: DictOfDaysAndClubDinghiesAtEventForPerson
    most_common_role_group_and_team_at_previous_events: RoleAndGroupAndTeam

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
        dict_of_people_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
        dict_of_volunteers_with_most_common_role_and_group_across_events: DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents,
        dict_of_teams_and_roles: DictOfTeamsWithRoles,
        list_of_roles_with_skills: ListOfRolesWithSkills,
        list_of_groups: ListOfGroups,
            dict_of_patrol_boat_labels_for_event: DictOfLabelsForEvent
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
        self._dict_of_people_and_club_dinghies_at_event = (
            dict_of_people_and_club_dinghies_at_event
        )
        self._dict_of_teams_and_roles = dict_of_teams_and_roles
        self._dict_of_volunteers_with_most_common_role_and_group_across_events = (
            dict_of_volunteers_with_most_common_role_and_group_across_events
        )
        self._list_of_groups = list_of_groups
        self._list_of_roles_with_skills = list_of_roles_with_skills
        self._event = event
        self._dict_of_patrol_boat_labels_for_event = dict_of_patrol_boat_labels_for_event



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
            dict_of_people_and_club_dinghies_at_event=self.dict_of_people_and_club_dinghies_at_event,
            dict_of_volunteers_with_most_common_role_and_group_across_events=self.dict_of_volunteers_with_most_common_role_and_group_across_events,
            event=self.event,
            dict_of_teams_and_roles=self.dict_of_teams_and_roles,
            list_of_groups=self.list_of_groups,
            list_of_roles_with_skills=self.list_of_roles_with_skills,
            dict_of_patrol_boat_labels_for_event=self.dict_of_patrol_boat_labels_for_event
        )

    @property
    def list_of_groups(self) -> ListOfGroups:
        return self._list_of_groups

    @property
    def list_of_roles_with_skills(self) -> ListOfRolesWithSkills:
        return self._list_of_roles_with_skills

    @property
    def dict_of_teams_and_roles(self) -> DictOfTeamsWithRoles:
        return self._dict_of_teams_and_roles

    @property
    def dict_of_registration_data_for_volunteers_at_event(
        self,
    ) -> DictOfRegistrationDataForVolunteerAtEvent:
        return self._dict_of_registration_data_for_volunteers_at_event

    @property
    def dict_of_volunteers_with_skills(self) -> DictOfVolunteersWithSkills:
        return self._dict_of_volunteers_with_skills

    @property
    def dict_of_people_and_club_dinghies_at_event(
        self,
    ) -> DictOfPeopleAndClubDinghiesAtEvent:
        return self._dict_of_people_and_club_dinghies_at_event

    @property
    def dict_of_volunteers_at_event_with_days_and_roles(
        self,
    ) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
        return self._dict_of_volunteers_at_event_with_days_and_roles

    @property
    def dict_of_volunteers_with_most_common_role_and_group_across_events(
        self,
    ) -> DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents:
        return self._dict_of_volunteers_with_most_common_role_and_group_across_events

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
    def event(self) -> Event:
        return self._event

    @property
    def dict_of_patrol_boat_labels_for_event(self) -> DictOfLabelsForEvent:
        return self._dict_of_patrol_boat_labels_for_event

    def list_of_volunteers(self):
        return ListOfVolunteers(list(self.keys()))

    @property
    def list_of_information_per_volunteer(self) -> List[AllEventDataForVolunteer]:
        return list(self.values())
