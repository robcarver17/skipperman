from typing import Union


from app.frontend.events.registration_details.registration_details_form import (
    get_registration_data,
    get_top_row_for_table_of_registration_details,
    row_for_cadet_in_event,
)
from app.frontend.events.registration_details.parse_registration_details_form import (
    parse_registration_details_from_form,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_tables import Table
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    cancel_menu_button,
    save_menu_button,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.cadets.ENTRY_view_cadets import sort_buttons, all_sort_types
from app.OLD_backend.data.cadets import SORT_BY_SURNAME
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import Event


def display_form_edit_registration_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    sort_order = interface.get_persistent_value(SORT_ORDER, SORT_BY_SURNAME)

    return display_form_edit_registration_details_given_event_and_sort_order(
        event=event, sort_order=sort_order, interface=interface
    )


def display_form_edit_registration_details_given_event_and_sort_order(
    interface: abstractInterface, event: Event, sort_order: str
) -> Union[Form, NewForm]:
    table = get_registration_details_inner_form_for_event(
        interface=interface, event=event, sort_order=sort_order
    )

    return Form(
        ListOfLines(
            [
                nav_buttons,
                _______________,
                Line(
                    Heading("Registration details for %s" % event, centred=True, size=4)
                ),
                _______________,
                sort_buttons,
                _______________,
                table,
                _______________,
                nav_buttons,
            ]
        )
    )


nav_buttons = ButtonBar([cancel_menu_button, save_menu_button])


def get_registration_details_inner_form_for_event(
    interface: abstractInterface, event: Event, sort_order: str
) -> Table:
    registration_details = get_registration_data(
        event=event, sort_order=sort_order, interface=interface
    )
    top_row = get_top_row_for_table_of_registration_details(
        all_columns=registration_details.all_columns_excluding_special_fields
    )
    rows_in_table = [
        row_for_cadet_in_event(
            cadet=cadet,
            registration_details=registration_details,
        )
        for cadet in registration_details.registration_data.list_of_cadets()
    ]

    return Table(
        [top_row] + rows_in_table, has_row_headings=True, has_column_headings=True
    )


def post_form_edit_registration_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set


    last_button_pressed = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)

    elif save_menu_button.pressed(last_button_pressed):
        event = get_event_from_state(interface)
        parse_registration_details_from_form(interface=interface, event=event)
        interface.flush_cache_to_store()

    elif last_button_pressed in all_sort_types:
        ## no change to stage required, just sort order
        sort_order = interface.last_button_pressed()
        interface.set_persistent_value(SORT_ORDER, sort_order)

    else:
        button_error_and_back_to_initial_state_form(interface)

    return display_form_edit_registration_details(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_registration_details
    )


SORT_ORDER = "sort_order"
