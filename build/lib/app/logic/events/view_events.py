from typing import Union
from app.logic.events.events_in_state import update_state_for_specific_event_given_event_description
from app.backend.events import get_sorted_list_of_events, confirm_event_exists_given_description
from app.objects.events import SORT_BY_START_ASC, SORT_BY_NAME, SORT_BY_START_DSC

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.events.constants import (
    ADD_EVENT_BUTTON_LABEL,
    ADD_EVENT_STAGE,
    VIEW_EVENT_STAGE,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

def display_form_view_of_events( interface: abstractInterface):
    return display_form_view_of_events_sort_order_passed(sort_by=SORT_BY_START_DSC, interface=interface)

def display_form_view_of_events_sort_order_passed( interface: abstractInterface, sort_by: str = SORT_BY_START_DSC):
    list_of_events_with_buttons = display_list_of_events_with_buttons(sort_by=sort_by)
    add_button = Button(ADD_EVENT_BUTTON_LABEL)

    contents_of_form = ListOfLines(
        [
            main_menu_button,
            _______________,
            sort_buttons,
            _______________,
            "Click on any event to view/edit/delete/upload/allocate/anything else",
            _______________,
            add_button,
            _______________,
            list_of_events_with_buttons,
        ]
    )

    return Form(contents_of_form)


def post_form_view_of_events(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == ADD_EVENT_BUTTON_LABEL:
        return NewForm(ADD_EVENT_STAGE)
    elif button_pressed in all_sort_types:
        ## no change to stage required
        sort_by = interface.last_button_pressed()
        return display_form_view_of_events_sort_order_passed(interface=interface, sort_by=sort_by)
    else:  ## must be an event
        return action_when_event_button_clicked(interface)

def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event_description_selected = interface.last_button_pressed()
    print("selected %s" % event_description_selected)

    confirm_event_exists_given_description(event_description_selected)
    ## so whilst we are in this stage, we know which event we are talking about
    print("updating state for %s" % event_description_selected)
    update_state_for_specific_event_given_event_description(
        interface=interface, event_description=event_description_selected)

    return NewForm(VIEW_EVENT_STAGE)


def display_list_of_events_with_buttons(sort_by=SORT_BY_START_DSC) -> ListOfLines:
    list_of_events = get_sorted_list_of_events(sort_by=sort_by)
    list_of_event_descriptions = list_of_events.list_of_event_descriptions
    list_with_buttons = [Line(Button(event_description)) for event_description in list_of_event_descriptions]

    return ListOfLines(list_with_buttons)


all_sort_types = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]
sort_buttons = Line([Button(sortby) for sortby in all_sort_types])
