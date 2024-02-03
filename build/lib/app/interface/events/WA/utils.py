from app.web.events.utils import get_event_from_state
from app.web.events.view_events import display_view_of_events
from app.web.flask.flash import flash_error, flash_log
from app.web.flask.state_for_action import StateDataForAction

from app.backend.wa_import.load_wa_file import (
    delete_raw_event_upload_with_event_id,
)


def reset_stage_and_return_previous(
    state_data: StateDataForAction, error_msg: str = "",
        log_msg: str=""
):
    if error_msg is not "":
        flash_error(error_msg)
    if log_msg is not "":
        flash_log(log_msg)
    state_data.clear_session_data_for_action_and_reset_stage()
    return display_view_of_events(state_data)


def delete_staged_file_for_current_event(state_data: StateDataForAction):
    event = get_event_from_state(state_data)
    delete_raw_event_upload_with_event_id(event.id)
