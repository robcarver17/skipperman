from dataclasses import dataclass
from typing import Dict

from app.objects.club_dinghies import ClubDinghy
from app.objects.composed.people_at_event_with_club_dinghies import (
    DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteers_last_role_across_events import \
    DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents
from app.objects.day_selectors import Day

from app.objects.cadets import ListOfCadets

from app.objects.composed.cadet_volunteer_associations import (
    DictOfCadetsAssociatedWithVolunteer,
)
from app.objects.events import ListOfEvents, Event
from app.objects.utilities.exceptions import arg_not_passed, MissingData
from app.objects.food import no_food_requirements
from app.objects.groups import Group
from app.objects.patrol_boats import PatrolBoat

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
    food_requirements: FoodRequirements
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
        dict_of_volunteers_with_food_at_event: DictOfVolunteersWithFoodRequirementsAtEvent,
        dict_of_people_and_club_dinghies_at_event: DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent,
            dict_of_volunteers_with_most_common_role_and_group_across_events: DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents
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
        self._dict_of_people_and_club_dinghies_at_event = (
            dict_of_people_and_club_dinghies_at_event
        )
        self._dict_of_volunteers_with_most_common_role_and_group_across_events = dict_of_volunteers_with_most_common_role_and_group_across_events
        self._event = event

    def copy_club_dinghy_for_instructor_across_all_days(
        self, day: Day, volunteer: Volunteer, club_dinghy: ClubDinghy
    ):
        days_available = self.dict_of_registration_data_for_volunteers_at_event.get_data_for_volunteer(
            volunteer
        ).availablity.days_available()
        self.dict_of_people_and_club_dinghies_at_event.copy_club_dinghy_for_instructor_across_all_days(
            volunteer=volunteer, days_available=days_available, club_dinghy=club_dinghy
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
        self, day: Day, club_dinghy: ClubDinghy
    ) -> ListOfVolunteers:
        return self.dict_of_people_and_club_dinghies_at_event.list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
            day=day, club_dinghy=club_dinghy
        )

    def allocate_club_dinghy_to_volunteer_on_day(
        self, day: Day, volunteer: Volunteer, club_dinghy: ClubDinghy
    ):
        self.dict_of_people_and_club_dinghies_at_event.allocate_club_boat_on_day(
            person=volunteer, club_boat=club_dinghy, day=day
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def remove_club_dinghy_from_volunteer_on_day(self, day: Day, volunteer: Volunteer):
        self.dict_of_people_and_club_dinghies_at_event.remove_persons_club_boat_allocation_on_day(
            person=volunteer, day=day
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def get_list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies(
        self, day: Day
    ) -> ListOfVolunteers:
        all_volunteers = (
            self.dict_of_registration_data_for_volunteers_at_event.list_of_volunteers_at_event()
        )
        all_volunteers = [
            volunteer
            for volunteer in all_volunteers
            if self.dict_of_registration_data_for_volunteers_at_event.get_data_for_volunteer(
                volunteer
            ).availablity.available_on_day(
                day
            )
            and not self.dict_of_people_and_club_dinghies_at_event.club_dinghys_for_person(
                volunteer
            ).has_any_dinghy_on_specific_day(
                day
            )
        ]

        return ListOfVolunteers(all_volunteers)

    def move_volunteer_into_empty_boat(
        self,
        original_volunteer: Volunteer,
        day_to_swap_with: Day,
        new_patrol_boat: PatrolBoat,
    ):
        self.dict_of_volunteers_at_event_with_patrol_boats.move_volunteer_into_empty_boat(
            original_volunteer=original_volunteer,
            day_to_swap_with=day_to_swap_with,
            new_patrol_boat=new_patrol_boat,
        )
        self.refresh_data_for_volunteer_from_underlying(original_volunteer)

    def swap_patrol_boats_for_volunteers_in_allocation(
        self,
        original_day: Day,
        original_volunteer: Volunteer,
        day_to_swap_with: Day,
        volunteer_to_swap_with: Volunteer,
    ):
        self.dict_of_volunteers_at_event_with_patrol_boats.swap_patrol_boats_for_volunteers_in_allocation(
            original_volunteer=original_volunteer,
            original_day=original_day,
            day_to_swap_with=day_to_swap_with,
            volunteer_to_swap_with=volunteer_to_swap_with,
        )
        self.refresh_data_for_volunteer_from_underlying(original_volunteer)
        self.refresh_data_for_volunteer_from_underlying(volunteer_to_swap_with)

    def delete_patrol_boat_for_volunteer_on_day(self, volunteer: Volunteer, day: Day):
        self.dict_of_volunteers_at_event_with_patrol_boats.delete_patrol_boat_for_volunteer_on_day(
            volunteer=volunteer, day=day
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def remove_patrol_boat_and_all_associated_volunteers_from_event(
        self, patrol_boat: PatrolBoat
    ):
        affected_volunteers = self.dict_of_volunteers_at_event_with_patrol_boats.remove_patrol_boat_and_all_associated_volunteers_from_event_and_return_volunteers(
            patrol_boat=patrol_boat
        )
        [
            self.refresh_data_for_volunteer_from_underlying(volunteer)
            for volunteer in affected_volunteers
        ]

    def copy_across_boats_at_event(
        self, volunteer: Volunteer, day: Day, allow_overwrite: bool
    ):
        volunteer_availablility_at_event = self.get_data_for_volunteer(
            volunteer
        ).registration_data.availablity
        self.dict_of_volunteers_at_event_with_patrol_boats.copy_across_boats_at_event(
            volunteer=volunteer,
            day=day,
            allow_overwrite=allow_overwrite,
            volunteer_availablility_at_event=volunteer_availablility_at_event,
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def add_volunteer_with_boat(
        self, volunteer: Volunteer, patrol_boat: PatrolBoat, day: Day
    ):
        self.dict_of_volunteers_at_event_with_patrol_boats.add_volunteer_with_boat(
            volunteer=volunteer, patrol_boat=patrol_boat, day=day
        )

        self.refresh_data_for_volunteer_from_underlying(volunteer)

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

    def update_volunteer_notes_at_event(self, volunteer: Volunteer, new_notes: str):
        existing_notes = self.get_data_for_volunteer(volunteer).registration_data.notes
        if existing_notes == new_notes:
            return

        self.dict_of_registration_data_for_volunteers_at_event.update_volunteer_notes_at_event(
            volunteer=volunteer, new_notes=new_notes
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def update_role_and_group_at_event_for_volunteer_on_day(
        self,
        volunteer: Volunteer,
        day: Day,
        new_role: RoleWithSkills,
        new_group: Group = arg_not_passed,  ### if not passed, no change
    ):
        self.dict_of_volunteers_at_event_with_days_and_roles.update_role_and_group_at_event_for_volunteer_on_day(
            volunteer=volunteer, day=day, new_role=new_role, new_group=new_group
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def add_new_volunteer(
        self,
        volunteer: Volunteer,
        registration_data: RegistrationDataForVolunteerAtEvent,
    ):
        self.dict_of_registration_data_for_volunteers_at_event.add_new_volunteer(
            volunteer=volunteer, registration_data=registration_data
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def swap_roles_and_groups_for_volunteers_in_allocation(
        self,
        original_volunteer: Volunteer,
        volunteer_to_swap_with: Volunteer,
        original_day: Day,
        day_to_swap_with: Day,
    ):
        self.dict_of_volunteers_at_event_with_days_and_roles.swap_roles_and_groups_for_volunteers_in_allocation(
            original_volunteer=original_volunteer,
            volunteer_to_swap_with=volunteer_to_swap_with,
            original_day=original_day,
            day_to_swap_with=day_to_swap_with,
        )
        self.refresh_data_for_volunteer_from_underlying(original_volunteer)
        self.refresh_data_for_volunteer_from_underlying(volunteer_to_swap_with)

    def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        self, volunteer: Volunteer, day: Day, allow_replacement: bool
    ):
        registration_data_for_volunteers_at_event = (
            self.dict_of_registration_data_for_volunteers_at_event
        )

        available_days = (
            registration_data_for_volunteers_at_event.get_data_for_volunteer(
                volunteer
            ).availablity
        )

        self.dict_of_volunteers_at_event_with_days_and_roles.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            volunteer=volunteer,
            day=day,
            available_days=available_days,
            allow_replacement=allow_replacement,
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

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

        self.refresh_data_for_volunteer_from_underlying(volunteer)

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

        self.refresh_data_for_volunteer_from_underlying(volunteer)

    def delete_volunteer_from_event(self, volunteer: Volunteer):
        try:
            self.pop(volunteer)
        except:
            return []

        messages = []
        messages.append("Deleting data for %s" % self.event)
        volunteer_registration_data = (
            self.dict_of_registration_data_for_volunteers_at_event
        )
        volunteer_registration_data.drop_volunteer(volunteer)
        messages.append("- dropped from registration data")

        days_and_roles_data = self.dict_of_volunteers_at_event_with_days_and_roles
        messages += days_and_roles_data.drop_volunteer(volunteer)

        patrol_boat_data = self.dict_of_volunteers_at_event_with_patrol_boats
        messages += patrol_boat_data.drop_volunteer(volunteer)

        food_data = self.dict_of_volunteers_with_food_at_event
        messages += food_data.drop_volunteer(volunteer)

        club_boats = self.dict_of_people_and_club_dinghies_at_event
        messages += club_boats.remove_person_from_event(volunteer)

        return messages

    def make_volunteer_available_on_day(self, volunteer: Volunteer, day: Day):
        volunteer_registration_data = (
            self.dict_of_registration_data_for_volunteers_at_event
        )
        volunteer_registration_data.make_volunteer_available_on_day(
            day=day, volunteer=volunteer
        )
        self.refresh_data_for_volunteer_from_underlying(volunteer)

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

        club_boat_data = self.dict_of_people_and_club_dinghies_at_event
        club_boat_data.remove_persons_club_boat_allocation_on_day(
            day=day, person=volunteer
        )

        self.refresh_data_for_volunteer_from_underlying(volunteer)

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
            dict_of_people_and_club_dinghies_at_event=self.dict_of_people_and_club_dinghies_at_event,
            dict_of_volunteers_with_most_common_role_and_group_across_events=self.dict_of_volunteers_with_most_common_role_and_group_across_events,
            event=self.event,
        )

    def refresh_data_for_volunteer_from_underlying(self, volunteer):
        self[volunteer] = AllEventDataForVolunteer(
            volunteer=volunteer,
            registration_data=self.dict_of_registration_data_for_volunteers_at_event[
                volunteer
            ],
            volunteer_skills=self.dict_of_volunteers_with_skills.get(
                volunteer, SkillsDict()
            ),
            roles_and_groups=self.dict_of_volunteers_at_event_with_days_and_roles.get(
                volunteer, DictOfDaysRolesAndGroupsAndTeams()
            ),
            patrol_boats=self.dict_of_volunteers_at_event_with_patrol_boats.get(
                volunteer, PatrolBoatByDayDict()
            ),
            associated_cadets=self.dict_of_cadets_associated_with_volunteers.get(
                volunteer, ListOfCadets([])
            ),
            food_requirements=self.dict_of_volunteers_with_food_at_event.food_for_volunteer(
                volunteer, default=no_food_requirements
            ),
            club_boats=self.dict_of_people_and_club_dinghies_at_event.club_dinghys_for_person(
                volunteer
            ),
            most_common_role_group_and_team_at_previous_events=self._dict_of_volunteers_with_most_common_role_and_group_across_events.get_most_common_role_and_group_for_volunteer_or_none(volunteer),
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
    def dict_of_people_and_club_dinghies_at_event(
        self,
    ) -> DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent:
        return self._dict_of_people_and_club_dinghies_at_event

    @property
    def dict_of_volunteers_at_event_with_days_and_roles(
        self,
    ) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
        return self._dict_of_volunteers_at_event_with_days_and_roles

    @property
    def dict_of_volunteers_with_most_common_role_and_group_across_events(self) -> DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents:
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
    dict_of_people_and_club_dinghies_at_event: DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent,
        dict_of_volunteers_with_most_common_role_and_group_across_events: DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents
) -> DictOfAllEventDataForVolunteers:
    event = list_of_events.event_with_id(event_id)

    raw_dict = compose_raw_dict_of_all_event_data_for_volunteers(
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
        dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers,
        dict_of_volunteers_with_food_at_event=dict_of_volunteers_with_food_at_event,
        dict_of_people_and_club_dinghies_at_event=dict_of_people_and_club_dinghies_at_event,
        dict_of_volunteers_with_most_common_role_and_group_across_events=dict_of_volunteers_with_most_common_role_and_group_across_events,

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
        dict_of_people_and_club_dinghies_at_event=dict_of_people_and_club_dinghies_at_event,
        dict_of_volunteers_with_most_common_role_and_group_across_events=dict_of_volunteers_with_most_common_role_and_group_across_events
    )


def compose_raw_dict_of_all_event_data_for_volunteers(
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer,
    dict_of_volunteers_with_food_at_event: DictOfVolunteersWithFoodRequirementsAtEvent,
    dict_of_people_and_club_dinghies_at_event: DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent,
        dict_of_volunteers_with_most_common_role_and_group_across_events: DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents,
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
                    club_boats=dict_of_people_and_club_dinghies_at_event.club_dinghys_for_person(
                        volunteer
                    ),
                    most_common_role_group_and_team_at_previous_events=dict_of_volunteers_with_most_common_role_and_group_across_events.get_most_common_role_and_group_for_volunteer_or_none(volunteer),
                    event=event,
                ),
            )
            for volunteer in volunteers_at_event
        ]
    )
