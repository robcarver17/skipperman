from dataclasses import dataclass
from typing import Dict, List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.events import get_sorted_list_of_events
from app.backend.group_allocations.cadet_event_allocations import \
    load_list_of_cadets_ids_with_group_allocations_active_cadets_only, get_list_of_cadets_unallocated_to_group_at_event
from app.backend.volunteers.volunteers import load_list_of_volunteer_skills
from app.backend.volunteers.volunteer_rota import load_list_of_volunteers_at_event, \
    get_volunteers_in_role_at_event_with_active_allocations, sort_volunteer_data_for_event_by_name_sort_order

from app.objects.cadets import ListOfCadets
from app.objects.constants import missing_data, arg_not_passed
from app.objects.day_selectors import Day
from app.objects.events import Event, SORT_BY_START_ASC, list_of_events_excluding_one_event
from app.objects.groups import ListOfCadetIdsWithGroups, GROUP_UNALLOCATED, Group, sorted_locations
from app.objects.volunteers import ListOfVolunteerSkills, Volunteer
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
    explanation =""
    if sorts_and_filters.sort_by_volunteer_name is not arg_not_passed:
        explanation+="Sorting by: volunteer name (%s). " % sorts_and_filters.sort_by_volunteer_name
    if sorts_and_filters.sort_by_day is not arg_not_passed:
        explanation+="Sorting by: group / role on %s. " % sorts_and_filters.sort_by_day.name
    if sorts_and_filters.sort_by_location:
        explanation+="Sorting by: cadet location. "

    explanation+=print_dict_nicely("Availability filter", sorts_and_filters.availability_filter)
    explanation+=". "+explain_filter(sorts_and_filters.skills_filter, "Skills filter")

    return explanation

from app.objects.utils import print_dict_nicely

def explain_filter(filter: Dict[str,bool], prepend_text: str) -> str:
    true_only_str = dict_elements_only_true(filter)
    if len(true_only_str)==0:
        return ""
    else:
        return "%s: %s" % (prepend_text, true_only_str)

def dict_elements_only_true(some_dict: Dict[str, bool]) -> str:
    true_only = [key for key, value in some_dict.items() if value]
    true_only = ", ".join(true_only)

    return true_only

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
            volunteer, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event,
            skills_filter=skills_filter, volunteer_skills=volunteer_skills,
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
    volunteers_in_roles_at_event = get_volunteers_in_role_at_event_with_active_allocations(event=event, interface=interface)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event=event, interface=interface)

    dict_of_volunteers_with_last_roles = get_dict_of_volunteers_with_last_roles(interface=interface,
                                                                                list_of_volunteer_ids=list_of_volunteers_at_event.list_of_volunteer_ids,
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


def get_dict_of_volunteers_with_last_roles(interface: abstractInterface, list_of_volunteer_ids: List[str], avoid_event: Event) -> Dict[str, str]:
    return dict([
        (volunteer_id, get_last_role_for_volunteer_id(interface=interface, volunteer_id=volunteer_id, avoid_event=avoid_event))
        for volunteer_id in list_of_volunteer_ids
    ])


def get_last_role_for_volunteer_id(interface: abstractInterface, volunteer_id: str, avoid_event: Event = arg_not_passed) -> str:
    roles = get_all_roles_across_recent_events_for_volunteer_id_as_list(
        interface=interface,
        volunteer_id=volunteer_id,
        avoid_event=avoid_event,
        sort_by=SORT_BY_START_ASC
    )
    if len(roles)==0:
        return ""

    return roles[-1] ## most recent role


def get_all_roles_across_recent_events_for_volunteer_id_as_list(interface: abstractInterface, volunteer_id: str, sort_by = SORT_BY_START_ASC, avoid_event: Event = arg_not_passed) -> list:
    roles_as_dict = get_all_roles_across_recent_events_for_volunteer_id_as_dict(
        interface=interface,
        volunteer_id=volunteer_id,
        sort_by=sort_by,
        avoid_event=avoid_event
    )
    return list(roles_as_dict.values())

HOW_MANY_EVENTS = 4 ## normally 3 but include last event

def get_all_roles_across_recent_events_for_volunteer_id_as_dict(interface: abstractInterface, volunteer_id: str, sort_by = SORT_BY_START_ASC, avoid_event: Event = arg_not_passed) -> dict:
    list_of_events = get_sorted_list_of_events(interface=interface, sort_by=sort_by)
    list_of_events = list_of_events[-HOW_MANY_EVENTS:]
    if avoid_event is arg_not_passed:
        pass ## can't exclude so do everything
    else:
        list_of_events = list_of_events_excluding_one_event(list_of_events=list_of_events,
                                                            event_to_exclude=avoid_event,
                                                                 sort_by=sort_by,
                                                                 only_past=True)

    roles = [get_role_and_group_for_event_and_volunteer_id(interface=interface, event=event, volunteer_id=volunteer_id) for event in list_of_events]
    roles_dict = dict([(event, role) for event, role in zip(list_of_events, roles) if role is not missing_data])

    return roles_dict


def get_role_and_group_for_event_and_volunteer_id(interface: abstractInterface, volunteer_id: str, event: Event) -> str:
    volunteer_data = get_volunteers_in_role_at_event_with_active_allocations(interface=interface, event=event)
    role = volunteer_data.most_common_role_and_group_at_event_for_volunteer(volunteer_id=volunteer_id)
    if role==NO_ROLE_SET:
        return missing_data
    return role


def sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event: ListOfVolunteersAtEvent,
        sort_by_day: Day,
        data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage) -> ListOfVolunteersAtEvent:

    tuple_of_volunteers_at_event_and_roles = [(volunteer_at_event,
                                                    data_to_be_stored.volunteer_in_role_at_event_on_day(
                                                    volunteer_id=volunteer_at_event.volunteer_id, day=sort_by_day).role_and_group
                                               )
                            for volunteer_at_event in list_of_volunteers_at_event]

    tuple_of_volunteers_at_event_and_roles.sort(key=lambda tup: tup[1])

    list_of_volunteers = [volunteer_at_event for volunteer_at_event, __ in tuple_of_volunteers_at_event_and_roles]

    return ListOfVolunteersAtEvent(list_of_volunteers)


def get_cadet_location_string(data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage, volunteer_at_event: VolunteerAtEvent):
    list_of_groups = list_of_cadet_groups_associated_with_volunteer(data_to_be_stored=data_to_be_stored,
                                                                    volunteer_at_event=volunteer_at_event)
    if len(list_of_groups)==0:
        return "x- no associated cadets -x" ## trick to get at end of sort

    return str_type_of_group_given_list_of_groups(list_of_groups)


def str_type_of_group_given_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    unique_list_of_group_locations = list(set(types_of_groups))
    sorted_list_of_group_locations = sorted_locations(unique_list_of_group_locations)
    return ", ".join(sorted_list_of_group_locations)


def str_dict_skills(volunteer: Volunteer, data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage):
    list_of_skills = data_to_be_stored.list_of_skills_given_volunteer_id(volunteer.id)
    if len(list_of_skills)==0:
        return "No skills recorded"

    return ", ".join(list_of_skills)


def get_sorted_and_filtered_list_of_volunteers_at_event(
        interface: abstractInterface,
        data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
        sorts_and_filters: RotaSortsAndFilters,
    ) -> ListOfVolunteersAtEvent:

    list_of_volunteers_at_event = data_to_be_stored.filtered_list_of_volunteers_at_event(sorts_and_filters)
    sorted_list_of_volunteers_at_event = sort_list_of_volunteers_at_event(
        interface=interface,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        data_to_be_stored=data_to_be_stored,
        sorts_and_filters=sorts_and_filters
    )

    return sorted_list_of_volunteers_at_event


def sort_list_of_volunteers_at_event(interface: abstractInterface,
        list_of_volunteers_at_event: ListOfVolunteersAtEvent,
                                     data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
                                     sorts_and_filters: RotaSortsAndFilters)-> ListOfVolunteersAtEvent:

    sort_by_location = sorts_and_filters.sort_by_location
    if sort_by_location:
        return sort_volunteer_data_for_event_by_location(
            list_of_volunteers_at_event=list_of_volunteers_at_event,
            data_to_be_stored=data_to_be_stored
        )

    sort_by_volunteer_name = sorts_and_filters.sort_by_volunteer_name
    if sort_by_volunteer_name is not arg_not_passed:
        return sort_volunteer_data_for_event_by_name_sort_order(
            interface=interface, volunteers_at_event=list_of_volunteers_at_event,
             sort_order=sort_by_volunteer_name)

    sort_by_day = sorts_and_filters.sort_by_day
    if sort_by_day is not arg_not_passed:
        return sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event, sort_by_day=sorts_and_filters.sort_by_day,
            data_to_be_stored=data_to_be_stored)

    return list_of_volunteers_at_event


def sort_volunteer_data_for_event_by_location(list_of_volunteers_at_event: ListOfVolunteersAtEvent,
                                              data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage)-> ListOfVolunteersAtEvent:

    list_of_locations = [
        get_cadet_location_string(data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event)
        for volunteer_at_event in list_of_volunteers_at_event]

    locations_and_volunteers = zip(list_of_locations, list_of_volunteers_at_event)

    sorted_by_location = sorted(locations_and_volunteers, key=lambda tup: tup[0])
    sorted_list_of_volunteers = ListOfVolunteersAtEvent([location_and_volunteer[1] for location_and_volunteer in sorted_by_location])

    return sorted_list_of_volunteers


def list_of_cadet_groups_associated_with_volunteer(data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage, volunteer_at_event: VolunteerAtEvent) -> List[Group]:
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    list_of_groups = [data_to_be_stored.group_given_cadet_id(cadet_id) for cadet_id in list_of_cadet_ids]
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return list_of_groups
