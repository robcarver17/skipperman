from dataclasses import dataclass
from typing import Dict, List

from app.objects.composed.volunteers_with_skills import SkillsDict
from app.objects.events import Event
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId

from app.objects.volunteer_roles_and_groups_with_id import (
    VolunteerWithIdInRoleAtEvent,
    RoleAndGroupDEPRECATE,
)
from app.objects.roles_and_teams import NO_ROLE_SET
from app.objects.volunteers import Volunteer

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.groups import Group, unallocated_group
from app.objects.day_selectors import Day, DaySelector
from app.objects_OLD.cadets_with_groups import ListOfCadetsAtEventWithGroupsByDay


## must match below


@dataclass
class VolunteerInRoleAtEventWithTeamName(GenericSkipperManObject):
    volunteer_in_role_at_event: VolunteerWithIdInRoleAtEvent
    team_name: str


## Not saved, used purely for sorting purposes


@dataclass
class DEPRECATE_VolunteerWithRoleAtEvent(GenericSkipperManObject):
    volunteer: Volunteer
    day: Day
    role: str = NO_ROLE_SET
    group: Group = unallocated_group

    @classmethod
    def from_volunteer_with_id_in_role_at_event(
        cls,
        volunteer_with_id_in_role_at_event: VolunteerWithIdInRoleAtEvent,
        volunteer: Volunteer,
    ):
        return cls(
            volunteer=volunteer,
            day=volunteer_with_id_in_role_at_event.day,
            role=volunteer_with_id_in_role_at_event.role,
            group=volunteer_with_id_in_role_at_event.group,
        )


class DEPRECATE_ListOfVolunteersWithRoleAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return DEPRECATE_VolunteerWithRoleAtEvent


class RoleAndGroupByDayDict(Dict[Day, RoleAndGroupDEPRECATE]):
    def has_role_on_day(self, day: Day, role: str) -> bool:
        return self.role_and_group_on_day(day).role == role

    def role_and_group_on_day(self, day: Day) -> RoleAndGroupDEPRECATE:
        return self.get(day, RoleAndGroupDEPRECATE.create_empty())


@dataclass
class VolunteerAtEventWithSkillsAndRoles:
    volunteer: Volunteer
    skills: SkillsDict
    volunteer_event_data: str
    role_and_group_by_day: RoleAndGroupByDayDict

    @classmethod
    def from_volunteer_at_event_with_skills(
        cls,
        volunteer_at_event_with_skills: str,
        role_and_group_by_day: RoleAndGroupByDayDict,
    ):
        return cls(
            volunteer=volunteer_at_event_with_skills.volunteer,
            skills=volunteer_at_event_with_skills.skills_dict,
            volunteer_event_data=volunteer_at_event_with_skills.volunteer_event_data,
            role_and_group_by_day=role_and_group_by_day,
        )


class ListOfVolunteersAtEventWithSkillsAndRoles(
    List[VolunteerAtEventWithSkillsAndRoles]
):
    pass


@dataclass
class VolunteerEventData_DEPRECATE:
    event: Event
    availablity: DaySelector
    list_of_associated_cadets: ListOfCadetsAtEventWithGroupsByDay
    preferred_duties: str = ""  ## information only
    same_or_different: str = ""  ## information only
    any_other_information: str = (
        ""  ## information only - double counted as required twice
    )
    notes: str = ""

    @classmethod
    def from_volunteer_at_event_with_id(
        cls,
        event: Event,
        volunteer_at_event_with_id: VolunteerAtEventWithId,
        list_of_associated_cadets: ListOfCadetsAtEventWithGroupsByDay,
    ):
        availability = volunteer_at_event_with_id.availablity.intersect(
            event.day_selector_for_days_in_event()
        )
        return cls(
            event=event,
            availablity=availability,
            list_of_associated_cadets=list_of_associated_cadets,
            preferred_duties=volunteer_at_event_with_id.preferred_duties,
            same_or_different=volunteer_at_event_with_id.same_or_different,
            any_other_information=volunteer_at_event_with_id.same_or_different,
        )


@dataclass
class VolunteerAtEventWithSkills_DEPRECATE:
    volunteer: Volunteer
    skills_dict: SkillsDict
    volunteer_event_data: VolunteerEventData_DEPRECATE

    @classmethod
    def from_volunteer_at_event_with_id(
        cls,
        event: Event,
        volunteer: Volunteer,
        volunteer_at_event_with_id: VolunteerAtEventWithId,
        skills_dict: SkillsDict,
        list_of_associated_cadets: ListOfCadetsAtEventWithGroupsByDay,
    ):
        return cls(
            volunteer=volunteer,
            skills_dict=skills_dict,
            volunteer_event_data=VolunteerEventData_DEPRECATE.from_volunteer_at_event_with_id(
                event=event,
                volunteer_at_event_with_id=volunteer_at_event_with_id,
                list_of_associated_cadets=list_of_associated_cadets,
            ),
        )


class ListOfVolunteersAtEventWithSkills(List[VolunteerAtEventWithSkills_DEPRECATE]):
    pass
