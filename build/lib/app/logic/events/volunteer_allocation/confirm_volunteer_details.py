from app.backend.data.volunteers import add_volunteer_connection_to_cadet_in_master_list_of_volunteers
from app.backend.form_utils import get_food_requirements_from_form, \
    get_availablity_from_form
from app.backend.volunteers.volunteer_allocation import get_volunteer_from_id, update_volunteer_food_at_event, update_volunteer_availability_at_event
from app.backend.data.volunteer_allocation import get_volunteer_at_event
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import  \
    get_relevant_information_for_current_volunteer, get_current_cadet_id
from app.backend.cadets import cadet_from_id
from app.logic.events.volunteer_allocation.volunteer_details_form_contents import get_header_text, \
    get_connection_checkbox, get_food_requirements_text, get_food_requirements_input_for_volunteer_at_event, \
    get_availablity_text, get_availability_checkbox_for_volunteer_at_event, FOOD_REQUIREMENTS, OTHER_FOOD, AVAILABILITY, \
    MAKE_CADET_CONNECTION, MAKE_CADET_CONNECTION_LABEL
from app.logic.events.constants import *
from app.logic.volunteers.volunteer_state import get_volunteer_id_selected_from_state
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.events import Event
from app.objects.food import FoodRequirements
from app.objects.day_selectors import DaySelector, no_days_selected

## once a volunteer is added, generate a form to capture / confirm availabilty and food preferences

## THIS IS NOT ROLE ALLOCATION

def display_form_confirm_volunteer_details(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event =get_event_from_state(interface)
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    relevant_information = get_relevant_information_for_current_volunteer(interface=interface)
    volunteer = get_volunteer_from_id(volunteer_id)

    header_text = get_header_text(interface=interface, volunteer=volunteer)
    connection_checkbox = get_connection_checkbox(interface=interface, volunteer=volunteer)

    food_requirements_text = get_food_requirements_text(relevant_information)
    food_requirements_input = get_food_requirements_input_for_volunteer_at_event(volunteer_at_event)
    available_text = get_availablity_text(relevant_information)
    available_checkbox = get_availability_checkbox_for_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)


    other_information = relevant_information.details.any_other_information

    return Form(ListOfLines([
        header_text,
        other_information,
        _______________,
        connection_checkbox,
        _______________,
        food_requirements_text,
        food_requirements_input,
        _______________,
        available_text,
        available_checkbox,
        _______________,
        Button(SAVE_CHANGES)
    ]))


def post_form_confirm_volunteer_details(interface: abstractInterface):
    form_ok = update_volunteer_at_event_with_form_contents_and_return_true_if_ok(interface)
    if not form_ok:
        return display_form_confirm_volunteer_details(interface)
    return continue_to_next_volunteer()

def update_volunteer_at_event_with_form_contents_and_return_true_if_ok(interface: abstractInterface) -> bool:

    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event =get_event_from_state(interface)
    availability = get_availablity_from_form(interface=interface, event=event, input_name=AVAILABILITY)
    food_requirement = get_food_requirements_from_form(interface=interface, checkbox_input_name =FOOD_REQUIREMENTS, other_input_name =OTHER_FOOD)
    okay_to_add_connection = get_connection_from_form(interface=interface)

    if no_days_selected(availability, possible_days=event.weekdays_in_event()):
        interface.log_error("No days selected for volunteer at event")
        return False

    update_volunteer_at_event_with_new_food_and_availability(event=event,
                                                             volunteer_id=volunteer_id,
                                                             availability=availability,
                                                             food_requirements=food_requirement)

    if okay_to_add_connection:
        add_cadet_connections_implicit_from_event_to_volunteer(volunteer_id=volunteer_id, interface=interface)

    return True

def get_connection_from_form(interface: abstractInterface):
    try:
        connection_tick_list = interface.value_of_multiple_options_from_form(MAKE_CADET_CONNECTION)
    except:
        ## already connected
        return False

    return MAKE_CADET_CONNECTION_LABEL in connection_tick_list

def update_volunteer_at_event_with_new_food_and_availability(volunteer_id: str, event: Event,
                                                             food_requirements: FoodRequirements,
                                                             availability: DaySelector):

    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)

    update_volunteer_food_at_event(volunteer_at_event=volunteer_at_event, food_requirements=food_requirements, event=event)
    update_volunteer_availability_at_event(volunteer_at_event=volunteer_at_event, availability=availability, event=event)

def continue_to_next_volunteer():
    ## Now loop to next volunteer for cadet
    return NewForm(WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_LOOP_IN_VIEW_EVENT_STAGE)



def add_cadet_connections_implicit_from_event_to_volunteer(interface: abstractInterface,
                                                           volunteer_id: str):

    volunteer =get_volunteer_from_id(volunteer_id)
    cadet_id = get_current_cadet_id(interface)
    cadet = cadet_from_id(cadet_id)
    add_volunteer_connection_to_cadet_in_master_list_of_volunteers(volunteer=volunteer,
                                                                   cadet=cadet)




