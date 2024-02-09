
from app.web.html.html import Html, html_joined_list_as_lines, html_joined_list, html_joined_list_as_paragraphs
from app.web.html.forms import html_button, form_html_wrapper
from app.web.flask.state_for_action import StateDataForAction

from app.web.events.utils import get_event_from_state
from app.web.events.constants import (
WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE
)
from app.web.events.WA.process_staged_files.process_file_to_update_master_event_records import process_file_to_update_master_event_records
from app.backend.data.mapped_events import load_existing_mapped_wa_event_with_ids

from app.backend.wa_import.update_master_event_data import remove_duplicated_row_from_mapped_wa_event_data

from app.objects.constants import  NoMoreData

def process_file_with_ids_to_remove_duplicate_cadets(state_data: StateDataForAction)-> Html:
    print("Now removing duplicate group_allocations")
    input("Press enter to continue")

    try:
        get_first_set_of_duplicate_rows_from_state_date(state_data)
    except NoMoreData:
        # next stage
        return action_to_take_when_all_duplicated_rows_removed(state_data)
    else:
        return interactively_remove_specific_duplicates_from_wa_file(
            state_data=state_data
        )

def get_first_set_of_duplicate_rows_from_state_date(state_data: StateDataForAction) -> list:
    event = get_event_from_state(state_data)
    mapped_event = load_existing_mapped_wa_event_with_ids(event)
    index_of_duplicate_cadet_ids = mapped_event.index_of_duplicate_cadet_ids_ignore_cancelled_and_deleted()

    if len(index_of_duplicate_cadet_ids)==0:
        # next stage
        raise NoMoreData

    list_of_duplicates = index_of_duplicate_cadet_ids[0]
    list_of_duplicate_rows = [
        mapped_event[idx] for idx in list_of_duplicates
    ]

    return list_of_duplicate_rows

def interactively_remove_specific_duplicates_from_wa_file(state_data: StateDataForAction,
                                                          )-> Html:
    state_data.stage = WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE
    list_of_duplicate_rows = get_first_set_of_duplicate_rows_from_state_date(state_data)

    html_list_of_rows = html_joined_list_as_lines([
        Html("Row %d: %s" % (idx, str(row))
             for idx, row in enumerate(list_of_duplicate_rows))
    ])

    html_buttons = html_joined_list(
        [
            from_row_number_to_button(row_number)
            for row_number in range(len(html_list_of_rows))
        ]
    )

    form_wrapper = form_html_wrapper(state_data.current_url)
    return form_wrapper.wrap_around(
        html_joined_list_as_paragraphs(
            [
                "Following group_allocations duplicated in WA file (probably cancel and re-entry)",
                html_list_of_rows,
                "Choose the row to keep (others will be ignored)",
                html_buttons
            ]
        )
    )

def from_row_number_to_button(row_number):
    return html_button("Row %d" % row_number)

def from_row_text_to_row_number(row_text:str):
    return int(row_text.split(" ")[1])

def post_response_of_removing_specific_duplicates_from_mapped_wa_event_data(state_data: StateDataForAction):
    list_of_duplicate_rows = get_first_set_of_duplicate_rows_from_state_date(state_data)
    button_pressed = state_data.last_button_pressed()
    row_number = from_row_text_to_row_number(button_pressed)

    try:
        assert row_number in range(len(list_of_duplicate_rows))
    except:
        # ERROR - tidying up will be handled upstream
        raise Exception("Mismatch in duplicate row buttons - try reloading and reimporting file")

    # delete duplicate row from file
    duplicate_row_idx = list_of_duplicate_rows[row_number]

    event = get_event_from_state(state_data)
    remove_duplicated_row_from_mapped_wa_event_data(event=event, idx=duplicate_row_idx)

    ## iterate again
    return process_file_with_ids_to_remove_duplicate_cadets(state_data)

def action_to_take_when_all_duplicated_rows_removed(state_data: StateDataForAction) ->Html:
    return process_file_to_update_master_event_records(state_data)



