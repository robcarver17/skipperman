from app.logic.data import DataAndInterface
from app.logic.events.backend.load_and_save_wa_mapped_events import (
    load_master_event,
)
from app.logic.cadets.load_and_save_master_list_of_cadets import (
    load_master_list_of_cadets,
)
from app.objects import ListOfCadets
from app.objects import Event


def get_list_of_cadets_in_mapped_wa_event(
    data_and_interface: DataAndInterface,
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> ListOfCadets:
    list_of_cadet_ids = get_list_of_cadet_ids_in_mapped_wa_event(
        data_and_interface=data_and_interface,
        event=event,
        exclude_active=exclude_active,
        exclude_deleted=exclude_deleted,
        exclude_cancelled=exclude_cancelled,
    )
    list_of_cadets = get_list_of_cadets_given_list_of_ids(
        data_and_interface=data_and_interface, list_of_cadet_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadets_given_list_of_ids(
    data_and_interface: DataAndInterface, list_of_cadet_ids: list
) -> ListOfCadets:
    master_list_of_cadets = load_master_list_of_cadets(
        data_and_interface=data_and_interface
    )
    list_of_cadets = ListOfCadets.subset_from_list_of_ids(
        master_list_of_cadets, list_of_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadet_ids_in_mapped_wa_event(
    data_and_interface: DataAndInterface,
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> list:
    mapped_wa_event_data_without_duplicates = (
        load_master_event(
            event=event, data_and_interface=data_and_interface
        )
    )
    list_of_cadet_ids = (
        mapped_wa_event_data_without_duplicates.list_of_cadet_ids_with_given_status(
            exclude_cancelled=exclude_cancelled,
            exclude_deleted=exclude_deleted,
            exclude_active=exclude_active,
        )
    )

    return list_of_cadet_ids
