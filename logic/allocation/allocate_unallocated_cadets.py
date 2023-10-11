from logic.allocation.allocate_cadet import allocate_cadet
from logic.allocation.load_and_save_allocations_for_events import (
    load_allocation_for_event,
    save_allocation_for_event,
)
from logic.allocation.allocation_data import get_unallocated_cadets

from logic.data_and_interface import DataAndInterface

from logic.events.choose_event import choose_event
from logic.events.get_list_of_cadets_at_event import (
    get_list_of_cadets_in_mapped_wa_event,
)


def allocate_unallocated_cadets(data_and_interface: DataAndInterface):

    event = choose_event(
        "Choose event to allocate cadets for", data_and_interface=data_and_interface
    )

    list_of_cadets_with_groups = load_allocation_for_event(
        event=event, data_and_interface=data_and_interface
    )

    unallocated_cadets = get_unallocated_cadets(
        event=event,
        data_and_interface=data_and_interface,
        list_of_cadet_ids_with_groups=list_of_cadets_with_groups,
    )

    for cadet in unallocated_cadets:
        allocate_cadet(
            cadet=cadet,
            list_of_cadets_with_groups=list_of_cadets_with_groups,
            data_and_interface=data_and_interface,
        )

    save_allocation_for_event(
        event=event,
        list_of_cadets_with_groups=list_of_cadets_with_groups,
        data_and_interface=data_and_interface,
    )
