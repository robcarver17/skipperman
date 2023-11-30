from typing import Union

from app.logic.forms_and_interfaces.abstract_form import Form, NewForm
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import UPLOAD_FILE_BUTTON_LABEL, WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE
from app.logic.events.import_wa.upload_event_file import get_form_for_wa_upload_with_prompt,upload_wa_file_and_save_as_raw_event_with_mapping
from app.logic.events.utilities import get_event_from_state
from app.objects.events import Event

def display_form_update_existing_event(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    return get_form_for_wa_upload(event=event)

def get_form_for_wa_upload(event: Event
) -> Union[Form, NewForm]:
    return get_form_for_wa_upload_with_prompt(
        "Select exported WA file for event %s to replace existing data" % str(event)
    )



def post_form_uupdate_existing_event(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_BUTTON_LABEL:
        return respond_to_uploaded_file_when_updating(interface)
    else:
        interface.log_error("Uknown button %s pressed" % button_pressed)
        return initial_state_form

def respond_to_uploaded_file_when_updating(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        upload_wa_file_and_save_as_raw_event_with_mapping(interface)
    except Exception as e:
        ## revert to view events
        interface.log_error("Problem with file upload %s" % e)
        return initial_state_form

    return NewForm(WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE)



