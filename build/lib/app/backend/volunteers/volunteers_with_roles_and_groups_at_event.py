from typing import Dict

from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)

from app.backend.events.list_of_events import get_sorted_list_of_events

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
)
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    RoleAndGroupAndTeam,
    RoleAndGroup, DictOfDaysRolesAndGroups,
)
from app.objects.day_selectors import Day

from app.objects.events import (
    Event,
    SORT_BY_START_DSC,
    list_of_events_excluding_one_event_and_past_events,
    ListOfEvents,
)
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.utils import most_common
from app.objects.volunteers import Volunteer

ALL_EVENTS = 999999999999


def get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(
    object_store: ObjectStore,
    volunteer: Volunteer,
    avoid_event: Event = arg_not_passed,
    N_events=ALL_EVENTS,
) -> Dict[Event, RoleAndGroup]:
    return get_all_roles_across_recent_events_for_volunteer_as_dict_with_sort_order(
        object_store=object_store,
        volunteer=volunteer,
        avoid_event=avoid_event,
        sort_by=SORT_BY_START_DSC,
        N_events=N_events,
    )


def get_all_roles_across_recent_events_for_volunteer_as_dict_with_sort_order(
    object_store: ObjectStore,
    volunteer: Volunteer,
    sort_by=SORT_BY_START_DSC,
    avoid_event: Event = arg_not_passed,
    N_events=ALL_EVENTS,
) -> Dict[Event, RoleAndGroup]:
    list_of_events = get_sorted_list_of_events(
        object_store=object_store, sort_by=sort_by
    )
    list_of_events = list_of_events_excluding_one_event_and_past_events(
        list_of_events=list_of_events, event_to_exclude=avoid_event, sort_by=sort_by
    )

    return get_all_roles_for_list_of_events_for_volunteer_as_dict(
        object_store=object_store,
        volunteer=volunteer,
        list_of_events=list_of_events,
        N_events=N_events,
    )


def get_all_roles_for_list_of_events_for_volunteer_as_dict(
    object_store: ObjectStore,
    volunteer: Volunteer,
    list_of_events: ListOfEvents,
    N_events=ALL_EVENTS,
) -> Dict[Event, RoleAndGroup]:
    list_of_roles_and_groups = [
        get_most_common_role_and_group_for_event_and_volunteer(
            object_store=object_store, event=event, volunteer=volunteer
        )
        for event in list_of_events
    ]
    roles_dict = dict(
        [
            (event, role_and_group)
            for event, role_and_group in zip(list_of_events, list_of_roles_and_groups)
            if not role_and_group.is_unallocated
        ]
    )
    if len(roles_dict) > N_events:
        roles_dict_keys = list(roles_dict.keys())
        roles_dict_keys_subset = roles_dict_keys[:N_events]
        roles_dict = dict(
            (event, roles_dict[event]) for event in roles_dict_keys_subset
        )

    return roles_dict


def get_role_and_group_on_day_for_event_and_volunteer(
    object_store: ObjectStore, volunteer: Volunteer, event: Event, day: Day
) -> RoleAndGroup:
    roles_and_groups_for_volunteer = get_role_and_groups_for_event_and_volunteer(object_store=object_store,event=event, volunteer=volunteer)

    return roles_and_groups_for_volunteer.role_and_group_on_day(day)



def get_most_common_role_and_group_for_event_and_volunteer(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
) -> RoleAndGroup:

    roles_and_groups_for_volunteer = get_role_and_groups_for_event_and_volunteer(
        object_store=object_store, event=event, volunteer=volunteer
    )
    most_common_role_and_group  = roles_and_groups_for_volunteer.most_common()

    return most_common_role_and_group



def get_role_and_groups_for_event_and_volunteer(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
) ->  DictOfDaysRolesAndGroups:
    return object_store.get(object_store.data_api.data_list_of_volunteers_in_roles_at_event.get_role_and_groups_for_event_and_volunteer,
                            event_id=event.id,
                            volunteer_id=volunteer.id)





def get_dict_of_volunteers_with_roles_and_groups_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
    return object_store.get(object_store.data_api.data_list_of_volunteers_in_roles_at_event.read, event_id=event.id)


def update_dict_of_volunteers_with_roles_and_groups_at_event(
    object_store: ObjectStore,
    dict_of_volunteers_with_roles_and_groups_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
):
    return object_store.DEPRECATE_update(
        object_definition=object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
        event_id=dict_of_volunteers_with_roles_and_groups_at_event.event.id,
        new_object=dict_of_volunteers_with_roles_and_groups_at_event,
    )


def is_volunteer_senior_instructor_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
):
    roles_and_groups_for_volunteer = get_role_and_groups_for_event_and_volunteer(object_store=object_store, event=event,
                                                                                 volunteer=volunteer)
    return roles_and_groups_for_volunteer.contains_si()


