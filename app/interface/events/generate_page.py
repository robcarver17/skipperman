from app.interface.events.initial_stage import generate_initial_stage_html_for_events
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import Html
from app.interface.flask.flash import html_error

from app.interface.events.constants import (
    ADD_EVENT_STAGE,
    VIEW_EVENT_STAGE,
    WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE,
    WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE,
    WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE,
    WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE,
    WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE,
WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE
)
from app.interface.events.add_event import display_view_for_add_event
from app.interface.events.specific_event.view_specific_event_post import post_view_of_selected_event
from app.interface.events.WA.wa_upload import post_response_to_wa_upload
from app.interface.events.WA.wa_import import display_view_for_specific_event_wa_import
from app.interface.events.WA.process_staged_files.wa_iteratively_add_cadet_ids import (
    post_response_when_adding_cadet_ids_to_event,
)
from app.interface.events.WA.wa_update import post_response_to_wa_update
from app.interface.events.WA.process_staged_files.process_file_to_remove_duplicates import (
    post_response_of_removing_specific_duplicates_from_mapped_wa_event_data
)
from app.interface.events.WA.process_staged_files.process_file_to_update_master_event_records import post_response_of_interactive_row_updating_of_mapped_wa_event_data

def generate_event_pages(state_data: StateDataForAction) -> Html:
    stage = state_data.stage
    if state_data.is_initial_stage:
        return generate_initial_stage_html_for_events(state_data)
    elif stage == ADD_EVENT_STAGE:
        return display_view_for_add_event(state_data)
    elif stage == VIEW_EVENT_STAGE:
        return post_view_of_selected_event(state_data)

    ## Following are available through view event stage
    elif stage == WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE:
        return post_response_to_wa_upload(state_data)
    elif stage == WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE:
        return display_view_for_specific_event_wa_import(state_data)
    elif stage == WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
        return post_response_to_wa_update(state_data)

    ## Following is called during import or update
    elif stage == WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE:
        return post_response_when_adding_cadet_ids_to_event(state_data)

    elif stage == WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE:
        return post_response_of_removing_specific_duplicates_from_mapped_wa_event_data(
            state_data
        )
    elif stage == WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE:
        return post_response_of_interactive_row_updating_of_mapped_wa_event_data(
            state_data
        )

    else:
        return html_error(
            "Stage %s not recognised something has gone horribly wrong"
            % state_data.stage
        )


