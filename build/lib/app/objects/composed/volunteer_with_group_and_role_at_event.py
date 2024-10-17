from dataclasses import dataclass
from typing import Dict, List

from app.objects.utils import most_common

from app.objects.events import ListOfEvents, Event

from app.objects.volunteer_roles_and_groups_with_id import ListOfVolunteersWithIdInRoleAtEvent, VolunteerWithIdInRoleAtEvent

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.day_selectors import Day

from app.objects.groups import Group, ListOfGroups, unallocated_group

from app.objects.composed.volunteer_roles import RoleWithSkills, ListOfRolesWithSkills, no_role_set
from app.objects.composed.roles_and_teams import ListOfRolesWithSkills

@dataclass
class VolunteerWithRoleAtEvent:
    volunteer: Volunteer
    day: Day
    role: RoleWithSkills
    group: Group

    @classmethod
    def from_volunteer_with_id_in_role_at_event(cls,volunteer_with_id_in_role_at_event: VolunteerWithIdInRoleAtEvent,
                                                list_of_volunteers: ListOfVolunteers,
                                                list_of_groups: ListOfGroups,
                                                list_of_roles_with_skills: ListOfRolesWithSkills,
                                                ):

        return cls(
            volunteer=list_of_volunteers.volunteer_with_id(volunteer_with_id_in_role_at_event.volunteer_id),
            role=list_of_roles_with_skills.role_with_id(volunteer_with_id_in_role_at_event.role_id),
            day=volunteer_with_id_in_role_at_event.day,
            group=list_of_groups.object_with_id(volunteer_with_id_in_role_at_event.group_id)
        )

@dataclass
class RoleAndGroup:
    role: RoleWithSkills
    group: Group

    def __repr__(self):
        if self.group.is_unallocated:
            return self.role.name
        else:
            return "%s (%s)" % (self.role.name, self.group.name)

    def __hash__(self):
        return hash(str(self.role)+"___"+str(self.group))

    @classmethod
    def create_unallocated(cls):
        return cls(
            no_role_set,
            unallocated_group
        )

    @property
    def is_unallocated(self):
        return self == unallocated_role_and_group

    @property
    def is_si(self) -> bool:
        return self.role.is_si()

class ListOfRolesAndGroups(List[RoleAndGroup]):
    @property
    def list_of_groups(self) -> ListOfGroups:
        return ListOfGroups([role_and_group.group for role_and_group in self])

unallocated_role_and_group =RoleAndGroup.create_unallocated()

class DictOfDaysRolesAndGroups(Dict[Day, RoleAndGroup]):
    def most_common_role_and_groups(self) -> RoleAndGroup:
        return most_common(self.list_of_roles_and_groups, default=RoleAndGroup.create_unallocated())

    def list_of_groups(self) -> ListOfGroups:
        return self.list_of_roles_and_groups.list_of_groups

    @property
    def list_of_roles_and_groups(self) -> ListOfRolesAndGroups:
        return ListOfRolesAndGroups(list(self.values()))

    def contains_si(self) -> bool:
        return any([
            role_and_group.is_si
            for role_and_group in self.list_of_roles_and_groups
            ]

        )

    def subset_where_role_in_list_of_roles(self, list_of_roles: List[RoleWithSkills]):
        return DictOfDaysRolesAndGroups(
            [
                (day, role_and_group)
                for day, role_and_group in self.items()
                if role_and_group.role in list_of_roles
            ]
        )

class ListOfVolunteersWithRoleAtEvent(List[VolunteerWithRoleAtEvent]):
    @classmethod
    def from_list_of_volunteers_with_id_in_role_at_event(cls,
                                                         list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
                                                         list_of_volunteers: ListOfVolunteers,
                                                         list_of_groups: ListOfGroups,
                                                         list_of_roles_with_skills: ListOfRolesWithSkills,
                                                         ):

        return cls([
            VolunteerWithRoleAtEvent.from_volunteer_with_id_in_role_at_event(
                volunteer_with_id_in_role_at_event=volunteer_with_id_in_role_at_event,
                list_of_groups=list_of_groups,
                list_of_roles_with_skills=list_of_roles_with_skills,
                list_of_volunteers=list_of_volunteers
            )
            for volunteer_with_id_in_role_at_event in list_of_volunteers_with_id_in_role_at_event
        ])

    def unique_list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(list(set([volunteer_with_role.volunteer for volunteer_with_role in self])))

    def dict_of_days_roles_and_groups_for_volunteer(self, volunteer: Volunteer) -> DictOfDaysRolesAndGroups:
        subset_for_volunteer = self.subset_for_volunteer(volunteer)
        return DictOfDaysRolesAndGroups(
            dict(
                [
                    (volunteer_with_role.day,
                     RoleAndGroup(
                         role=volunteer_with_role.role,
                         group=volunteer_with_role.group
                     ))

                    for volunteer_with_role in subset_for_volunteer
                ]
            )
        )

    def subset_for_volunteer(self, volunteer: Volunteer):
        return ListOfVolunteersWithRoleAtEvent(
            [volunteer_with_role for volunteer_with_role in self if volunteer_with_role.volunteer == volunteer]
        )

class DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups(Dict[Volunteer, DictOfDaysRolesAndGroups]):
    def __init__(self, raw_dict: Dict[Volunteer, DictOfDaysRolesAndGroups], list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent, event: Event):
        super().__init__(raw_dict)
        self._list_of_volunteers_with_id_in_role_at_event = list_of_volunteers_with_id_in_role_at_event
        self._event = event

    def days_and_roles_for_volunteer(self, volunteer: Volunteer):
        return self.get(volunteer, DictOfDaysRolesAndGroups())

    @property
    def list_of_volunteers_with_id_in_role_at_event(self) -> ListOfVolunteersWithIdInRoleAtEvent:
        return self._list_of_volunteers_with_id_in_role_at_event

    @property
    def event(self) -> Event:
        return self._event

def compose_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
        event_id: str,
        list_of_events: ListOfEvents,
        list_of_volunteers: ListOfVolunteers,
        list_of_groups: ListOfGroups,
        list_of_roles_with_skills: ListOfRolesWithSkills,
list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent
) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:

    event = list_of_events.object_with_id(event_id)
    raw_dict = compose_raw_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
        list_of_volunteers=list_of_volunteers,
        list_of_groups=list_of_groups,
        list_of_roles_with_skills=list_of_roles_with_skills,
        list_of_volunteers_with_id_in_role_at_event=list_of_volunteers_with_id_in_role_at_event
    )

    return DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups(
        raw_dict=raw_dict,
        event = event,
        list_of_volunteers_with_id_in_role_at_event=list_of_volunteers_with_id_in_role_at_event
    )

def compose_raw_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
        list_of_volunteers: ListOfVolunteers,
        list_of_groups: ListOfGroups,
        list_of_roles_with_skills: ListOfRolesWithSkills,
    list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent
) -> Dict[Volunteer, DictOfDaysRolesAndGroups]:

    list_of_volunteers_with_role_in_event = ListOfVolunteersWithRoleAtEvent.from_list_of_volunteers_with_id_in_role_at_event(
        list_of_volunteers_with_id_in_role_at_event=list_of_volunteers_with_id_in_role_at_event,
        list_of_volunteers=list_of_volunteers,
        list_of_groups=list_of_groups,
        list_of_roles_with_skills=list_of_roles_with_skills
    )

    volunteers_at_event = list_of_volunteers_with_role_in_event.unique_list_of_volunteers()

    return dict(
        [
            (volunteer,
             list_of_volunteers_with_role_in_event.dict_of_days_roles_and_groups_for_volunteer(volunteer))
            for volunteer in volunteers_at_event
        ]
    )