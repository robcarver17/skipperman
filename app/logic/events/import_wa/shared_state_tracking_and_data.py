from app.backend.data.mapped_events import load_mapped_wa_event, save_mapped_wa_event
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import missing_data, NoMoreData
from app.objects.events import Event
from app.objects.mapped_wa_event import RowInMappedWAEvent

ROW_ID = "row_id"


def get_and_save_next_row_id_in_mapped_event_data(interface: abstractInterface) -> str:
    current_id = get_current_row_id(interface)
    if current_id is missing_data:
        new_id = get_first_row_id_in_event_data(interface)
    else:
        new_id = get_next_row_id_in_event_data(
            interface=interface, current_id=current_id
        )

    save_new_row_id(interface=interface, new_id=new_id)

    return new_id


def get_first_row_id_in_event_data(interface: abstractInterface) -> str:
    list_of_ids = list_of_row_ids_in_mapped_event_data(interface)
    id = list_of_ids[0]

    print("Getting first ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_row_id_in_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    list_of_ids = list_of_row_ids_in_mapped_event_data(interface)
    current_index = list_of_ids.index(current_id)
    new_index = current_index+1

    try:
        new_id = list_of_ids[new_index]
    except:
        raise NoMoreData

    print("Getting next ID %s (index %d) from list %s was %s (index %d)" % (new_id, new_index, list_of_ids, current_id, current_index))


    return new_id


def list_of_row_ids_in_mapped_event_data(interface: abstractInterface) -> list:
    event = get_event_from_state(interface)

    event_delta = load_mapped_wa_event(event)

    all_ids = event_delta.list_of_row_ids()

    return all_ids


def get_current_row_id(interface: abstractInterface) -> str:
    return interface.get_persistent_value(ROW_ID, default=missing_data)

def save_new_row_id(interface: abstractInterface, new_id):
    interface.set_persistent_value(ROW_ID, new_id)

def clear_row_in_state(interface: abstractInterface):
    interface.clear_persistent_value(ROW_ID)

def remove_row_id_from_current_mapped_event(interface: abstractInterface, row_id: str):
    event = get_event_from_state(interface)

    event_data = load_mapped_wa_event(event)
    event_data.pop_id(row_id)
    save_mapped_wa_event(event=event, mapped_wa_event_data=event_data)

def add_rows_to_current_mapped_event(interface: abstractInterface, new_row: RowInMappedWAEvent):
    event = get_event_from_state(interface)

    event_data = load_mapped_wa_event(event)
    event_data.append(new_row)
    save_mapped_wa_event(event=event, mapped_wa_event_data=event_data)
