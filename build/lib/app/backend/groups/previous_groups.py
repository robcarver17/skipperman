from typing import List, Dict

from app.backend.cadets.list_of_cadets import DEPRECATE_get_list_of_cadets
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)
from app.backend.events.list_of_events import (
    get_list_of_last_N_events,
    ALL_EVENTS,
    get_list_of_events,
)
from app.data_access.store.object_definitions import \
    object_definition_for_dict_of_group_names_for_events_and_cadets_persistent_version

from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.composed.cadets_at_event_with_groups import (
    DictOfCadetsWithDaysAndGroupsAtEvent,
)
from app.objects.composed.dict_of_previous_cadet_groups import \
    DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds
from app.objects.events import Event, ListOfEvents
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.groups import Group, missing_group_display_only


def get_list_of_previous_groups_as_str(
    object_store: ObjectStore,
    event_to_exclude: Event,
    cadet: Cadet,
    only_events_before_excluded_event: bool = True,
) -> List[str]:
    dict_of_groups = get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
        object_store=object_store,
        excluding_event=event_to_exclude,
        cadet=cadet,
        only_events_before_excluded_event=only_events_before_excluded_event,
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


def get_dict_of_all_event_allocations_for_single_cadet(
    object_store: ObjectStore,
    cadet: Cadet,
    remove_unallocated: bool = False,
    excluding_event: Event = arg_not_passed,
    only_events_before_excluded_event: bool = True,
    N_events: int = ALL_EVENTS,
) -> Dict[Event, Group]:
    return get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
        object_store=object_store,
        cadet=cadet,
        N_events=N_events,
        excluding_event=excluding_event,
        remove_unallocated=remove_unallocated,
        only_events_before_excluded_event=only_events_before_excluded_event,
    )


class DictOfEventAllocations(Dict[Cadet, Dict[Event, str]]):
    def __init__(
        self, raw_dict: Dict[Cadet, Dict[Event, str]], list_of_events: ListOfEvents
    ):
        super().__init__(raw_dict)
        self._list_of_events = list_of_events

    def previous_group_names_for_cadet_as_list(self, cadet: Cadet):
        previous_groups_for_cadet_by_event = self.get(cadet)
        ## ordered by event already
        return list(previous_groups_for_cadet_by_event.values())

    @property
    def list_of_events(self) -> ListOfEvents:
        return self._list_of_events





def get_dict_of_event_allocations_given_list_of_events_from_stored_data(
    object_store: ObjectStore,
    list_of_cadets: ListOfCadets,
    list_of_events: ListOfEvents,
):
    dict_of_all_group_names_for_events = get_dict_of_group_names_for_events_and_cadets_persistent_version(object_store)
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

def get_dict_of_group_names_for_events_and_cadets_persistent_version(object_store: ObjectStore) -> DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds:
    return object_store.DEPRECATE_get(object_definition=object_definition_for_dict_of_group_names_for_events_and_cadets_persistent_version)


def update_dict_of_group_names_for_events_and_cadets_persistent_version(object_store: ObjectStore, dict_of_group_names_for_events_and_cadets: DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds):
    object_store.DEPRECATE_update(
        dict_of_group_names_for_events_and_cadets,
        object_definition=object_definition_for_dict_of_group_names_for_events_and_cadets_persistent_version
    )


def get_dict_of_event_allocations_for_single_cadet_given_list_of_events_from_persistent_data(
    cadet: Cadet,
    dict_of_all_group_names_for_events: DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds,
    list_of_events: ListOfEvents,
) -> Dict[Event, str]:
    group_names_in_dict_for_cadet = dict_of_all_group_names_for_events.get_dict_of_group_names_for_cadet(cadet)

    dict_of_previous_groups = dict(
        [
            (event, group_names_in_dict_for_cadet.get(event, ""))
            for event in list_of_events
        ]
    )

    return dict_of_previous_groups



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
    dict_of_previous_groups = get_dict_of_event_allocations_for_single_cadet_given_list_of_events(
        object_store=object_store,
        cadet=cadet,
        list_of_events=list_of_events,
        remove_unallocated=remove_unallocated,
    )

    return dict_of_previous_groups


def update_dict_of_group_names_for_events_and_cadets_persistent_version_from_core_data(object_store: ObjectStore):
    dict_of_group_names_for_events_and_cadets_persistent_version =get_dict_of_group_names_for_events_and_cadets_persistent_version(object_store)
    list_of_cadets = DEPRECATE_get_list_of_cadets(object_store)
    list_of_events = get_list_of_events(object_store)

    for cadet in list_of_cadets:
        dict_of_event_allocations_for_single_cadet_given_list_of_events = get_dict_of_event_allocations_for_single_cadet_given_list_of_events(
            object_store=object_store,
            cadet=cadet,
            list_of_events=list_of_events,
            pad=True,
            remove_unallocated=False
        )
        dict_of_events_and_group_names = dict(
            [
                (event, group.name)
                for event, group in dict_of_event_allocations_for_single_cadet_given_list_of_events.items()
            ]
        )

        dict_of_group_names_for_events_and_cadets_persistent_version.update_most_group_names_across_events_for_cadet(
            cadet=cadet,
            dict_of_group_names_by_event=dict_of_events_and_group_names
        )

    update_dict_of_group_names_for_events_and_cadets_persistent_version(dict_of_group_names_for_events_and_cadets=dict_of_group_names_for_events_and_cadets_persistent_version,
                                                                        object_store=object_store)




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
    dict_of_previous_groups = most_common_allocation_for_cadet_in_previous_events(
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


def get_group_allocations_for_event_active_cadets_only(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    all_cadet_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)

    return all_cadet_event_data.dict_of_cadets_with_groups_for_all_cadets_in_data()


def most_common_allocation_for_cadet_in_previous_events(
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
