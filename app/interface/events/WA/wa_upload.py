from app.interface.events.WA.utils import (
    get_form_for_wa_upload,
    verify_and_save_uploaded_wa_event_file,
    reset_stage_and_return_previous,
    upload_wa_file_and_save_as_raw_event_with_mapping,
)
from app.interface.events.utils import get_event_from_state
from app.interface.events.constants import UPLOAD_FILE_LABEL

from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.components import back_button_only_with_text

from app.logic.events.map_wa_files import verify_and_if_required_add_wa_mapping
from app.logic.events.load_wa_file import save_raw_event_upload_with_event_id


def display_form_wa_upload(state_data: StateDataForAction):
    ## no need to check post as always will be
    event = get_event_from_state(state_data)

    return get_form_for_wa_upload(event=event, state_data=state_data)


def post_response_to_wa_upload(state_data: StateDataForAction):
    ## no need to check post as always will be. Sent here from generate_page
    # get the event from the state
    button_pressed = state_data.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_LABEL:
        return respond_to_uploaded_file(state_data)
    else:
        return reset_stage_and_return_previous(state_data)


def respond_to_uploaded_file(state_data: StateDataForAction):
    try:
        upload_wa_file_and_save_as_raw_event_with_mapping(state_data)
    except Exception as e:
        ## revert to view specific event
        ## update stage only, keep event stored
        return reset_stage_and_return_previous(
            state_data=state_data, error_msg="Problem with file upload %s" % e
        )

    state_data.clear_session_data_for_action_and_reset_stage()

    return back_button_only_with_text(
        state_data=state_data, some_text="Uploaded file for event"
    )
