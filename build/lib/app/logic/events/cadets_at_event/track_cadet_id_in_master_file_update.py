from app.backend.data.mapped_events import load_mapped_wa_event
from app.backend.data.cadets_at_event import load_cadets_at_event
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import missing_data, NoMoreData
from app.objects.events import Event
from app.objects.utils import union_of_x_and_y

CADET_ID_AT_EVENT = "cadetid_at_event"


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

    print("Getting first ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_cadet_id_in_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    list_of_ids = list_of_cadet_ids_at_event_and_in_mapped_data(interface)
    current_index = list_of_ids.index(current_id)
    new_index = current_index+1

    try:
        new_id = list_of_ids[new_index]
    except:
        raise NoMoreData

    return new_id


def list_of_cadet_ids_at_event_and_in_mapped_data(interface:abstractInterface) -> list:
    event = get_event_from_state(interface)

    cadets_at_event = load_cadets_at_event(event)
    mapped_event = load_mapped_wa_event(event)

    existing_ids = cadets_at_event.list_of_cadet_ids()
    mapped_ids = mapped_event.list_of_row_ids()

    all_ids = union_of_x_and_y(existing_ids, mapped_ids)
    all_ids.sort() ## MUST be sorted otherwise can go horribly wrong

    return all_ids


def get_current_cadet_id_at_event(interface: abstractInterface) -> str:
    cadet_id = interface.get_persistent_value(CADET_ID_AT_EVENT, default=missing_data)

    return cadet_id

def save_cadet_id_at_event(interface: abstractInterface, cadet_id: str):
    interface.set_persistent_value(CADET_ID_AT_EVENT, cadet_id)
