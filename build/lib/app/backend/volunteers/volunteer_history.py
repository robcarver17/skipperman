from typing import List, Dict

from app.OLD_backend.events import get_sorted_list_of_events
from app.OLD_backend.rota.volunteer_rota import get_volunteers_in_role_at_event_with_active_allocations
from app.OLD_backend.volunteers.volunteers import DEPRECATE_get_volunteer_from_id
from app.data_access.store.data_layer import DataLayer
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.exceptions import arg_not_passed
from app.objects.events import Event, SORT_BY_START_ASC, list_of_events_excluding_one_event, ListOfEvents
from app.objects.volunteers import Volunteer
from app.objects_OLD.volunteers_at_event import ListOfVolunteersAtEvent
from app.objects_OLD.primtive_with_id.volunteer_roles_and_groups import RoleAndGroup


def DEPRECATE_get_dict_of_volunteers_with_last_roles(
    interface: abstractInterface, list_of_volunteer_ids: List[str], avoid_event: Event
) -> Dict[str, RoleAndGroup]:
    return dict(
        [
            (
                volunteer_id,
                DEPRECATE_get_last_role_for_volunteer_id(
                    interface=interface,
                    volunteer_id=volunteer_id,
                    avoid_event=avoid_event,
                ),
            )
            for volunteer_id in list_of_volunteer_ids
        ]
    )


def get_dict_of_volunteers_with_last_roles(
    data_layer: DataLayer,
    list_of_volunteers_at_event: ListOfVolunteersAtEvent,
    avoid_event: Event,
) -> Dict[str, RoleAndGroup]:
    return dict(
        [
            (
                volunteer_at_event.volunteer.id,
                get_last_role_for_volunteer_id(
                    data_layer=data_layer,
                    volunteer=volunteer_at_event.volunteer,
                    avoid_event=avoid_event,
                ),
            )
            for volunteer_at_event in list_of_volunteers_at_event
        ]
    )


def DEPRECATE_get_last_role_for_volunteer_id(
    interface: abstractInterface, volunteer_id: str, avoid_event: Event = arg_not_passed
) -> RoleAndGroup:
    volunteer = DEPRECATE_get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)
    roles = get_all_roles_across_recent_events_for_volunteer_id_as_list(
        data_layer=interface.data,
        volunteer=volunteer,
        avoid_event=avoid_event,
        sort_by=SORT_BY_START_ASC,
    )
    if len(roles) == 0:
        return RoleAndGroup()

    return roles[-1]  ## most recent role


def get_last_role_for_volunteer_id(
    data_layer: DataLayer, volunteer: Volunteer, avoid_event: Event = arg_not_passed
) -> RoleAndGroup:
    roles = get_all_roles_across_recent_events_for_volunteer_id_as_list(
        data_layer=data_layer,
        volunteer=volunteer,
        avoid_event=avoid_event,
        sort_by=SORT_BY_START_ASC,
    )
    if len(roles) == 0:
        return RoleAndGroup()

    return roles[-1]  ## most recent role


def get_all_roles_across_recent_events_for_volunteer_id_as_list(
    data_layer: DataLayer,
    volunteer: Volunteer,
    sort_by=SORT_BY_START_ASC,
    avoid_event: Event = arg_not_passed,
) -> List[RoleAndGroup]:
    roles_as_dict = get_all_roles_across_recent_events_for_volunteer_as_dict(
        data_layer=data_layer,
        volunteer=volunteer,
        sort_by=sort_by,
        avoid_event=avoid_event,
    )
    return list(roles_as_dict.values())


def get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(
    data_layer: DataLayer,
    volunteer: Volunteer,
    sort_by=SORT_BY_START_ASC,
    avoid_event: Event = arg_not_passed,
) -> Dict[Event, RoleAndGroup]:

    pass


def get_all_roles_across_recent_events_for_volunteer_as_dict(
    data_layer: DataLayer,
    volunteer: Volunteer,
    sort_by=SORT_BY_START_ASC,
    avoid_event: Event = arg_not_passed,
) -> Dict[Event, RoleAndGroup]:
    list_of_events = get_sorted_list_of_events(data_layer=data_layer, sort_by=sort_by)
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
        data_layer=data_layer, volunteer=volunteer, list_of_events=list_of_events
    )


def get_all_roles_for_list_of_events_for_volunteer_as_dict(
    data_layer: DataLayer, volunteer: Volunteer, list_of_events: ListOfEvents
) -> Dict[Event, RoleAndGroup]:
    list_of_roles_and_groups = [
        get_role_and_group_for_event_and_volunteer(
            data_layer=data_layer, event=event, volunteer=volunteer
        )
        for event in list_of_events
    ]
    roles_dict = dict(
        [
            (event, role_and_group)
            for event, role_and_group in zip(list_of_events, list_of_roles_and_groups)
            if not role_and_group.missing
        ]
    )

    return roles_dict


def get_role_and_group_for_event_and_volunteer(
    data_layer: DataLayer, volunteer: Volunteer, event: Event
) -> RoleAndGroup:
    volunteer_data = get_volunteers_in_role_at_event_with_active_allocations(
        data_layer=data_layer, event=event
    )
    role_and_group = volunteer_data.most_common_role_and_group_at_event_for_volunteer(
        volunteer=volunteer
    )

    return role_and_group
