from typing import Union
from app.logic.events.utilities import get_list_of_events

from app.logic.forms_and_interfaces.abstract_form import Button, Form, ListOfLines, _______________, Line, NewForm, main_menu_button
from app.logic.events.constants import ADD_EVENT_BUTTON_LABEL, ADD_EVENT_STAGE, VIEW_EVENT_STAGE, SORT_BY_START_ASC, \
    SORT_BY_START_DSC, SORT_BY_NAME
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface


def display_form_view_of_events(
    sort_by: str = SORT_BY_START_DSC
):
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
        return display_form_view_of_events(sort_by=sort_by)
    else:  ## must be an event
        return NewForm(VIEW_EVENT_STAGE)

def display_list_of_events_with_buttons(sort_by=SORT_BY_START_DSC) -> ListOfLines:
    list_of_events = get_list_of_events(sort_by=sort_by)

    list_with_buttons = [
        Line(Button(str(event))) for event in list_of_events
    ]

    return ListOfLines(list_with_buttons)


all_sort_types = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]
sort_buttons = Line([Button(sortby) for sortby in all_sort_types])


