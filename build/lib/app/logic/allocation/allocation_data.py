from app.logic.allocation.load_and_save_allocations_for_events import (
    load_allocation_for_event,
)

from app.logic.data import DataAndInterface
from app.logic.events import (
    get_list_of_cadets_in_mapped_wa_event,
)
from app.logic.cadets.load_and_save_master_list_of_cadets import load_master_list_of_cadets

from app.objects import ListOfCadets
from app.objects import arg_not_passed
from app.objects import Event
from app.objects import ListOfCadetsWithGroup


def get_unallocated_cadets(
    event: Event,
    data_and_interface: DataAndInterface,
    list_of_cadet_ids_with_groups=arg_not_passed,
) -> ListOfCadets:

    if list_of_cadet_ids_with_groups is arg_not_passed:
        list_of_cadet_ids_with_groups = load_allocation_for_event(
            event=event, data_and_interface=data_and_interface
        )

    list_of_cadets_in_event = get_list_of_cadets_in_mapped_wa_event(
        data_and_interface=data_and_interface,
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
    data_and_interface: DataAndInterface, list_of_cadet_ids_with_groups=arg_not_passed
) -> ListOfCadetsWithGroup:

    list_of_cadets = load_master_list_of_cadets(data_and_interface)

    try:
        list_of_cadet_with_groups = (
            ListOfCadetsWithGroup.from_list_of_cadets_and_list_of_allocations(
                list_of_cadets=list_of_cadets,
                list_of_allocations=list_of_cadet_ids_with_groups,
            )
        )
    except:
        raise Exception("Cadets in allocation missing from master list of cadets")

    return list_of_cadet_with_groups
