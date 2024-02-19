from typing import Union

from app.backend.data.volunteers import get_sorted_list_of_volunteers
from app.backend.volunteers.volunteer_allocation import add_identified_volunteer, mark_volunteer_as_skipped
from app.backend.volunteers.volunter_relevant_information import get_volunteer_from_relevant_information

from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.import_wa.shared_state_tracking_and_data import get_and_save_next_row_id_in_mapped_event_data, \
    reset_row_id, get_current_row_id
from app.logic.events.volunteer_allocation.add_volunteers_to_event import \
    display_add_volunteers_to_event
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import clear_volunteer_index, \
    get_and_save_next_volunteer_index, get_relevant_information_for_current_volunteer, get_volunteer_index
from app.logic.events.volunteer_allocation.volunteer_identification import display_form_volunteer_selection_at_event
from app.logic.volunteers.volunteer_state import update_state_with_volunteer_id
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,

)

from app.logic.events.constants import *

from app.objects.constants import NoMoreData, missing_data
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer
from app.objects.volunteers import Volunteer


### First pass- loop over mapped data and identify volunteers
### Identified volunteer data object with row_id (include row data, volunteer index)


#WA_VOLUNTEER_IDENITIFICATION_INITIALISE_IN_VIEW_EVENT_STAGE
def display_form_volunteer_identification_initalise_loop(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## this only happens once, the rest of the time is a post call
    reset_row_id(interface)

    return next_row_of_volunteers(interface)

def next_row_of_volunteers(interface: abstractInterface)-> NewForm:
    return interface.get_new_form_given_function(display_form_volunteer_identification_from_mapped_event_data)


# WA_VOLUNTEER_IDENITIFICATION_LOOP_IN_VIEW_EVENT_STAGE
def display_form_volunteer_identification_from_mapped_event_data(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    print("Looping through identifying master event data volunteers")

    try:
        get_and_save_next_row_id_in_mapped_event_data(interface)
    except NoMoreData:
        print("Finished looping - next stage is to add details")
        goto_add_identified_volunteers_to_event(interface)

    return identify_volunteers_in_specific_row_initialise(interface=interface)



def identify_volunteers_in_specific_row_initialise(interface: abstractInterface) -> NewForm:
    clear_volunteer_index(interface)
    return next_volunteer_in_row(interface)


def next_volunteer_in_row(interface:abstractInterface)-> NewForm:
    return interface.get_new_form_given_function(identify_volunteers_in_specific_row_loop)

#WA_IDENTIFY_VOLUNTEERS_IN_SPECIFIC_ROW_LOOP_IN_VIEW_EVENT_STAGE
def identify_volunteers_in_specific_row_loop(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        get_and_save_next_volunteer_index(interface)
    except NoMoreData:
        return next_row_of_volunteers(interface)

    return add_specific_volunteer_at_event(interface=interface)


def add_specific_volunteer_at_event(interface: abstractInterface)-> Union[Form,NewForm]:
    event = get_event_from_state(interface)

    relevant_information = get_relevant_information_for_current_volunteer(interface)
    volunteer = get_volunteer_from_relevant_information(relevant_information.identify)

    list_of_volunteers = get_sorted_list_of_volunteers()
    matched_volunteer_with_id = list_of_volunteers.matching_volunteer(volunteer)

    if matched_volunteer_with_id is missing_data:
        print("Volunteer %s not matched" % str(volunteer))
        return display_volunteer_selection_form(interface)

    print("Volunteer %s matched id is %s" % (str(volunteer), matched_volunteer_with_id.id))
    return process_identification_when_volunteer_matched(
        interface=interface, volunteer = matched_volunteer_with_id,
        event=event
    )

def display_volunteer_selection_form(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_volunteer_selection_at_event)  ## different file


def process_identification_when_volunteer_matched(interface: abstractInterface, volunteer: Volunteer,
                                                   event: Event) -> Union[Form, NewForm]:

    current_row_id = get_current_row_id(interface)
    current_index =  get_volunteer_index(interface)

    print("Adding volunteer %s as identified for event %s" % (str(volunteer), str(event)))
    add_identified_volunteer(volunteer_id=volunteer.id,
                                event=event,
                                row_id = current_row_id,
                             volunteer_index = int(current_index))


    return next_volunteer_in_row(interface)



def goto_add_identified_volunteers_to_event(interface: abstractInterface)-> NewForm:
    return interface.get_new_form_given_function(display_add_volunteers_to_event)


### UNUSED POST FORMS - JUST IN CASE

def post_form_volunteer_identification_initialise(
    interface: abstractInterface,

) -> Union[Form, NewForm]:
    interface.log_error("Post form should not be reached - contact support")

    return form_with_message_and_finished_button("Post form should not be reached - contact support", interface=interface)

def post_form_volunteer_identification_looping(
            interface: abstractInterface,
    ) -> Union[Form, NewForm]:
        interface.log_error("Post form should not be reached - contact support")
        return form_with_message_and_finished_button("Post form should not be reached - contact support",
                                                     interface=interface)
def post_form_add_volunteers_to_cadet_initialise(interface: abstractInterface) -> Form:
    # should never be reached
    interface.log_error("Post form should not be reached - contact support")
    return form_with_message_and_finished_button("Post form should not be reached - contact support",
                                                 interface=interface)


def post_form_add_volunteers_to_cadet_loop(interface: abstractInterface) -> Form:
    # should never be reached
    interface.log_error("Post form should not be reached - contact support")
    return form_with_message_and_finished_button("Post form should not be reached - contact support",
                                                 interface=interface)


