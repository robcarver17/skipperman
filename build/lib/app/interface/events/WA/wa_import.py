from app.interface.events.WA.process_staged_files.process_staged_file import (
    process_wa_staged_file_already_uploaded,
)
from app.interface.events.WA.utils import (
    reset_stage_and_return_previous,
    delete_staged_file_for_current_event,
)
from app.interface.flask.state_for_action import StateDataForAction


def display_view_for_specific_event_wa_import(state_data: StateDataForAction):
    try:
        ## deletes staged file if works ok
        return process_wa_staged_file_already_uploaded(state_data)
    except Exception as e:
        # will have to upload again
        delete_staged_file_for_current_event(state_data)
        return reset_stage_and_return_previous(
            state_data=state_data,
            error_msg="Problem with file import %s try uploading again" % e,
        )

