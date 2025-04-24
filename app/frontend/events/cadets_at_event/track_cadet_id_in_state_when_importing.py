from app.objects.cadets import Cadet

from app.backend.registration_data.identified_cadets_at_event import (
    list_of_cadet_ids_in_event_data_and_identified_in_raw_registration_data_for_event,
)
from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import missing_data, NoMoreData, MissingData
from app.objects.utilities.utils import percentage_of_x_in_y

CADET_ID_AT_EVENT = "cadet_id_at_event"


def percentage_of_cadets_processed_at_event(interface: abstractInterface):
    current_id = get_current_cadet_id_at_event(interface)
    list_of_ids = list_of_cadet_ids_at_event_and_in_mapped_data(interface)
    current_index = list_of_ids.index(current_id)

    return percentage_of_x_in_y(current_index, list_of_ids)


def get_and_save_next_cadet_in_event_data(interface: abstractInterface) -> Cadet:

    next_id = get_and_save_next_cadet_id_in_event_data(interface=interface)
    return get_cadet_from_id(object_store=interface.object_store, cadet_id=next_id)


def get_and_save_next_cadet_id_in_event_data(interface: abstractInterface) -> str:
    current_id = get_current_cadet_id_at_event(interface)
    if current_id is missing_data:
        new_id = get_first_cadet_id_in_event_data(interface)
    else:
        new_id = get_next_cadet_id_in_event_data(
            interface=interface, current_id=current_id
        )
    save_cadet_id_at_event(interface=interface, cadet_id=new_id)

    return new_id


def get_first_cadet_id_in_event_data(interface: abstractInterface) -> str:
    list_of_ids = list_of_cadet_ids_at_event_and_in_mapped_data(interface)
    id = list_of_ids[0]

    print("Getting first Cadet ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_cadet_id_in_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    list_of_ids = list_of_cadet_ids_at_event_and_in_mapped_data(interface)
    current_index = list_of_ids.index(current_id)
    new_index = current_index + 1

    try:
        new_id = list_of_ids[new_index]
    except:
        raise NoMoreData

    return new_id


def list_of_cadet_ids_at_event_and_in_mapped_data(interface: abstractInterface) -> list:
    event = get_event_from_state(interface)
    all_ids = list_of_cadet_ids_in_event_data_and_identified_in_raw_registration_data_for_event(
        object_store=interface.object_store,
        event=event,
        include_identified_in_raw_registration_data=True,
    )

    return all_ids


def get_current_cadet_at_event(interface: abstractInterface) -> Cadet:
    cadet_id = get_current_cadet_id_at_event(interface)
    if cadet_id is missing_data:
        raise MissingData("Cadet ID not stored")

    return get_cadet_from_id(object_store=interface.object_store, cadet_id=cadet_id)


def get_current_cadet_id_at_event(interface: abstractInterface) -> str:
    cadet_id = interface.get_persistent_value(CADET_ID_AT_EVENT, default=missing_data)

    return cadet_id


def save_cadet_id_at_event(interface: abstractInterface, cadet_id: str):
    interface.set_persistent_value(CADET_ID_AT_EVENT, cadet_id)


def clear_cadet_id_at_event(interface: abstractInterface):
    interface.clear_persistent_value(CADET_ID_AT_EVENT)
