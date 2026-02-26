from typing import List, Dict

from app.backend.cadets.list_of_cadets import get_list_of_cadets
from app.backend.events.list_of_events import (
    get_list_of_last_N_events,
    ALL_EVENTS,
    get_list_of_events,
)
from app.backend.groups.cadets_with_groups_at_event import (
    get_group_allocations_for_event_active_cadets_only,
)

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.composed.cadets_at_event_with_groups import (
    DictOfEventAllocations,
    DictOfCadetsWithDaysAndGroupsAtEvent,
)
from app.objects.composed.dict_of_previous_cadet_groups import (
    DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds,
)
from app.objects.events import Event, ListOfEvents
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.groups import Group, missing_group_display_only


## EXTERNAL
def get_list_of_previous_groups_as_str(
    object_store: ObjectStore,
    event_to_exclude: Event,
    cadet: Cadet,
) -> List[str]:
    dict_of_groups = get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
        object_store=object_store,
        excluding_event=event_to_exclude,
        cadet=cadet,
        only_events_before_excluded_event=False,
    )
    dict_of_groups = dict(
        [
            (key, value)
            for key, value in dict_of_groups.items()
            if not value.is_unallocated
        ]
    )
    list_of_groups_as_str = [
        "%s: %s" % (str(event), group.name) for event, group in dict_of_groups.items()
    ]

    return list_of_groups_as_str


## external
def get_dict_of_most_common_group_names_at_event_for_single_cadet(
    object_store: ObjectStore,
    cadet: Cadet,
) -> Dict[Event, str]:
    dict_of_events_and_groups = object_store.get(
        object_store.data_api.data_list_of_cadets_with_groups.get_dict_of_most_common_group_allocations_for_single_cadet,
        cadet_id=cadet.id,
    )

    return dict(
        [(event, group.name) for event, group in dict_of_events_and_groups.items()]
    )


## external
def get_dict_of_event_allocations_given_list_of_events_from_persistent_data(
    object_store: ObjectStore,
    list_of_cadets: ListOfCadets,
    list_of_events: ListOfEvents,
) -> DictOfEventAllocations:
    dict_of_all_group_names_for_events = (
        get_dict_of_group_names_for_events_and_cadets_persistent_version(object_store)
    )
    raw_dict = dict(
        [
            (
                cadet,
                get_dict_of_event_allocations_for_single_cadet_given_list_of_events_from_persistent_data(
                    dict_of_all_group_names_for_events=dict_of_all_group_names_for_events,
                    cadet=cadet,
                    list_of_events=list_of_events,
                ),
            )
            for cadet in list_of_cadets
        ]
    )

    return DictOfEventAllocations(raw_dict, list_of_events=list_of_events)


def get_dict_of_event_allocations_for_single_cadet_given_list_of_events_from_persistent_data(
    cadet: Cadet,
    dict_of_all_group_names_for_events: DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds,
    list_of_events: ListOfEvents,
) -> Dict[Event, str]:
    group_names_in_dict_for_cadet = (
        dict_of_all_group_names_for_events.get_dict_of_group_names_for_cadet(cadet)
    )

    dict_of_previous_groups = dict(
        [
            (event, group_names_in_dict_for_cadet.get(event, ""))
            for event in list_of_events
        ]
    )

    return dict_of_previous_groups


def get_dict_of_group_names_for_events_and_cadets_persistent_version(
    object_store: ObjectStore,
) -> DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds:
    return object_store.get(
        object_store.data_api.data_list_of_group_names_for_events_and_cadets_persistent_version.get_dict_of_group_names_for_events_and_cadets_persistent_version
    )


## external
def delete_persistent_version_of_previous_groups_for_cadet(
    interface: abstractInterface, cadet: Cadet
):
    interface.update(
        interface.object_store.data_api.data_list_of_group_names_for_events_and_cadets_persistent_version.delete_persistent_version_of_previous_groups_for_cadet,
        cadet_id=cadet.id,
    )


def update_dict_of_group_names_for_events_and_cadets_persistent_version(
    interface: abstractInterface,
    dict_of_group_names_for_events_and_cadets: DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds,
):
    interface.update(
        interface.object_store.data_api.data_list_of_group_names_for_events_and_cadets_persistent_version.update_dict_of_group_names_for_events_and_cadets_persistent_version,
        dict_of_group_names_for_events_and_cadets=dict_of_group_names_for_events_and_cadets,
    )


def get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
    object_store: ObjectStore,
    cadet: Cadet,
    N_events: int = ALL_EVENTS,
    excluding_event: Event = arg_not_passed,
    remove_unallocated: bool = False,
    only_events_before_excluded_event: bool = True,
) -> Dict[Event, Group]:
    list_of_events = get_list_of_last_N_events(
        object_store=object_store,
        N_events=N_events,
        excluding_event=excluding_event,
        only_events_before_excluded_event=only_events_before_excluded_event,
    )
    dict_of_previous_groups = (
        get_dict_of_event_allocations_for_single_cadet_given_list_of_events(
            object_store=object_store,
            cadet=cadet,
            list_of_events=list_of_events,
            remove_unallocated=remove_unallocated,
        )
    )

    return dict_of_previous_groups


## external
def update_dict_of_group_names_for_events_and_cadets_persistent_version_from_core_data(
    interface: abstractInterface,
):
    object_store = interface.object_store

    dict_of_group_names_for_events_and_cadets_persistent_version = (
        get_dict_of_group_names_for_events_and_cadets_persistent_version(object_store)
    )
    list_of_cadets = get_list_of_cadets(object_store)
    list_of_events = get_list_of_events(object_store)

    for cadet in list_of_cadets:
        dict_of_event_allocations_for_single_cadet_given_list_of_events = (
            get_dict_of_event_allocations_for_single_cadet_given_list_of_events(
                object_store=object_store,
                cadet=cadet,
                list_of_events=list_of_events,
                pad=True,
                remove_unallocated=False,
            )
        )
        dict_of_events_and_group_names = dict(
            [
                (event, group.name)
                for event, group in dict_of_event_allocations_for_single_cadet_given_list_of_events.items()
            ]
        )

        dict_of_group_names_for_events_and_cadets_persistent_version.update_most_group_names_across_events_for_cadet(
            cadet=cadet, dict_of_group_names_by_event=dict_of_events_and_group_names
        )

    update_dict_of_group_names_for_events_and_cadets_persistent_version(
        dict_of_group_names_for_events_and_cadets=dict_of_group_names_for_events_and_cadets_persistent_version,
        interface=interface,
    )


def get_dict_of_event_allocations_for_single_cadet_given_list_of_events(
    object_store: ObjectStore,
    cadet: Cadet,
    list_of_events: ListOfEvents,
    remove_unallocated: bool = False,
    pad: bool = False,
) -> Dict[Event, Group]:
    previous_allocations_as_dict = (
        get_dict_of_group_allocations_for_list_of_events_active_cadets_only(
            object_store=object_store, list_of_events=list_of_events
        )
    )
    dict_of_previous_groups = get_most_common_allocation_for_cadet_in_previous_events(
        cadet=cadet, previous_allocations_as_dict=previous_allocations_as_dict, pad=pad
    )

    if (not pad) & remove_unallocated:
        dict_of_previous_groups = dict(
            [
                (event, group)
                for event, group in dict_of_previous_groups.items()
                if not group.is_unallocated
            ]
        )

    return dict_of_previous_groups


def get_most_common_allocation_for_cadet_in_previous_events(
    cadet: Cadet,
    previous_allocations_as_dict: Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent],
    pad: bool = False,
) -> Dict[Event, Group]:
    dict_of_allocations = dict(
        [
            (
                event,
                dict_of_allocations_for_event.get_most_common_group_for_cadet(
                    cadet, default_group=missing_group_display_only
                ),
            )
            for event, dict_of_allocations_for_event in previous_allocations_as_dict.items()
        ]
    )

    if not pad:
        dict_of_allocations = dict(
            [
                (event, allocation)
                for event, allocation in dict_of_allocations.items()
                if allocation is not missing_group_display_only
            ]
        )

    return dict_of_allocations


## external
def get_dict_of_group_allocations_for_all_events_active_cadets_only(
    object_store: ObjectStore,
) -> Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent]:
    list_of_events = get_list_of_events(object_store)
    list_of_events = list_of_events.sort_by_start_date_asc()

    return get_dict_of_group_allocations_for_list_of_events_active_cadets_only(
        object_store=object_store, list_of_events=list_of_events
    )


def get_dict_of_group_allocations_for_list_of_events_active_cadets_only(
    object_store: ObjectStore, list_of_events: list
) -> Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent]:
    allocations_as_dict = dict(
        [
            (
                event,
                get_group_allocations_for_event_active_cadets_only(
                    object_store=object_store, event=event
                ),
            )
            for event in list_of_events
        ]
    )

    return allocations_as_dict
