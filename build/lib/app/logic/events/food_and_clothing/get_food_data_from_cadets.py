from typing import Union

from app.logic.events.food_and_clothing.get_food_data_from_volunteers import display_interactively_add_volunteer_food_to_event
from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.objects.food import guess_food_requirements_from_food_field

from app.backend.cadets import  cadet_name_from_id
from app.backend.food import is_cadet_with_id_already_at_event_with_food, add_new_cadet_with_food_to_event
from app.backend.forms.form_utils import get_food_requirements_input, get_food_requirements_from_form
from app.backend.wa_import.update_cadets_at_event import        get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active

from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import \
    get_and_save_next_cadet_id_in_event_data, clear_cadet_id_at_event, get_current_cadet_id_at_event
from app.objects.abstract_objects.abstract_buttons import SAVE_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.data_access.configuration.field_list import CADET_FOOD_PREFERENCE
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.logic.events.events_in_state import get_event_from_state


from app.objects.events import Event
from app.objects.constants import NoMoreData, DuplicateCadets
from app.objects.mapped_wa_event import RowInMappedWAEvent


def display_form_interactively_update_cadet_food_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is a post call

    clear_cadet_id_at_event(interface)

    return process_next_cadet_food_at_event(interface)


def process_next_cadet_food_at_event(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id_in_event_data(interface)
    except NoMoreData:
        clear_cadet_id_at_event(interface)
        return finished_looping_go_to_volunteer_food(interface)

    print("Current cadet id is %s" % cadet_id)

    return process_update_to_cadet_food_data(
        interface=interface, event=event, cadet_id=cadet_id
    )



def process_update_to_cadet_food_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    cadet_already_at_event = is_cadet_with_id_already_at_event_with_food(
        interface=interface,
        event=event, cadet_id=cadet_id
    )

    print("STATUS: ID %s already at event %s" % (cadet_id, str(cadet_already_at_event)))
    if cadet_already_at_event:
        ## WE DON'T DELETE FOOD IF A CADET IS UPDATED AND EG CANCELLED
        ## INSTEAD WE MASK FOOD WITH REGISTRATION DETAILS
        ## SO NO ACTION REQUIRED FOR EXISTING CADETS
        return process_next_cadet_food_at_event(interface)

    else:
        return process_update_to_cadet_new_to_event_with_food(
            event=event, cadet_id=cadet_id, interface=interface
        )



def process_update_to_cadet_new_to_event_with_food(
        interface: abstractInterface, event: Event, cadet_id: str
) -> Form:

    print("New row in master data for cadet with id %s" % cadet_id)

    try:
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id, event=event,
            raise_error_on_duplicate=True
        )
    except DuplicateCadets:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!"
            % cadet_name_from_id(cadet_id=cadet_id, interface=interface)
        )
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id, event=event,
            raise_error_on_duplicate=False ## try again this time allowing duplicates
        )
    except NoMoreData:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s vanished from WA mapping file - contact support"
            % cadet_name_from_id(cadet_id=cadet_id, interface=interface)
        )
        return process_next_cadet_food_at_event(interface)

    return display_form_for_new_cadet_food_requirements(
        interface=interface,
        event=event,
        relevant_row=relevant_row,
        cadet_id=cadet_id
    )

OTHER_FOOD = "other"
CHECKBOX_FOOD = "food_check"

def display_form_for_new_cadet_food_requirements(
        interface: abstractInterface,
        relevant_row: RowInMappedWAEvent,
                                                       event: Event,
            cadet_id: str) -> Form:

    food_from_registration = relevant_row.get_item(CADET_FOOD_PREFERENCE, '')
    food_guess = guess_food_requirements_from_food_field(food_from_registration)
    food_inputs = get_food_requirements_input(existing_food_requirements=food_guess,
                                              other_input_name=OTHER_FOOD,
                                              checkbox_input_name=CHECKBOX_FOOD,
                                              other_input_label="Other")

    cadet_name = cadet_name_from_id(interface=interface, cadet_id=cadet_id)

    button = Button(SAVE_BUTTON_LABEL)

    message = "Select food_and_clothing requirements for cadet %s, in form was %s" % (cadet_name, food_from_registration)

    form = Form(
        ListOfLines(
            [
                message,

            ]+food_inputs+[button]
        ).add_Lines()
    )

    return form


def post_form_interactively_update_food_for_cadets_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    food_requirements = get_food_requirements_from_form(interface=interface,
                                    other_input_name=OTHER_FOOD,
                                    checkbox_input_name=CHECKBOX_FOOD)

    cadet_id = get_current_cadet_id_at_event(interface)
    event = get_event_from_state(interface)

    add_new_cadet_with_food_to_event(interface=interface, event=event, food_requirements=food_requirements, cadet_id=cadet_id)
    interface.save_stored_items()
    interface.clear_stored_items()

    return process_next_cadet_food_at_event(interface)


def finished_looping_go_to_volunteer_food(interface: abstractInterface)-> NewForm:
    ## works even if no volunteers at event
    return interface.get_new_form_given_function(display_interactively_add_volunteer_food_to_event)

