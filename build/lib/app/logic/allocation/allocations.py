from app.data_access.data import data
from app.logic.events.backend.load_and_save_wa_mapped_events import (
    load_master_event,
)
from app.logic.cadets.view_cadets import cadet_from_id_with_passed_list
from app.logic.cadets.backend import get_list_of_cadets
from app.objects.cadets import ListOfCadets
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups, ListOfCadetsWithGroup

from app.objects.constants import arg_not_passed

def get_list_of_cadets_in_master_event(
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> ListOfCadets:
    list_of_cadet_ids = get_list_of_cadet_ids_in_mapped_wa_event(
        event=event,
        exclude_active=exclude_active,
        exclude_deleted=exclude_deleted,
        exclude_cancelled=exclude_cancelled,
    )
    list_of_cadets = get_list_of_cadets_given_list_of_ids(
        list_of_cadet_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadets_given_list_of_ids(
    list_of_cadet_ids: list
) -> ListOfCadets:
    master_list_of_cadets = get_list_of_cadets()
    list_of_cadets = ListOfCadets.subset_from_list_of_ids(
        master_list_of_cadets, list_of_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadet_ids_in_mapped_wa_event(
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> list:
    master_event = load_master_event(event)
    list_of_cadet_ids = (
        master_event.list_of_cadet_ids_with_given_status(
            exclude_cancelled=exclude_cancelled,
            exclude_deleted=exclude_deleted,
            exclude_active=exclude_active,
        )
    )

    return list_of_cadet_ids

def get_list_of_cadets_in_mapped_wa_event(event: Event,
                                          exclude_deleted: bool = True,
                                          exclude_cancelled: bool = True,
                                          exclude_active: bool = False,
                                          ) -> ListOfCadets:
    list_of_ids = get_list_of_cadet_ids_in_mapped_wa_event(event=event,
                                                           exclude_active=exclude_active,
                                                           exclude_deleted=exclude_deleted,
                                                           exclude_cancelled=exclude_cancelled)
    list_of_cadets = get_list_of_cadets()

    cadets_in_event = [cadet_from_id_with_passed_list(cadet_id=cadet_id, list_of_cadets=list_of_cadets) for cadet_id in list_of_ids]

    return ListOfCadets(cadets_in_event)

def get_current_allocations(event: Event) -> ListOfCadetIdsWithGroups:
    return data.data_list_of_cadets_with_groups.read_groups_for_event(event_id=event.id)

def get_previous_allocations() -> ListOfCadetIdsWithGroups:
    return data.data_list_of_cadets_with_groups.read_last_groups()

def save_current_allocations_for_event(event: Event, list_of_cadets_with_groups: ListOfCadetIdsWithGroups):
    data.data_list_of_cadets_with_groups.write_groups_for_event(event_id=event.id, list_of_cadets_with_groups=list_of_cadets_with_groups)

def update_previous_allocations(list_of_cadets_with_groups: ListOfCadetIdsWithGroups):
    data.data_list_of_cadets_with_groups.write_last_groups(
                                                                list_of_cadets_with_groups)


def get_unallocated_cadets(
    event: Event,
    list_of_cadet_ids_with_groups=arg_not_passed,
) -> ListOfCadets:

    if list_of_cadet_ids_with_groups is arg_not_passed:
        list_of_cadet_ids_with_groups = get_current_allocations(
            event=event
        )

    list_of_cadets_in_event = get_list_of_cadets_in_mapped_wa_event(
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
    list_of_cadet_ids_with_groups
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
        raise Exception("Cadets in backend missing from master list of cadets")

    return list_of_cadet_with_groups
