from app.web.events.WA.utils import (
    reset_stage_and_return_previous,
)
from app.web.events.WA.wa_import_logic import upload_wa_file_and_save_as_raw_event_with_mapping, \
    verify_and_save_uploaded_wa_event_file
from app.web.events.WA.wa_forms import get_form_for_wa_upload
from app.web.events.utils import get_event_from_state
from app.web.events.constants import UPLOAD_FILE_BUTTON_LABEL

from app.web.flask.state_for_action import StateDataForAction
from app.web.html.components import back_button_only_with_text

def display_view_for_specific_event_wa_upload(state_data: StateDataForAction):
    ## no need to check post as always will be
    event = get_event_from_state(state_data)

    return get_form_for_wa_upload(event=event, state_data=state_data)


def post_response_to_wa_upload(state_data: StateDataForAction):
    ## no need to check post as always will be. Sent here from generate_page
    # get the event from the state
    button_pressed = state_data.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_BUTTON_LABEL:
        return respond_to_uploaded_file(state_data)
    else:
        return reset_stage_and_return_previous(state_data)


def respond_to_uploaded_file(state_data: StateDataForAction):
    try:
        upload_wa_file_and_save_as_raw_event_with_mapping(state_data)
    except Exception as e:
        ## revert to view events
        return reset_stage_and_return_previous(
            state_data=state_data, error_msg="Problem with file upload %s" % e
        )

    return reset_stage_and_return_previous(
        state_data=state_data,
        log_msg="File upload done"
    )