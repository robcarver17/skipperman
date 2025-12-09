from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers
from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import \
    get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroup, RoleAndGroupAndTeam
from app.objects.events import Event
from app.objects.utilities.utils import most_common
from app.objects.volunteers import Volunteer
from app.data_access.store.object_definitions import dict_of_volunteers_with_most_common_role_and_group_across_events
from app.objects.composed.volunteers_last_role_across_events import DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents

def get_most_common_role_and_group_or_none_for_volunteer_at_previous_events(
    object_store: ObjectStore, volunteer: Volunteer
) -> RoleAndGroupAndTeam:
    dict_of_volunteers = get_dict_of_volunteers_with_last_role_and_group_across_events(object_store)

    return dict_of_volunteers.get_most_common_role_and_group_for_volunteer_or_none(volunteer)

def get_dict_of_volunteers_with_last_role_and_group_across_events(
    object_store: ObjectStore
) -> DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents:
    return object_store.get(
        object_definition=dict_of_volunteers_with_most_common_role_and_group_across_events
    )


def update_dict_of_volunteers_with_last_role_and_group_across_events(
    object_store: ObjectStore,
dict_of_volunteers_with_last_role_and_group_across_events: DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents

):
    return object_store.update(
        object_definition=dict_of_volunteers_with_most_common_role_and_group_across_events,
        new_object=dict_of_volunteers_with_last_role_and_group_across_events
    )

def update_dict_of_volunteers_with_most_common_role_and_group_across_events_from_core_data(object_store: ObjectStore):
    list_of_volunteers = get_list_of_volunteers(object_store)
    dict_of_volunteers_with_most_common_role_and_group = get_dict_of_volunteers_with_last_role_and_group_across_events(object_store)
    for volunteer in list_of_volunteers:
        most_common_role_for_volunteer_at_previous_events = get_most_common_role_for_volunteer_at_previous_events(
            object_store=object_store,
            volunteer=volunteer
        )
        if (most_common_role_for_volunteer_at_previous_events is None) or most_common_role_for_volunteer_at_previous_events.is_unallocated:
            continue

        dict_of_volunteers_with_most_common_role_and_group.update_most_common_role_and_group_for_volunteer(
            role_with_skills_and_group_and_team=most_common_role_for_volunteer_at_previous_events,
            volunteer=volunteer
        )

    update_dict_of_volunteers_with_last_role_and_group_across_events(object_store=object_store, dict_of_volunteers_with_last_role_and_group_across_events=dict_of_volunteers_with_most_common_role_and_group)

def get_most_common_role_for_volunteer_at_previous_events(
    object_store: ObjectStore, volunteer: Volunteer
) -> RoleAndGroupAndTeam:
    dict_of_previous_roles = (
        get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(
            object_store=object_store, volunteer=volunteer
        )
    )
    list_of_previous_roles_groups_and_teams = list(dict_of_previous_roles.values())

    return most_common(list_of_previous_roles_groups_and_teams, default=None)