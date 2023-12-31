from app.interface.events.WA.process_staged_files.wa_add_or_select_existing_cadet import (
    get_add_or_select_existing_cadet_form,
)
from app.objects.constants import NoMoreData

from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import  Html
from app.interface.cadets.add_cadet import (
    add_cadet_from_form_to_data,
)
from app.interface.cadets.view_specific_cadet import (
    confirm_cadet_exists,
    get_cadet_from_list_of_cadets,
)
from app.interface.events.WA.process_staged_files.process_file_to_remove_duplicates import (
    process_file_with_ids_to_remove_duplicate_cadets,
)
from app.interface.events.utils import get_event_from_state
from app.interface.events.constants import (
    WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE,
    CHECK_CADET_BUTTON_LABEL,
    FINAL_CADET_ADD_BUTTON_LABEL,
    SEE_ALL_CADETS_BUTTON_LABEL,
    SEE_SIMILAR_CADETS_ONLY_LABEL,
)

from app.logic.events.backend.add_cadet_ids_to_mapped_wa_event_data import (
    get_first_unmapped_row_for_event,
    add_row_data_with_id_included_and_delete_from_unmapped_data,
    get_cadet_data_from_row_of_mapped_data_no_checks,
)
from app.logic.cadets.backend import get_list_of_cadets

from app.objects.mapped_wa_event_no_ids import RowInMappedWAEventNoId
from app.objects.cadets import Cadet

header_text = "Looks like a new cadet in the WA entry file. You can edit them and then add them to the existing list of cadets, or choose an existing cadet instead (avoid creating duplicates!)"


def process_rows_of_unmapped_data_and_proceed_to_process_file_with_ids(
    state_data: StateDataForAction,
) -> Html:
    event = get_event_from_state(state_data)
    print("Looping through allocating IDs on WA file without IDs")
    input("Press enter to continue")

    try:
        next_row = get_first_unmapped_row_for_event(event)
        print("On row %s" % str(next_row))
        return process_next_row(next_row=next_row, state_data=state_data)
    except NoMoreData:
        print("Finished looping through allocating IDs")
        return action_when_reached_end_of_data(state_data)


def process_next_row(
    next_row: RowInMappedWAEventNoId, state_data: StateDataForAction
) -> Html:
    try:
        cadet = get_cadet_data_from_row_of_mapped_data_no_checks(next_row)
    except Exception as e:
        ## Mapping has gone badly wrong, or date field corrupted
        raise Exception("Error code %s cannot identify cadet from row %s: file is probably corrupt re-upload"
            % (str(e), str(next_row)),
        )

    list_of_cadets = get_list_of_cadets()
    if cadet in list_of_cadets:
        ## MATCHED
        print("Cadet %s matched" % str(cadet))
        return process_row_when_cadet_matched(state_data=state_data, cadet=cadet)
    else:
        ## NOT MATCHED
        print("Cadet %s not matched" % str(cadet))
        return process_row_when_cadet_unmatched(state_data=state_data, cadet=cadet)


def process_row_when_cadet_matched(
    state_data: StateDataForAction, cadet: Cadet
) -> Html:
    event = get_event_from_state(state_data)
    next_row = get_first_unmapped_row_for_event(event)
    print("adding matched row %s with id %s" % (str(next_row), cadet.id))
    add_row_data_with_id_included_and_delete_from_unmapped_data(event=event, new_row=next_row, cadet_id=cadet.id)
    ## run recursively until no more data
    return process_rows_of_unmapped_data_and_proceed_to_process_file_with_ids(state_data)


def process_row_when_cadet_unmatched(
    state_data: StateDataForAction, cadet: Cadet
) -> Html:
    ## Need to display a form with 'verification' text'
    # Also need to change state so will get callback on post
    state_data.stage = WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE

    return get_add_or_select_existing_cadet_form(
        cadet=cadet,
        state_data=state_data,
        see_all_cadets=False,
        include_final_button=False
    )


## POST RESPONSE WHEN BUTTONS PRESSED (from generate_page in events action)
def post_response_when_adding_cadet_ids_to_event(
    state_data: StateDataForAction,
) -> Html:
    ## don't need to check for post as will always be one
    last_button_pressed = state_data.last_button_pressed()
    if (
        last_button_pressed == CHECK_CADET_BUTTON_LABEL
        or last_button_pressed == SEE_SIMILAR_CADETS_ONLY_LABEL
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            state_data=state_data,
            include_final_button=True,
            see_all_cadets=False
        )

    elif last_button_pressed == SEE_ALL_CADETS_BUTTON_LABEL:
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            state_data=state_data,
            include_final_button=True,
            see_all_cadets=True
        )

    elif last_button_pressed == FINAL_CADET_ADD_BUTTON_LABEL:
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added(state_data)

    else:
        ## must be an existing cadet that has been selected
        # no need to reset stage
        return process_form_when_existing_cadet_chosen(state_data=state_data)


def process_form_when_verified_cadet_to_be_added(
    state_data: StateDataForAction
) -> Html:
    try:
        cadet = add_cadet_from_form_to_data(state_data=state_data)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return process_row_when_cadet_matched(state_data=state_data, cadet=cadet)


def process_form_when_existing_cadet_chosen(state_data: StateDataForAction) -> Html:
    cadet_selected = state_data.last_button_pressed()

    try:
        confirm_cadet_exists(cadet_selected)
    except:
        raise Exception("Cadet selected no longer exists - file corruption or someone deleted?",
        )

    cadet = get_cadet_from_list_of_cadets(cadet_selected)

    return process_row_when_cadet_matched(state_data=state_data, cadet=cadet)


def action_when_reached_end_of_data(state_data: StateDataForAction) -> Html:
    ## We now have dealt with the staging file, plus we have no unmatched events

    return process_file_with_ids_to_remove_duplicate_cadets(state_data)


