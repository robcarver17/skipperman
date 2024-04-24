from typing import Union

from app.logic.events.import_wa.import_wa_file import display_form_import_event_file
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.constants import *
from app.logic.events.import_wa.upload_event_file import (
    get_form_for_wa_upload_with_prompt,
    verify_uploaded_wa_file_and_save_as_staged_file,
)
from app.logic.events.events_in_state import get_event_from_state
from app.objects.events import Event
from app.web.html.forms import BACK_BUTTON_LABEL


def display_form_update_existing_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    return get_form_for_wa_upload(event=event)


def get_form_for_wa_upload(event: Event) -> Union[Form, NewForm]:
    return get_form_for_wa_upload_with_prompt(
        "Select exported WA file for event %s to replace existing data" % str(event)
    )


def post_form_update_existing_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_BUTTON_LABEL:
        return respond_to_uploaded_file_when_updating(interface)
    elif button_pressed==BACK_BUTTON_LABEL:
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)

def respond_to_uploaded_file_when_updating(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        verify_uploaded_wa_file_and_save_as_staged_file(interface)
    except Exception as e:
        ## revert to view events
        interface.log_error("Problem with file upload %s" % e)
        return previous_form(interface)

    return import_event_file(interface)

def import_event_file(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_import_event_file)



def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_update_existing_event)

