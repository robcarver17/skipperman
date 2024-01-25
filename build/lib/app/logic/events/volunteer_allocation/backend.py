from app.data_access.data import data
from app.backend.load_and_save_wa_mapped_events import load_master_event
from app.logic.events.constants import CADET_ID
from app.logic.events.events_in_state import get_event_from_state
from app.logic.abstract_interface import abstractInterface
from app.objects.constants import missing_data, NoMoreData
from app.objects.events import Event
from app.objects.field_list import LIST_OF_VOLUNTEER_FIELDS

def any_volunteers_in_data_excluding_no_volunteer(event: Event, cadet_id: str) -> bool:
    volunteer_ids = volunteer_ids_associated_with_cadet(event=event, cadet_id=cadet_id)
    return len(volunteer_ids)>0


def any_volunteers_in_data_including_no_volunteer(event: Event, cadet_id: str) -> bool:
    volunteer_data = get_volunteer_data_for_event(event)
    volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(cadet_id)

    return len(volunteer_ids)>0


def volunteer_ids_associated_with_cadet(event: Event, cadet_id: str) -> list:
    volunteer_data = get_volunteer_data_for_event(event)
    volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(cadet_id)

    return volunteer_ids


def get_volunteer_data_for_event(event: Event):
    return data.data_list_of_volunteers_at_event.read(event_id=event.id)


def get_and_save_next_cadet_id(interface: abstractInterface) -> str:
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
    list_of_ids = list_of_cadet_ids_in_master_data(event)
    id = list_of_ids[0]

    print("Getting first ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_cadet_id_in_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    event = get_event_from_state(interface)
    list_of_ids = list_of_cadet_ids_in_master_data(event)
    current_index = list_of_ids.index(current_id)

    try:
        new_id = list_of_ids[current_index + 1]
    except:
        raise NoMoreData

    return new_id


def list_of_cadet_ids_in_master_data(event: Event) -> list:
    master_event = load_master_event(event)
    master_ids = master_event.list_of_cadet_ids
    master_ids.sort()

    return master_ids


def get_current_cadet_id(interface: abstractInterface) -> str:
    cadet_id = interface.get_persistent_value(CADET_ID)

    return cadet_id


def reset_current_cadet_id_store(interface: abstractInterface):
    interface.clear_persistent_value(CADET_ID)


number_of_volunteers_allowed = len(LIST_OF_VOLUNTEER_FIELDS)
VOLUNTEER_ID = 'volunteer_id'
def get_and_save_next_volunteer_index(interface: abstractInterface) -> int:
    volunteer_index = interface.get_persistent_value(VOLUNTEER_ID)
    if volunteer_index is missing_data:
        volunteer_index=0
    else:
        volunteer_index+=1
        if (volunteer_index+1)>number_of_volunteers_allowed:
            raise NoMoreData

    interface.set_persistent_value(VOLUNTEER_ID, volunteer_index)

    return volunteer_index

def clear_volunteer_index(interface: abstractInterface):
    interface.clear_persistent_value(VOLUNTEER_ID)