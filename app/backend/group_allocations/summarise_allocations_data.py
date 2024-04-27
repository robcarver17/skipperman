from typing import List

from app.backend.forms.summarys import summarise_generic_counts_for_event
from app.backend.group_allocations.cadet_event_allocations import DEPRECATE_get_list_of_cadets_unallocated_to_group_at_event, DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only
from app.backend.data.cadets_at_event import DEPRECATED_load_cadets_at_event
from app.objects.groups import ListOfCadetIdsWithGroups
from app.objects.events import Event
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.groups import Group, GROUP_UNALLOCATED, ALL_GROUPS_NAMES

def summarise_allocations_for_event(event: Event) -> PandasDFTable:
    list_of_cadet_ids_with_groups = DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only(event)
    cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    availability_dict = dict([(cadet.cadet_id, cadet.availability)
                              for cadet in cadets_at_event.list_of_active_cadets_at_event()])
    groups = get_sorted_groups_plus_unalloacted(list_of_cadet_ids_with_groups)

    return summarise_generic_counts_for_event(
        get_id_function=get_relevant_cadet_ids_for_group,
        event=event,
        groups=groups,
        availability_dict=availability_dict,
        list_of_ids_with_groups=list_of_cadet_ids_with_groups
    )


def get_sorted_groups_plus_unalloacted(list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups) ->List[Group]:
    groups_in_passed_list = list(set(list_of_cadet_ids_with_groups.groups))
    group_names_in_passed_list = [group.group_name for group in groups_in_passed_list]
    group_names = [group_name for group_name in ALL_GROUPS_NAMES if group_name in group_names_in_passed_list] ## preserve order
    groups = [Group(group_name) for group_name in group_names]

    return groups+[GROUP_UNALLOCATED]

def get_relevant_cadet_ids_for_group(group: Group,
                                     event: Event,
                                     list_of_ids_with_groups: ListOfCadetIdsWithGroups)-> List[str]:
    if group == GROUP_UNALLOCATED:
        unallocated_cadets = DEPRECATE_get_list_of_cadets_unallocated_to_group_at_event(
            event=event,
            list_of_cadet_ids_with_groups=list_of_ids_with_groups,
        )
        list_of_ids = unallocated_cadets.list_of_ids
    else:
        list_of_ids = [cadet_and_group.cadet_id for cadet_and_group in list_of_ids_with_groups if cadet_and_group.group == group]

    return list_of_ids



