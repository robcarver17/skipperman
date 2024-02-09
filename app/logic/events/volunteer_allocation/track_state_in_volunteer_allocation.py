from app.backend.data.mapped_events import load_master_event
from app.backend.wa_import.update_master_event_data import get_row_in_master_event_for_cadet_id
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer
from app.backend.volunteers.volunter_relevant_information import get_relevant_information_for_volunteer
from app.objects.constants import missing_data, NoMoreData
from app.objects.events import Event
from app.objects.field_list import LIST_OF_VOLUNTEER_FIELDS

CADET_ID = "cadet_id"

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
    first_cadet_id = list_of_ids[0]

    print("Getting first ID %s from list %s " % (first_cadet_id, list_of_ids))

    return first_cadet_id


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
    cadet_id = interface.get_persistent_value(CADET_ID, default=missing_data)

    return cadet_id


def reset_current_cadet_id_store(interface: abstractInterface):
    interface.clear_persistent_value(CADET_ID)


number_of_volunteers_allowed = len(LIST_OF_VOLUNTEER_FIELDS)
VOLUNTEER_INDEX = 'volunteer_index'


def get_and_save_next_volunteer_index(interface: abstractInterface) -> int:
    volunteer_index = get_volunteer_index(interface)
    if volunteer_index is missing_data:
        volunteer_index=0
    else:
        volunteer_index+=1
        if (volunteer_index+1)>number_of_volunteers_allowed:
            raise NoMoreData

    interface.set_persistent_value(VOLUNTEER_INDEX, volunteer_index)

    return volunteer_index

def get_volunteer_index(interface:abstractInterface) -> int:
    return interface.get_persistent_value(VOLUNTEER_INDEX)


def clear_volunteer_index(interface: abstractInterface):
    interface.clear_persistent_value(VOLUNTEER_INDEX)



def get_relevant_information_for_current_volunteer(interface: abstractInterface) -> RelevantInformationForVolunteer:
    cadet_id = get_current_cadet_id(interface)
    volunteer_index = get_volunteer_index(interface)
    event = get_event_from_state(interface)
    row_in_master_event = get_row_in_master_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )

    relevant_information = get_relevant_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index)

    return relevant_information
