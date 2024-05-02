from typing import Union

from app.objects.abstract_objects.abstract_text import Heading

from app.logic.events.ENTRY_view_events import display_given_list_of_events_with_buttons
from app.backend.events import sort_buttons_for_event_list
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button, ButtonBar
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.data.security import  get_volunteer_id_of_logged_in_user_or_superuser, SUPERUSER
from app.objects.events import ListOfEvents, Event
from app.backend.data.events import get_list_of_all_events

def display_form_main_instructors_page(interface: abstractInterface) -> Form:
    event_buttons = get_event_buttons(interface)
    navbar = ButtonBar([main_menu_button])
    sort_buttons = sort_buttons_for_event_list
    header = Line(Heading("Tick sheets and reports for instructors: Select event", centred=False, size=4))
    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header,
            _______________,
            _______________,
            sort_buttons,
            _______________,
            event_buttons

        ]
    )

    return Form(lines_inside_form)

def post_form_main_instructors_page(interface: abstractInterface) -> Form:
    button_pressed = interface.last_button_pressed()
    if button_pressed == ADD_EVENT_BUTTON_LABEL:
        return form_for_add_event(interface)
    elif button_pressed in all_sort_types:
        ## no change to stage required
        sort_by = interface.last_button_pressed()
        return display_form_view_of_events_sort_order_passed(interface=interface, sort_by=sort_by)
    else:  ## must be an event
        return action_when_event_button_clicked(interface)


def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event_description_selected = interface.last_button_pressed()
    confirm_event_exists_given_description(event_description_selected)
    update_state_for_specific_event_given_event_description(
        interface=interface, event_description=event_description_selected)

    return form_for_view_event(interface)


def get_event_buttons(interface: abstractInterface) -> Line:
    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser(interface)
    list_of_events = get_list_of_events_entitled_to_see(interface=interface, volunteer_id=volunteer_id)
    return display_given_list_of_events_with_buttons(list_of_events)

def get_list_of_events_entitled_to_see(interface: abstractInterface, volunteer_id: str):
    all_events = get_list_of_all_events(interface)
    all_events = ListOfEvents([event for event in all_events if can_volunteer_id_see_event(interface=interface,
                                                                                           event=event,
                                                                                           volunteer_id=volunteer_id)])

    return all_events

def can_volunteer_id_see_event(interface: abstractInterface, event: Event, volunteer_id: str):
    if volunteer_id==SUPERUSER:
        return True
    else:
        interface.log_error("Instructors can't yet see any tick sheets - feature needs implementing")
        return False