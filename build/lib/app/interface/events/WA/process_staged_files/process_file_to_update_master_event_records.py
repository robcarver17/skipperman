from app.web.events.WA.process_staged_files.forms_interactively_update_modified_event_records import \
    display_form_for_update_to_existing_row_of_event_data, update_mapped_wa_event_data_with_new_data, \
    update_mapped_wa_event_data_with_form_data,increment_and_save_id_in_event_data, get_current_row_id_in_event_data


from app.web.html.html import Html
from app.web.events.WA.utils import (
    reset_stage_and_return_previous,
)
from app.web.flask.state_for_action import StateDataForAction

from app.web.events.utils import get_event_from_state
from app.web.events.constants import (
    USE_NEW_DATA, USE_DATA_IN_FORM, USE_ORIGINAL_DATA
)

from app.backend.data.mapped_events import load_master_event
from app.backend.wa_import.update_master_event_data import \
    report_on_missing_data_from_mapped_wa_event_data_and_save_to_master_event, get_row_from_event_file_with_ids, \
    add_new_row_to_master_event_data

from app.objects.constants import  NoMoreData
from app.objects.mapped_wa_event_with_ids import RowInMappedWAEventWithId
from app.objects.events import Event
from app.objects.master_event import get_row_of_master_event_from_mapped_row_with_idx_and_status


def process_file_to_update_master_event_records(state_data: StateDataForAction)-> Html:
    input("Press enter to continue")

    event = get_event_from_state(state_data)
    print("Now updating group_allocations which are missing")
    report_on_missing_data_from_mapped_wa_event_data_and_save_to_master_event(event)

    return process_updates_to_master_event_data(state_data)

def process_updates_to_master_event_data(state_data: StateDataForAction) -> Html:
    print("Looping through updating master event data")
    input("Press enter to continue")
    event = get_event_from_state(state_data)
    row_idx = get_current_row_id_in_event_data(state_data)

    try:
        row_in_mapped_wa_event_with_id = (
            get_row_from_event_file_with_ids(event, row_idx=row_idx)
        )
    except NoMoreData:
        print("Finished looping")
        return action_when_finished(state_data=state_data)

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
        print("Not a new cadet")
        return process_update_to_existing_row_of_event_data(state_data=state_data,
                                                            event=event,
                                                            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id)
    else:
        # new cadet
        ## updates wa_event_data_without_duplicates in memory no return required
        print("New cadet, adding to master event data %s" % str(row_in_mapped_wa_event_with_id))
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
        print("No change to %s" % (str(existing_row_in_master_event)))
        return iterate_to_next_row_of_mapped_wa_data(state_data)
    else:
        print("Data has changed displaying form")
        return display_form_for_update_to_existing_row_of_event_data(state_data=state_data,
                                                                     existing_row_in_master_event=existing_row_in_master_event,
                                                                     new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)


def post_response_of_interactive_row_updating_of_mapped_wa_event_data(
    state_data: StateDataForAction,
) -> Html:
    ## Called by generate_page
    last_button_pressed = state_data.last_button_pressed()
    if last_button_pressed == USE_ORIGINAL_DATA:
        ## nothing to do, no change to master file
        print("Using original data")
    elif last_button_pressed==USE_NEW_DATA:
        print("using new data")
        update_mapped_wa_event_data_with_new_data(state_data)
    elif last_button_pressed==USE_DATA_IN_FORM:
        print("Updating from form data")
        update_mapped_wa_event_data_with_form_data(state_data)

    return iterate_to_next_row_of_mapped_wa_data(state_data)


def iterate_to_next_row_of_mapped_wa_data(state_data: StateDataForAction)-> Html:
    ## we don't delete from the event data with ID, but increment a row marker
    increment_and_save_id_in_event_data(state_data)
    ## next row until file finished
    return process_updates_to_master_event_data(state_data)

def action_when_finished(state_data: StateDataForAction):
    ## nothing more required and clear up handled by calling functions
    return reset_stage_and_return_previous(
        state_data=state_data,
        log_msg="File import_wa done"
    )

