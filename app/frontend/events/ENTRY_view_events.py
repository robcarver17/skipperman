from typing import Union

from app.frontend.events.add_event import display_form_view_for_add_event
from app.frontend.shared.events_state import (
    update_state_for_specific_event_given_event_description,
)
from app.backend.events.list_of_events import get_sorted_list_of_events
from app.backend.events.list_of_events import all_sort_types_for_event_list, sort_buttons_for_event_list

from app.frontend.events.view_individual_events import display_form_view_individual_event
from app.objects.events import SORT_BY_START_DSC, ListOfEvents

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
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
    navbar = ButtonBar([main_menu_button, add_button])

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

add_button = Button(ADD_EVENT_BUTTON_LABEL, nav_button=True)

def post_form_view_of_events(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if add_button.pressed(button_pressed):
        return form_for_add_event(interface)
    elif button_pressed in all_sort_types_for_event_list:
        ## no change to stage required
        sort_by = interface.last_button_pressed()
        return display_form_view_of_events_sort_order_passed(
            interface=interface, sort_by=sort_by
        )
    else:  ## must be an event
        return action_when_event_button_clicked(interface)


def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event_description_selected = interface.last_button_pressed()
    update_state_for_specific_event_given_event_description(
        interface=interface, event_description=event_description_selected
    )

    return form_for_view_event(interface)


def display_list_of_events_with_buttons(
    interface: abstractInterface, sort_by=SORT_BY_START_DSC
) -> Line:
    list_of_events = get_sorted_list_of_events(
        object_store=interface.object_store, sort_by=sort_by
    )
    return display_given_list_of_events_with_buttons(list_of_events)


def display_given_list_of_events_with_buttons(list_of_events: ListOfEvents) -> Line:
    list_of_event_descriptions = list_of_events.list_of_event_descriptions
    list_with_buttons = [
        Button(event_description, tile=True)
        for event_description in list_of_event_descriptions
    ]

    return Line(list_with_buttons)


def form_for_add_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_for_add_event)


def form_for_view_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_individual_event)
