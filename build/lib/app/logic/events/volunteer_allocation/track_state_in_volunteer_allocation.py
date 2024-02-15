from app.backend.data.mapped_events import get_row_in_mapped_event_data_given_id
from app.backend.volunteers.volunteer_allocation import list_of_unique_volunteer_ids_in_identified_event_data

from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.import_wa.shared_state_tracking_and_data import get_current_row_id
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer
from app.backend.volunteers.volunter_relevant_information import get_relevant_information_for_volunteer
from app.objects.constants import missing_data, NoMoreData
from app.objects.events import Event
from app.objects.field_list import LIST_OF_VOLUNTEER_FIELDS


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
    row_id = get_current_row_id(interface)
    volunteer_index = get_volunteer_index(interface)
    event = get_event_from_state(interface)
    relevant_information = get_relevant_information_for_volunteer_given_details(
        row_id=row_id,
        volunteer_index=volunteer_index,
        event=event
    )


    return relevant_information

def get_relevant_information_for_volunteer_given_details(
    row_id: str,
        volunteer_index: int,
        event: Event
) -> RelevantInformationForVolunteer:

    row_in_mapped_event = get_row_in_mapped_event_data_given_id(event=event, row_id=row_id)

    relevant_information = get_relevant_information_for_volunteer(row_in_mapped_event=row_in_mapped_event, volunteer_index=volunteer_index, event=event)

    return relevant_information



VOLUNTEER_AT_EVENT_ID = "vol_at_ev_id"


def get_and_save_next_volunteer_id_in_mapped_event_data(interface: abstractInterface) -> str:
    current_id = get_current_volunteer_id_at_event(interface)
    if current_id is missing_data:
        new_id = get_first_volunteer_id_in_identified_event_data(interface)
    else:
        new_id = get_next_volunteer_id_in_identified_event_data(
            interface=interface, current_id=current_id
        )

    save_new_volunteer_id_at_event(interface=interface, new_id=new_id)

    return new_id


def get_first_volunteer_id_in_identified_event_data(interface: abstractInterface) -> str:

    list_of_ids = list_of_unique_volunteer_ids_in_identified_event_data(interface)
    id = list_of_ids[0]

    print("Getting first ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_volunteer_id_in_identified_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    list_of_ids = list_of_unique_volunteer_ids_in_identified_event_data(interface)
    current_index = list_of_ids.index(current_id)
    new_index = current_index+1

    try:
        new_id = list_of_ids[new_index]
    except:
        raise NoMoreData

    return new_id


def get_current_volunteer_id_at_event(interface: abstractInterface) -> str:
    return interface.get_persistent_value(VOLUNTEER_AT_EVENT_ID , default=missing_data)

def  save_new_volunteer_id_at_event(interface: abstractInterface, new_id):
    interface.set_persistent_value(VOLUNTEER_AT_EVENT_ID, new_id)

def reset_new_volunteer_id_at_event(interface: abstractInterface):
    interface.clear_persistent_value(VOLUNTEER_AT_EVENT_ID)



