from typing import Union, Callable

from app.frontend.events.food.automatically_get_food_data import (
    display_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
)

from app.frontend.events.clothing.automatically_get_clothing_data_from_cadets import (
    display_call_to_update_cadet_clothing_at_event_during_import,
)

from app.frontend.events.cadets_at_event.interactively_update_records_of_cadets_at_event import (
    start_process_of_interactively_update_cadets_at_event,
)
from app.frontend.events.cadets_at_event.iteratively_identify_cadets_in_import_stage import (
    start_cadet_id_process,
)
from app.frontend.events.import_data.background_processses import display_call_to_update_background_data_during_import
from app.frontend.events.import_data.upload_event_file import display_form_upload_event_file
from app.frontend.events.volunteer_identification.add_volunteers_to_event import (
    display_add_volunteers_to_event,
)

from app.frontend.events.volunteer_identification.ENTRY_volunteer_identification import (
    begin_volunteer_identification_process,
)

from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.objects.utilities.exceptions import NoMoreData
from app.objects.abstract_objects.abstract_form import NewForm, Form

"""
Here are the stages that are called in order when new or updated registration data is available
"""
import_stages_in_order = [
    start_cadet_id_process,
    start_process_of_interactively_update_cadets_at_event,
    begin_volunteer_identification_process,
    display_add_volunteers_to_event,
    display_call_to_update_cadet_clothing_at_event_during_import,
    display_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
display_call_to_update_background_data_during_import
]


### KEEP TRACK OF WHICH IMPORT STAGES HAVE BEEN DONE, AND THEN CALLS NEW FORMS AS REQUIRED
def import_controller(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        next_import = next_import_required_for_event(interface=interface)
    except NoMoreData:
        interface.log_error("Finished importing WA data")
        clear_index_of_last_import_done_in_state(interface)
        return interface.get_new_display_form_for_parent_of_function(display_form_upload_event_file)

    print("Next import %s" % str(next_import))

    return interface.get_new_form_given_function(next_import)


def post_import_controller(interface):
    raise Exception("Should never get here")


## order matters, as other things rely on cadets
## Group allocation doesn't appear here since not done as an import, neithier do clothes or food which are done manually

NO_IMPORT_DONE_YET_INDEX = -1


def next_import_required_for_event(interface: abstractInterface) -> Callable:
    index_of_next_import = return_and_increment_import_state_index(interface)
    try:
        return import_stages_in_order[index_of_next_import]
    except IndexError:
        raise NoMoreData


LAST_IMPORT_DONE = "last_import"


def return_and_increment_import_state_index(interface: abstractInterface) -> int:
    last_import = get_index_of_last_import_done_in_state(interface)
    if last_import == NO_IMPORT_DONE_YET_INDEX:
        next_import = 0
    else:
        next_import = last_import + +1

    set_index_of_last_import_done_in_state(
        interface=interface, next_import_index=next_import
    )

    return next_import


def get_index_of_last_import_done_in_state(interface: abstractInterface) -> int:
    return int(interface.get_persistent_value(
        LAST_IMPORT_DONE, default=NO_IMPORT_DONE_YET_INDEX
    ))


def set_index_of_last_import_done_in_state(
    interface: abstractInterface, next_import_index: int
):
    interface.set_persistent_value(LAST_IMPORT_DONE, next_import_index)

def clear_index_of_last_import_done_in_state(
    interface: abstractInterface
):
    interface.clear_persistent_value(LAST_IMPORT_DONE)
