from typing import Dict

from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers
)

from app.backend.events.list_of_events import get_sorted_list_of_events

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
)
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    RoleAndGroupAndTeam, )

from app.objects.events import (
    Event,
    SORT_BY_START_DSC,
    list_of_events_excluding_one_event,
    ListOfEvents, )
from app.objects.exceptions import arg_not_passed
from app.objects.volunteers import Volunteer

ALL_EVENTS = 999999999999


def get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(
    object_store: ObjectStore,
    volunteer: Volunteer,
    avoid_event: Event = arg_not_passed,
    N_events=ALL_EVENTS,
) -> Dict[Event, RoleAndGroupAndTeam]:
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
) -> Dict[Event, RoleAndGroupAndTeam]:
    list_of_events = get_sorted_list_of_events(
        object_store=object_store, sort_by=sort_by
    )
    if avoid_event is arg_not_passed:
        pass  ## can't exclude so do everything
    else:
        list_of_events = list_of_events_excluding_one_event(
            list_of_events=list_of_events,
            event_to_exclude=avoid_event,
            sort_by=sort_by,
            only_past=True,
        )

    return get_all_roles_for_list_of_events_for_volunteer_as_dict(
        object_store=object_store, volunteer=volunteer, list_of_events=list_of_events
    )


def get_all_roles_for_list_of_events_for_volunteer_as_dict(
    object_store: ObjectStore, volunteer: Volunteer, list_of_events: ListOfEvents
) -> Dict[Event, RoleAndGroupAndTeam]:
    list_of_roles_and_groups = [
        get_role_and_group_for_event_and_volunteer(
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

    return roles_dict


def get_role_and_group_for_event_and_volunteer(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
) -> RoleAndGroupAndTeam:
    dict_of_all_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    dict_of_roles_and_groups = (
        dict_of_all_event_data.dict_of_volunteers_at_event_with_days_and_role
    )
    roles_and_groups_for_volunteer = (
        dict_of_roles_and_groups.days_and_roles_for_volunteer(volunteer)
    )

    role_and_group = roles_and_groups_for_volunteer.most_common_role_and_groups()

    return role_and_group


def get_dict_of_volunteers_with_roles_and_groups_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
    return object_store.get(
        object_definition=object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
        event_id=event.id,
    )


def update_dict_of_volunteers_with_roles_and_groups_at_event(
    object_store: ObjectStore,
    dict_of_volunteers_with_roles_and_groups_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
):
    return object_store.update(
        object_definition=object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
        event_id=dict_of_volunteers_with_roles_and_groups_at_event.event.id,
        new_object=dict_of_volunteers_with_roles_and_groups_at_event,
    )


def is_volunteer_senior_instructor_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
):
    dict_of_all_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    volunteer_days_and_roles = dict_of_all_event_data.dict_of_volunteers_at_event_with_days_and_role.days_and_roles_for_volunteer(
        volunteer
    )
    return volunteer_days_and_roles.contains_si()


def get_last_role_or_none_for_volunteer_at_previous_events(object_store: ObjectStore, volunteer: Volunteer, avoid_event: Event):
    previous_roles = get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(object_store=object_store,
                                                                                          volunteer=volunteer,
                                                                                          avoid_event=avoid_event
                                                                                          )
    if len(previous_roles)==0:
        return None

    previous_role = list(previous_roles.values())[0] ## latest first

    return previous_role
