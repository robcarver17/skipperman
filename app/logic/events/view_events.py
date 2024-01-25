from typing import Union
from app.logic.events.events_in_state import get_list_of_events, confirm_event_exists, update_state_for_specific_event

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
    SORT_BY_START_ASC,
    SORT_BY_START_DSC,
    SORT_BY_NAME,
)
from app.logic.abstract_interface import abstractInterface


def display_form_view_of_events( interface: abstractInterface, sort_by: str = SORT_BY_START_DSC):
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
        return display_form_view_of_events(interface=interface, sort_by=sort_by)
    else:  ## must be an event
        event_name_selected = button_pressed

        try:
            confirm_event_exists(event_name_selected)
            ## so whilst we are in this stage, we know which event we are talking about
            update_state_for_specific_event(
                interface=interface, event_selected=event_name_selected
            )
        except:
            ## Must have been redirected from further forward
            interface.log_error(
                "Event %s not recognised - corrupt data?" % button_pressed
            )

        return NewForm(VIEW_EVENT_STAGE)


def display_list_of_events_with_buttons(sort_by=SORT_BY_START_DSC) -> ListOfLines:
    list_of_events = get_list_of_events(sort_by=sort_by)

    list_with_buttons = [Line(Button(str(event))) for event in list_of_events]

    return ListOfLines(list_with_buttons)


all_sort_types = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]
sort_buttons = Line([Button(sortby) for sortby in all_sort_types])
