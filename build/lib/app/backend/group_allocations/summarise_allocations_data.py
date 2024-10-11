from typing import List, Dict

from app.objects.day_selectors import Day

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.forms import summarise_generic_counts_for_event_over_days
from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.OLD_backend.data.group_allocations import GroupAllocationsData
from app.objects.events import Event
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.groups import Group
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups


def summarise_allocations_for_event(interface: abstractInterface, event: Event) -> PandasDFTable:
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    group_allocations_data = GroupAllocationsData(interface.data)

    availability_dict =cadets_at_event_data.get_availability_dict_for_active_cadet_ids_at_event(event)

    list_of_cadet_ids_with_groups = group_allocations_data.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(event)
    groups = group_allocations_data.get_list_of_groups_at_event(event)

    return summarise_generic_counts_for_event_over_days(
        get_id_function=get_relevant_cadet_ids_for_group,
        event=event,
        groups=groups,
        availability_dict=availability_dict,
        list_of_ids_with_groups=list_of_cadet_ids_with_groups
    )


def get_relevant_cadet_ids_for_group(group: Group,
                                     event: Event,
                                     list_of_ids_with_groups: ListOfCadetIdsWithGroups)  -> Dict[Day, List[str]]:

    result_dict = {}
    for day in event.weekdays_in_event():
        result_dict[day]=list_of_ids_with_groups.list_of_cadet_ids_in_group_on_day(day=day, group=group)

    return result_dict


