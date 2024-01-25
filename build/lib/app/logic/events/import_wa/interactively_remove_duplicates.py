from typing import Union

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_interface import abstractInterface
from app.logic.events.constants import WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE

from app.logic.events.events_in_state import get_event_from_state

from app.backend.load_and_save_wa_mapped_events import (
load_existing_mapped_wa_event_with_ids
)

from app.backend.update_master_event_data import remove_duplicated_row_from_mapped_wa_event_data

from app.objects.constants import  NoMoreData

def display_form_interactively_remove_duplicates_during_import(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    print("Now removing duplicate cadets")
    input("Press enter to continue")

    try:
        get_first_set_of_duplicate_rows_from_state_date(interface)
    except NoMoreData:
        # next stage
        return NewForm(WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE)
    else:
        return interactively_remove_specific_duplicates_from_wa_file(
            interface
        )


def get_first_set_of_duplicate_rows_from_state_date(interface: abstractInterface) -> list:
    event = get_event_from_state(interface)
    mapped_event = load_existing_mapped_wa_event_with_ids(event)
    index_of_duplicate_cadet_ids = mapped_event.index_of_duplicate_cadet_ids_ignore_cancelled_and_deleted()

    if len(index_of_duplicate_cadet_ids) == 0:
        # no more duplicates next stage
        raise NoMoreData

    list_of_duplicates = index_of_duplicate_cadet_ids[0]
    list_of_duplicate_rows = [
        mapped_event[idx] for idx in list_of_duplicates
    ]

    return list_of_duplicate_rows


def interactively_remove_specific_duplicates_from_wa_file(interface: abstractInterface
) -> Union[Form, NewForm]:
    ## FIXME ONLY WANT TO DO THIS ONCE PER FILE...?
    list_of_duplicate_rows = get_first_set_of_duplicate_rows_from_state_date(interface)

    duplicate_rows = ListOfLines([
        "Row %d: %s" % (idx, str(row))
             for idx, row in enumerate(list_of_duplicate_rows)
    ])

    line_of_buttons = Line(
        [
            from_row_number_to_button(row_number)
            for row_number in range(len(duplicate_rows))
        ]
    )

    return Form(

                ListOfLines(
                    [
                        "Following cadets duplicated in WA file (probably cancel and re-entry)",
                        _______________,
                        duplicate_rows,
                        _______________,
                        _______________,
                        "Choose the row to keep (others will be ignored)",
                        line_of_buttons
                    ]
                )
            )


def from_row_number_to_button(row_number) -> Button:
    return Button("Row %d" % row_number)


def from_row_text_to_row_number(row_text: str):
    return int(row_text.split(" ")[1])


def post_form_interactively_remove_duplicates_during_import(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    ## don't need to check for post as will always be one
    list_of_duplicate_rows = get_first_set_of_duplicate_rows_from_state_date(interface)
    button_pressed = interface.last_button_pressed()
    row_number = from_row_text_to_row_number(button_pressed)

    try:
        assert row_number in range(len(list_of_duplicate_rows))
    except:
        # ERROR - tidying up will be handled upstream
        raise Exception("Mismatch in duplicate row buttons - try reloading and reimporting file")

    # delete duplicate row from file
    ## FIXME DOESN'T ACTUALLY REMOVE DUPLICATES!!!
    duplicate_row_idx = list_of_duplicate_rows[row_number]

    event = get_event_from_state(interface)
    remove_duplicated_row_from_mapped_wa_event_data(event=event, idx=duplicate_row_idx)

    ## iterate again
    return display_form_interactively_remove_duplicates_during_import(interface)





