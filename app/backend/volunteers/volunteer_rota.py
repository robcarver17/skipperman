from dataclasses import dataclass
from typing import List

from app.backend.volunteers.volunteers import get_volunteer_name_from_id

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.volunteer_rota import VolunteerRotaData, \
    get_volunteer_roles, update_role_at_event_for_volunteer_on_day
from app.data_access.configuration.configuration import VOLUNTEER_ROLES
from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingVolunteerRotaPage,  RotaSortsAndFilters

from app.backend.data.volunteers import DEPRECATED_get_sorted_list_of_volunteers
from app.objects.constants import missing_data, arg_not_passed
from app.objects.events import Event
from app.objects.groups import Group, ALL_GROUPS_NAMES, GROUP_UNALLOCATED_TEXT, sorted_locations
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfVolunteersAtEvent
from app.objects.volunteers import Volunteer
from app.objects.volunteers_in_roles import NO_ROLE_SET, VolunteerInRoleAtEvent

from app.objects.day_selectors import Day


@dataclass
class SwapData:
    event: Event
    original_day: Day
    day_to_swap_with: Day
    swap_boats: bool
    swap_roles: bool
    volunteer_id_to_swap_with: str
    original_volunteer_id: str

def update_role_at_event_for_volunteer_on_day_at_event(interface: abstractInterface,
                                                       event: Event,
                                                       day: Day,
                                                       volunteer_id: str,
                                                       new_role: str):

    volunteer_in_role_at_event_on_day =  VolunteerInRoleAtEvent(day=day, volunteer_id=volunteer_id)
    update_role_at_event_for_volunteer_on_day(interface=interface, event=event, volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                              new_role=new_role)


def get_volunteer_role_at_event_on_day(interface: abstractInterface, event: Event, volunteer_id: str, day: Day) -> str:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteer_role_at_event_on_day(event=event, volunteer_id=volunteer_id, day=day)

def get_volunteer_with_role_at_event_on_day(interface: abstractInterface, event: Event, volunteer_id: str, day: Day) -> VolunteerInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteer_with_role_at_event_on_day(event=event, volunteer_id=volunteer_id, day=day)





def sort_volunteer_data_for_event_by_name_sort_order(volunteers_at_event: ListOfVolunteersAtEvent, sort_order) -> ListOfVolunteersAtEvent:
    list_of_volunteers = DEPRECATED_get_sorted_list_of_volunteers(sort_by=sort_order)
    ## this works because if an ID is missing we just ignore it
    return volunteers_at_event.sort_by_list_of_volunteer_ids(list_of_volunteers.list_of_ids)

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
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    if len(list_of_cadet_ids)==0:
        return "No associated cadets"
    list_of_groups = [data_to_be_stored.group_given_cadet_id(cadet_id) for cadet_id in list_of_cadet_ids]
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

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

def dict_of_groups_for_dropdown(interface: abstractInterface): ## Future proof to when groups come from files
    dict_of_groups = {group:group for group in ALL_GROUPS_NAMES}
    dict_of_groups[GROUP_UNALLOCATED_TEXT]= GROUP_UNALLOCATED_TEXT

    return dict_of_groups

MAKE_UNAVAILABLE = "* UNAVAILABLE *"
def dict_of_roles_for_dropdown(interface: abstractInterface):
    volunteer_roles = get_volunteer_roles(interface)
    dict_of_roles = {role:role for role in volunteer_roles}
    dict_of_roles[NO_ROLE_SET] = NO_ROLE_SET
    dict_of_roles[MAKE_UNAVAILABLE] = MAKE_UNAVAILABLE

    return dict_of_roles

def DEPRECATE_dict_of_roles_for_dropdown():
    volunteer_roles = VOLUNTEER_ROLES
    dict_of_roles = {role:role for role in volunteer_roles}
    dict_of_roles[NO_ROLE_SET] = NO_ROLE_SET
    dict_of_roles[MAKE_UNAVAILABLE] = MAKE_UNAVAILABLE

    return dict_of_roles


def boat_related_role_str_on_day_for_volunteer_id(interface: abstractInterface, day: Day, event: Event, volunteer_id: str)-> str:
    volunteer_rota = VolunteerRotaData(interface.data)
    volunteer_on_day = volunteer_rota.get_volunteer_with_role_at_event_on_day(event=event, day=day, volunteer_id=volunteer_id)
    if volunteer_on_day is missing_data:
        return ""
    elif volunteer_on_day.requires_boat:
        return volunteer_on_day.role
    else:
        return ""


def is_possible_to_copy_roles_for_non_grouped_roles_only(interface: abstractInterface, event: Event, volunteer_id:str) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    all_volunteer_positions = get_list_of_volunteer_with_role_across_days_for_volunteer_at_event(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id
    )

    all_roles = [volunteer_with_role.role for volunteer_with_role in all_volunteer_positions]

    no_roles_to_copy = len(all_roles)==0
    all_roles_match = len(set(all_roles))<=1

    roles_require_groups = [volunteer_with_role.requires_group for volunteer_with_role in all_volunteer_positions]
    at_least_one_role_require_group = any(roles_require_groups)

    ## copy not possible if all roles the same, or at least one requires a group, or nothing to copy
    if all_roles_match or at_least_one_role_require_group or no_roles_to_copy:
        return False
    else:
        return True


def get_list_of_volunteer_with_role_across_days_for_volunteer_at_event(interface: abstractInterface, event: Event, volunteer_id:str) ->\
    List[VolunteerInRoleAtEvent]:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteers_with_roles_in_event_including_missing_data = [get_volunteer_with_role_at_event_on_day(interface=interface,
                                                                                                     volunteer_id=volunteer_id,
                                                                                                    day=day, event=event)
                                                             for day in event.weekdays_in_event()]

    all_volunteer_positions = [volunteer_with_role for volunteer_with_role in volunteers_with_roles_in_event_including_missing_data
                               if volunteer_with_role is not missing_data]

    return all_volunteer_positions

def is_possible_to_swap_roles_on_one_day_for_non_grouped_roles_only(interface: abstractInterface,
                                                                    event: Event,
                                                                    volunteer_id:str,
                                                                    day: Day) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteer_with_role = get_volunteer_with_role_at_event_on_day(interface=interface,
                                                                  volunteer_id=volunteer_id,
                                                                            day=day, event=event)
    role_requires_group = volunteer_with_role.requires_group
    possible_to_swap = not role_requires_group

    return possible_to_swap




def swap_roles_for_volunteers_in_allocation(interface: abstractInterface,
                                            swap_data: SwapData):

    volunteer_rota_data = VolunteerRotaData(interface.data)
    try:
        volunteer_rota_data.swap_roles_for_volunteers_in_allocation(
            event=swap_data.event,
            original_volunteer_id=swap_data.original_volunteer_id,
            volunteer_id_to_swap_with=swap_data.volunteer_id_to_swap_with,
            day_to_swap_with=swap_data.day_to_swap_with,
            original_day=swap_data.original_day
        )
    except Exception as e:
        first_name = get_volunteer_name_from_id(interface=interface, volunteer_id=swap_data.original_volunteer_id)
        second_name = get_volunteer_name_from_id(interface=interface, volunteer_id=swap_data.volunteer_id_to_swap_with)
        interface.log_error("Swap roles of %s and %s failed on day %s, error %s" % (first_name, second_name, swap_data.day_to_swap_with.name, str(e)))

def swap_and_groups_for_volunteers_in_allocation(interface:abstractInterface,
                                                                            event: Event,
                                                                           original_day: Day,
                                                                           original_volunteer_id: str,
                                                                           day_to_swap_with: Day,
                                                                           volunteer_id_to_swap_with: str):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.swap_and_groups_for_volunteers_in_allocation(event=event,
                                                                     original_day=original_day,
                                                                     day_to_swap_with=day_to_swap_with,
                                                                     original_volunteer_id=original_volunteer_id,
                                                                     volunteer_id_to_swap_with=volunteer_id_to_swap_with)



def get_sorted_and_filtered_list_of_volunteers_at_event(
        data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
        sorts_and_filters: RotaSortsAndFilters,
    ) -> ListOfVolunteersAtEvent:

    list_of_volunteers_at_event = data_to_be_stored.filtered_list_of_volunteers_at_event(sorts_and_filters)
    sorted_list_of_volunteers_at_event = sort_list_of_volunteers_at_event(
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        data_to_be_stored=data_to_be_stored,
        sorts_and_filters=sorts_and_filters
    )

    return sorted_list_of_volunteers_at_event

def sort_list_of_volunteers_at_event(list_of_volunteers_at_event: ListOfVolunteersAtEvent,
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
            list_of_volunteers_at_event, sort_order=sort_by_volunteer_name)

    sort_by_day = sorts_and_filters.sort_by_day
    if sort_by_day is not arg_not_passed:
        return sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event, sort_by_day=sorts_and_filters.sort_by_day,
            data_to_be_stored=data_to_be_stored)

    return list_of_volunteers_at_event



def sort_volunteer_data_for_event_by_location(list_of_volunteers_at_event: ListOfVolunteersAtEvent,
                                              data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage)-> ListOfVolunteersAtEvent:

    list_of_locations = [get_cadet_location_string(data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event)
                    for volunteer_at_event in list_of_volunteers_at_event]

    locations_and_volunteers = zip(list_of_locations, list_of_volunteers_at_event)

    sorted_by_location = sorted(locations_and_volunteers, key=lambda tup: tup[0])
    sorted_list_of_volunteers = ListOfVolunteersAtEvent([location_and_volunteer[1] for location_and_volunteer in sorted_by_location])

    return sorted_list_of_volunteers


