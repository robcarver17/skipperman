from typing import Union

from app.data_access.configuration.fixed import ADD_KEYBOARD_SHORTCUT
from app.frontend.events.registration_details.add_unregistered_cadet import \
    display_add_unregistered_cadet_from_registration_form
from app.frontend.events.registration_details.registration_details_form import (
    get_registration_details_inner_form_for_event,
)
from app.frontend.events.registration_details.parse_registration_details_form import (
    parse_registration_details_from_form,
)
from app.frontend.shared.buttons import get_button_value_for_sort_order
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    cancel_menu_button,
    save_menu_button,
    HelpButton, Button,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.backend.cadets.list_of_cadets import all_sort_types
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import Event
from app.objects.exceptions import arg_not_passed


def display_form_edit_registration_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    sort_order = get_sort_order_for_registration(interface)

    return display_form_edit_registration_details_given_event_and_sort_order(
        event=event, sort_order=sort_order, interface=interface
    )


def display_form_edit_registration_details_given_event_and_sort_order(
    interface: abstractInterface, event: Event, sort_order: str
) -> Union[Form, NewForm]:
    table = get_registration_details_inner_form_for_event(
        interface=interface, event=event, sort_order=sort_order
    )
    sort_buttons = get_sort_buttons()
    return Form(
        ListOfLines(
            [
                nav_buttons_top,
                _______________,
                Line(
                    Heading("Registration details for %s" % event, centred=True, size=4)
                ),
                _______________,
                sort_buttons,
                _______________,
                table,
                _______________,
                nav_buttons_bottom,
            ]
        )
    )


help_button = HelpButton("registration_editing_help")
add_button = Button("Add unregistered sailor", nav_button=True, shortcut=ADD_KEYBOARD_SHORTCUT)

nav_buttons_top = ButtonBar([cancel_menu_button, save_menu_button, help_button])
nav_buttons_bottom = ButtonBar([cancel_menu_button, save_menu_button, add_button, help_button])

from app.frontend.shared.buttons import is_button_sort_order, sort_order_from_button_pressed

def post_form_edit_registration_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    last_button_pressed = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)

    elif add_button.pressed(last_button_pressed):
        return interface.get_new_form_given_function(display_add_unregistered_cadet_from_registration_form)

    elif save_menu_button.pressed(last_button_pressed):
        save_details_from_form(interface)

    elif is_button_sort_order(last_button_pressed):
        ## no change to stage required, just sort order
        sort_order =  sort_order_from_button_pressed(last_button_pressed)
        set_sort_order_in_state(interface=interface, sort_order=sort_order)

    elif clear_sort_button.pressed(last_button_pressed):
        clear_sort_order_in_state(interface)

    else:
        button_error_and_back_to_initial_state_form(interface)

    return display_form_edit_registration_details(interface)

def save_details_from_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    parse_registration_details_from_form(interface=interface, event=event)
    interface.save_cache_to_store_without_clearing()

def previous_form(interface: abstractInterface):
    interface.flush_cache_to_store()
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_registration_details
    )


def get_sort_order_for_registration(interface: abstractInterface):
    sort_order = interface.get_persistent_value(SORT_ORDER, default=arg_not_passed)

    return sort_order

def set_sort_order_in_state(interface: abstractInterface, sort_order: str):
    interface.set_persistent_value(SORT_ORDER, sort_order)

def clear_sort_order_in_state(interface: abstractInterface):
    interface.clear_persistent_value(SORT_ORDER)

SORT_ORDER = "sort_order_registration_data"

def get_sort_buttons():
    sort_buttons_list = [Button(label=sort_by, value=get_button_value_for_sort_order(sort_by),
                                nav_button=True) for sort_by in all_sort_types]

    sort_buttons = ButtonBar(sort_buttons_list+[clear_sort_button])

    return sort_buttons

clear_sort_button = Button(label="Sort by registration order", nav_button=True)
