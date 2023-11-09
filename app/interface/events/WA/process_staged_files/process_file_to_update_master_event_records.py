from copy import copy

from app.interface.html.html import Html
from app.interface.html.components import back_button_only_with_text, BACK_BUTTON_LABEL

from app.interface.flask.state_for_action import StateDataForAction

from app.interface.events.utils import get_event_from_state
from app.interface.events.view_events import display_view_of_events
from app.interface.events.constants import (
ROW_IN_EVENT_DATA, WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE,
USE_NEW_DATA, USE_DATA_IN_FORM, USE_ORIGINAL_DATA
)

from app.logic.events.load_and_save_wa_mapped_events import (
    load_master_event
)
from app.logic.events.update_master_event_data import \
    report_on_missing_data_from_mapped_wa_event_data_and_save_to_master_event, get_row_from_event_file_with_ids, \
    add_new_row_to_master_event_data, message_about_status_change

from app.objects.constants import  NoMoreData, missing_data
from app.objects.mapped_wa_event_with_ids import RowInMappedWAEventWithId
from app.objects.events import Event
from app.objects.master_event import get_row_of_master_event_from_mapped_row_with_idx_and_status
from app.objects.cadets import cadet_name_from_id

def process_file_to_update_master_event_records(state_data: StateDataForAction)-> Html:
    ## we do this now so if there is no interaction required when the back button
    ##   appears at the end we know how to post respond to it
    state_data.stage = WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE
    event = get_event_from_state(state_data)
    report_on_missing_data_from_mapped_wa_event_data_and_save_to_master_event(event)

    return process_updates_to_event_data(state_data)

def process_updates_to_event_data(state_data: StateDataForAction) -> Html:
    event = get_event_from_state(state_data)
    row_idx = get_current_row_id_in_event_data(state_data)

    try:
        row_in_mapped_wa_event_with_id = (
            get_row_from_event_file_with_ids(event, row_idx=row_idx)
        )
    except NoMoreData:
        return Html("Finished ") ## not actually used since nothing more to do

    if row_in_mapped_wa_event_with_id.cancelled_or_deleted:
        return iterate_to_next_row_of_mapped_wa_data(state_data)

    return process_update_to_next_row_of_event_data(
        state_data=state_data,
        event=event,
        row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
    )

def process_update_to_next_row_of_event_data(state_data: StateDataForAction,
                                             event: Event,
                                             row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId) ->Html:
    cadet_already_present_in_master_data = is_cadet_already_in_master_data(
        event=event,
        row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
    )

    if cadet_already_present_in_master_data:
        return process_update_to_existing_row_of_event_data(state_data=state_data,
                                                            event=event,
                                                            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id)
    else:
        # new cadet
        ## updates wa_event_data_without_duplicates in memory no return required
        add_new_row_to_master_event_data(
            event, row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
        return iterate_to_next_row_of_mapped_wa_data(state_data)

def is_cadet_already_in_master_data(event: Event,
                                row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId) -> bool:
    master_event = load_master_event(
        event
    )
    ## confirm isn't a deleted or cancelled
    cadet_id = row_in_mapped_wa_event_with_id.cadet_id
    cadet_already_present_in_master_data = master_event.is_cadet_id_in_event(
        cadet_id
    )

    return cadet_already_present_in_master_data


def process_update_to_existing_row_of_event_data(
    state_data: StateDataForAction,
    row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId,
    event: Event,
) -> Html:

    master_event = load_master_event(
        event
    )

    new_row_in_mapped_wa_event_with_status = (
        get_row_of_master_event_from_mapped_row_with_idx_and_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
    )
    existing_row_in_master_event = (
        master_event.get_row_with_id(
            new_row_in_mapped_wa_event_with_status.cadet_id
        )
    )

    if new_row_in_mapped_wa_event_with_status==existing_row_in_master_event:
        ## nothing to do
        print("No change to %s" % (existing_row_in_master_event))
        return iterate_to_next_row_of_mapped_wa_data(state_data)

    status_change_message = message_about_status_change(existing_row_in_master_event=existing_row_in_master_event,
                                                       new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)

    dict_of_dict_diffs = (
        existing_row_in_master_event.dict_of_row_diffs_in_rowdata(
            new_row_in_mapped_wa_event_with_status
        )
    )

    for key, diff in dict_of_dict_diffs.items():
        thing = (key, diff.old_value, diff.new_value)

def buttons_for_update_row():
    # USE_NEW_DATA, USE_DATA_IN_FORM, USE_ORIGINAL_DATA
    #


def post_response_of_interactive_row_updating_of_mapped_wa_event_data(
    state_data: StateDataForAction,
) -> Html:
    ## Called by generate_page
    last_button_pressed = state_data.last_button_pressed()

    if last_button_pressed ==BACK_BUTTON_LABEL:
        ## Needs to have back button even though one not created in form as we use when finished
        state_data.clear_session_data_for_action_and_reset_stage()
    # USE_NEW_DATA, USE_DATA_IN_FORM, USE_ORIGINAL_DATA

def iterate_to_next_row_of_mapped_wa_data(state_data: StateDataForAction)-> Html:
    ## we don't delete from the event data with ID, but increment a row marker
    increment_and_save_id_in_event_data(state_data)
    ## next row until file finished
    return process_updates_to_event_data(state_data)




def increment_and_save_id_in_event_data(state_data: StateDataForAction):
    id = get_current_row_id_in_event_data(state_data)
    id+=1
    state_data.set_value(ROW_IN_EVENT_DATA, id)

def get_current_row_id_in_event_data(state_data: StateDataForAction):
    id = state_data.get_value(ROW_IN_EVENT_DATA)
    if id is missing_data:
        return 0


