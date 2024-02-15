from typing import Dict, List
from dataclasses import dataclass

from app.backend.events import get_sorted_list_of_events
from app.backend.group_allocations.cadet_event_allocations import get_list_of_cadets_at_event, \
    load_allocation_for_event
from app.backend.group_allocations.previous_allocations import allocation_for_cadet_in_previous_events, \
    get_dict_of_allocations_for_events_and_list_of_cadets
from app.data_access.configuration.configuration import UNALLOCATED_GROUP_NAME
from app.backend.data.cadets_at_event import load_cadets_at_event
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.events import Event, list_of_events_excluding_one_event, SORT_BY_START_ASC
from app.objects.groups import ListOfCadetIdsWithGroups, Group

from app.objects.cadet_at_event import ListOfCadetsAtEvent


@dataclass
class AllocationData:
    current_allocation_for_event: ListOfCadetIdsWithGroups
    cadets_at_event: ListOfCadetsAtEvent
    list_of_cadets: ListOfCadets
    previous_allocations_as_dict: Dict[Event, ListOfCadetIdsWithGroups]

    def previous_event_names(self) -> list:
        previous_events = self.previous_allocations_as_dict.keys()
        event_names = [str(event) for event in previous_events]

        return event_names

    def previous_groups_as_list_of_str(self, cadet: Cadet) -> list:
        previous_groups_as_list = self.previous_groups_as_list(cadet)
        return [x.as_str_replace_unallocated_with_empty() for x in previous_groups_as_list]


    def previous_groups_as_list(self, cadet: Cadet) -> List[Group]:
        return allocation_for_cadet_in_previous_events(cadet=cadet,previous_allocations_as_dict=self.previous_allocations_as_dict)

    def get_last_group(self, cadet: Cadet):
        previous_allocation = self.previous_groups_as_list(cadet)
        previous_allocation.reverse() ## last event first when considering
        for allocation in previous_allocation:
            if allocation == UNALLOCATED_GROUP_NAME:
                continue
            else:
                return allocation

        return UNALLOCATED_GROUP_NAME

    def get_current_group(self, cadet: Cadet):
        try:
            current_allocation = self.current_allocation_for_event.item_with_cadet_id(
                cadet_id=cadet.id
            ).group

        except:
            current_allocation = self.get_last_group(cadet)

        return current_allocation


def get_allocation_data(event: Event) -> AllocationData:
    current_allocation_for_event = load_allocation_for_event(event)
    cadets_at_event = load_cadets_at_event(event)
    unsorted_list_of_cadets = get_list_of_cadets_at_event(event)
    list_of_cadets = reorder_list_of_cadets_by_allocated_group(list_of_cadets=unsorted_list_of_cadets, current_allocation_for_event=current_allocation_for_event)
    list_of_events = get_sorted_list_of_events()
    list_of_previous_events = list_of_events_excluding_one_event(list_of_events=list_of_events,event_to_exclude=event, only_past=True, sort_by=SORT_BY_START_ASC)
    previous_allocations_as_dict = get_dict_of_allocations_for_events_and_list_of_cadets(list_of_events=list_of_previous_events)

    return AllocationData(
        current_allocation_for_event=current_allocation_for_event,
        cadets_at_event=cadets_at_event,
        list_of_cadets=list_of_cadets,
        previous_allocations_as_dict=previous_allocations_as_dict
    )


def reorder_list_of_cadets_by_allocated_group(list_of_cadets: ListOfCadets, current_allocation_for_event: ListOfCadetIdsWithGroups)-> ListOfCadets:
    print("full list %s" % str(list_of_cadets))
    print("current allocation %s" % current_allocation_for_event)
    sorted_by_group = current_allocation_for_event.sort_by_group()
    sorted_list_of_ids = sorted_by_group.list_of_row_ids
    unallocated_cadets = (
        current_allocation_for_event.cadets_in_list_not_allocated_to_group(
            list_of_cadets
        )
    )
    unallocated_ids = unallocated_cadets.list_of_ids
    joint_ids = sorted_list_of_ids+unallocated_ids ## sorted, then unallocated
    print("joint ids %s" % str(joint_ids))

    return ListOfCadets.subset_from_list_of_ids(list_of_cadets, list_of_ids=joint_ids)