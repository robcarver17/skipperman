from app.backend.cadets import get_list_of_cadets
from app.backend.wa_import.load_and_save_wa_mapped_events import load_master_event
from app.data_access.data import data
from app.objects.cadets import ListOfCadets
from app.objects.constants import arg_not_passed
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups, ListOfCadetsWithGroup


def get_list_of_cadets_in_master_event(
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> ListOfCadets:
    list_of_cadet_ids = get_list_of_cadet_ids_at_event(
        event=event,
        exclude_active=exclude_active,
        exclude_deleted=exclude_deleted,
        exclude_cancelled=exclude_cancelled,
    )
    list_of_cadets = get_list_of_cadets_given_list_of_ids(
        list_of_cadet_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadets_given_list_of_ids(list_of_cadet_ids: list) -> ListOfCadets:
    master_list_of_cadets = get_list_of_cadets()
    list_of_cadets = ListOfCadets.subset_from_list_of_ids(
        master_list_of_cadets, list_of_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadet_ids_at_event(
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> list:
    master_event = load_master_event(event)
    list_of_cadet_ids = master_event.list_of_cadet_ids_with_given_status(
        exclude_cancelled=exclude_cancelled,
        exclude_deleted=exclude_deleted,
        exclude_active=exclude_active,
    )

    return list_of_cadet_ids




def save_current_allocations_for_event(
    event: Event, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
):
    data.data_list_of_cadets_with_groups.write_groups_for_event(
        event_id=event.id, list_of_cadets_with_groups=list_of_cadets_with_groups
    )


def get_unallocated_cadets(
    event: Event,
    list_of_cadet_ids_with_groups=arg_not_passed,
) -> ListOfCadets:
    if list_of_cadet_ids_with_groups is arg_not_passed:
        list_of_cadet_ids_with_groups = load_allocation_for_event(event=event)

    list_of_cadets_in_event = get_list_of_cadets_in_master_event(
        event=event,
        exclude_cancelled=True,
        exclude_deleted=True,
        exclude_active=False,
    )

    unallocated_cadets = (
        list_of_cadet_ids_with_groups.cadets_in_list_not_allocated_to_group(
            list_of_cadets_in_event
        )
    )
    return unallocated_cadets


def get_list_of_cadets_with_groups(
    list_of_cadet_ids_with_groups,
) -> ListOfCadetsWithGroup:
    list_of_cadets = get_list_of_cadets()

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


def load_allocation_for_event(event: Event) -> ListOfCadetIdsWithGroups:
    event_id = event.id

    list_of_cadets_with_groups = (
        data.data_list_of_cadets_with_groups.read_groups_for_event(event_id)
    )

    return list_of_cadets_with_groups


