from typing import Union

from app.data_access.configuration.fixed import ADD_KEYBOARD_SHORTCUT
from app.frontend.events.add_event import display_form_view_for_add_event
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.event_selection import display_list_of_events_with_buttons, sort_buttons_for_event_list
from app.frontend.shared.events_state import (
 update_state_for_specific_event,
)

from app.frontend.shared.buttons import is_button_sort_order, \
    sort_order_from_button_pressed, is_button_event_selection, \
    event_from_button_pressed

from app.frontend.events.view_individual_events import (
    display_form_view_individual_event,
)
from app.objects.events import SORT_BY_START_DSC

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

ADD_EVENT_BUTTON_LABEL = "Add event"


def display_form_view_of_events(interface: abstractInterface):
    return display_form_view_of_events_sort_order_passed(
        sort_by=SORT_BY_START_DSC, interface=interface
    )


def display_form_view_of_events_sort_order_passed(
    interface: abstractInterface, sort_by: str = SORT_BY_START_DSC
):
    list_of_events_with_buttons = display_list_of_events_with_buttons(
        interface=interface, sort_by=sort_by
    )
    navbar = ButtonBar([main_menu_button, add_button, help_button])

    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            sort_buttons_for_event_list,
            _______________,
            list_of_events_with_buttons,
        ]
    )

    return Form(contents_of_form)


add_button = Button(
    ADD_EVENT_BUTTON_LABEL, nav_button=True, shortcut=ADD_KEYBOARD_SHORTCUT
)
help_button = HelpButton("view_list_of_events_help")


def post_form_view_of_events(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if add_button.pressed(button_pressed):
        return form_for_add_event(interface)
    elif is_button_sort_order(button_pressed):
        ## no change to stage required
        sort_by = sort_order_from_button_pressed(button_pressed)
        return display_form_view_of_events_sort_order_passed(
            interface=interface, sort_by=sort_by
        )
    elif is_button_event_selection(button_pressed):
        return action_when_event_button_clicked(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)



def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event = event_from_button_pressed(value_of_button_pressed=interface.last_button_pressed(), object_store=interface.object_store)
    update_state_for_specific_event(interface=interface, event=event)

    return form_for_view_event(interface)


def form_for_add_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_for_add_event)


def form_for_view_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_individual_event)

