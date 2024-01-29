from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.backend.cadet_event_allocations import get_unallocated_cadets, load_allocation_for_event
from app.objects.groups import ListOfCadetIdsWithGroups
from app.objects.cadets import ListOfCadets
from app.objects.events import Event
def summarise_allocations_for_event(event) -> ListOfLines:
    list_of_cadet_ids_with_groups = load_allocation_for_event(event)

    total_in_each_group_as_dict = list_of_cadet_ids_with_groups.total_in_each_group_as_dict()
    total_in_each_group_as_dict["Unallocated"] = count_unallocated_cadets(event=event, list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups)

    total_as_list_of_lines = ListOfLines([
        "%s: %d" % (group, total) for group, total in total_in_each_group_as_dict.items()
    ])

    return ListOfLines([
        _______________,
        "Group allocations for event %s:" % str (event),
        _______________]+
        total_as_list_of_lines+[
        _______________
    ])

def count_unallocated_cadets(event: Event,list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups) -> int:
    unallocated_cadets = get_unallocated_cadets(
        event=event,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
    )
    return len(unallocated_cadets)


def reorder_list_of_cadets_by_allocated_group(list_of_cadets: ListOfCadets, current_allocation_for_event: ListOfCadetIdsWithGroups)-> ListOfCadets:
    print(list_of_cadets)
    sorted_by_group = current_allocation_for_event.sort_by_group()
    print(sorted_by_group)
    sorted_list_of_ids = sorted_by_group.list_of_ids
    print(sorted_list_of_ids)
    unallocated_cadets = (
        current_allocation_for_event.cadets_in_list_not_allocated_to_group(
            list_of_cadets
        )
    )
    print(unallocated_cadets)
    unallocated_ids = unallocated_cadets.list_of_ids
    print(unallocated_ids)
    joint_ids = sorted_list_of_ids+unallocated_ids
    print(joint_ids)

    return ListOfCadets.subset_from_list_of_ids(list_of_cadets, list_of_ids=joint_ids)