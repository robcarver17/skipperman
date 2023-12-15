from app.logic import allocate_cadet
from app.logic.data import DataAndInterface
from app.logic.events import choose_event
from app.logic.events.allocation.backend import (
    load_allocation_for_event,
    save_allocation_for_event,
)
from app.logic.events import (
    get_list_of_cadets_in_mapped_wa_event,
)


def change_allocated_cadets(data_and_interface: DataAndInterface):

    event = choose_event(
        "Choose event to allocate cadets for", data_and_interface=data_and_interface
    )

    list_of_cadets_with_groups = load_allocation_for_event(
        event=event, data_and_interface=data_and_interface
    )
    list_of_cadets = get_list_of_cadets_in_mapped_wa_event(
        data_and_interface=data_and_interface,
        event=event,
        exclude_cancelled=True,
        exclude_deleted=True,
        exclude_active=False,
    )

    for cadet in list_of_cadets:
        allocate_cadet(
            cadet=cadet,
            data_and_interface=data_and_interface,
            list_of_cadets_with_groups=list_of_cadets_with_groups,
        )

    save_allocation_for_event(
        event=event,
        data_and_interface=data_and_interface,
        list_of_cadets_with_groups=list_of_cadets_with_groups,
    )
