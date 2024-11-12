from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer

from app.objects.groups import unallocated_group

from app.data_access.store.object_store import ObjectStore
from app.backend.volunteers.roles_and_teams import get_list_of_roles
from app.backend.groups.list_of_groups import get_list_of_groups
from app.objects.composed.volunteer_roles import no_role_set

MAKE_UNAVAILABLE = "* UNAVAILABLE *"
NO_ROLE_SET = "No role allocated"

def get_dict_of_roles_for_dropdown(object_store: ObjectStore):
    volunteer_roles = get_list_of_roles(object_store)
    dict_of_roles = {role.name: role.name for role in volunteer_roles}
    dict_of_roles[no_role_set.name] = no_role_set.name
    dict_of_roles[MAKE_UNAVAILABLE] = MAKE_UNAVAILABLE

    return dict_of_roles

def get_dict_of_groups_for_dropdown(object_store: ObjectStore):
    groups = get_list_of_groups(object_store)
    dict_of_groups = {group.name: group.name for group in groups}
    dict_of_groups[unallocated_group.name] = unallocated_group.name

    # return dict_of_groups
    return {}


def all_roles_match_across_event(
    volunteer_data_at_event: AllEventDataForVolunteer
) -> bool:
    all_volunteers_in_roles_at_event_including_no_role_set = [volunteer_data_at_event.roles_and_groups.role_and_group_on_day(day)
                                                    for day in volunteer_data_at_event.event.weekdays_in_event()]

    if len(all_volunteers_in_roles_at_event_including_no_role_set) == 0:
        return False

    all_roles = [
        volunteer_in_role_at_event_on_day.role
        for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event_including_no_role_set
    ]
    all_groups = [
        volunteer_in_role_at_event_on_day.group
        for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event_including_no_role_set
    ]

    all_groups_match = len(set(all_groups)) <= 1
    all_roles_match = len(set(all_roles)) <= 1

    return all_roles_match and all_groups_match


def volunteer_has_empty_available_days_without_role(
    volunteer_data_at_event: AllEventDataForVolunteer,
) -> bool:
    all_volunteers_in_roles_at_event_including_no_role_set = [volunteer_data_at_event.roles_and_groups.role_and_group_on_day(day)
                                                    for day in volunteer_data_at_event.event.weekdays_in_event()]
    unallocated_roles = [
        volunteer_role_and_group.role
        for volunteer_role_and_group in all_volunteers_in_roles_at_event_including_no_role_set
        if volunteer_role_and_group.role.is_no_role_set()
    ]

    return len(unallocated_roles) > 0


def volunteer_has_at_least_one_day_in_role_and_all_roles_and_groups_match(
    volunteer_data_at_event: AllEventDataForVolunteer,

) -> bool:
    all_volunteers_in_roles_at_event_including_no_role_set = [volunteer_data_at_event.roles_and_groups.role_and_group_on_day(day)
                                                    for day in volunteer_data_at_event.event.weekdays_in_event()]

    allocated_roles = [
        volunteer_role_and_group.role
        for volunteer_role_and_group in all_volunteers_in_roles_at_event_including_no_role_set
        if not volunteer_role_and_group.role.is_no_role_set()
    ]

    if len(allocated_roles) == 0:
        return False

    unique_allocated_roles = set(allocated_roles)
    all_match = len(unique_allocated_roles)==1

    return all_match
