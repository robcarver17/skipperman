from dataclasses import dataclass
from typing import Dict, List

from app.backend.events import get_sorted_list_of_events
from app.backend.group_allocations.cadet_event_allocations import get_unallocated_cadets, \
    load_allocation_for_event
from app.backend.data.volunteers import  get_list_of_volunteer_skills
from app.backend.data.volunteer_rota import get_volunteers_in_role_at_event
from app.backend.data.volunteer_allocation import get_list_of_volunteers_at_event

from app.objects.cadets import ListOfCadets
from app.objects.constants import missing_data, arg_not_passed
from app.objects.day_selectors import Day
from app.objects.events import Event, SORT_BY_START_ASC, list_of_events_excluding_one_event
from app.objects.groups import ListOfCadetIdsWithGroups, GROUP_UNALLOCATED
from app.objects.volunteers import ListOfVolunteerSkills
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent, VolunteerInRoleAtEvent, NO_ROLE_SET


@dataclass
class DataToBeStoredWhilstConstructingTableBody:
    event: Event
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
    unallocated_cadets_at_event: ListOfCadets
    volunteer_skills: ListOfVolunteerSkills
    volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent
    list_of_volunteers_at_event: ListOfVolunteersAtEvent
    dict_of_volunteers_with_last_roles: Dict[str, str]

    def group_given_cadet_id(self, cadet_id):
        try:
            cadet_with_group = self.list_of_cadet_ids_with_groups.item_with_cadet_id(cadet_id)
            return cadet_with_group.group
        except:
            try:
                __unallocated_cadet_unused = self.unallocated_cadets_at_event.object_with_id(cadet_id)
                return GROUP_UNALLOCATED
            except:
                return missing_data

    def list_of_skills_given_volunteer_id(self, volunteer_id: str)->dict:
        return self.volunteer_skills.skills_for_volunteer_id(volunteer_id)

    def volunteer_in_role_at_event_on_day(self, volunteer_id: str, day: Day) -> VolunteerInRoleAtEvent:
        return self.volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(volunteer_id=volunteer_id, day=day)



    def all_roles_match_across_event(self, volunteer_id: str)->bool:
        availability = self.list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id=volunteer_id).availablity
        all_volunteers_in_roles_at_event_including_no_role_set = [self.volunteer_in_role_at_event_on_day(volunteer_id=volunteer_id,
                                                                                   day=day)
                                            for day in availability.days_available()]

        if len(all_volunteers_in_roles_at_event_including_no_role_set)==0:
            return False

        all_roles = [volunteer_in_role_at_event_on_day.role for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event_including_no_role_set]
        all_groups = [volunteer_in_role_at_event_on_day.group for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event_including_no_role_set]

        all_groups_match = len(set(all_groups))<=1
        all_roles_match = len(set(all_roles))<=1

        return all_roles_match and all_groups_match


def get_data_to_be_stored(event: Event) -> DataToBeStoredWhilstConstructingTableBody:
    list_of_cadet_ids_with_groups = load_allocation_for_event(event=event)
    unallocated_cadets_at_event = get_unallocated_cadets(event=event, list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups)
    volunteer_skills = get_list_of_volunteer_skills()
    volunteers_in_roles_at_event = get_volunteers_in_role_at_event(event)
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(event)

    dict_of_volunteers_with_last_roles = get_dict_of_volunteers_with_last_roles(list_of_volunteers_at_event.list_of_volunteer_ids,
                                                                                avoid_event=event)

    return DataToBeStoredWhilstConstructingTableBody(
        event=event,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        unallocated_cadets_at_event=unallocated_cadets_at_event,
        volunteer_skills=volunteer_skills,
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        dict_of_volunteers_with_last_roles=dict_of_volunteers_with_last_roles
    )


def get_dict_of_volunteers_with_last_roles(list_of_volunteer_ids: List[str], avoid_event: Event) -> Dict[str, str]:
    return dict([
        (volunteer_id, get_last_role_for_volunteer_id(volunteer_id=volunteer_id, avoid_event=avoid_event))
        for volunteer_id in list_of_volunteer_ids
    ])


def get_last_role_for_volunteer_id(volunteer_id: str, avoid_event: Event = arg_not_passed) -> str:
    roles = get_all_roles_across_past_events_for_volunteer_id_as_list(
        volunteer_id=volunteer_id,
        avoid_event=avoid_event,
        sort_by=SORT_BY_START_ASC
    )
    if len(roles)==0:
        return ""

    return roles[-1] ## most recent role


def get_all_roles_across_past_events_for_volunteer_id_as_list(volunteer_id: str, sort_by = SORT_BY_START_ASC, avoid_event: Event = arg_not_passed) -> list:
    roles_as_dict = get_all_roles_across_past_events_for_volunteer_id_as_dict(
        volunteer_id=volunteer_id,
        sort_by=sort_by,
        avoid_event=avoid_event
    )
    return list(roles_as_dict.values())

def get_all_roles_across_past_events_for_volunteer_id_as_dict(volunteer_id: str, sort_by = SORT_BY_START_ASC, avoid_event: Event = arg_not_passed) -> dict:
    list_of_events = get_sorted_list_of_events(sort_by)
    if avoid_event is arg_not_passed:
        pass ## can't exclude so do everything
    else:
        list_of_events = list_of_events_excluding_one_event(list_of_events=list_of_events,
                                                            event_to_exclude=avoid_event,
                                                                 sort_by=sort_by,
                                                                 only_past=True)

    roles = [get_role_for_event_and_volunteer_id(volunteer_id, event) for event in list_of_events]
    roles_dict = dict([(event, role) for event, role in zip(list_of_events, roles) if role is not missing_data])

    return roles_dict


def get_role_for_event_and_volunteer_id(volunteer_id: str, event: Event) -> str:
    volunteer_data = get_volunteers_in_role_at_event(event)
    role = volunteer_data.most_common_role_at_event_for_volunteer(volunteer_id=volunteer_id)
    if role==NO_ROLE_SET:
        return missing_data
    return role


