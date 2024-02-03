from typing import Union

from app.logic.events.registration_details.registration_details_form import get_registration_data, \
    get_top_row_for_table_of_registration_details, row_for_cadet_in_event
from app.logic.events.registration_details.parse_registration_details_form import parse_registration_details_from_form
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm
)
from app.objects.abstract_objects.abstract_tables import Table
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, Button
from app.logic.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.logic.cadets.view_cadets import sort_buttons, all_sort_types
from app.backend.cadets import SORT_BY_SURNAME
from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.objects.events import Event


# EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE
def display_form_edit_registration_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    sort_order = interface.get_persistent_value(SORT_ORDER, SORT_BY_SURNAME)

    return display_form_edit_registration_details_given_event_and_sort_order(
        event=event,
        sort_order=sort_order
    )

def display_form_edit_registration_details_given_event_and_sort_order(
        event: Event,
        sort_order: str
) -> Union[Form, NewForm]:

    table = get_registration_details_inner_form_for_event(event, sort_order=sort_order)

    return Form(
        ListOfLines(
            [
                "Registration details for %s" % event,
                "(Excludes group allocation and volunteer information; plus cadet name/DOB - edit in the appropriate places)",
                "*CHECK FOOD PREFERENCES - autocompleted and may not be accurate*",
                _______________,
                back_button,
                "Always save before sorting - sorting will lose any edits",
                sort_buttons,
                _______________,

                save_button,
                table,
                save_button,
                back_button

            ]
        )
    )

save_button = Button(SAVE_CHANGES, big=True)
back_button = Button(BACK_BUTTON_LABEL)

def get_registration_details_inner_form_for_event(
    event: Event,
        sort_order: str
) -> Table:
    registration_details = get_registration_data(event=event, sort_order=sort_order)
    top_row = get_top_row_for_table_of_registration_details(all_columns=registration_details.all_columns_excluding_special_fields)
    rows_in_table = [
        row_for_cadet_in_event(row_in_event=row_in_event, registration_details=registration_details)
                     for row_in_event in registration_details.master_event_details]

    return Table([top_row]+rows_in_table)




def post_form_edit_registration_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    event = get_event_from_state(interface)

    last_button_pressed = interface.last_button_pressed()

    if interface.last_button_pressed() == BACK_BUTTON_LABEL:
        return NewForm(VIEW_EVENT_STAGE)

    elif last_button_pressed in all_sort_types:
        ## no change to stage required, just sort order
        sort_order = interface.last_button_pressed()
        interface.set_persistent_value(SORT_ORDER, sort_order)

        return display_form_edit_registration_details(interface)

    elif last_button_pressed==SAVE_CHANGES:
        parse_registration_details_from_form(interface=interface, event=event)
        return display_form_edit_registration_details(interface)

    else:
        button_error_and_back_to_initial_state_form(interface)