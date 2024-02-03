from typing import Dict
from app.data_access.data import data
from app.objects.cadets import Cadet
from app.objects.events import Event, ListOfEvents
from app.objects.groups import ListOfCadetIdsWithGroups, Group
from app.data_access.configuration.configuration import UNALLOCATED_GROUP_NAME


def list_of_events_excluding_one_event(event_to_exclude: Event) -> ListOfEvents:
    list_of_events= data.data_list_of_events.read()
    list_of_events.pop_with_id(event_to_exclude.id)
    list_of_events = list_of_events.sort_by_start_date_asc()

    return list_of_events

def get_dict_of_allocations_for_events_and_list_of_cadets(list_of_events: list) -> Dict[Event, ListOfCadetIdsWithGroups]:
    allocations_as_dict = dict([(event, allocation_for_event(event)) for event in list_of_events])

    return allocations_as_dict

def get_dict_of_all_event_allocations_for_single_cadet(cadet: Cadet) -> Dict[Event, Group]:
    list_of_events = data.data_list_of_events.read()
    previous_allocations_as_dict = get_dict_of_allocations_for_events_and_list_of_cadets(list_of_events)
    list_of_previous_groups = allocation_for_cadet_in_previous_events(cadet=cadet, previous_allocations_as_dict=previous_allocations_as_dict)

    dict_of_previous = dict([
        (event, group)
        for event, group in zip(list_of_events, list_of_previous_groups)
    ])

    return dict_of_previous

def allocation_for_event(event: Event) ->ListOfCadetIdsWithGroups:
    return data.data_list_of_cadets_with_groups.read_groups_for_event(event.id)


def allocation_for_cadet_in_previous_events(cadet: Cadet, previous_allocations_as_dict: Dict[Event, ListOfCadetIdsWithGroups]):
    list_of_events = list(previous_allocations_as_dict.keys())
    allocations = [group_for_cadet_and_event(cadet=cadet, event=event, previous_allocations_as_dict=previous_allocations_as_dict) for event in list_of_events]

    return allocations


def group_for_cadet_and_event(cadet: Cadet, event: Event, previous_allocations_as_dict: Dict[Event, ListOfCadetIdsWithGroups]) -> Group:
    cadet_id = cadet.id
    allocations_for_event = previous_allocations_as_dict[event]
    try:
        group = allocations_for_event.item_with_cadet_id(cadet_id).group
    except:
        group = UNALLOCATED_GROUP_NAME

    return group

