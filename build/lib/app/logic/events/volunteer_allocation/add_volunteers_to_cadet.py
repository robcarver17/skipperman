from app.backend.update_master_event_data import get_row_in_master_event_for_cadet_id
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.relevant_information import get_relevant_information_for_volunteer, \
    get_volunteer_from_relevant_information
from app.backend.volunteers import get_list_of_volunteers
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import clear_volunteer_index, \
    get_and_save_next_volunteer_index, get_current_cadet_id, save_allocated_volunteer_id
from app.backend.volunteer_allocation import add_volunteer_and_cadet_association
from typing import Union
from app.logic.events.volunteer_allocation.relevant_information import RelevantInformationForVolunteer
from app.logic.events.constants import *
from app.backend.volunteer_allocation import mark_cadet_as_been_processed_if_no_volunteers_available
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.logic.abstract_interface import abstractInterface
from app.objects.events import Event
from app.objects.volunteers import Volunteer


from app.objects.constants import NoMoreData

#WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_INIT_IN_VIEW_EVENT_STAGE
def display_form_add_volunteers_to_cadet_initialise(interface: abstractInterface) -> Form:
    clear_volunteer_index(interface)

    return display_form_add_volunteers_to_cadet_loop(interface)

#WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_LOOP_IN_VIEW_EVENT_STAGE
def display_form_add_volunteers_to_cadet_loop(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        volunteer_index = get_and_save_next_volunteer_index(interface)
    except NoMoreData:
        cadet_id = get_current_cadet_id(interface)
        event = get_event_from_state(interface)
        ## This is so we don't bother processing them again next tinme
        mark_cadet_as_been_processed_if_no_volunteers_available(cadet_id=cadet_id, event=event)

        return NewForm(WA_VOLUNTEER_EXTRACTION_LOOP_IN_VIEW_EVENT_STAGE)

    return add_specific_volunteer_for_cadet_at_event(interface=interface, volunteer_index=volunteer_index)

def add_specific_volunteer_for_cadet_at_event(interface: abstractInterface, volunteer_index: int)-> Union[Form,NewForm]:

    cadet_id = get_current_cadet_id(interface)
    event = get_event_from_state(interface)
    row_in_master_event = get_row_in_master_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )

    relevant_information = get_relevant_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index)
    volunteer = get_volunteer_from_relevant_information(relevant_information.identify)

    list_of_volunteers = get_list_of_volunteers()
    if volunteer in list_of_volunteers:
        ## MATCHED, WE NEED TO GET THE ID
        matched_volunteer_with_id = list_of_volunteers.matching_volunteer(volunteer)
        print("Volunteer %s matched id is %s" % (str(volunteer), matched_volunteer_with_id.id))
        return process_update_when_volunteer_matched(
            interface=interface, volunteer = matched_volunteer_with_id,
            cadet_id=cadet_id,
            event=event,
            relevant_information=relevant_information
        )
    else:
        ## NOT MATCHED
        print("Volunteer %s not matched" % str(volunteer))
        return NewForm(WA_VOLUNTEER_EXTRACTION_SELECTION_IN_VIEW_EVENT_STAGE)

def process_update_when_volunteer_matched(interface: abstractInterface, volunteer: Volunteer, relevant_information: RelevantInformationForVolunteer,
                                          cadet_id: str, event: Event) -> Union[Form, NewForm]:

    add_volunteer_and_cadet_association(volunteer_id=volunteer.id,
                                        cadet_id=cadet_id,
                                        event_id=event.id,
                                        relevant_information=relevant_information)
    save_allocated_volunteer_id(interface=interface, id=volunteer.id)

    return NewForm(WA_VOLUNTEER_EXTRACTION_ADD_DETAILS_IN_VIEW_EVENT_STAGE)


def post_form_add_volunteers_to_cadet_initialise(interface: abstractInterface) -> Form:
    # should never be reached
    pass

def post_form_add_volunteers_to_cadet_loop(interface: abstractInterface) -> Form:
    # should never be reached
    pass
