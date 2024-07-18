from app.OLD_backend.data.mapped_events import MappedEventsData
from app.logic.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.exceptions import missing_data, NoMoreData

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


def get_next_row_id_in_event_data(interface: abstractInterface, current_id: str) -> str:
    list_of_ids = list_of_row_ids_in_mapped_event_data(interface)
    current_index = list_of_ids.index(current_id)
    new_index = current_index + 1

    try:
        new_id = list_of_ids[new_index]
    except:
        raise NoMoreData

    print(
        "Getting next ID %s (index %d) from list %s was %s (index %d)"
        % (new_id, new_index, list_of_ids, current_id, current_index)
    )

    return new_id


def list_of_row_ids_in_mapped_event_data(interface: abstractInterface) -> list:
    mapped_events_data = MappedEventsData(interface.data)
    event = get_event_from_state(interface)
    all_ids = mapped_events_data.get_list_of_row_ids_for_event(event)

    return all_ids


def get_current_row_id(interface: abstractInterface) -> str:
    return interface.get_persistent_value(ROW_ID, default=missing_data)


def save_new_row_id(interface: abstractInterface, new_id):
    interface.set_persistent_value(ROW_ID, new_id)


def clear_row_in_state(interface: abstractInterface):
    interface.clear_persistent_value(ROW_ID)
