from dataclasses import dataclass
from typing import Dict, List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.events import get_sorted_list_of_events
from app.backend.group_allocations.cadet_event_allocations import \
    load_list_of_cadets_ids_with_group_allocations_active_cadets_only, get_list_of_cadets_unallocated_to_group_at_event
from app.backend.data.volunteers import  load_list_of_volunteer_skills
from app.backend.data.volunteer_rota import DEPRECATE_load_volunteers_in_role_at_event
from app.backend.data.volunteer_allocation import DEPRECATED_load_list_of_volunteers_at_event

from app.objects.cadets import ListOfCadets
from app.objects.constants import missing_data, arg_not_passed
from app.objects.day_selectors import Day
from app.objects.events import Event, SORT_BY_START_ASC, list_of_events_excluding_one_event
from app.objects.groups import ListOfCadetIdsWithGroups, GROUP_UNALLOCATED
from app.objects.volunteers import ListOfVolunteerSkills
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent, VolunteerAtEvent
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent, VolunteerInRoleAtEvent, NO_ROLE_SET, \
    FILTER_ALL, FILTER_AVAILABLE, FILTER_UNALLOC_AVAILABLE, FILTER_ALLOC_AVAILABLE, FILTER_UNAVAILABLE


@dataclass
class RotaSortsAndFilters:
    sort_by_volunteer_name: str
    sort_by_day: Day
    skills_filter: dict
    availability_filter: dict
    sort_by_location: bool

def get_explanation_of_sorts_and_filters(sorts_and_filters: RotaSortsAndFilters):
    sort_by =""
    if sorts_and_filters.sort_by_volunteer_name is not arg_not_passed:
        sort_by+="Sorting by volunteer name (%s). " % sorts_and_filters.sort_by_volunteer_name
    if sorts_and_filters.sort_by_day is not arg_not_passed:
        sort_by+="Sorting by day %s. " % sorts_and_filters.sort_by_day.name
    if sorts_and_filters.sort_by_location:
        sort_by+="Sort by cadet location"

    sort_by+="Availability filter %s. " % str(sorts_and_filters.availability_filter)
    sort_by+="Skills filter %s" % str(sorts_and_filters.skills_filter)

    return sort_by

@dataclass
class DataToBeStoredWhilstConstructingVolunteerRotaPage:
    event: Event
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
    unallocated_cadets_at_event: ListOfCadets
    volunteer_skills: ListOfVolunteerSkills
    volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent
    list_of_volunteers_at_event: ListOfVolunteersAtEvent
    dict_of_volunteers_with_last_roles: Dict[str, str]

    def filtered_list_of_volunteers_at_event(self, sorts_and_filters: RotaSortsAndFilters) -> ListOfVolunteersAtEvent:
        skills_filter = sorts_and_filters.skills_filter
        original_list = self.list_of_volunteers_at_event
        volunteer_skills = self.volunteer_skills
        availability_filter_dict = sorts_and_filters.availability_filter
        list_of_volunteers_in_roles_at_event = self.volunteers_in_roles_at_event

        new_list = ListOfVolunteersAtEvent([volunteer for volunteer in original_list if filter_volunteer(
            volunteer, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event, skills_filter=skills_filter, volunteer_skills=volunteer_skills,
            availability_filter_dict=availability_filter_dict
        )])

        return new_list

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

def filter_volunteer(volunteer_at_event: VolunteerAtEvent,
                     list_of_volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent,
                     skills_filter: dict,     volunteer_skills: ListOfVolunteerSkills,
                     availability_filter_dict: dict)-> bool:

    filter_by_skills = filter_volunteer_by_skills(volunteer_at_event=volunteer_at_event, skills_filter=skills_filter, volunteer_skills=volunteer_skills)
    filter_by_availability = filter_volunteer_by_availability(volunteer_at_event=volunteer_at_event,
                                                              list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event,
                                                              availability_filter_dict=availability_filter_dict)

    return filter_by_skills and filter_by_availability

def filter_volunteer_by_skills(volunteer_at_event: VolunteerAtEvent, skills_filter: dict,     volunteer_skills: ListOfVolunteerSkills,)-> bool:
    volunteer_skills = volunteer_skills.skills_for_volunteer_id(volunteer_id=volunteer_at_event.volunteer_id)
    if not any(skills_filter.values()):
        ## nothing to filter on
        return True

    required_skill_present = [skill_name for skill_name, filter_by_this_skill in skills_filter.items()
                              if filter_by_this_skill and skill_name in volunteer_skills]

    return any(required_skill_present)

def filter_volunteer_by_availability(volunteer_at_event: VolunteerAtEvent,
                    list_of_volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent,
                     availability_filter_dict: dict)-> bool:

    filter_by_day = [filter_volunteer_by_availability_on_given_day(
        volunteer_at_event=volunteer_at_event,
       list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event,
        day = Day[name_of_day],
        availability_filter=availability_filter
    )
    for name_of_day, availability_filter in availability_filter_dict.items()
    ]

    return all(filter_by_day)

def filter_volunteer_by_availability_on_given_day(volunteer_at_event: VolunteerAtEvent,
                                    list_of_volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent,
                                     day: Day,
                                      availability_filter: str) -> bool:

    if availability_filter==FILTER_ALL:
        return True ## no filtering

    role_today = list_of_volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(volunteer_at_event.volunteer_id,
                                                                                           day=day,
                                                                                           return_empty_if_missing=True)

    unallocated = role_today.no_role_set
    allocated = not unallocated
    available =volunteer_at_event.available_on_day(day)

    if availability_filter == FILTER_AVAILABLE:
        return available
    elif availability_filter==FILTER_UNAVAILABLE:
        return not available
    elif availability_filter == FILTER_ALLOC_AVAILABLE:
        return available and allocated
    elif availability_filter== FILTER_UNALLOC_AVAILABLE:
        return available and unallocated


def get_data_to_be_stored_for_volunteer_rota_page(interface: abstractInterface, event: Event) -> DataToBeStoredWhilstConstructingVolunteerRotaPage:
    list_of_cadet_ids_with_groups = load_list_of_cadets_ids_with_group_allocations_active_cadets_only(event=event, interface=interface)
    unallocated_cadets_at_event = get_list_of_cadets_unallocated_to_group_at_event(event=event, interface=interface)
    volunteer_skills = load_list_of_volunteer_skills(interface)
    volunteers_in_roles_at_event = DEPRECATE_load_volunteers_in_role_at_event(event)
    list_of_volunteers_at_event = DEPRECATED_load_list_of_volunteers_at_event(event)

    dict_of_volunteers_with_last_roles = get_dict_of_volunteers_with_last_roles(list_of_volunteers_at_event.list_of_volunteer_ids,
                                                                                avoid_event=event)

    return DataToBeStoredWhilstConstructingVolunteerRotaPage(
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
    volunteer_data = DEPRECATE_load_volunteers_in_role_at_event(event)
    role = volunteer_data.most_common_role_at_event_for_volunteer(volunteer_id=volunteer_id)
    if role==NO_ROLE_SET:
        return missing_data
    return role



