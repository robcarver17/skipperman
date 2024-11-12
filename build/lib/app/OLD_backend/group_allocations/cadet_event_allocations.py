from typing import List, Dict

from app.data_access.store.data_access import DataLayer

from app.objects.day_selectors import Day

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.objects.cadets import ListOfCadets
from app.objects.events import Event
from app.objects.composed.cadets_at_event_with_groups import ListOfCadetsWithGroupOnDay
from app.objects.groups import Group
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.OLD_backend.data.group_allocations import GroupAllocationsData


def get_list_of_groups_at_event_given_list_of_cadets(
    data_layer: DataLayer, event: Event, list_of_cadets: ListOfCadets
) -> List[Group]:
    group_allocation_data = GroupAllocationsData(data_layer)
    return group_allocation_data.get_list_of_groups_at_event_given_list_of_cadets(
        event=event, list_of_cadets=list_of_cadets
    )


def DEPRECATE_get_list_of_active_cadets_at_event(
    interface: abstractInterface, event: Event
) -> ListOfCadets:
    cadets_at_event = CadetsAtEventIdLevelData(interface.data)

    return cadets_at_event.list_of_active_cadets_at_event(event)


def get_list_of_active_cadets_at_event(
    data_layer: DataLayer, event: Event
) -> ListOfCadets:
    cadets_at_event = CadetsAtEventIdLevelData(data_layer)

    return cadets_at_event.list_of_active_cadets_at_event(event)


def DEPRECATE_get_list_of_cadets_unallocated_to_group_at_event(
    interface: abstractInterface,
    event: Event,
) -> ListOfCadets:
    group_allocations_data = GroupAllocationsData(interface.data)
    return group_allocations_data.unallocated_cadets_at_event(event)


def get_list_of_cadets_unallocated_to_group_at_event(
    data_layer: DataLayer,
    event: Event,
) -> ListOfCadets:
    group_allocations_data = GroupAllocationsData(data_layer)
    return group_allocations_data.unallocated_cadets_at_event(event)


def DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only(
    interface: abstractInterface, event: Event
) -> ListOfCadetIdsWithGroups:
    group_allocations_data = GroupAllocationsData(interface.data)
    return group_allocations_data.active_cadet_ids_at_event_with_allocations(event)


def load_list_of_cadets_ids_with_group_allocations_active_cadets_only(
    data_layer: DataLayer, event: Event
) -> ListOfCadetIdsWithGroups:
    group_allocations_data = GroupAllocationsData(data_layer)
    return group_allocations_data.active_cadet_ids_at_event_with_allocations(event)


def load_list_of_cadets_with_group_allocations_active_cadets_only(
    data_layer: DataLayer, event: Event
) -> ListOfCadetsWithGroupOnDay:
    group_allocations_data = GroupAllocationsData(data_layer)
    return group_allocations_data.list_of_active_cadets_with_groups(event)


def count_of_cadet_ids_allocated_to_group_by_day(
    interface: abstractInterface, event: Event
) -> Dict[Day, int]:
    group_allocations_data = GroupAllocationsData(interface.data)
    return group_allocations_data.active_cadet_ids_at_event_with_allocations(
        event
    ).count_of_ids_by_day(event)


def load_list_of_cadets_with_allocated_groups_at_event(
    interface: abstractInterface, event: Event
) -> ListOfCadetIdsWithGroups:
    group_allocation_data = GroupAllocationsData(interface.data)
    return group_allocation_data.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
        event
    )
