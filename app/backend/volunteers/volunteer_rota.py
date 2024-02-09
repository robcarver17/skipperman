from typing import List

from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingTableBody
from app.backend.data.volunteers import get_sorted_list_of_volunteers
from app.objects.constants import missing_data
from app.objects.groups import Group, ALL_GROUPS_NAMES, GROUP_UNALLOCATED_TEXT
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfVolunteersAtEvent
from app.objects.volunteers import Volunteer
from app.objects.volunteers_in_roles import VOLUNTEER_ROLES, \
    NO_ROLE_SET

from app.objects.day_selectors import Day


def sort_volunteer_data_for_event_by_name_sort_order(volunteers_at_event: ListOfVolunteersAtEvent, sort_order) -> ListOfVolunteersAtEvent:
    list_of_volunteers = get_sorted_list_of_volunteers(sort_by=sort_order)
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



