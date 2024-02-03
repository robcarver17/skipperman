from app.backend.wa_import.load_and_save_wa_mapped_events import load_master_event, load_existing_mapped_wa_event_with_ids
from app.logic.events.events_in_state import get_event_from_state
from app.logic.abstract_interface import abstractInterface
from app.objects.constants import missing_data, NoMoreData
from app.objects.events import Event
from app.objects.utils import union_of_x_and_y

CADET_ID = "cadet_id"


def get_and_save_next_cadet_id_in_event_data(interface: abstractInterface) -> str:
    current_id = get_current_cadet_id(interface)
    if current_id is missing_data:
        new_id = get_first_cadet_id_in_event_data(interface)
    else:
        new_id = get_next_cadet_id_in_event_data(
            interface=interface, current_id=current_id
        )

    interface.set_persistent_value(CADET_ID, new_id)

    return new_id


def get_first_cadet_id_in_event_data(interface: abstractInterface) -> str:
    event = get_event_from_state(interface)
    list_of_ids = list_of_cadet_ids_in_master_and_mapped_data(event)
    id = list_of_ids[0]

    print("Getting first ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_cadet_id_in_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    event = get_event_from_state(interface)
    list_of_ids = list_of_cadet_ids_in_master_and_mapped_data(event)
    current_index = list_of_ids.index(current_id)
    new_index = current_index+1

    try:
        new_id = list_of_ids[new_index]
    except:
        raise NoMoreData

    return new_id


def list_of_cadet_ids_in_master_and_mapped_data(event: Event) -> list:
    master_event = load_master_event(event)
    mapped_event = load_existing_mapped_wa_event_with_ids(event)

    master_ids = master_event.list_of_cadet_ids
    mapped_ids = mapped_event.list_of_cadet_ids

    all_ids = union_of_x_and_y(master_ids, mapped_ids)
    all_ids.sort() ## MUST be sorted otherwise can go horribly wrong

    return all_ids


def get_current_cadet_id(interface: abstractInterface) -> str:
    cadet_id = interface.get_persistent_value(CADET_ID, default=missing_data)

    return cadet_id
