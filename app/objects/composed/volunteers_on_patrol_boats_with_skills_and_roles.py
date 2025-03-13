from dataclasses import dataclass
from typing import List

from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.patrol_boats import PatrolBoat

from app.objects.events import Event

from app.objects.composed.volunteers_with_skills import SkillsDict

from app.objects.volunteers import Volunteer
from app.objects.day_selectors import DaySelector, Day
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfDaysRolesAndGroupsAndTeams,
    RoleAndGroupAndTeam,
)
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    PatrolBoatByDayDict,
)


@dataclass
class VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday:
    volunteer: Volunteer
    event: Event
    skills: SkillsDict
    role_and_group: RoleAndGroupAndTeam
    patrol_boat: PatrolBoat
    day: Day
    role_and_group_by_day: DictOfDaysRolesAndGroupsAndTeams
    patrol_boat_by_day: PatrolBoatByDayDict
    availability: DaySelector

    def __hash__(self):
        return hash(self.volunteer.name + self.patrol_boat.name)

    def has_volunteer_role(self, role: RoleWithSkills):
        return self.role_and_group.role == role


class ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday(
    List[VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday]
):
    def has_volunteer_role_on_day(self, role: RoleWithSkills):
        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday(
            [
                volunteer_at_event
                for volunteer_at_event in self
                if volunteer_at_event.has_volunteer_role(role=role)
            ]
        )


@dataclass
class VolunteerAtEventWithSkillsAndRolesAndPatrolBoats:
    volunteer: Volunteer
    event: Event
    skills: SkillsDict
    availability: DaySelector
    role_and_group_by_day: DictOfDaysRolesAndGroupsAndTeams
    patrol_boat_by_day: PatrolBoatByDayDict

    def assigned_to_boat_on_day(self, patrol_boat: PatrolBoat, day: Day) -> bool:
        return self.patrol_boat_by_day.assigned_to_boat_on_day(
            patrol_boat=patrol_boat, day=day
        )

    def assigned_to_any_boat_on_day(self, day: Day) -> bool:
        return self.patrol_boat_by_day.on_any_patrol_boat_on_given_day(day)

    def __hash__(self):
        return hash(self.volunteer.name)

    def for_specific_day(
        self, day: Day
    ) -> VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday:
        return VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday(
            volunteer=self.volunteer,
            skills=self.skills,
            event=self.event,
            role_and_group=self.role_and_group_by_day.role_and_group_and_team_on_day(
                day
            ),
            patrol_boat=self.patrol_boat_by_day.boat_on_day(day),
            day=day,
            availability=self.availability,
            role_and_group_by_day=self.role_and_group_by_day,
            patrol_boat_by_day=self.patrol_boat_by_day,
        )


class ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats(
    List[VolunteerAtEventWithSkillsAndRolesAndPatrolBoats]
):
    def assigned_to_boat_on_day(
        self, patrol_boat: PatrolBoat, day: Day
    ) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday:
        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday(
            [
                volunteer_at_event.for_specific_day(day)
                for volunteer_at_event in self
                if volunteer_at_event.assigned_to_boat_on_day(
                    patrol_boat=patrol_boat, day=day
                )
            ]
        )

    def assigned_to_any_boat_on_day(
        self, day: Day
    ) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday:
        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday(
            [
                volunteer_at_event.for_specific_day(day)
                for volunteer_at_event in self
                if volunteer_at_event.assigned_to_any_boat_on_day(day)
            ]
        )
