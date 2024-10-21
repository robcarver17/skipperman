
from typing import Dict, List

from app.objects.exceptions import arg_not_passed

from app.objects.day_selectors import DictOfDaySelectors

from app.backend.events.cadets_at_event import get_dict_of_all_event_info_for_cadets, \
    get_attendance_matrix_for_list_of_cadets_at_event

from app.backend.events.list_of_events import get_list_of_events

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.composed.cadets_at_event_with_groups import DictOfCadetsWithDaysAndGroupsAtEvent

from app.objects.events import Event

from app.data_access.store.object_definitions import object_definition_for_cadets_with_ids_and_groups_at_event, \
    object_definition_for_dict_of_cadets_with_groups_at_event
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups

from app.data_access.store.object_store import ObjectStore
from app.objects.groups import Group




def get_joint_attendance_matrix_for_cadets_in_group_at_event(
        object_store: ObjectStore, event: Event, group: Group, list_of_cadets: ListOfCadets = arg_not_passed
):
    if list_of_cadets is arg_not_passed:
        all_cadet_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event,
                                                                     active_only=True)
        list_of_cadets= all_cadet_event_data.dict_of_cadets_with_days_and_groups.cadets_in_group_during_event(group)

    attendance_data = get_attendance_matrix_for_list_of_cadets_at_event(
        object_store=object_store,
        event=event, list_of_cadets=list_of_cadets
    )
    attendance_in_group = get_attendance_matrix_for_group_at_event(
        object_store=object_store,
        event=event,  group=group
    )

    joint_attendance = attendance_data.intersect(attendance_in_group)
    joint_attendance = joint_attendance.align_with_list_of_days(
        event.weekdays_in_event()
    )

    return joint_attendance



def get_attendance_matrix_for_group_at_event(
    object_store: ObjectStore, event: Event, group: Group
) -> DictOfDaySelectors:
    all_cadet_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event, active_only=True)
    cadets_in_group_during_event = all_cadet_event_data.dict_of_cadets_with_days_and_groups.cadets_in_group_during_event(group)

    all_selectors = {}
    for cadet in cadets_in_group_during_event:
        days_and_groups = all_cadet_event_data.dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(cadet)
        all_selectors[cadet] = days_and_groups.day_selector_for_group(group)

    return DictOfDaySelectors(all_selectors)




ALL_EVENTS = 99999999999999

def get_dict_of_all_event_allocations_for_single_cadet(
    object_store:ObjectStore, cadet: Cadet, remove_unallocated: bool = False
) -> Dict[Event, Group]:
    return get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
        object_store=object_store,
        cadet=cadet,
        N_events=ALL_EVENTS,
        remove_unallocated=remove_unallocated
    )

def get_dict_of_event_allocations_for_last_N_events_for_single_cadet(
        object_store: ObjectStore, cadet: Cadet, N_events: int = ALL_EVENTS, remove_unallocated: bool = False
) -> Dict[Event, Group]:

    unsorted_list_of_events = get_list_of_events(object_store)
    list_of_events = unsorted_list_of_events.sort_by_start_date_desc()
    list_of_events_to_get = list_of_events[:N_events]

    previous_allocations_as_dict = (
        get_dict_of_group_allocations_for_list_of_events_active_cadets_only(
            object_store=object_store, list_of_events=list_of_events_to_get
        )
    )
    dict_of_previous_groups = most_common_allocation_for_cadet_in_previous_events(
        cadet=cadet, previous_allocations_as_dict=previous_allocations_as_dict
    )


    if remove_unallocated:
        dict_of_previous_groups  = dict(
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
        object_store: ObjectStore, event: Event) -> DictOfCadetsWithDaysAndGroupsAtEvent:

    all_cadet_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event, active_only=True)

    return all_cadet_event_data.dict_of_cadets_with_days_and_groups

def most_common_allocation_for_cadet_in_previous_events(
    cadet: Cadet, previous_allocations_as_dict: Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent]
) -> Dict[Event, Group]:
    dict_of_allocations = dict([(
        event,
        dict_of_allocations_for_event.get_most_common_group_for_cadet(cadet, default_group=None))
        for event, dict_of_allocations_for_event in previous_allocations_as_dict.items()

    ])

    dict_of_allocations= dict([(event, allocation) for event,allocation in dict_of_allocations.items() if allocation is not None])

    return dict_of_allocations


## FOLLOWING OLD CODE MIGHT BE REFACTORED
def allocation_for_cadet_in_previous_events_as_dictCONSIDER_REFACTOR(
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



### FOLLOWING NEW CODE MIGHT NOT BE NEEDED
def get_dict_of_cadets_with_groups_at_event(object_store: ObjectStore,
                                            event: Event) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_with_groups_at_event,
        event_id = event.id
    )

def update_dict_of_cadets_with_groups_at_event(object_store: ObjectStore, event: Event, dict_of_cadets_with_groups_at_event: DictOfCadetsWithDaysAndGroupsAtEvent):
    object_store.update(
        new_object=dict_of_cadets_with_groups_at_event,
        object_definition=object_definition_for_dict_of_cadets_with_groups_at_event,
        event_id=event.id,
    )

def get_list_of_cadets_with_ids_with_groups_at_event(object_store: ObjectStore, event: Event) -> ListOfCadetIdsWithGroups:
    return object_store.get(object_definition=object_definition_for_cadets_with_ids_and_groups_at_event,
                            event_id=event.id)

def update_list_of_cadets_with_ids_with_groups_at_event(object_store: ObjectStore, event: Event, list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups):
    object_store.update(
        new_object=list_of_cadet_ids_with_groups,
        object_definition=object_definition_for_cadets_with_ids_and_groups_at_event,
        event_id=event.id,
    )
