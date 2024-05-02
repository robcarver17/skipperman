from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.cadets import DEPRECATE_get_sorted_list_of_cadets
from app.backend.data.group_allocations import GroupAllocationsData
from app.backend.data.group_allocations_old import load_list_of_cadets_with_allocated_groups_at_event
from app.backend.data.cadets_at_event import DEPRECATED_load_cadets_at_event
from app.objects.cadets import ListOfCadets
from app.objects.constants import arg_not_passed
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups, ListOfCadetsWithGroup
from app.objects.groups import Group
from app.backend.data.group_allocations import GroupAllocationsData

def get_list_of_groups_at_event_given_list_of_cadets(interface: abstractInterface,
                                                        event: Event,
                                                        list_of_cadets: ListOfCadets) -> List[Group]:

    group_allocation_data = GroupAllocationsData(interface.data)
    return group_allocation_data.get_list_of_groups_at_event_given_list_of_cadets(event=event, list_of_cadets=list_of_cadets)

def get_list_of_active_cadets_at_event(
    event: Event
) -> ListOfCadets:
    list_of_cadet_ids = get_list_of_active_cadet_ids_at_event(
        event=event,

    )
    list_of_cadets = get_list_of_cadets_given_list_of_ids(
        list_of_cadet_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadets_given_list_of_ids(list_of_cadet_ids: list) -> ListOfCadets:
    master_list_of_cadets = DEPRECATE_get_sorted_list_of_cadets()
    list_of_cadets = ListOfCadets.subset_from_list_of_ids(
        master_list_of_cadets, list_of_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_active_cadet_ids_at_event(
    event: Event
) -> list:
    cadets_of_event = DEPRECATED_load_cadets_at_event(event)
    list_of_cadet_ids = cadets_of_event.list_of_active_cadet_ids(
    )

    return list_of_cadet_ids


def DEPRECATE_get_list_of_cadets_unallocated_to_group_at_event(
    event: Event,
    list_of_cadet_ids_with_groups=arg_not_passed,
) -> ListOfCadets:
    if list_of_cadet_ids_with_groups is arg_not_passed:
        list_of_cadet_ids_with_groups = DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only(event=event)

    list_of_cadets_in_event = get_list_of_active_cadets_at_event(
        event=event
    )

    unallocated_cadets = (
        list_of_cadet_ids_with_groups.cadets_in_passed_list_not_allocated_to_any_group(
            list_of_cadets_in_event
        )
    )
    return unallocated_cadets

def get_list_of_cadets_unallocated_to_group_at_event(
        interface: abstractInterface,
    event: Event,
) -> ListOfCadets:
    group_allocations_data = GroupAllocationsData(interface.data)
    return group_allocations_data.unallocated_cadets_at_event(event)

def get_list_of_cadets_with_groups(
    list_of_cadet_ids_with_groups,
) -> ListOfCadetsWithGroup:
    list_of_cadets = DEPRECATE_get_sorted_list_of_cadets()

    try:
        list_of_cadet_with_groups = (
            ListOfCadetsWithGroup.from_list_of_cadets_and_list_of_allocations(
                list_of_cadets=list_of_cadets,
                list_of_allocations=list_of_cadet_ids_with_groups,
            )
        )
    except:
        raise Exception("Cadets in backend missing from master list of group_allocations")

    return list_of_cadet_with_groups



def DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only(event: Event) -> ListOfCadetIdsWithGroups:

    list_of_cadets_with_groups = load_list_of_cadets_with_allocated_groups_at_event(event)
    list_of_active_cadet_ids_at_event = get_list_of_active_cadet_ids_at_event(event)

    list_of_allocated_cadets_with_groups = [cadet_with_group for cadet_with_group in list_of_cadets_with_groups
                                            if cadet_with_group.cadet_id in list_of_active_cadet_ids_at_event]

    return ListOfCadetIdsWithGroups(list_of_allocated_cadets_with_groups)


def load_list_of_cadets_ids_with_group_allocations_active_cadets_only(interface: abstractInterface, event: Event) -> ListOfCadetIdsWithGroups:
    group_allocations_data = GroupAllocationsData(interface.data)
    return group_allocations_data.active_cadet_ids_at_event_with_allocations(event)

