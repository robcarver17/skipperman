from typing import Dict

from app.backend.groups.previous_groups import \
    most_common_allocation_for_cadet_in_previous_events as most_popular_allocation_for_cadet_in_previous_events
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import Cadet
from app.objects.events import Event
from app.objects.groups import Group, unallocated_group
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.OLD_backend.group_allocations.cadet_event_allocations import (
    DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only,
)
from app.OLD_backend.events import (
    DEPRECATE_get_sorted_list_of_events,
)


def DEPRECATE_get_dict_of_allocations_for_events_and_list_of_cadets(
    interface: abstractInterface, list_of_events: list
) -> Dict[Event, ListOfCadetIdsWithGroups]:
    allocations_as_dict = dict(
        [
            (
                event,
                DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only(
                    interface=interface, event=event
                ),
            )
            for event in list_of_events
        ]
    )

    return allocations_as_dict


def DEPRECATE_get_dict_of_all_event_allocations_for_single_cadet(
    interface: abstractInterface, cadet: Cadet, remove_unallocated: bool = False
) -> Dict[Event, Group]:
    list_of_events = DEPRECATE_get_sorted_list_of_events(interface)
    previous_allocations_as_dict = (
        DEPRECATE_get_dict_of_allocations_for_events_and_list_of_cadets(
            interface=interface, list_of_events=list_of_events
        )
    )
    list_of_previous_groups = most_popular_allocation_for_cadet_in_previous_events(
        cadet=cadet, previous_allocations_as_dict=previous_allocations_as_dict
    )

    dict_of_previous = dict(
        [
            (event, group)
            for event, group in zip(list_of_events, list_of_previous_groups)
        ]
    )

    if remove_unallocated:
        dict_of_previous = dict(
            [
                (event, group)
                for event, group in dict_of_previous.items()
                if group is not unallocated_group
            ]
        )

    return dict_of_previous
