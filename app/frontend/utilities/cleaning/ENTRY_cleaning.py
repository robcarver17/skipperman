from typing import Union

from app.backend.events.cleaning import clean_sensitive_data_for_event
from app.objects.abstract_objects.abstract_text import Heading

from app.frontend.events.ENTRY_view_events import (
    display_given_list_of_events_with_buttons,
)
from app.backend.events.list_of_events import (
    get_sorted_list_of_events,
    all_sort_types_for_event_list,
    sort_buttons_for_event_list,
    get_event_from_list_of_events_given_event_description,
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
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
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
            Heading("Choose event to remove sensitive data for", size=2),
            Heading(
                "WARNING CANNOT BE UNDONE EXCEPT VIA BACKUP OR SNAPSHOT RESTORE! You will not be asked to confirm your choice.",
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
        interface.flush_cache_to_store()
        return interface.get_new_display_form_for_parent_of_function(
            display_form_for_event_cleaning
        )
    if button_pressed in all_sort_types_for_event_list:
        ## no change to stage required
        sort_by = interface.last_button_pressed()
        return display_form_for_event_cleaning_sort_order_passed(
            interface=interface, sort_by=sort_by
        )
    else:  ## must be an event
        return action_when_event_button_clicked(interface)


def action_when_event_button_clicked(interface: abstractInterface) -> Form:
    event_description = interface.last_button_pressed()
    event = get_event_from_list_of_events_given_event_description(
        object_store=interface.object_store, event_description=event_description
    )
    clean_sensitive_data_for_event(object_store=interface.object_store, event=event)
    interface.flush_cache_to_store()
    return form_with_message_and_finished_button(
        "Cleaned sensitive data for event %s" % str(event),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_for_event_cleaning,
    )


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
