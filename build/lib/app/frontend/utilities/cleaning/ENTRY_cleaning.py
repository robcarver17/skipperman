from typing import Union

from app.backend.events.cleaning import clean_sensitive_data_for_event
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_text import Heading

from app.frontend.shared.event_selection import (
    display_given_list_of_events_with_buttons,
)
from app.backend.events.list_of_events import (
    get_sorted_list_of_events,
    all_sort_types_for_event_list,
)
from app.frontend.shared.buttons import (
    is_button_sort_order,
    sort_order_from_button_pressed,
    is_button_event_selection,
    event_from_button_pressed,
    get_button_value_for_sort_order,
)
from app.objects.events import SORT_BY_START_DSC, ListOfEvents

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    HelpButton,
    back_menu_button,
    Button,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)


def display_form_for_event_cleaning(interface: abstractInterface):
    return display_form_for_event_cleaning_sort_order_passed(
        sort_by=SORT_BY_START_DSC, interface=interface
    )


def display_form_for_event_cleaning_sort_order_passed(
    interface: abstractInterface, sort_by: str = SORT_BY_START_DSC
):
    list_of_events_with_buttons = (
        display_list_of_events_with_buttons_ignoring_future_events(
            interface=interface, sort_by=sort_by
        )
    )
    navbar = ButtonBar([back_menu_button, HelpButton("event_cleaning_help")])

    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            Heading(
                "Choose event to remove sensitive data for. Only events that have finished are shown.",
                size=2,
            ),
            Heading(
                "WARNING CANNOT BE UNDONE EXCEPT VIA RESTORE BACKUP OR RESTORE SNAPSHOT! You will not be asked to confirm your choice.",
                size=4,
            ),
            _______________,
            sort_buttons_for_event_list,
            _______________,
            list_of_events_with_buttons,
        ]
    )

    return Form(contents_of_form)


def post_form_view_of_event_data_cleaning(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            display_form_for_event_cleaning
        )
    elif is_button_sort_order(button_pressed):
        ## no change to stage required
        sort_by = sort_order_from_button_pressed(button_pressed)
        return display_form_for_event_cleaning_sort_order_passed(
            interface=interface, sort_by=sort_by
        )
    elif is_button_event_selection(button_pressed):
        return action_when_event_button_clicked(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event = event_from_button_pressed(
        value_of_button_pressed=interface.last_button_pressed(),
        object_store=interface.object_store,
    )
    
    clean_sensitive_data_for_event(object_store=interface.object_store, event=event)
    interface.flush_and_clear()

    interface.log_error("Cleaned sensitive data for event %s" % str(event))

    return interface.get_new_display_form_for_parent_of_function(display_form_for_event_cleaning)


def display_list_of_events_with_buttons_ignoring_future_events(
    interface: abstractInterface, sort_by=SORT_BY_START_DSC
) -> Line:
    list_of_events = get_sorted_list_of_events(
        object_store=interface.object_store, sort_by=sort_by
    )
    list_of_events = ListOfEvents(
        [event for event in list_of_events if event.in_the_past()]
    )

    return display_given_list_of_events_with_buttons(list_of_events)


sort_buttons_for_event_list = ButtonBar(
    [
        Button(
            label=sortby, value=get_button_value_for_sort_order(sortby), nav_button=True
        )
        for sortby in all_sort_types_for_event_list
    ]
)
