from typing import Dict, List

from app.data_access.storage_layer.api import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import Cadet
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups, Group, GROUP_UNALLOCATED
from app.backend.group_allocations.cadet_event_allocations import (
    DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only,
    load_list_of_cadets_ids_with_group_allocations_active_cadets_only,
)
from app.backend.events import (
    DEPRECATE_get_sorted_list_of_events,
    get_sorted_list_of_events,
    get_list_of_all_events,
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
    list_of_previous_groups = allocation_for_cadet_in_previous_events(
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
                if group is not GROUP_UNALLOCATED
            ]
        )

    return dict_of_previous


def get_dict_of_all_event_allocations_for_single_cadet(
    data_layer: DataLayer, cadet: Cadet, remove_unallocated: bool = False
) -> Dict[Event, Group]:
    unsorted_list_of_events = get_list_of_all_events(data_layer)
    list_of_events = unsorted_list_of_events.sort_by_start_date_desc()
    previous_allocations_as_dict = (
        get_dict_of_allocations_for_events_and_list_of_cadets(
            data_layer=data_layer, list_of_events=list_of_events
        )
    )
    list_of_previous_groups = allocation_for_cadet_in_previous_events(
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
                if not group.is_unallocated
            ]
        )

    return dict_of_previous


def get_dict_of_allocations_for_events_and_list_of_cadets(
    data_layer: DataLayer, list_of_events: list
) -> Dict[Event, ListOfCadetIdsWithGroups]:
    allocations_as_dict = dict(
        [
            (
                event,
                load_list_of_cadets_ids_with_group_allocations_active_cadets_only(
                    data_layer=data_layer, event=event
                ),
            )
            for event in list_of_events
        ]
    )

    return allocations_as_dict


def allocation_for_cadet_in_previous_events(
    cadet: Cadet, previous_allocations_as_dict: Dict[Event, ListOfCadetIdsWithGroups]
) -> List[Group]:
    list_of_events = list(previous_allocations_as_dict.keys())
    allocations = [
        group_for_cadet_and_event(
            cadet=cadet,
            event=event,
            previous_allocations_as_dict=previous_allocations_as_dict,
        )
        for event in list_of_events
    ]

    return allocations


def allocation_for_cadet_in_previous_events_as_dict(
    previous_allocations_as_dict: Dict[Event, ListOfCadetIdsWithGroups],
    cadet: Cadet,
    number_of_events: int = 3,
) -> Dict[Event, Group]:
    list_of_events = list(previous_allocations_as_dict.keys())
    list_of_events = list_of_events[-number_of_events:]
    allocations = dict(
        [
            (
                event,
                group_for_cadet_and_event(
                    cadet=cadet,
                    event=event,
                    previous_allocations_as_dict=previous_allocations_as_dict,
                ),
            )
            for event in list_of_events
        ]
    )

    return allocations


def group_for_cadet_and_event(
    cadet: Cadet,
    event: Event,
    previous_allocations_as_dict: Dict[Event, ListOfCadetIdsWithGroups],
) -> Group:
    cadet_id = cadet.id
    allocations_for_event = previous_allocations_as_dict[event]
    try:
        group = allocations_for_event.item_with_cadet_id(cadet_id).group
    except:
        group = Group.create_unallocated()

    return group
