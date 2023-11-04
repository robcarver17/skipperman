from app.interface.html.html import Html
from app.interface.html.components import back_button_only_with_text
from app.interface.flask.state_for_action import StateDataForAction

from app.interface.events.utils import get_event_from_state
from app.interface.events.constants import ROW_IN_EVENT_DATA, WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE
from app.logic.events.remove_duplicates_from_mapped_wa_event_data import save_and_report_on_missing_data_from_mapped_wa_event_data, get_row_from_file_with_ids_and_possible_duplicates, add_new_unique_row_to_mapped_wa_event_data
from app.logic.events.load_and_save_wa_mapped_events import load_mapped_wa_event_data_without_duplicates, save_mapped_wa_event_data_without_duplicates

from app.objects.constants import missing_data, NoMoreData

def process_file_with_ids(
    state_data: StateDataForAction,
) -> Html:
    event = get_event_from_state(state_data)
    save_and_report_on_missing_data_from_mapped_wa_event_data(event)

    return process_updates_to_event_data(state_data)

def process_updates_to_event_data(state_data: StateDataForAction) -> Html:
    event = get_event_from_state(state_data)
    row_id = get_current_row_id_in_event_data(state_data)
    ## think carefully about order should be from bottom of original file which is top of this one?

    try:
        row_in_mapped_wa_event_with_id = get_row_from_file_with_ids_and_possible_duplicates(event, row_id=row_id)
    except NoMoreData:
        return action_to_take_on_finish(state_data)

    wa_event_data_without_duplicates = load_mapped_wa_event_data_without_duplicates(event)

    cadet_id = row_in_mapped_wa_event_with_id.cadet_id
    cadet_already_present = wa_event_data_without_duplicates.is_cadet_id_in_event(
        cadet_id
    )

    if cadet_already_present:
        return interactively_update_row_of_mapped_wa_event_data(
            state_data
        )

    else:
        # new cadet
        ## updates wa_event_data_without_duplicates in memory no return required
        add_new_row_to_mapped_wa_data_without_duplicates(event, row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id)
        increment_and_save_id_in_event_data(state_data)

        ## recursive until file finished
        return process_updates_to_event_data(state_data)

def interactively_update_row_of_mapped_wa_event_data(state_data: StateDataForAction) -> Html:
    ## display form with differences
    state_data.stage =WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE
    pass

def post_response_of_interactive_row_updating_of_mapped_wa_event_data(state_data: StateDataForAction) -> Html:
    ## Called by generate_page
    update_row_in_mapped_wa_data_without_duplicates()

def add_new_row_to_mapped_wa_data_without_duplicates(event, row_in_mapped_wa_event_with_id):
    wa_event_data_without_duplicates = load_mapped_wa_event_data_without_duplicates(event)

    add_new_unique_row_to_mapped_wa_event_data(
        row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id,
        wa_event_data_without_duplicates=wa_event_data_without_duplicates,
    )
    save_mapped_wa_event_data_without_duplicates(event=event,
                                                 wa_event_data_without_duplicates=wa_event_data_without_duplicates)

def update_row_in_mapped_wa_data_without_duplicates(event, new_row_in_mapped_wa_event_with_status):
    wa_event_data_without_duplicates = load_mapped_wa_event_data_without_duplicates(event)

    wa_event_data_without_duplicates.update_row(
        row_of_mapped_wa_event_data_with_id_and_status=new_row_in_mapped_wa_event_with_status
    )
    save_mapped_wa_event_data_without_duplicates(event=event,
                                                 wa_event_data_without_duplicates=wa_event_data_without_duplicates)


def action_to_take_on_finish(state_data: StateDataForAction) -> Html:
    ## for the sake of good order may be ignored
    state_data.clear_session_data_for_action_and_reset_stage()
    return back_button_only_with_text(
        state_data=state_data, some_text="Imported data for event"
    )


def increment_and_save_id_in_event_data(state_data: StateDataForAction):
    id = state_data.get_value(ROW_IN_EVENT_DATA)
    if id is missing_data:
        return 0

def get_current_row_id_in_event_data(state_data: StateDataForAction):
    id = state_data.get_value(ROW_IN_EVENT_DATA)
    if id is missing_data:
        return 0

