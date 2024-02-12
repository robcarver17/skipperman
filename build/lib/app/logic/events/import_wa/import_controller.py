from typing import List, Union

from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.constants import *

from app.objects.abstract_objects.abstract_interface import abstractInterface, form_with_message_and_finished_button
from app.objects.events import Event, CADETS, VOLUNTEERS, GROUP_ALLOCATION, FOOD, CLOTHING, \
    get_event_attribute_given_container
from app.objects.constants import NoMoreData
from app.objects.abstract_objects.abstract_form import NewForm, Form


### KEEP TRACK OF WHICH IMPORT STAGES HAVE BEEN DONE, AND THEN CALLS NEW FORMS AS REQUIRED
def import_controller(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    return form_with_message_and_finished_button("deltas created", interface=interface)

    try:
        next_import = next_import_required_for_event(event=event, interface=interface)
    except NoMoreData:
        ### FIXME DELETE DELTA FILES
        return form_with_message_and_finished_button(
            "Finished importing WA data", interface=interface,
            set_stage_name_to_go_to_on_button_press=VIEW_EVENT_STAGE
        )

    form_name = IMPORTS_AND_FORM_NAMES[next_import]

    return NewForm(form_name)

def post_import_controller(interface):
    raise Exception("Should never get here")

ORDERED_LIST_OF_POSSIBLE_IMPORTS = [CADETS, VOLUNTEERS, GROUP_ALLOCATION, FOOD, CLOTHING]

IMPORTS_AND_FORM_NAMES = {
    CADETS: WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE,
    VOLUNTEERS: WA_VOLUNTEER_EXTRACTION_INITIALISE_IN_VIEW_EVENT_STAGE
}

NO_IMPORT_DONE_YET_INDEX = -1

def next_import_required_for_event(event: Event, interface: abstractInterface):
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
