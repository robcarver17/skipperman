from typing import List, Union, Callable

from app.logic.events.cadets_at_event.iteratively_add_cadet_ids_in_wa_import_stage import \
    display_form_add_cadet_ids_during_import
from app.logic.events.events_in_state import get_event_from_state

from app.logic.events.volunteer_allocation.volunteer_identification import \
    display_form_volunteer_identification_initalise_loop

from app.objects.abstract_objects.abstract_interface import abstractInterface, form_with_message_and_finished_button
from app.objects.events import Event, CADETS, VOLUNTEERS, GROUP_ALLOCATION, FOOD, CLOTHING, \
    get_event_attribute_given_container
from app.objects.constants import NoMoreData
from app.objects.abstract_objects.abstract_form import NewForm, Form


### KEEP TRACK OF WHICH IMPORT STAGES HAVE BEEN DONE, AND THEN CALLS NEW FORMS AS REQUIRED
def import_controller(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    try:
        next_import = next_import_required_for_event(event=event, interface=interface)
    except NoMoreData:
        return form_with_message_and_finished_button(
            "Finished importing WA data", interface=interface,
            function_whose_parent_go_to_on_button_press=import_controller
        )

    function = IMPORTS_AND_FUNCTION_NAMES[next_import]

    return interface.get_new_form_given_function(function)

def post_import_controller(interface):
    raise Exception("Should never get here")

## order matters, as other things rely on cadets
## Group allocation doesn't appear here
ORDERED_LIST_OF_POSSIBLE_IMPORTS = [CADETS, VOLUNTEERS]

#ORDERED_LIST_OF_POSSIBLE_IMPORTS = [CADETS, VOLUNTEERS, #GROUP_ALLOCATION,
#                                     FOOD, CLOTHING]

IMPORTS_AND_FUNCTION_NAMES = {
    CADETS: display_form_add_cadet_ids_during_import,
    VOLUNTEERS: display_form_volunteer_identification_initalise_loop
}

NO_IMPORT_DONE_YET_INDEX = -1

def next_import_required_for_event(event: Event, interface: abstractInterface) -> str:
    all_imports_required = imports_required_given_event(event)
    index_of_next_import = return_and_increment_import_state_index(interface)
    try:
        input_name = all_imports_required[index_of_next_import]
    except IndexError:
        raise NoMoreData

    return input_name


def imports_required_given_event(event: Event) -> List[str]:
    return [contained_in for contained_in in
            ORDERED_LIST_OF_POSSIBLE_IMPORTS
            if getattr(event, get_event_attribute_given_container(contained_in), False)]


LAST_IMPORT_DONE = "last_import"

def return_and_increment_import_state_index(interface: abstractInterface) -> int:
    last_import = get_index_of_last_import_done_in_state(interface)
    if last_import==NO_IMPORT_DONE_YET_INDEX:
        next_import = 0
    else:
        next_import = last_import++1

    set_index_of_last_import_done_in_state(interface=interface, next_import_index=next_import)

    return next_import

def get_index_of_last_import_done_in_state(interface: abstractInterface):
    return interface.get_persistent_value(LAST_IMPORT_DONE, default=NO_IMPORT_DONE_YET_INDEX)

def set_index_of_last_import_done_in_state(interface: abstractInterface, next_import_index: int):
    interface.set_persistent_value(LAST_IMPORT_DONE, next_import_index)
