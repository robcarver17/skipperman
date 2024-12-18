from typing import List, Dict

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets
from app.backend.events.list_of_events import get_list_of_events

from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.composed.cadets_at_event_with_groups import DictOfCadetsWithDaysAndGroupsAtEvent
from app.objects.events import Event,  ListOfEvents
from app.objects.exceptions import arg_not_passed
from app.objects.groups import Group


def get_list_of_previous_groups_as_str(
    object_store: ObjectStore, event_to_exclude: Event, cadet: Cadet
) -> List[str]:
    dict_of_groups = get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
        object_store=object_store,
        excluding_event=event_to_exclude,
        cadet=cadet
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


ALL_EVENTS = 99999999999999


def get_dict_of_all_event_allocations_for_single_cadet(
    object_store: ObjectStore, cadet: Cadet, remove_unallocated: bool = False
) -> Dict[Event, Group]:
    return get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
        object_store=object_store,
        cadet=cadet,
        N_events=ALL_EVENTS,
        remove_unallocated=remove_unallocated,
    )


class DictOfEventAllocations(Dict[Cadet, Dict[Event, Group]]):
    def __init__(self, raw_dict: Dict[Cadet, Dict[Event, Group]], list_of_events: ListOfEvents):
        super().__init__(raw_dict)
        self._list_of_events = list_of_events

    def previous_groups_for_cadet_as_list(self, cadet: Cadet):
        return list(self.get(cadet).keys())

    @property
    def list_of_events(self) -> ListOfEvents:
        return self._list_of_events


def get_dict_of_event_allocations_for_last_N_events_for_list_of_cadets(
        object_store: ObjectStore,
        list_of_cadets: ListOfCadets,
        N_events: int = ALL_EVENTS,
        remove_unallocated: bool = False,
        excluding_event: Event = arg_not_passed

    ) -> DictOfEventAllocations:
        list_of_events = get_list_of_last_N_events(object_store=object_store, N_events=N_events, excluding_event=excluding_event)
        raw_dict = dict(
            [(cadet,
             get_dict_of_event_allocations_for_last_N_events_for_single_cadet_given_list_of_events(
                 object_store=object_store,
                 cadet=cadet,
                 list_of_events=list_of_events,
                 remove_unallocated=remove_unallocated
             )) for cadet in list_of_cadets]
        )

        return DictOfEventAllocations(raw_dict, list_of_events=list_of_events)


def get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
    object_store: ObjectStore,
    cadet: Cadet,
    N_events: int = ALL_EVENTS,
    excluding_event: Event = arg_not_passed,
    remove_unallocated: bool = False,
) -> Dict[Event, Group]:
    list_of_events = get_list_of_last_N_events(object_store=object_store, N_events=N_events, excluding_event=excluding_event)
    dict_of_previous_groups = get_dict_of_event_allocations_for_last_N_events_for_single_cadet_given_list_of_events(
        object_store=object_store,
        cadet=cadet,
        list_of_events=list_of_events,
        remove_unallocated=remove_unallocated
    )

    return dict_of_previous_groups


def get_list_of_last_N_events(object_store: ObjectStore, N_events: int = ALL_EVENTS, excluding_event: Event = arg_not_passed):
    unsorted_list_of_events = get_list_of_events(object_store)
    if excluding_event is not arg_not_passed:
        unsorted_list_of_events.remove(excluding_event)

    list_of_all_events = unsorted_list_of_events.sort_by_start_date_desc()
    list_of_events = list_of_all_events[:N_events]

    return list_of_events


def get_dict_of_event_allocations_for_last_N_events_for_single_cadet_given_list_of_events(
    object_store: ObjectStore,
    cadet: Cadet,
    list_of_events: ListOfEvents,
    remove_unallocated: bool = False,
) -> Dict[Event, Group]:

    previous_allocations_as_dict = (
        get_dict_of_group_allocations_for_list_of_events_active_cadets_only(
            object_store=object_store, list_of_events=list_of_events
        )
    )
    dict_of_previous_groups = most_common_allocation_for_cadet_in_previous_events(
        cadet=cadet, previous_allocations_as_dict=previous_allocations_as_dict
    )

    if remove_unallocated:
        dict_of_previous_groups = dict(
            [
                (event, group)
                for event, group in dict_of_previous_groups.items()
                if not group.is_unallocated
            ]
        )

    return dict_of_previous_groups


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


def get_group_allocations_for_event_active_cadets_only(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    all_cadet_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )

    return all_cadet_event_data.dict_of_cadets_with_days_and_groups


def most_common_allocation_for_cadet_in_previous_events(
    cadet: Cadet,
    previous_allocations_as_dict: Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent],
) -> Dict[Event, Group]:
    dict_of_allocations = dict(
        [
            (
                event,
                dict_of_allocations_for_event.get_most_common_group_for_cadet(
                    cadet, default_group=None
                ),
            )
            for event, dict_of_allocations_for_event in previous_allocations_as_dict.items()
        ]
    )

    dict_of_allocations = dict(
        [
            (event, allocation)
            for event, allocation in dict_of_allocations.items()
            if allocation is not None
        ]
    )

    return dict_of_allocations
