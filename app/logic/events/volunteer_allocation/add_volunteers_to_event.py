from typing import Union, List

from app.backend.volunteers.volunteer_allocation import list_of_identified_volunteers_with_volunteer_id, \
    get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet, \
    update_volunteer_at_event_with_associated_cadet_id
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.backend.data.volunteer_allocation import is_volunteer_already_at_event
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.add_volunteers_process_form import \
    add_volunteer_at_event_with_form_contents_and_return_true_if_ok
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import \
    reset_new_volunteer_id_at_event, \
    get_and_save_next_volunteer_id_in_mapped_event_data, get_current_volunteer_id_at_event, \
    get_relevant_information_for_volunteer_given_details
from app.logic.events.volunteer_allocation.add_volunteer_to_event_form_contents import get_header_text, \
    get_connection_checkbox, get_availablity_text, get_availability_checkbox_for_volunteer_at_event_based_on_relevant_information, \
    get_any_other_information_text, get_any_other_information_input, get_preferred_duties_text, \
    get_preferred_duties_input, get_same_or_different_text, get_same_or_different_input
from app.logic.events.constants import *
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.constants import NoMoreData
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer


## once a volunteer is added, generate a form to capture / confirm availabilty and food preferences

## THIS IS NOT ROLE ALLOCATION
#VOLUNTEER_DETAILS_INITIALISE_IN_VIEW_EVENT_STAGE
def initialise_loop_over_volunteers_identifed_in_event(interface: abstractInterface)  -> Union[Form, NewForm]:
    reset_new_volunteer_id_at_event(interface)

    return loop_over_volunteers_identified_in_event(interface)

##  Next, compare identified volunteers with volunteers allocated to event - if new then add volunteer at event with volunteer details
###  Note, for availability show the user the availability for all connected cadets and relevant rows in case it's different....?

#VOLUNTEER_DETAILS_LOOP_IN_VIEW_EVENT_STAGE
def loop_over_volunteers_identified_in_event(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        get_and_save_next_volunteer_id_in_mapped_event_data(interface)
    except NoMoreData:
        return return_to_controller(interface)

    return display_form_for_volunteer_details(interface)


def process_identified_volunteer_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    volunteer_id = get_current_volunteer_id_at_event(interface)
    event =get_event_from_state(interface)
    already_added = is_volunteer_already_at_event(volunteer_id=volunteer_id, event=event)

    if already_added:
        action_when_volunteer_already_at_event(event=event, volunteer_id=volunteer_id)
        ## Next volunteer
        return next_volunteer(interface)
    else:
        return display_form_for_volunteer_details(interface)


def action_when_volunteer_already_at_event(event: Event, volunteer_id: str):
    ## If a new volunteer is added
    list_of_associated_cadet_id = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        event=event, volunteer_id=volunteer_id)
    update_volunteer_at_event_with_associated_cadet_id(list_of_associated_cadet_id=list_of_associated_cadet_id,
                                                       volunteer_id=volunteer_id,
                                                       event=event)


def display_form_for_volunteer_details(interface: abstractInterface)-> Form:

    volunteer_id = get_current_volunteer_id_at_event(interface)
    volunteer = get_volunteer_from_id(volunteer_id)
    event =get_event_from_state(interface)

    list_of_relevant_information = get_list_of_relevant_information(volunteer_id=volunteer_id, event=event)

    header_text = get_header_text(event=event, volunteer=volunteer)

    connection_checkbox = get_connection_checkbox( volunteer=volunteer,
                                                  event=event)

    any_other_information_text  = get_any_other_information_text(list_of_relevant_information=list_of_relevant_information)
    any_other_information_input  = get_any_other_information_input(list_of_relevant_information=list_of_relevant_information)

    preferred_duties_text  = get_preferred_duties_text(list_of_relevant_information=list_of_relevant_information)
    preferred_duties_input  = get_preferred_duties_input(list_of_relevant_information=list_of_relevant_information)

    same_or_different_text  = get_same_or_different_text(list_of_relevant_information=list_of_relevant_information)
    same_or_different_input  = get_same_or_different_input(list_of_relevant_information=list_of_relevant_information)

    available_text = get_availablity_text(list_of_relevant_information=list_of_relevant_information)
    available_checkbox = get_availability_checkbox_for_volunteer_at_event_based_on_relevant_information(list_of_relevant_information=list_of_relevant_information, event=event)


    return Form(ListOfLines([
        header_text,
        _______________,
        connection_checkbox,
        _______________,
        available_text,
        available_checkbox,
        _______________,
        any_other_information_text,
        any_other_information_input,
        _______________,
        preferred_duties_text,
        preferred_duties_input,
        _______________,
        same_or_different_text,
        same_or_different_input,
        _______________,
        Button(SAVE_CHANGES)
    ]))


def get_list_of_relevant_information(volunteer_id: str, event: Event) -> List[RelevantInformationForVolunteer]:

    list_of_identified_volunteers = list_of_identified_volunteers_with_volunteer_id(volunteer_id=volunteer_id, event=event) ## can appear more than once

    list_of_relevant_information = [get_relevant_information_for_volunteer_given_details(
        row_id=identified_volunteer.row_id,
        volunteer_index=identified_volunteer.volunteer_index,
        event=event
            ) for identified_volunteer in list_of_identified_volunteers]

    return list_of_relevant_information

def post_form_confirm_volunteer_details(interface: abstractInterface):
    form_ok = add_volunteer_at_event_with_form_contents_and_return_true_if_ok(interface)
    if not form_ok:
        return display_form_for_volunteer_details(interface)
    return next_volunteer(interface)

def return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(initialise_loop_over_volunteers_identifed_in_event)

def next_volunteer(interface: abstractInterface)-> NewForm:
    return interface.get_new_display_form_given_function(loop_over_volunteers_identified_in_event)
