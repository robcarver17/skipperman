from typing import List

from app.backend.data.volunteer_rota import save_volunteers_in_role_at_event
from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingTableBody, \
    load_volunteers_in_role_at_event, RotaSortsAndFilters
from app.backend.data.volunteers import DEPRECATED_get_sorted_list_of_volunteers
from app.objects.constants import missing_data, arg_not_passed
from app.objects.events import Event
from app.objects.groups import Group, ALL_GROUPS_NAMES, GROUP_UNALLOCATED_TEXT
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfVolunteersAtEvent
from app.objects.volunteers import Volunteer
from app.objects.volunteers_in_roles import VOLUNTEER_ROLES, \
    NO_ROLE_SET, VolunteerInRoleAtEvent

from app.objects.day_selectors import Day


def update_role_at_event_for_volunteer_on_day_at_event(event: Event,
                                                       day: Day,
                                                       volunteer_id: str,
                                                       new_role: str):

    volunteer_in_role_at_event_on_day =  VolunteerInRoleAtEvent(day=day, volunteer_id=volunteer_id)

    list_of_volunteers_in_roles_at_event = load_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.update_volunteer_in_role_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
                                                             new_role=new_role)
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def get_volunteer_role_at_event_on_day(event: Event, volunteer_id: str, day: Day) -> str:
    volunteer_in_role = get_volunteer_with_role_at_event_on_day(event=event, day=day, volunteer_id=volunteer_id)
    if volunteer_in_role is missing_data:
        return missing_data

    return volunteer_in_role.role


def get_volunteer_with_role_at_event_on_day(event: Event, volunteer_id: str, day: Day) -> VolunteerInRoleAtEvent:
    volunteers_in_roles_at_event= load_volunteers_in_role_at_event(event)
    volunteer_in_role = volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(volunteer_id=volunteer_id, day=day)

    return volunteer_in_role

def sort_volunteer_data_for_event_by_name_sort_order(volunteers_at_event: ListOfVolunteersAtEvent, sort_order) -> ListOfVolunteersAtEvent:
    list_of_volunteers = DEPRECATED_get_sorted_list_of_volunteers(sort_by=sort_order)
    ## this works because if an ID is missing we just ignore it
    return volunteers_at_event.sort_by_list_of_volunteer_ids(list_of_volunteers.list_of_ids)

def sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event: ListOfVolunteersAtEvent,
        sort_by_day: Day,
        data_to_be_stored: DataToBeStoredWhilstConstructingTableBody) -> ListOfVolunteersAtEvent:

    tuple_of_volunteers_at_event_and_roles = [(volunteer_at_event,
                                                    data_to_be_stored.volunteer_in_role_at_event_on_day(
                                                    volunteer_id=volunteer_at_event.volunteer_id, day=sort_by_day).role_and_group
                                               )
                            for volunteer_at_event in list_of_volunteers_at_event]

    tuple_of_volunteers_at_event_and_roles.sort(key=lambda tup: tup[1])

    list_of_volunteers = [volunteer_at_event for volunteer_at_event, __ in tuple_of_volunteers_at_event_and_roles]

    return ListOfVolunteersAtEvent(list_of_volunteers)


def get_cadet_location_string(data_to_be_stored: DataToBeStoredWhilstConstructingTableBody, volunteer_at_event: VolunteerAtEvent):
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    if len(list_of_cadet_ids)==0:
        return "No associated cadets"
    list_of_groups = [data_to_be_stored.group_given_cadet_id(cadet_id) for cadet_id in list_of_cadet_ids]
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return str_type_of_group_given_list_of_groups(list_of_groups)


def str_type_of_group_given_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    unique_list_of_groups = list(set(types_of_groups))

    return ", ".join(unique_list_of_groups)

def str_dict_skills(volunteer: Volunteer, data_to_be_stored: DataToBeStoredWhilstConstructingTableBody):
    list_of_skills = data_to_be_stored.list_of_skills_given_volunteer_id(volunteer.id)
    if len(list_of_skills)==0:
        return "No skills recorded"

    return ", ".join(list_of_skills)

def dict_of_groups_for_dropdown():
    dict_of_groups = {group:group for group in ALL_GROUPS_NAMES}
    dict_of_groups[GROUP_UNALLOCATED_TEXT]= GROUP_UNALLOCATED_TEXT

    return dict_of_groups

MAKE_UNAVAILABLE = "* UNAVAILABLE *"
def dict_of_roles_for_dropdown():
    dict_of_roles = {role:role for role in VOLUNTEER_ROLES}
    dict_of_roles[NO_ROLE_SET] = NO_ROLE_SET
    dict_of_roles[MAKE_UNAVAILABLE] = MAKE_UNAVAILABLE

    return dict_of_roles

def boat_related_role_str_on_day_for_volunteer_id(day: Day, event: Event, volunteer_id: str)-> str:
    volunteers_in_role_at_event = load_volunteers_in_role_at_event(event)
    volunteer_on_day = volunteers_in_role_at_event.member_matching_volunteer_id_and_day(volunteer_id=volunteer_id, day=day, return_empty_if_missing=False)
    if volunteer_on_day is missing_data:
        return ""
    elif volunteer_on_day.requires_boat:
        return volunteer_on_day.role
    else:
        return ""




def is_possible_to_copy_roles_for_non_grouped_roles_only(event: Event, volunteer_id:str) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteers_with_roles_in_event_including_missing_data = [get_volunteer_with_role_at_event_on_day(volunteer_id=volunteer_id,
                                                                               day=day, event=event)
                                        for day in event.weekdays_in_event()]

    all_volunteer_positions = [volunteer_with_role for volunteer_with_role in volunteers_with_roles_in_event_including_missing_data
                               if volunteer_with_role is not missing_data]

    all_roles = [volunteer_with_role.role for volunteer_with_role in all_volunteer_positions]

    if len(all_roles)==0:
        ## nothing to copy
        return False

    all_roles_match = len(set(all_roles))<=1

    roles_require_groups = [volunteer_with_role.requires_group for volunteer_with_role in all_volunteer_positions]
    at_least_one_role_require_group = any(roles_require_groups)

    ## copy not possible if all roles the same, or at least one requires a group
    if all_roles_match or at_least_one_role_require_group:
        return False
    else:
        return True


def is_possible_to_swap_roles_on_one_day_for_non_grouped_roles_only(event: Event, volunteer_id:str, day: Day) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteer_with_role = get_volunteer_with_role_at_event_on_day(volunteer_id=volunteer_id,
                                                                               day=day, event=event)

    return not volunteer_with_role.requires_group


def swap_roles_for_volunteers_in_allocation(event: Event,
                                                                           original_day: Day,
                                                                           original_volunteer_id: str,
                                                                           day_to_swap_with: Day,
                                                                           volunteer_id_to_swap_with: str):
    volunteers_in_role_at_event = load_volunteers_in_role_at_event(event)
    volunteers_in_role_at_event.swap_roles_for_volunteers_in_allocation(
            original_volunteer_id=original_volunteer_id,
        original_day=original_day,
        day_to_swap_with=day_to_swap_with,
        volunteer_id_to_swap_with=volunteer_id_to_swap_with
    )
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=volunteers_in_role_at_event)

def swap_and_groups_for_volunteers_in_allocation(event: Event,
                                                                           original_day: Day,
                                                                           original_volunteer_id: str,
                                                                           day_to_swap_with: Day,
                                                                           volunteer_id_to_swap_with: str):
    volunteers_in_role_at_event = load_volunteers_in_role_at_event(event)
    volunteers_in_role_at_event.swap_roles_and_groups_for_volunteers_in_allocation(
            original_volunteer_id=original_volunteer_id,
        original_day=original_day,
        day_to_swap_with=day_to_swap_with,
        volunteer_id_to_swap_with=volunteer_id_to_swap_with
    )
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=volunteers_in_role_at_event)


def get_sorted_and_filtered_list_of_volunteers_at_event(
        data_to_be_stored: DataToBeStoredWhilstConstructingTableBody,
        sorts_and_filters: RotaSortsAndFilters,
    ):

    list_of_volunteers_at_event = data_to_be_stored.filtered_list_of_volunteers_at_event(sorts_and_filters)

    if sorts_and_filters.sort_by_volunteer_name is not arg_not_passed:
        list_of_volunteers_at_event = sort_volunteer_data_for_event_by_name_sort_order(
            list_of_volunteers_at_event, sort_order=sorts_and_filters.sort_by_volunteer_name)
    elif sorts_and_filters.sort_by_day is not arg_not_passed:
        print("SORTBY %s" % sorts_and_filters.sort_by_day.name)
        list_of_volunteers_at_event = sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event, sort_by_day=sorts_and_filters.sort_by_day,
            data_to_be_stored=data_to_be_stored)

    return list_of_volunteers_at_event
