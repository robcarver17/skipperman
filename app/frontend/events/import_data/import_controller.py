from typing import Union, Callable

from app.frontend.events.food.automatically_get_food_data import (
    display_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
)

from app.frontend.events.clothing.automatically_get_clothing_data_from_cadets import (
    display_call_to_update_cadet_clothing_at_event_during_import,
)

from app.frontend.events.cadets_at_event.interactively_update_records_of_cadets_at_event import (
    display_form_interactively_update_cadets_at_event,
)
from app.frontend.events.cadets_at_event.iteratively_identify_cadets_in_import_stage import (
    display_form_identify_cadets_during_import,
)
from app.frontend.events.volunteer_identification.add_volunteers_to_event import (
    display_add_volunteers_to_event,
)

from app.frontend.events.volunteer_identification.ENTRY_volunteer_identification import (
    display_form_volunteer_identification,
)

from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)

from app.objects.exceptions import NoMoreData
from app.objects.abstract_objects.abstract_form import NewForm, Form

"""
Here are the stages that are called in order when new or updated registration data is available
"""
import_stages_in_order = [
    display_form_identify_cadets_during_import,
    display_form_interactively_update_cadets_at_event,
    display_form_volunteer_identification,
    display_add_volunteers_to_event,
    display_call_to_update_cadet_clothing_at_event_during_import,
    display_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
]


### KEEP TRACK OF WHICH IMPORT STAGES HAVE BEEN DONE, AND THEN CALLS NEW FORMS AS REQUIRED
def import_controller(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        next_import = next_import_required_for_event(interface=interface)
    except NoMoreData:
        return form_with_message_and_finished_button(
            "Finished importing WA data",
            interface=interface,
        )

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


def get_index_of_last_import_done_in_state(interface: abstractInterface):
    return interface.get_persistent_value(
        LAST_IMPORT_DONE, default=NO_IMPORT_DONE_YET_INDEX
    )


def set_index_of_last_import_done_in_state(
    interface: abstractInterface, next_import_index: int
):
    interface.set_persistent_value(LAST_IMPORT_DONE, next_import_index)
